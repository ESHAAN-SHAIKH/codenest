"""
Beginner Routes Blueprint

Thin presentation layer only. All evaluation is delegated to UnifiedSubmissionService.
No evaluation logic lives here.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Challenge
from app.services.unified_submission import UnifiedSubmissionService, run_transition_check
from app.services.mascot_engine import MascotEngine
import logging

logger = logging.getLogger(__name__)
beginner_bp = Blueprint('beginner', __name__)


def _get_user_or_404():
    """Helper: resolve JWT identity to User, return (user, error_response)."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return None, (jsonify({'error': 'User not found'}), 404)
    return user, None


# ─── Routes ───────────────────────────────────────────────────────────────────

@beginner_bp.route('/challenges', methods=['GET'])
@jwt_required()
def get_scaffolded_challenges():
    """
    Returns challenges ordered for beginner progression.
    Filters by challenge_mode='scaffolded' (or 'guided' in guided phase).
    Uses existing Challenge.is_unlocked_for_user() — no new ordering logic.
    """
    try:
        user, err = _get_user_or_404()
        if err:
            return err

        # Phase determines which modes surface
        if user.beginner_phase == 'scaffolded':
            modes = ['scaffolded']
        elif user.beginner_phase == 'guided':
            modes = ['scaffolded', 'guided']
        else:
            modes = ['scaffolded', 'guided', 'freeform']

        challenges = Challenge.query.filter(
            Challenge.challenge_mode.in_(modes)
        ).order_by(Challenge.id.asc()).all()

        data = []
        for c in challenges:
            d = c.to_dict(user_id=user.user_id)
            data.append(d)

        return jsonify({
            'success': True,
            'challenges': data,
            'beginner_phase': user.beginner_phase,
            'is_beginner_mode': user.is_beginner_mode,
        })

    except Exception as e:
        logger.error(f"get_scaffolded_challenges error: {e}")
        return jsonify({'error': 'Failed to load challenges'}), 500


@beginner_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_challenge():
    """
    Unified submission endpoint for all scaffolded challenge types.
    Routes to UnifiedSubmissionService.evaluate() — no evaluation logic here.
    """
    try:
        user, err = _get_user_or_404()
        if err:
            return err

        data = request.json or {}
        challenge_id = data.get('challenge_id')
        user_input = data.get('user_input', {})
        time_taken = data.get('time_taken', 0)
        hints_used = data.get('hints_used', 0)

        if not challenge_id:
            return jsonify({'error': 'challenge_id is required'}), 400

        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404

        result = UnifiedSubmissionService.evaluate(
            user=user,
            challenge=challenge,
            user_input=user_input,
            time_taken=int(time_taken),
            hints_used=int(hints_used),
        )
        return jsonify({'success': True, **result})

    except Exception as e:
        logger.error(f"submit_challenge error: {e}")
        return jsonify({'error': 'Submission failed. Please try again.'}), 500


@beginner_bp.route('/settings', methods=['POST'])
@jwt_required()
def toggle_beginner_mode():
    """Toggle is_beginner_mode for authenticated user."""
    try:
        user, err = _get_user_or_404()
        if err:
            return err

        data = request.json or {}
        # Accept explicit value or toggle
        if 'is_beginner_mode' in data:
            user.is_beginner_mode = bool(data['is_beginner_mode'])
        else:
            user.is_beginner_mode = not user.is_beginner_mode

        db.session.commit()

        return jsonify({
            'success': True,
            'is_beginner_mode': user.is_beginner_mode,
            'beginner_phase': user.beginner_phase,
        })

    except Exception as e:
        logger.error(f"toggle_beginner_mode error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500


@beginner_bp.route('/transition-check', methods=['GET'])
@jwt_required()
def transition_check():
    """
    Returns phase transition eligibility and criteria.
    Mascot message included if eligible.
    """
    try:
        user, err = _get_user_or_404()
        if err:
            return err

        result = run_transition_check(user)
        return jsonify({'success': True, **result})

    except Exception as e:
        logger.error(f"transition_check error: {e}")
        return jsonify({'error': 'Failed to check transition'}), 500


@beginner_bp.route('/arena-framing', methods=['GET'])
@jwt_required()
def arena_framing():
    """
    Returns mascot framing text for Arena.
    Called by frontend when user navigates to Arena in beginner phase.
    Backend Elo still runs normally; this only provides UI framing.
    """
    try:
        user, err = _get_user_or_404()
        if err:
            return err

        mascot = MascotEngine.respond_to_arena(user.beginner_phase)
        return jsonify({
            'success': True,
            'show_framing': bool(mascot),
            'mascot': mascot,
            'suppress_elo_display': user.beginner_phase in ('scaffolded', 'guided'),
        })

    except Exception as e:
        logger.error(f"arena_framing error: {e}")
        return jsonify({'error': 'Failed to load framing'}), 500
