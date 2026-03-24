"""
UnifiedSubmissionService — Single evaluation entry point for all challenge types.

ALL challenge submissions pass through here regardless of challenge_mode.
Mode affects feedback formatting only — core evaluation, ConceptMastery,
spaced repetition, analytics, and Elo/archetype updates always run.

Beginner response layer is additive: applied after core evaluation when
user.is_beginner_mode is True. It does NOT expose mastery_delta, elo_update,
or difficulty_adjustment to the serialized response.
"""

import logging
import time
from typing import Optional
from datetime import datetime

from app.extensions import db
from app.models import User, Challenge, Analytics
from app.services.sandbox import MultiLanguageSandbox
from app.services.misconception_detector import MisconceptionDetector
from app.services.cognitive_engine import CognitiveEngine
from app.services.mascot_engine import MascotEngine
from app.services.error_interpreter import ErrorInterpreter
from app.cognitive_models.cognitive import Concept, ConceptMastery

logger = logging.getLogger(__name__)

_sandbox = MultiLanguageSandbox(timeout=15, max_memory_mb=100)


# ─── Public Interface ─────────────────────────────────────────────────────────

class UnifiedSubmissionService:
    """
    Single evaluation pipeline for all challenge types and modes.

    challenge_mode determines scaffold input shape:
      'fill_in_blank'   → user_input: { "filled_blanks": [...] }
      'predict_output'  → user_input: { "prediction": str, "code": str }
      'error_spotting'  → user_input: { "line_number": int, "explanation": str }
      'freeform'        → user_input: { "code": str }
    """

    @staticmethod
    def evaluate(user: User, challenge: Challenge, user_input: dict,
                 time_taken: int = 0, hints_used: int = 0) -> dict:
        """
        Evaluate a challenge submission.

        Returns a response dict whose shape depends on user.is_beginner_mode:
          - beginner=True  → layered feedback + mascot, NO mastery/elo numbers
          - beginner=False → bare result identical to current main engine output
        """
        t_start = time.time()

        # ── 1. Resolve executable code from user input ─────────────────────
        code, prediction = _resolve_code(challenge, user_input)

        # ── 2. Execute (always) ────────────────────────────────────────────
        exec_result = _sandbox.execute_code(code=code, language='python')
        actual_output = (exec_result.get('output') or '').strip()
        raw_error = exec_result.get('error') or ''
        ran_successfully = exec_result.get('success', False) and not raw_error

        # ── 3. Score submission ────────────────────────────────────────────
        passed, score = _score_submission(challenge, exec_result, user_input,
                                          actual_output, prediction)

        # ── 4. Misconception detection (always, stored to DB) ──────────────
        misconceptions = []
        if code.strip():
            try:
                misconceptions = MisconceptionDetector.analyze_code_for_misconceptions(
                    user_id=user.id,
                    code=code,
                    challenge_id=challenge.id,
                    language='python',
                )
            except Exception as e:
                logger.warning(f"Misconception detection error: {e}")

        # ── 5. Concept mastery update (always) ────────────────────────────
        mastery_updates = _update_concept_mastery(user, challenge, passed,
                                                  time_taken, hints_used)

        # ── 6. Spaced repetition (always) ─────────────────────────────────
        _update_spaced_repetition(user, challenge, passed)

        # ── 7. Archetype progress (always, best-effort) ───────────────────
        _update_archetype_progress(user, challenge, score)

        # ── 8. Phase transition check (mutates user.beginner_phase) ────────
        phase_changed, new_phase = _check_phase_transition(user)

        # ── 9. Analytics logging (always) ─────────────────────────────────
        elapsed = time.time() - t_start
        _log_event(user, challenge, user_input, exec_result,
                   misconceptions, elapsed, passed=passed)

        db.session.commit()

        # ── 10. Build response ─────────────────────────────────────────────
        base = {
            'passed': passed,
            'score': score,
            'output': actual_output,
            'error': raw_error or None,
            'ran': ran_successfully,
        }

        if user.is_beginner_mode:
            return _apply_beginner_layer(
                base=base,
                challenge=challenge,
                user=user,
                code=code,
                actual_output=actual_output,
                raw_error=raw_error,
                prediction=prediction,
                misconceptions=misconceptions,
                phase_changed=phase_changed,
                new_phase=new_phase,
            )

        # Non-beginner mode: return base result (identical to main engine)
        return base


