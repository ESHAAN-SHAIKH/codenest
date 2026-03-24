from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.rate_limiting import rate_limit, check_quota, api_limiter
from app.extensions import db
from app.cognitive_models.arena import ArenaMatch, ArenaRating
from datetime import datetime
import random, uuid, json, logging

logger = logging.getLogger(__name__)

arena_bp = Blueprint('arena', __name__)

# ── LLM integration ──────────────────────────────────────────────────────────
try:
    from app.services.llm_service import LLMService
    llm_service = LLMService()
except Exception:
    llm_service = None

# ── Challenge templates (fallback when LLM is unavailable) ────────────────────
CHALLENGE_TEMPLATES = {
    'debug_duel': [
        {
            'title': 'Fix the Fibonacci',
            'description': 'This Fibonacci function has a bug that causes incorrect results for n > 2. Find and fix it.',
            'buggy_code': 'def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n - 1) + fibonacci(n - 3)\n\nprint(fibonacci(6))',
            'expected_output': '8',
            'difficulty': 'easy',
            'hint': 'Check the recursive case carefully — which previous terms should be summed?',
            'time_limit': 180,
        },
        {
            'title': 'Fix the List Reversal',
            'description': 'This function should reverse a list in-place but it produces wrong results. Find the bug.',
            'buggy_code': 'def reverse_list(lst):\n    n = len(lst)\n    for i in range(n):\n        lst[i], lst[n - 1 - i] = lst[n - 1 - i], lst[i]\n    return lst\n\nprint(reverse_list([1, 2, 3, 4, 5]))',
            'expected_output': '[5, 4, 3, 2, 1]',
            'difficulty': 'easy',
            'hint': 'How many swaps do you actually need? Think about what happens halfway through.',
            'time_limit': 180,
        },
        {
            'title': 'Fix the Binary Search',
            'description': 'This binary search function runs forever on some inputs. Find and fix the bug.',
            'buggy_code': 'def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid\n        else:\n            high = mid\n    return -1\n\nprint(binary_search([1, 3, 5, 7, 9, 11], 7))',
            'expected_output': '3',
            'difficulty': 'medium',
            'hint': 'When you update low or high, are you actually narrowing the search range?',
            'time_limit': 240,
        },
    ],
    'refactor_race': [
        {
            'title': 'Clean Up This Mess',
            'description': 'Refactor this working but messy code to be clean and readable. Keep the same output.',
            'buggy_code': 'x = [1,2,3,4,5,6,7,8,9,10]\nr1 = []\nfor i in x:\n    if i % 2 == 0:\n        r1.append(i * i)\nprint(r1)\nr2 = 0\nfor i in r1:\n    r2 = r2 + i\nprint(r2)',
            'expected_output': '[4, 16, 36, 64, 100]\n220',
            'difficulty': 'easy',
            'hint': 'Consider using list comprehensions and the sum() function.',
            'time_limit': 180,
        },
        {
            'title': 'Simplify the Validator',
            'description': 'Refactor this password validator to be cleaner while preserving behavior.',
            'buggy_code': 'def check_password(p):\n    ok = True\n    if len(p) < 8:\n        ok = False\n    has_upper = False\n    has_lower = False\n    has_digit = False\n    for c in p:\n        if c.isupper():\n            has_upper = True\n        if c.islower():\n            has_lower = True\n        if c.isdigit():\n            has_digit = True\n    if has_upper == False:\n        ok = False\n    if has_lower == False:\n        ok = False\n    if has_digit == False:\n        ok = False\n    return ok\n\nprint(check_password("Abc12345"))\nprint(check_password("abc"))',
            'expected_output': 'True\nFalse',
            'difficulty': 'medium',
            'hint': 'Use any() with generator expressions and combine conditions.',
            'time_limit': 240,
        },
    ],
    'optimization_battle': [
        {
            'title': 'Optimize Two Sum',
            'description': 'This O(n²) solution works but is slow. Optimize it to O(n) using a better approach.',
            'buggy_code': 'def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []\n\nprint(two_sum([2, 7, 11, 15], 9))',
            'expected_output': '[0, 1]',
            'difficulty': 'medium',
            'hint': 'A dictionary/hash map can find complements in O(1).',
            'time_limit': 240,
        },
        {
            'title': 'Optimize Duplicate Finder',
            'description': 'Find duplicates in O(n) time instead of O(n²). The current approach is too slow for large lists.',
            'buggy_code': 'def find_duplicates(lst):\n    dupes = []\n    for i in range(len(lst)):\n        for j in range(i + 1, len(lst)):\n            if lst[i] == lst[j] and lst[i] not in dupes:\n                dupes.append(lst[i])\n    return dupes\n\nprint(find_duplicates([1, 2, 3, 2, 4, 5, 1, 6]))',
            'expected_output': '[2, 1]',
            'difficulty': 'easy',
            'hint': 'Use a set to track what you have seen so far.',
            'time_limit': 180,
        },
    ],
}

