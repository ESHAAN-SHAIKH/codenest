"""
Cognitive API endpoints
Handles concept mastery, adaptive learning, and knowledge tracking
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.cognitive_engine import CognitiveEngine
from app.cognitive_models.cognitive import Concept
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

cognitive_bp = Blueprint('cognitive', __name__)


@cognitive_bp.route('/concepts', methods=['GET'])
def get_concepts():
    """Get all concepts in taxonomy — public, no auth needed."""
    try:
        concepts = Concept.query.order_by(Concept.difficulty_level, Concept.category).all()
        return jsonify({
            'success': True,
            'data': {
                'concepts': [c.to_dict() for c in concepts],
                'total': len(concepts)
            }
        })
    except Exception as e:
        logger.error(f"Error getting concepts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/mastery/me', methods=['GET'])
@jwt_required()
def get_mastery_profile():
    """Get the current user's complete mastery profile (JWT-identity based)."""
    try:
        user_id = int(get_jwt_identity())
        profile = CognitiveEngine.get_user_mastery_profile(user_id)
        return jsonify({
            'success': True,
            'data': profile
        })
    except Exception as e:
        logger.error(f"Error getting mastery profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/update', methods=['POST'])
@jwt_required()
def update_mastery():
    """Update concept mastery based on performance (uses JWT identity, not body user_id)."""
    try:
        user_id = int(get_jwt_identity())
        data = request.json or {}

        required = ['concept_id', 'success', 'time_taken']
        if not all(field in data for field in required):
            return jsonify({'success': False, 'error': 'Missing required fields: concept_id, success, time_taken'}), 400

        result = CognitiveEngine.update_concept_mastery(
            user_id=user_id,
            concept_id=int(data['concept_id']),
            success=bool(data['success']),
            time_taken=int(data['time_taken']),
            hints_used=int(data.get('hints_used', 0))
        )

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Error updating mastery: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/weak-concepts', methods=['GET'])
@jwt_required()
def get_weak_concepts():
    """Get the current user's concepts needing remediation."""
    try:
        user_id = int(get_jwt_identity())
        threshold = request.args.get('threshold', 0.5, type=float)
        weak_concepts = CognitiveEngine.get_weak_concepts(user_id, threshold)

        return jsonify({
            'success': True,
            'data': {
                'weak_concepts': weak_concepts,
                'count': len(weak_concepts)
            }
        })
    except Exception as e:
        logger.error(f"Error getting weak concepts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/due-for-review', methods=['GET'])
@jwt_required()
def get_due_concepts():
    """Get the current user's concepts due for spaced repetition review."""
    try:
        user_id = int(get_jwt_identity())
        due_concepts = CognitiveEngine.get_concepts_due_for_review(user_id)

        return jsonify({
            'success': True,
            'data': {
                'due_concepts': due_concepts,
                'count': len(due_concepts)
            }
        })
    except Exception as e:
        logger.error(f"Error getting due concepts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/adaptive-next', methods=['GET'])
@jwt_required()
def get_adaptive_next():
    """Get adaptive next challenge recommendation for current user."""
    try:
        user_id = int(get_jwt_identity())
        recommendation = CognitiveEngine.get_adaptive_next_challenge(user_id)

        if not recommendation:
            return jsonify({
                'success': True,
                'data': {
                    'has_recommendation': False,
                    'message': "Great job! You've mastered all available concepts."
                }
            })

        return jsonify({
            'success': True,
            'data': {
                'has_recommendation': True,
                **recommendation
            }
        })
    except Exception as e:
        logger.error(f"Error getting adaptive recommendation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@cognitive_bp.route('/knowledge-gaps', methods=['GET'])
@jwt_required()
def get_knowledge_gaps():
    """Get identified knowledge gaps for current user."""
    try:
        user_id = int(get_jwt_identity())
        gaps = CognitiveEngine.detect_knowledge_gaps(user_id)

        return jsonify({
            'success': True,
            'data': {
                'gaps': gaps,
                'count': len(gaps)
            }
        })
    except Exception as e:
        logger.error(f"Error getting knowledge gaps: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