# ─── Transition Check ─────────────────────────────────────────────────────────

def run_transition_check(user: User) -> dict:
    """
    Public helper for the /transition-check endpoint.
    Returns transition eligibility and criteria states.
    """
    from app.models import Analytics as AnalyticsModel

    scaffolded_done = _count_passed_by_mode(user.id, 'scaffolded')
    predict_passed = _has_passed_scaffold_type(user.id, 'predict_output')
    spot_passed = _has_passed_scaffold_type(user.id, 'error_spotting')
    freeform_syntax_clean = _has_syntax_free_freeform(user.id)

    # Mastery gate: all linked concepts > 0.35
    mastery_ok = _mastery_gate(user.id, threshold=0.35)
    hint_ratio_ok = _hint_ratio_ok(user.id)

    eligible = (
        user.beginner_phase == 'scaffolded'
        and scaffolded_done >= 4
        and predict_passed
        and spot_passed
    ) or (
        user.beginner_phase == 'guided'
        and freeform_syntax_clean
        and mastery_ok
        and hint_ratio_ok
    ) or (
        user.beginner_phase == 'freeform'
        and _phase_complete_gate(user.id)
    )

    return {
        'current_phase': user.beginner_phase,
        'eligible': eligible,
        'criteria': {
            'scaffolded_completed': scaffolded_done,
            'predict_output_passed': predict_passed,
            'error_spotting_passed': spot_passed,
            'freeform_syntax_clean': freeform_syntax_clean,
            'mastery_gate_ok': mastery_ok,
        },
        'mascot': MascotEngine.respond_to_transition() if eligible else None,
    }


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _resolve_code(challenge: Challenge, user_input: dict):
    """
    Build the executable code string from challenge + user input.
    Also returns the user's prediction (for predict_output challenges).
    """
    scaffold = challenge.scaffold_data or {}
    mode = scaffold.get('type') or challenge.challenge_mode
    prediction = None

    if mode == 'fill_in_blank':
        template = scaffold.get('template', '')
        filled = user_input.get('filled_blanks', [])
        code = template
        for blank_val in filled:
            code = code.replace('___', str(blank_val), 1)
        return code, prediction

    elif mode == 'predict_output':
        prediction = user_input.get('prediction', '').strip()
        # Use provided code or fall back to scaffold template
        code = user_input.get('code') or scaffold.get('code', '')
        return code, prediction

    elif mode == 'error_spotting':
        # Run the buggy code to confirm error, then user edits externally
        code = user_input.get('code') or scaffold.get('buggy_code', '')
        return code, prediction

    else:  # freeform / guided
        code = user_input.get('code', '')
        return code, prediction


def _score_submission(challenge: Challenge, exec_result: dict,
                      user_input: dict, actual_output: str,
                      prediction: Optional[str]) -> tuple:
    """
    Returns (passed: bool, score: float 0.0–1.0).
    Scoring logic varies by scaffold type.
    """
    scaffold = challenge.scaffold_data or {}
    mode = scaffold.get('type') or challenge.challenge_mode

    if mode == 'predict_output':
        # Prediction must match actual output; code must also run
        ran = exec_result.get('success') and not exec_result.get('error')
        prediction_correct = (prediction or '').strip() == actual_output
        passed = ran and prediction_correct
        score = 1.0 if passed else (0.5 if ran else 0.0)
        return passed, score

    elif mode == 'error_spotting':
        # Score: identified line (0.5) + explanation quality (0.5, keyword match)
        expected_line = scaffold.get('fault_line')
        user_line = user_input.get('line_number')
        explanation = (user_input.get('explanation') or '').lower()
        keywords = [k.lower() for k in scaffold.get('fault_keywords', [])]

        line_ok = expected_line and user_line == expected_line
        keyword_ok = any(k in explanation for k in keywords) if keywords else bool(explanation)

        score = (0.5 if line_ok else 0.0) + (0.5 if keyword_ok else 0.0)
        passed = score >= 0.5
        return passed, score

    else:
        # fill_in_blank / freeform / guided: match expected output or test cases
        ran = exec_result.get('success') and not exec_result.get('error')
        if not ran:
            return False, 0.0

        expected = (challenge.expected_output or '').strip()
        if expected:
            passed = actual_output == expected
            return passed, 1.0 if passed else 0.0

        # If test cases exist, use sandbox validation
        test_cases = challenge.test_cases or []
        if test_cases:
            # Basic: output must match first test case expected output
            first_expected = (test_cases[0].get('expected_output') or '').strip()
            passed = actual_output == first_expected
            return passed, 1.0 if passed else 0.0

        # No expected output defined: ran without error = pass
        return ran, 1.0 if ran else 0.0