MATCH_TYPES = ['debug_duel', 'refactor_race', 'optimization_battle']

# Sentinel player2_id for AI matches (not a real user ID)
AI_PLAYER_ID = 0


def _get_or_create_rating(user_id, match_type):
    """Get or create a rating record for a user + match type."""
    rating = ArenaRating.query.filter_by(user_id=user_id, match_type=match_type).first()
    if not rating:
        # Initialize at 1500 to match the model column default
        rating = ArenaRating(
            user_id=user_id,
            match_type=match_type,
            rating=1500,
            peak_rating=1500,
            lowest_rating=1500,
        )
        db.session.add(rating)
        db.session.commit()
    return rating


# ═══════════════════════════════════════════════════════════════════════════════
#  GET  /arena/rating/me
# ═══════════════════════════════════════════════════════════════════════════════
@arena_bp.route('/arena/rating/me', methods=['GET'])
@jwt_required()
def get_user_rating():
    """Get the current user's Elo ratings across all match types."""
    try:
        user_id = int(get_jwt_identity())
        ratings = {}
        for mt in MATCH_TYPES:
            r = _get_or_create_rating(user_id, mt)
            ratings[mt] = {
                'rating': r.rating,
                'matches_played': r.matches_played,
                'wins': r.wins,
                'losses': r.losses,
                'win_rate': r.get_win_rate(),
                'current_win_streak': r.current_win_streak,
                'best_win_streak': r.best_win_streak,
            }
        return jsonify({'success': True, 'data': {'ratings': ratings}})
    except Exception as e:
        logger.error(f"Error fetching ratings: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  GET  /arena/history/me
# ═══════════════════════════════════════════════════════════════════════════════
@arena_bp.route('/arena/history/me', methods=['GET'])
@jwt_required()
def get_match_history():
    """Get the current user's match history."""
    try:
        user_id = int(get_jwt_identity())
        matches = ArenaMatch.query.filter(
            ArenaMatch.player1_id == user_id
        ).filter(ArenaMatch.status == 'completed').order_by(
            ArenaMatch.completed_at.desc()
        ).limit(20).all()

        result = []
        for m in matches:
            match_data = m.match_data or {}
            rating_change = match_data.get('player1_rating_change', 0)
            result.append({
                'match_id': m.match_id,
                'match_type': m.match_type,
                'winner_id': m.winner_id,
                'user_id': user_id,
                'player1_score': m.player1_score,
                'player2_score': m.player2_score,
                'rating_change': rating_change,
                'completed_at': m.completed_at.isoformat() if m.completed_at else None,
            })

        return jsonify({'success': True, 'data': {'matches': result}})
    except Exception as e:
        logger.error(f"Error fetching match history: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  POST  /arena/match/start  — Start a vs-AI match
# ═══════════════════════════════════════════════════════════════════════════════
@arena_bp.route('/arena/match/start', methods=['POST'])
@jwt_required()
@rate_limit(api_limiter)
@check_quota('arena_matches_per_day')
def start_match():
    """Start a new vs-AI arena match with a coding challenge."""
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}
        match_type = data.get('match_type', 'debug_duel')

        if match_type not in MATCH_TYPES:
            return jsonify({'error': 'Invalid match type'}), 400

        # Generate challenge
        challenge = _generate_challenge(match_type)

        # Create match in DB — player2_id=0 signals an AI opponent
        match_id = f"match_{user_id}_ai_{uuid.uuid4().hex[:8]}"
        ai_name = random.choice([
            'CodeBot Alpha', 'PyMaster 3000', 'Debug Ninja',
            'Algorithm Ace', 'Syntax Sage', 'Logic Lord',
        ])
        match = ArenaMatch(
            match_id=match_id,
            match_type=match_type,
            player1_id=user_id,
            player2_id=user_id,  # AI match — same user ID; ai_opponent flag in match_data distinguishes
            status='in_progress',
            started_at=datetime.utcnow(),
            match_data={
                'challenge': challenge,
                'ai_opponent': True,
                'ai_name': ai_name,
                'ai_time': random.randint(30, int(challenge.get('time_limit', 180) * 0.8)),
            },
        )
        db.session.add(match)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'match_id': match_id,
                'match_type': match_type,
                'challenge': challenge,
                'ai_opponent': ai_name,
                'time_limit': challenge.get('time_limit', 180),
            },
        })
    except Exception as e:
        logger.error(f"Error starting match: {e}")
        return jsonify({'error': str(e)}), 500


