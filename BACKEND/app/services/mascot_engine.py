"""
MascotEngine — Cognitive Translator for Beginner Mode

Professor Hoot explains *thinking*, not outcomes.
- Context bound: only explains concepts tied to the current challenge/lesson.
- Not the instructor: the lesson content leads; mascot reframes and points.
- Max 3 sentences per message. No generic encouragement.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


# ─── Rule Bank ────────────────────────────────────────────────────────────────
# Keyed by error_type (from ErrorInterpreter / MisconceptionDetector).
# Each entry has messages for intervention levels 1–3 (rule-based).
# Level 4–5 triggers an optional LLM call with challenge context.

_ERROR_RULES = {
    'runtime_undefined': {
        'reasoning_focus': 'logic_error',
        'message': (
            "You're using a variable before creating it. "
            "Python reads top to bottom, so it needs to see the variable defined first. "
            "Look above the line that failed and check if the name is spelled the same way."
        ),
        'suggested_next_step': "Define the variable before the line where you use it.",
        'intervention_level': 2,
    },
    'syntax': {
        'reasoning_focus': 'logic_error',
        'message': (
            "Python couldn't parse your code before running it. "
            "This usually means a missing colon after an `if`, `for`, or `def`, "
            "or a bracket that was opened but never closed."
        ),
        'suggested_next_step': "Check the line flagged in the error — look for a missing colon or unmatched bracket.",
        'intervention_level': 2,
    },
    'logic_indexing': {
        'reasoning_focus': 'misconception',
        'message': (
            "You tried to access a position that doesn't exist in the list. "
            "If a list has 3 items, valid positions are 0, 1, and 2 — not 3. "
            "The last valid index is always len(list) - 1."
        ),
        'suggested_next_step': "Print len() of your list and compare it to the index you used.",
        'intervention_level': 2,
    },
    'logic_type': {
        'reasoning_focus': 'misconception',
        'message': (
            "Python can't do that operation on those types. "
            "For example, you can't add a number and a string directly. "
            "Try converting one of the values first with int() or str()."
        ),
        'suggested_next_step': "Check what type each variable holds using print(type(variable)).",
        'intervention_level': 2,
    },
    'runtime_division': {
        'reasoning_focus': 'logic_error',
        'message': (
            "Division by zero is undefined in mathematics and in Python. "
            "Your denominator is reaching zero during execution. "
            "Add a check before dividing: `if divisor != 0:`."
        ),
        'suggested_next_step': "Guard the division with an if-check.",
        'intervention_level': 2,
    },
    'conceptual_infinite_loop': {
        'reasoning_focus': 'misconception',
        'message': (
            "Your loop ran until the time limit — it never found a reason to stop. "
            "A `while` loop needs a condition that eventually becomes False, or a `break` statement. "
            "Check whether your loop variable is actually changing each iteration."
        ),
        'suggested_next_step': "Add a print of the loop variable at the top of the loop body to see if it changes.",
        'intervention_level': 3,
    },
    'logic_dictionary': {
        'reasoning_focus': 'logic_error',
        'message': (
            "You tried to access a key that doesn't exist in the dictionary. "
            "Use `key in dict` to check before accessing, or use dict.get(key) to avoid the error. "
            "Print your dictionary to see its actual keys."
        ),
        'suggested_next_step': "Use dict.get('key', default) to safely access dictionary values.",
        'intervention_level': 2,
    },
    'off_by_one': {
        'reasoning_focus': 'misconception',
        'message': (
            "range(n) produces numbers from 0 up to n-1, not including n. "
            "If you wanted 1 through 10, use range(1, 11). "
            "This is one of the most common first-loop surprises in Python."
        ),
        'suggested_next_step': "Try printing each value your range produces to verify the sequence.",
        'intervention_level': 2,
    },
    'unknown': {
        'reasoning_focus': 'strategy',
        'message': (
            "Something unexpected happened when running your code. "
            "Reading the error message carefully usually points to the exact line. "
            "Expand 'Technical Details' to see the full error."
        ),
        'suggested_next_step': "Expand the technical details and identify the line number.",
        'intervention_level': 3,
    },
}

_MISCONCEPTION_RULES = {
    'off_by_one': _ERROR_RULES['off_by_one'],
    'infinite_loop': _ERROR_RULES['conceptual_infinite_loop'],
    'null_handling': {
        'reasoning_focus': 'misconception',
        'message': (
            "Use `is None` instead of `== None` to check for None in Python. "
            "The `==` operator can be overridden by classes; `is` checks object identity directly. "
            "This is a convention that prevents subtle bugs in larger programs."
        ),
        'suggested_next_step': "Replace `== None` with `is None` in your condition.",
        'intervention_level': 1,
    },
    'variable_scope_confusion': {
        'reasoning_focus': 'misconception',
        'message': (
            "Using `global` usually means a variable is being shared in a way that makes code hard to reason about. "
            "Try passing the value as a function argument and returning the result instead. "
            "Functions that don't rely on globals are easier to test and understand."
        ),
        'suggested_next_step': "Pass the variable as a parameter and return the modified value.",
        'intervention_level': 2,
    },
}

_CORRECT_MESSAGES = {
    'fill_in_blank': {
        'reasoning_focus': 'execution_flow',
        'message': (
            "Your answer produced the right output. "
            "Notice how the value you placed in the blank controlled what the code did. "
            "That's the core idea — arguments and parameters shape execution."
        ),
        'suggested_next_step': None,
        'intervention_level': 1,
    },
    'predict_output': {
        'reasoning_focus': 'execution_flow',
        'message': (
            "Correct prediction — you traced the execution mentally before the computer did it. "
            "That skill, visualizing what code does step-by-step, is how experienced programmers debug. "
            "Keep practicing this before running each piece of code."
        ),
        'suggested_next_step': None,
        'intervention_level': 1,
    },
    'error_spotting': {
        'reasoning_focus': 'logic_error',
        'message': (
            "You located the fault. "
            "Finding bugs requires reading code as a sequence of instructions, not as intent. "
            "The computer does exactly what is written, not what was meant."
        ),
        'suggested_next_step': None,
        'intervention_level': 1,
    },
    'freeform': {
        'reasoning_focus': 'execution_flow',
        'message': (
            "Your code ran and produced the expected output. "
            "Take a moment to trace through what happened: which lines ran, and in what order. "
            "Understanding why it worked is as important as the result."
        ),
        'suggested_next_step': None,
        'intervention_level': 1,
    },
}

_WRONG_PREDICTION_MESSAGE = {
    'reasoning_focus': 'misconception',
    'message': (
        "Your prediction didn't match the actual output — that's useful information. "
        "Compare what you expected with what happened, line by line. "
        "The gap between expectation and result is exactly where the learning is."
    ),
    'suggested_next_step': "Re-read the code one statement at a time and track the value of each variable.",
    'intervention_level': 3,
}

_TRANSITION_MESSAGE = {
    'reasoning_focus': 'strategy',
    'message': (
        "You've completed the structured exercises and demonstrated execution reasoning. "
        "Freeform challenges give you a blank editor — the constraint is just the problem statement. "
        "The skills you built here transfer directly."
    ),
    'suggested_next_step': "Open a freeform challenge and write your solution from scratch.",
    'intervention_level': 1,
}

_ARENA_FRAMING_MESSAGE = {
    'reasoning_focus': 'strategy',
    'message': (
        "Arena is a space to experiment. "
        "Your result here doesn't define your progress — every attempt teaches something. "
        "Focus on understanding the problem, not the outcome."
    ),
    'suggested_next_step': None,
    'intervention_level': 1,
}


# ─── Engine ───────────────────────────────────────────────────────────────────

class MascotEngine:
    """
    Generates contextually-bound mascot responses for beginner mode.
    Always context-bound to the current challenge/lesson metadata.
    Optionally elevates to LLM for intervention_level >= 4.
    """

    @staticmethod
    def respond_to_error(
        error_type: str,
        code: str,
        challenge_context: Optional[dict] = None,
        use_llm: bool = False,
    ) -> dict:
        """
        Returns a mascot response dict for a failed submission.

        Args:
            error_type: From ErrorInterpreter.translate() or MisconceptionDetector.classify_error_type()
            code: The submitted code (used for LLM context if needed)
            challenge_context: dict with keys: title, description, category, concept_keywords
            use_llm: If True and intervention_level >= 4, attempts LLM call
        """
        rule = _ERROR_RULES.get(error_type, _ERROR_RULES['unknown'])
        response = dict(rule)  # shallow copy

        if use_llm and response['intervention_level'] >= 4 and challenge_context:
            try:
                llm_msg = MascotEngine._llm_fallback(error_type, code, challenge_context)
                if llm_msg:
                    response['message'] = llm_msg
            except Exception as e:
                logger.warning(f"MascotEngine LLM fallback failed: {e}")

        return response

    @staticmethod
    def respond_to_misconception(
        misconception_type: str,
        challenge_context: Optional[dict] = None,
    ) -> dict:
        """Returns a mascot response for a detected code pattern misconception."""
        rule = _MISCONCEPTION_RULES.get(misconception_type, _ERROR_RULES['unknown'])
        return dict(rule)

    @staticmethod
    def respond_to_correct(challenge_mode: str) -> dict:
        """Returns a mascot response for a correct submission."""
        mode = challenge_mode if challenge_mode in _CORRECT_MESSAGES else 'freeform'
        return dict(_CORRECT_MESSAGES[mode])

    @staticmethod
    def respond_to_wrong_prediction() -> dict:
        """Returns a mascot response when prediction != actual output."""
        return dict(_WRONG_PREDICTION_MESSAGE)

    @staticmethod
    def respond_to_transition() -> dict:
        """Returns a mascot response explaining the scaffold -> freeform transition."""
        return dict(_TRANSITION_MESSAGE)

    @staticmethod
    def respond_to_arena(beginner_phase: str) -> dict:
        """Returns mascot framing for Arena during early beginner phases."""
        if beginner_phase in ('scaffolded', 'guided'):
            return dict(_ARENA_FRAMING_MESSAGE)
        return {}

    # ─── Private ──────────────────────────────────────────────────────────────

    @staticmethod
    def _llm_fallback(error_type: str, code: str, challenge_context: dict) -> Optional[str]:
        """
        Attempts to generate a context-specific mascot message via LLMService.
        Only called at intervention_level >= 4. Returns None on failure.
        """
        try:
            from app.services.llm_service import LLMService
            prompt = (
                f"You are Professor Hoot, a concise coding tutor. "
                f"A beginner got a {error_type} error on this challenge: "
                f"'{challenge_context.get('title', '')}' "
                f"(category: {challenge_context.get('category', '')}).\n"
                f"Their code:\n{code[:400]}\n\n"
                f"Explain in exactly 2-3 sentences: what went wrong causally, "
                f"and one concrete next step. No praise. No fluff."
            )
            llm = LLMService()
            result = llm.generate_text(prompt, max_tokens=120)
            return result.strip() if result else None
        except Exception:
            return None