def _update_concept_mastery(user: User, challenge: Challenge,
                             passed: bool, time_taken: int,
                             hints_used: int) -> list:
    """Update ConceptMastery for all concepts linked to challenge category."""
    updates = []
    try:
        category = challenge.category or ''
        concepts = Concept.query.filter(
            Concept.category.ilike(f'%{category}%')
        ).limit(3).all()

        for concept in concepts:
            update = CognitiveEngine.update_concept_mastery(
                user_id=user.id,
                concept_id=concept.id,
                success=passed,
                time_taken=time_taken,
                hints_used=hints_used,
            )
            updates.append(update)
    except Exception as e:
        logger.warning(f"Concept mastery update error: {e}")
    return updates


def _update_spaced_repetition(user: User, challenge: Challenge, passed: bool):
    """Nudge spaced repetition schedule for concepts linked to challenge."""
    try:
        from datetime import timedelta
        category = challenge.category or ''
        concepts = Concept.query.filter(
            Concept.category.ilike(f'%{category}%')
        ).limit(3).all()

        for concept in concepts:
            mastery = CognitiveEngine.get_or_create_mastery(user.id, concept.id)
            if passed:
                # Increase interval on success
                current_interval = 3
                if mastery.spaced_repetition_due_date and mastery.last_practiced_at:
                    delta = (mastery.spaced_repetition_due_date - mastery.last_practiced_at).days
                    current_interval = max(delta, 1)
                new_interval = min(int(current_interval * 1.5) + 1, 30)
                mastery.spaced_repetition_due_date = (
                    datetime.utcnow() + timedelta(days=new_interval)
                )
            else:
                # Failed — review sooner
                mastery.spaced_repetition_due_date = (
                    datetime.utcnow() + timedelta(days=1)
                )
            mastery.last_practiced_at = datetime.utcnow()
    except Exception as e:
        logger.warning(f"Spaced repetition update error: {e}")


def _update_archetype_progress(user: User, challenge: Challenge, score: float):
    """Best-effort archetype progress update."""
    try:
        from app.services.archetype_engine import ArchetypeEngine
        ArchetypeEngine.update_from_submission(
            user_id=user.id,
            category=challenge.category or '',
            score=score,
        )
    except Exception as e:
        logger.debug(f"Archetype update skipped: {e}")


def _check_phase_transition(user: User) -> tuple:
    """
    Evaluate whether user.beginner_phase should advance.
    Returns (changed: bool, new_phase: str).
    Mutates user.beginner_phase in-place if eligible (not committed yet).
    """
    if not user.is_beginner_mode:
        return False, user.beginner_phase

    current = user.beginner_phase
    new_phase = current

    try:
        if current == 'scaffolded':
            if (
                _count_passed_by_mode(user.id, 'scaffolded') >= 4
                and _has_passed_scaffold_type(user.id, 'predict_output')
                and _has_passed_scaffold_type(user.id, 'error_spotting')
            ):
                new_phase = 'guided'

        elif current == 'guided':
            if (
                _has_syntax_free_freeform(user.id)
                and _mastery_gate(user.id, threshold=0.35)
                and _hint_ratio_ok(user.id)
            ):
                new_phase = 'freeform'

        elif current == 'freeform':
            if _phase_complete_gate(user.id):
                new_phase = 'complete'
                user.is_beginner_mode = False

    except Exception as e:
        logger.warning(f"Phase transition check error: {e}")
        return False, current

    if new_phase != current:
        user.beginner_phase = new_phase
        return True, new_phase

    return False, current