def _generate_challenge(match_type):
    """Generate a challenge, trying LLM first, falling back to templates."""

    if llm_service and llm_service.api_key:
        try:
            type_labels = {
                'debug_duel': 'a Python code snippet with exactly ONE subtle bug that the user must find and fix',
                'refactor_race': 'a working but messy Python code snippet that needs to be refactored into clean, readable code',
                'optimization_battle': 'a correct but inefficient (O(n²)) Python solution that needs to be optimized',
            }

            prompt = f"""Generate {type_labels.get(match_type, 'a coding challenge')} for an educational coding arena.

Return ONLY a valid JSON object with these exact keys:
{{
  "title": "short challenge name",
  "description": "what the user needs to do (1-2 sentences)",
  "buggy_code": "the code to fix/refactor/optimize",
  "expected_output": "expected console output",
  "difficulty": "easy or medium",
  "hint": "a helpful hint",
  "time_limit": 180
}}

Keep the code SHORT (under 15 lines). Use only Python stdlib. No explanations outside the JSON."""

            messages = [
                {'role': 'system', 'content': 'You are a coding challenge generator. Return ONLY valid JSON.'},
                {'role': 'user', 'content': prompt},
            ]
            result = llm_service._make_request(messages, max_tokens=600)
            if result:
                content = result['choices'][0]['message']['content'].strip()
                if '{' in content:
                    json_str = content[content.index('{'):content.rindex('}') + 1]
                    challenge = json.loads(json_str)
                    if all(k in challenge for k in ['title', 'buggy_code', 'expected_output']):
                        challenge.setdefault('time_limit', 180)
                        challenge.setdefault('difficulty', 'medium')
                        challenge.setdefault('hint', 'Think carefully about the logic.')
                        challenge.setdefault('description', 'Fix the code to produce the expected output.')
                        challenge['llm_generated'] = True
                        return challenge
        except Exception as e:
            logger.warning(f"LLM challenge generation failed, using template: {e}")

    templates = CHALLENGE_TEMPLATES.get(match_type, CHALLENGE_TEMPLATES['debug_duel'])
    return {**random.choice(templates), 'llm_generated': False}


# ═══════════════════════════════════════════════════════════════════════════════
#  POST  /arena/match/submit  — Submit solution, get LLM evaluation
# ═══════════════════════════════════════════════════════════════════════════════
@arena_bp.route('/arena/match/submit', methods=['POST'])
@jwt_required()
@rate_limit(api_limiter)
def submit_match():
    """Submit code for evaluation. LLM evaluates, Elo updated."""
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}
        match_id = data.get('match_id')
        user_code = data.get('code', '')
        time_taken = data.get('time_taken', 0)

        if not match_id:
            return jsonify({'error': 'match_id required'}), 400

        match = ArenaMatch.query.filter_by(match_id=match_id).first()
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        if match.player1_id != user_id:
            return jsonify({'error': 'Forbidden'}), 403
        if match.status != 'in_progress':
            return jsonify({'error': 'Match already completed'}), 400

        challenge = (match.match_data or {}).get('challenge', {})
        ai_time = (match.match_data or {}).get('ai_time', 60)

        evaluation = _evaluate_submission(user_code, challenge, match.match_type, time_taken, ai_time)

        user_score = evaluation.get('score', 50)
        ai_score = random.randint(40, 80)
        user_won = user_score > ai_score

        rating = _get_or_create_rating(user_id, match.match_type)
        ai_rating = 1500 + random.randint(-100, 100)  # AI opponent at ~1500 baseline
        result_str = 'win' if user_won else 'loss'
        rating_info = rating.update_rating(ai_rating, result_str)

        match.winner_id = user_id if user_won else None
        match.player1_score = user_score
        match.player2_score = ai_score
        match.status = 'completed'
        match.completed_at = datetime.utcnow()

        match_data = match.match_data or {}
        match_data['player1_submission'] = {'code': user_code, 'time': time_taken}
        match_data['player1_rating_change'] = rating_info['rating_change']
        match_data['evaluation'] = evaluation
        match.match_data = match_data

        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'user_won': user_won,
                'user_score': user_score,
                'ai_score': ai_score,
                'rating_change': rating_info['rating_change'],
                'new_rating': rating_info['new_rating'],
                'feedback': evaluation.get('feedback', 'Good attempt!'),
                'improvements': evaluation.get('improvements', []),
                'time_taken': time_taken,
                'ai_time': ai_time,
            },
        })
    except Exception as e:
        logger.error(f"Error submitting match: {e}")
        return jsonify({'error': str(e)}), 500


