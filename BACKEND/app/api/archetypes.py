"""
Archetype progression API endpoints
Handles identity-based skill progression
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.archetype_engine import ArchetypeEngine
from app.models import User
import logging

logger = logging.getLogger(__name__)

archetypes_bp = Blueprint('archetypes', __name__)


@archetypes_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_archetype_progress():
    """Get current user's archetype progression across all types"""
    try:
        current_user_id = int(get_jwt_identity())
        profile = ArchetypeEngine.get_user_archetype_profile(current_user_id)

        return jsonify({
            'success': True,
            'data': profile
        })
    except Exception as e:
        logger.error(f"Error getting archetype progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@archetypes_bp.route('/track-behavior', methods=['POST'])
@jwt_required()
def track_behavior():
    """Track user behavior for archetype progression"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.json or {}

        required = ['archetype_type', 'behavior_data']
        if not all(field in data for field in required):
            return jsonify({'success': False, 'error': 'Missing required fields: archetype_type, behavior_data'}), 400

        result = ArchetypeEngine.track_behavior(
            user_id=current_user_id,
            archetype_type=data['archetype_type'],
            behavior_data=data['behavior_data']
        )

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Error tracking behavior: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@archetypes_bp.route('/evolution/<archetype_type>', methods=['GET'])
@jwt_required()
def get_evolution_path(archetype_type):
    """Get evolution tree for a specific archetype of the current user"""
    try:
        current_user_id = int(get_jwt_identity())
        path = ArchetypeEngine.get_evolution_path(current_user_id, archetype_type)

        if 'error' in path:
            return jsonify({'success': False, 'error': path['error']}), 404

        return jsonify({
            'success': True,
            'data': path
        })
    except Exception as e:
        logger.error(f"Error getting evolution path: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@archetypes_bp.route('/leaderboard/<archetype_type>', methods=['GET'])
@jwt_required()
def get_leaderboard(archetype_type):
    """Get leaderboard for specific archetype"""
    try:
        limit = request.args.get('limit', 10, type=int)
        leaderboard = ArchetypeEngine.get_archetype_leaderboard(archetype_type, limit)

        return jsonify({
            'success': True,
            'data': {
                'archetype_type': archetype_type,
                'leaderboard': leaderboard,
                'total': len(leaderboard)
            }
        })
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@archetypes_bp.route('/definitions', methods=['GET'])
@jwt_required()
def get_archetype_definitions():
    """Get all archetype definitions"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'archetypes': ArchetypeEngine.ARCHETYPES
            }
        })
    except Exception as e:
        logger.error(f"Error getting archetype definitions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
