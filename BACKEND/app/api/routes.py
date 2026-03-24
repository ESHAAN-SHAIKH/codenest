from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Challenge, User

api_bp = Blueprint('api', __name__)


@api_bp.route('/', methods=['GET'])
def api_root():
    return jsonify({
        'message': 'CodeNest API Root',
        'version': '1.0.0',
        'endpoints': {
            'progress': '/api/progress',
            'execution': '/api/execute',
            'ai': '/api/ai',
            'challenges': '/api/challenges'
        }
    })


# ── Challenge endpoints ────────────────────────────────────────────────────────

@api_bp.route('/challenges', methods=['GET'])
@jwt_required()
def list_challenges():
    """List all challenges, optionally filtered by difficulty / category."""
    identity = get_jwt_identity()
    user = User.query.filter_by(user_id=identity).first()

    difficulty = request.args.get('difficulty')
    category   = request.args.get('category')

    q = Challenge.query
    if difficulty:
        q = q.filter_by(difficulty=difficulty)
    if category:
        q = q.filter_by(category=category)

    challenges = q.order_by(Challenge.min_level, Challenge.id).all()
    user_id_str = user.user_id if user else None

    return jsonify({
        'success': True,
        'challenges': [c.to_dict(user_id=user_id_str) for c in challenges]
    })


@api_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """Fetch a single challenge by its integer primary key."""
    identity = get_jwt_identity()
    user = User.query.filter_by(user_id=identity).first()

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({'error': f'Challenge {challenge_id} not found'}), 404

    user_id_str = user.user_id if user else None
    return jsonify(challenge.to_dict(user_id=user_id_str))