def _log_event(user: User, challenge: Challenge, user_input: dict,
               exec_result: dict, misconceptions: list, elapsed: float,
               passed: bool = False):
    """Log analytics events: scaffolded_interaction, misconception_detected."""
    try:
        scaffold = challenge.scaffold_data or {}
        scaffold_type = scaffold.get('type')

        # scaffolded_interaction — use the real computed 'passed' bool, not sandbox success
        event = Analytics(
            user_id=user.id,
            event_type='scaffolded_interaction',
            event_data={
                'challenge_id': challenge.id,
                'challenge_mode': challenge.challenge_mode,
                'scaffold_type': scaffold_type,
                'beginner_phase': user.beginner_phase,
                'passed': passed,
                'time_to_correct': round(elapsed, 2),
                'user_response': _safe_truncate(user_input),
            },
        )
        db.session.add(event)

        # misconception_detected entries
        for m in misconceptions:
            db.session.add(Analytics(
                user_id=user.id,
                event_type='misconception_detected',
                event_data={
                    'misconception_type': m.get('type'),
                    'challenge_mode': challenge.challenge_mode,
                    'beginner_phase': user.beginner_phase,
                },
            ))
    except Exception as e:
        logger.warning(f"Analytics log error: {e}")


def _apply_beginner_layer(base: dict, challenge: Challenge, user: User,
                          code: str, actual_output: str, raw_error: str,
                          prediction: Optional[str], misconceptions: list,
                          phase_changed: bool, new_phase: str) -> dict:
    """
    Decorate the base result with beginner-specific feedback.
    Does NOT include mastery_delta, elo_update, or difficulty_adjustment.
    """
    scaffold = challenge.scaffold_data or {}
    mode = scaffold.get('type') or challenge.challenge_mode

    # Error translation
    beginner_error = None
    mascot_response = {}

    if raw_error:
        translated = ErrorInterpreter.translate(raw_error, code)
        beginner_error = translated['beginner']
        error_type = translated['error_type']

        # Log mascot translation event
        try:
            db.session.add(Analytics(
                user_id=user.id,
                event_type='mascot_translation',
                event_data={
                    'error_type': error_type,
                    'reasoning_focus': 'logic_error',
                    'intervention_level': 2,
                    'challenge_id': challenge.id,
                },
            ))
        except Exception:
            pass

        challenge_ctx = {
            'title': challenge.title,
            'category': challenge.category,
            'description': challenge.description,
        }
        mascot_response = MascotEngine.respond_to_error(
            error_type=error_type,
            code=code,
            challenge_context=challenge_ctx,
        )

    elif not base['passed'] and mode == 'predict_output' and prediction is not None:
        mascot_response = MascotEngine.respond_to_wrong_prediction()

    elif not base['passed'] and misconceptions:
        mascot_response = MascotEngine.respond_to_misconception(
            misconception_type=misconceptions[0].get('type', 'unknown'),
        )

    elif base['passed']:
        mascot_response = MascotEngine.respond_to_correct(challenge_mode=mode)

    # Build plain-language "what happened" from actual output
    what_happened = _describe_output(actual_output, base['ran'], raw_error)

    # Predict-output: include comparison
    prediction_feedback = None
    if mode == 'predict_output' and prediction is not None:
        prediction_feedback = {
            'your_prediction': prediction,
            'actual_output': actual_output,
            'matched': prediction.strip() == actual_output.strip(),
        }

    # Transition notice
    transition_notice = None
    if phase_changed:
        transition_notice = {
            'previous_phase': _prev_phase(new_phase),
            'new_phase': new_phase,
            'mascot': MascotEngine.respond_to_transition(),
        }

    return {
        **base,
        'what_happened': what_happened,
        'why': _why_text(base['passed'], mode, scaffold),
        'next_step': mascot_response.get('suggested_next_step'),
        'mascot': mascot_response,
        'beginner_error': beginner_error,
        'show_technical_details': raw_error or None,
        'prediction_feedback': prediction_feedback,
        'misconceptions_detected': [m.get('type') for m in misconceptions],
        'transition_notice': transition_notice,
        # mastery_delta, elo_update, difficulty_adjustment intentionally omitted
    }


# ─── Gate Queries ─────────────────────────────────────────────────────────────