def _evaluate_submission(user_code, challenge, match_type, time_taken, ai_time):
    """Evaluate user's code using LLM if available, else basic heuristic."""

    if llm_service and llm_service.api_key:
        try:
            type_criteria = {
                'debug_duel': 'Did the user correctly identify and fix the bug? Does the code now produce the expected output?',
                'refactor_race': 'Is the refactored code cleaner, more readable, and Pythonic while preserving the original behavior?',
                'optimization_battle': 'Is the code more efficient than the original? Did they improve the time/space complexity?',
            }

            prompt = f"""Evaluate this coding arena submission.

MATCH TYPE: {match_type}
ORIGINAL CODE:
```python
{challenge.get('buggy_code', '')}
```

EXPECTED OUTPUT: {challenge.get('expected_output', 'N/A')}

USER'S SUBMISSION:
```python
{user_code}
```

CRITERIA: {type_criteria.get(match_type, 'Is the code correct?')}

Return ONLY a valid JSON object:
{{
  "score": <0-100 integer>,
  "feedback": "1-2 sentence feedback on their solution",
  "improvements": ["suggestion 1", "suggestion 2"],
  "correct": true/false
}}"""

            messages = [
                {'role': 'system', 'content': 'You are a code evaluator. Return ONLY valid JSON. Be encouraging but honest.'},
                {'role': 'user', 'content': prompt},
            ]
            result = llm_service._make_request(messages, max_tokens=300)
            if result:
                content = result['choices'][0]['message']['content'].strip()
                if '{' in content:
                    json_str = content[content.index('{'):content.rindex('}') + 1]
                    evaluation = json.loads(json_str)
                    evaluation['llm_evaluated'] = True
                    if time_taken < ai_time:
                        evaluation['score'] = min(100, evaluation.get('score', 50) + 10)
                        evaluation['feedback'] = evaluation.get('feedback', '') + ' Speed bonus! ⚡'
                    return evaluation
        except Exception as e:
            logger.warning(f"LLM evaluation failed, using heuristic: {e}")

    return _heuristic_evaluate(user_code, challenge, match_type, time_taken, ai_time)


def _heuristic_evaluate(user_code, challenge, match_type, time_taken, ai_time):
    """Simple heuristic evaluation when LLM is unavailable."""
    buggy = challenge.get('buggy_code', '')
    code_changed = user_code.strip() != buggy.strip()
    code_length = len(user_code.strip())
    has_comments = '#' in user_code

    score = 30
    feedback_parts = []
    improvements = []

    if not code_changed:
        return {
            'score': 10,
            'feedback': "It looks like you didn't change the code. Try fixing the issue!",
            'improvements': ['Read the challenge description and identify the problem.'],
            'correct': False,
            'llm_evaluated': False,
        }

    score += 20
    feedback_parts.append('You modified the code')

    if code_length > 20:
        score += 10

    if has_comments:
        score += 5
        feedback_parts.append('with helpful comments')

    if time_taken < ai_time:
        score += 15
        feedback_parts.append('and finished faster than the AI! ⚡')
    else:
        feedback_parts.append('— keep practicing to beat the AI timer!')

    if match_type == 'refactor_race' and len(user_code) < len(buggy):
        score += 10
        improvements.append('Great job making the code more concise!')
    elif match_type == 'optimization_battle':
        if 'for' in buggy and user_code.count('for') < buggy.count('for'):
            score += 15
            improvements.append('Nice optimization — fewer loops!')

    score = min(100, score)

    return {
        'score': score,
        'feedback': ' '.join(feedback_parts) + '.',
        'improvements': improvements or ['Keep practicing to improve your skills!'],
        'correct': score >= 60,
        'llm_evaluated': False,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Queue endpoints (kept for future multiplayer)
# ═══════════════════════════════════════════════════════════════════════════════
matchmaking_queue = {}


@arena_bp.route('/arena/queue/join', methods=['POST'])
@jwt_required()
@rate_limit(api_limiter)
@check_quota('arena_matches_per_day')
def join_queue():
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}
        match_type = data.get('match_type', 'debug_duel')
        if match_type not in matchmaking_queue:
            matchmaking_queue[match_type] = []
        matchmaking_queue[match_type].append({'user_id': user_id, 'joined_at': datetime.utcnow()})
        return jsonify({'success': True, 'data': {'position_in_queue': len(matchmaking_queue[match_type])}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@arena_bp.route('/arena/queue/leave', methods=['POST'])
@jwt_required()
def leave_queue():
    try:
        user_id = int(get_jwt_identity())
        for mt in matchmaking_queue:
            matchmaking_queue[mt] = [e for e in matchmaking_queue[mt] if e['user_id'] != user_id]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@arena_bp.route('/arena/queue/status', methods=['GET'])
@jwt_required()
def get_queue_status():
    try:
        return jsonify({'success': True, 'data': {'in_queue': False, 'match_found': False}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@arena_bp.route('/arena/match/<match_id>', methods=['GET'])
@jwt_required()
def get_match_details(match_id):
    try:
        user_id = int(get_jwt_identity())
        match = ArenaMatch.query.filter_by(match_id=match_id).first()
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        if match.player1_id != user_id:
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'success': True, 'data': match.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
