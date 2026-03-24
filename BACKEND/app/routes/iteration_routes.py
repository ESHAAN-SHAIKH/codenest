"""
Iteration Chamber backend routes.

Stores code iterations in the DB (code_iterations table) so history
survives server restarts.  No Redis / rate-limit decorators — those
break the response pipeline when Redis is absent.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
from app.cognitive_models.learning import CodeIteration
from app.services.llm_service import LLMService
from datetime import datetime
import json
import re

iteration_bp = Blueprint('iteration', __name__)
llm_service = LLMService()

STAGES = ['functional', 'quality', 'performance', 'edge_cases']

STAGE_CRITERIA = {
    'functional': {
        'focus': 'Correctness and functionality',
        'checks': ['runs without errors', 'produces correct output', 'handles basic cases'],
    },
    'quality': {
        'focus': 'Code readability and maintainability',
        'checks': ['clear variable names', 'proper structure', 'helpful comments', 'consistent style'],
    },
    'performance': {
        'focus': 'Efficiency and optimization',
        'checks': ['optimal time complexity', 'efficient memory use', 'no unnecessary operations'],
    },
    'edge_cases': {
        'focus': 'Robustness and error handling',
        'checks': ['handles empty inputs', 'null checks', 'boundary conditions', 'error handling'],
    },
}


# ── Submit iteration ──────────────────────────────────────────────────────────

@iteration_bp.route('/iteration/submit', methods=['POST'])
@jwt_required()
def submit_iteration():
    """Analyse code for the given stage and persist the iteration."""
    try:
        identity = get_jwt_identity()
        user = User.query.filter_by(user_id=identity).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json(silent=True) or {}
        challenge_id   = data.get('challenge_id')
        code           = (data.get('code') or '').strip()
        stage          = data.get('stage', 'functional')
        iteration_num  = int(data.get('iteration_number', 1))

        if not challenge_id:
            return jsonify({'error': 'Missing required field: challenge_id'}), 400
        if not code:
            return jsonify({'error': 'Missing required field: code'}), 400
        if stage not in STAGES:
            return jsonify({'error': f'Invalid stage. Must be one of: {STAGES}'}), 400

        # Analyse code and compute score
        feedback     = _analyse(code, stage)
        stage_score  = float(feedback.get('stage_score', 0.6))
        stage_passed = stage_score >= 0.8
        feedback['stage_passed'] = stage_passed

        # Persist iteration
        iteration = CodeIteration(
            user_id          = user.id,
            challenge_id     = int(challenge_id),
            iteration_number = iteration_num,
            stage            = stage,
            code_snapshot    = code,
            ai_feedback      = feedback,
            quality_score    = stage_score,
            passed_stage     = stage_passed,
            submitted_at     = datetime.utcnow(),
        )
        db.session.add(iteration)
        db.session.commit()

        # Engineering maturity (average score across all iterations for this challenge)
        all_rows     = CodeIteration.query.filter_by(user_id=user.id, challenge_id=int(challenge_id)).all()
        scores       = [r.quality_score for r in all_rows if r.quality_score is not None]
        eng_maturity = round(sum(scores) / len(scores), 3) if scores else 0.0

        # Determine next stage
        if stage_passed:
            idx        = STAGES.index(stage)
            next_stage = STAGES[idx + 1] if idx < len(STAGES) - 1 else stage
        else:
            next_stage = stage

        return jsonify({
            'success': True,
            'data': {
                'feedback':                  feedback,
                'stage_score':               stage_score,
                'stage_passed':              stage_passed,
                'engineering_maturity_score': eng_maturity,
                'next_stage':                next_stage,
            },
        })

    except Exception as exc:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


# ── Iteration history ─────────────────────────────────────────────────────────

@iteration_bp.route('/iteration/history/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_iteration_history(challenge_id):
    """Return all iterations for (current user, challenge_id)."""
    try:
        identity = get_jwt_identity()
        user = User.query.filter_by(user_id=identity).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        rows = (
            CodeIteration.query
            .filter_by(user_id=user.id, challenge_id=challenge_id)
            .order_by(CodeIteration.submitted_at.asc())
            .all()
        )

        if not rows:
            return jsonify({
                'success': True,
                'data': {'iterations': [], 'current_stage': 'functional', 'current_iteration': 1},
            })

        iterations = []
        for row in rows:
            fb = row.ai_feedback if isinstance(row.ai_feedback, dict) else {}
            iterations.append({
                'iteration_number': row.iteration_number,
                'stage':            row.stage,
                'code_snapshot':    row.code_snapshot,
                'feedback':         fb,
                'quality_score':    row.quality_score,
                'submitted_at':     row.submitted_at.isoformat() if row.submitted_at else None,
            })

        # Derive current stage: last row's stage, advanced if it passed
        last        = rows[-1]
        last_stage  = last.stage or 'functional'
        last_passed = bool(last.passed_stage)

        if last_passed:
            idx           = STAGES.index(last_stage) if last_stage in STAGES else 0
            current_stage = STAGES[idx + 1] if idx < len(STAGES) - 1 else last_stage
            current_iter  = 1
        else:
            current_stage = last_stage
            current_iter  = sum(1 for r in rows if r.stage == last_stage) + 1

        return jsonify({
            'success': True,
            'data': {
                'iterations':        iterations,
                'current_stage':     current_stage,
                'current_iteration': current_iter,
            },
        })

    except Exception as exc:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


# ── Analysis helpers ──────────────────────────────────────────────────────────

def _analyse(code: str, stage: str) -> dict:
    """Try LLM analysis; fall back to deterministic heuristics."""
    criteria = STAGE_CRITERIA.get(stage, STAGE_CRITERIA['functional'])
    prompt = (
        f"Analyse this code for the {stage.upper()} refinement stage.\n"
        f"Focus: {criteria['focus']}\n"
        f"Criteria: {', '.join(criteria['checks'])}\n\n"
        f"Code:\n```\n{code}\n```\n\n"
        "Respond with ONLY valid JSON (no markdown fences):\n"
        '{"strengths":[],"issues":[],"suggestions":[],"stage_score":0.0}\n'
        "stage_score is 0.0–1.0; >= 0.8 means stage passed."
    )
    try:
        raw   = llm_service.generate_response(prompt)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            score  = max(0.0, min(1.0, float(parsed.get('stage_score', 0.6))))
            return {
                'strengths':   parsed.get('strengths',   []) or [],
                'issues':      parsed.get('issues',      []) or [],
                'suggestions': parsed.get('suggestions', []) or [],
                'stage_score': round(score, 2),
            }
    except Exception:
        pass
    return _heuristic(code, stage)


def _heuristic(code: str, stage: str) -> dict:
    """
    Deterministic scoring when LLM is unavailable.

    Thresholds are calibrated so that well-written code reaches 0.8
    (the passing bar), which lets users actually advance through stages.
    """
    lines     = code.strip().splitlines()
    non_empty = [l for l in lines if l.strip()]
    score     = 0.6
    strengths, issues, suggestions = [], [], []

    if stage == 'functional':
        if not non_empty:
            return {'strengths': [], 'issues': ['No code submitted'],
                    'suggestions': ['Write your solution'], 'stage_score': 0.0}
        try:
            compile(code, '<string>', 'exec')
            strengths.append('Code compiles without syntax errors')
            score = 0.85                           # ✅ passes
        except SyntaxError as exc:
            issues.append(f'Syntax error: {exc}')
            suggestions.append('Fix the syntax error and resubmit')
            score = 0.2
        if len(non_empty) > 2:
            strengths.append('Code has multiple lines of logic')
            score = min(score + 0.05, 1.0)

    elif stage == 'quality':
        score        = 0.75
        has_comments = any(l.strip().startswith('#') for l in lines)
        if has_comments:
            strengths.append('Code includes explanatory comments')
            score += 0.10                          # → 0.85 ✅
        else:
            issues.append('No comments found')
            suggestions.append('Add a # comment explaining your logic')

        ALLOWED = {'i', 'j', 'k', 'n', 'm', 'x', 'y', 'z'}
        bad = [w for l in lines for w in l.split()
               if len(w) == 1 and w.isalpha() and w not in ALLOWED]
        if bad:
            issues.append('Single-letter variable names detected (except loop counters)')
            suggestions.append('Use descriptive variable names')
            score = max(score - 0.05, 0.0)
        else:
            strengths.append('Variable names appear descriptive')
            score = min(score + 0.05, 1.0)

    elif stage == 'performance':
        loops = sum(1 for l in lines
                    if l.strip().startswith('for') or l.strip().startswith('while'))
        if loops > 3:
            issues.append('Many loops may indicate high complexity')
            suggestions.append('Consider using built-ins (sum, map, filter) or dicts/sets')
            score = 0.65
        elif loops > 1:
            issues.append('Multiple loops — ensure they are not unnecessarily nested')
            suggestions.append('Verify inner loops are required')
            score = 0.75
        else:
            strengths.append('No excessive looping detected')
            score = 0.85                           # ✅ passes

        if any('import' in l for l in lines):
            strengths.append('Uses library imports — good for leveraging optimised code')

    elif stage == 'edge_cases':
        score   = 0.70
        has_try = any('try:' in l for l in lines)
        has_if  = any(l.strip().startswith('if') for l in lines)
        if has_try:
            strengths.append('Uses try/except for error handling')
            score += 0.15                          # → 0.85 ✅
        else:
            issues.append('No try/except block found')
            suggestions.append('Wrap risky operations in try/except')
        if has_if:
            strengths.append('Conditional checks present — good defensive coding')
            score = min(score + 0.05, 1.0)
        else:
            issues.append('No conditional guard clauses found')
            suggestions.append('Add if-checks for empty inputs or boundary values')

    return {
        'strengths':   strengths   or ['Code submitted'],
        'issues':      issues      or ['Continue refining for this stage'],
        'suggestions': suggestions or [f'Review the {stage} stage guide'],
        'stage_score': round(min(max(score, 0.0), 1.0), 2),
    }
