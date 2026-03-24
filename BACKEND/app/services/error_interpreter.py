"""
ErrorInterpreter — Beginner Error Translation Layer

Transforms raw sandbox error text into beginner-readable explanations.
Reuses MisconceptionDetector.classify_error_type() — no duplicate classification logic.

Frontend contract:
  {
    "beginner": str,    -- shown by default
    "technical": str,   -- revealed on 'Show Technical Details' click
    "error_type": str   -- from MisconceptionDetector classification
  }
"""

import re
import logging

logger = logging.getLogger(__name__)


# ─── Beginner-readable templates ──────────────────────────────────────────────
# Keyed by error_type returned from MisconceptionDetector.classify_error_type()

_BEGINNER_TEMPLATES = {
    'runtime_undefined': (
        "You're using a variable before creating it. "
        "Python reads code from top to bottom, so it needs to see the variable "
        "defined before you use it. Check the spelling — it might be a typo too."
    ),
    'syntax': (
        "Python couldn't understand your code before running it — "
        "this usually means a missing colon after `if`, `for`, or `def`, "
        "or a bracket/quote that was opened but never closed."
    ),
    'logic_indexing': (
        "You tried to access a list position that doesn't exist. "
        "List positions start at 0, so a list with 3 items has positions 0, 1, and 2 — not 3. "
        "The last valid position is always length minus one."
    ),
    'logic_dictionary': (
        "You tried to look up a key that doesn't exist in your dictionary. "
        "Use `key in my_dict` to check first, or use `my_dict.get(key)` "
        "to return None instead of crashing."
    ),
    'logic_type': (
        "Python can't perform that operation on those types of values. "
        "For example, you can't directly add a number and a string. "
        "Convert one of them — use int(), float(), or str()."
    ),
    'logic_value': (
        "You passed a value that is technically the right type but not valid for that operation. "
        "For example, converting the string 'hello' to an integer will fail. "
        "Check what value you're passing and whether it makes sense."
    ),
    'logic_attribute': (
        "You tried to use a method or property that doesn't exist on that type of object. "
        "Check what type your variable actually holds using print(type(variable)). "
        "The method might be named differently or not available."
    ),
    'runtime_division': (
        "Division by zero is undefined — you can't divide any number by zero. "
        "Your denominator is reaching zero during execution. "
        "Add a check: `if denominator != 0:` before the division."
    ),
    'runtime_recursion': (
        "Your function called itself too many times without stopping. "
        "Every recursive function needs a base case — a condition where it stops calling itself. "
        "Check that your base case is reachable."
    ),
    'conceptual_infinite_loop': (
        "Your loop never found a reason to stop, so it ran until the time limit. "
        "A `while` loop needs a condition that eventually becomes False, or a `break`. "
        "Make sure something inside the loop changes the variable being tested."
    ),
    'conceptual_efficiency': (
        "Your code took too long to finish — it may be doing far more work than needed. "
        "Look for nested loops or repeated calculations that could be simplified. "
        "Try to find a pattern instead of brute-forcing every possibility."
    ),
    'unknown': (
        "Something unexpected stopped your code from running. "
        "Read the error message carefully — it usually points to the exact line. "
        "Expand 'Technical Details' below to see the full output."
    ),
}


# ─── Interpreter ──────────────────────────────────────────────────────────────

class ErrorInterpreter:
    """
    Translates raw sandbox error output into a tiered explanation dict.
    Does NOT duplicate classification logic — delegates to MisconceptionDetector.
    """

    @staticmethod
    def translate(error_message: str, code: str) -> dict:
        """
        Produce a tiered error explanation.

        Args:
            error_message: Raw error string from sandbox (stderr/error field)
            code: Source code that caused the error

        Returns:
            {
              "beginner": str,   -- plain language explanation
              "technical": str,  -- raw error (hidden until user expands)
              "error_type": str  -- classification key
            }
        """
        if not error_message:
            return {
                'beginner': "Your code ran but produced no output. Check that you have a print() statement.",
                'technical': '',
                'error_type': 'no_output',
            }

        # Delegate classification to existing service (no duplication)
        from app.services.misconception_detector import MisconceptionDetector
        error_type = MisconceptionDetector.classify_error_type(error_message, code)

        beginner_text = _BEGINNER_TEMPLATES.get(error_type, _BEGINNER_TEMPLATES['unknown'])

        # Optionally enrich with variable name from NameError
        if error_type == 'runtime_undefined':
            match = re.search(r"name '(\w+)' is not defined", error_message)
            if match:
                var_name = match.group(1)
                beginner_text = (
                    f"You're using `{var_name}` before creating it. "
                    "Python reads code from top to bottom, so it needs to see the variable "
                    "defined before you use it. Check for typos in the name."
                )

        # Optionally enrich with line number from SyntaxError
        elif error_type == 'syntax':
            line_match = re.search(r'line (\d+)', error_message)
            if line_match:
                line_num = line_match.group(1)
                beginner_text = (
                    f"Python found a syntax problem near line {line_num}. "
                    "Look for a missing colon after `if`, `for`, or `def`, "
                    "or a bracket/quote that was opened but never closed."
                )

        return {
            'beginner': beginner_text,
            'technical': error_message.strip(),
            'error_type': error_type,
        }