def _count_passed_by_mode(user_id: int, mode: str) -> int:
    """Count challenges passed by challenge_mode for this user via Analytics."""
    try:
        events = Analytics.query.filter(
            Analytics.user_id == user_id,
            Analytics.event_type == 'scaffolded_interaction',
        ).all()
        return sum(
            1 for e in events
            if (e.event_data or {}).get('challenge_mode') == mode
            and (e.event_data or {}).get('passed') is True
        )
    except Exception:
        return 0


def _has_passed_scaffold_type(user_id: int, scaffold_type: str) -> bool:
    """Check if user has ever passed a challenge of a specific scaffold type."""
    try:
        events = Analytics.query.filter(
            Analytics.user_id == user_id,
            Analytics.event_type == 'scaffolded_interaction',
        ).all()
        return any(
            (e.event_data or {}).get('scaffold_type') == scaffold_type
            and (e.event_data or {}).get('passed') is True
            for e in events
        )
    except Exception:
        return False


def _has_syntax_free_freeform(user_id: int) -> bool:
    """Check if user has at least one freeform submission without SyntaxError."""
    try:
        events = Analytics.query.filter(
            Analytics.user_id == user_id,
            Analytics.event_type == 'scaffolded_interaction',
        ).all()
        return any(
            (e.event_data or {}).get('challenge_mode') == 'freeform'
            and (e.event_data or {}).get('passed') is True
            for e in events
        )
    except Exception:
        return False


def _mastery_gate(user_id: int, threshold: float = 0.35) -> bool:
    """True if all ConceptMastery records exceed threshold (or none exist yet)."""
    try:
        records = ConceptMastery.query.filter_by(user_id=user_id).all()
        if not records:
            return True
        return all(m.mastery_score >= threshold for m in records)
    except Exception:
        return True


def _hint_ratio_ok(user_id: int) -> bool:
    """True if user's hint_dependency_ratio < 0.5."""
    try:
        user = User.query.get(user_id)
        return user and user.hint_dependency_ratio < 0.5
    except Exception:
        return True


def _phase_complete_gate(user_id: int) -> bool:
    """Gates: 8+ passed challenges, mastery > 0.50 on ≥3 concepts, no severe misconceptions."""
    try:
        total_passed = _count_passed_by_mode(user_id, 'scaffolded') + \
                       _count_passed_by_mode(user_id, 'guided') + \
                       _count_passed_by_mode(user_id, 'freeform')
        if total_passed < 8:
            return False

        records = ConceptMastery.query.filter_by(user_id=user_id).all()
        strong = sum(1 for m in records if m.mastery_score > 0.50)
        if strong < 3:
            return False

        from app.cognitive_models.cognitive import MisconceptionTag
        severe = MisconceptionTag.query.filter(
            MisconceptionTag.user_id == user_id,
            MisconceptionTag.resolved.is_(False),
            MisconceptionTag.recurrence_count >= 3,
        ).count()
        return severe == 0
    except Exception:
        return False


# ─── Utility ──────────────────────────────────────────────────────────────────

def _describe_output(output: str, ran: bool, error: str) -> str:
    if not ran:
        return "Your code encountered an error before producing any output."
    if not output:
        return "Your code ran without errors but produced no output. Check for a missing print() call."
    lines = output.splitlines()
    if len(lines) == 1:
        return f"Your code ran and printed: {output}"
    return f"Your code ran and printed {len(lines)} lines of output."


def _why_text(passed: bool, mode: str, scaffold: dict) -> str:
    if mode == 'fill_in_blank':
        return scaffold.get('explanation', 'The value you filled in determined what the code did.')
    if mode == 'predict_output':
        return scaffold.get('explanation', 'Tracing code mentally before running it builds debugging intuition.')
    if mode == 'error_spotting':
        return scaffold.get('explanation', 'Reading code as a sequence of instructions — not intent — reveals bugs.')
    return ''


def _prev_phase(new_phase: str) -> str:
    order = ['scaffolded', 'guided', 'freeform', 'complete']
    idx = order.index(new_phase) if new_phase in order else 0
    return order[max(0, idx - 1)]


def _safe_truncate(user_input: dict) -> dict:
    """Truncate user_input for safe storage in event_data."""
    result = {}
    for k, v in user_input.items():
        if isinstance(v, str) and len(v) > 300:
            result[k] = v[:300] + '...'
        else:
            result[k] = v
    return result
