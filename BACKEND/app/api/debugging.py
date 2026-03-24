"""
Debugging API endpoints
Handles debugging challenges and skill tracking
"""

from flask import Blueprint, request, jsonify
from app.services.debugging_engine import DebuggingEngine
from app.services.misconception_detector import MisconceptionDetector
from app.cognitive_models.learning import DebuggingSession
import logging

logger = logging.getLogger(__name__)

debugging_bp = Blueprint('debugging', __name__)


@debugging_bp.route('/start', methods=['POST'])
def start_session():
    """Start a new debugging session"""
    try:
        data = request.json
        
        if 'user_id' not in data:
            return jsonify({'success': False, 'error': 'user_id required'}), 400
        
        difficulty = data.get('difficulty', 'medium')
        bug_type = data.get('bug_type')
        
        session = DebuggingEngine.start_debugging_session(
            user_id=int(data['user_id']),
            difficulty=difficulty,
            bug_type=bug_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'session': session.to_dict(),
                'challenge': {
                    'code': session.code_with_bug,
                    'expected_output': session.expected_output,
                    'buggy_output': session.actual_buggy_output,
                    'bug_type': session.bug_type,
                    'difficulty': session.difficulty
                }
            }
        })
    except Exception as e:
        logger.error(f"Error starting debugging session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@debugging_bp.route('/submit', methods=['POST'])
def submit_solution():
    """Submit debugging solution"""
    try:
        data = request.json
        
        required = ['session_id', 'user_explanation', 'corrected_code']
        if not all(field in data for field in required):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = DebuggingEngine.submit_debugging_solution(
            session_id=int(data['session_id']),
            user_explanation=data['user_explanation'],
            corrected_code=data['corrected_code'],
            bug_location_line=data.get('bug_location_line')
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Error submitting debugging solution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@debugging_bp.route('/skills/<user_id>', methods=['GET'])
def get_debugging_skills(user_id):
    """Get user's debugging skill metrics"""
    try:
        metrics = DebuggingEngine.get_debugging_skill_metrics(int(user_id))
        
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logger.error(f"Error getting debugging skills: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@debugging_bp.route('/history/<user_id>', methods=['GET'])
def get_debugging_history(user_id):
    """Get debugging session history"""
    try:
        sessions = DebuggingSession.query.filter_by(
            user_id=int(user_id)
        ).order_by(DebuggingSession.started_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'data': {
                'sessions': [s.to_dict() for s in sessions],
                'total': len(sessions)
            }
        })
    except Exception as e:
        logger.error(f"Error getting debugging history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@debugging_bp.route('/misconceptions/<user_id>', methods=['GET'])
def get_misconceptions(user_id):
    """Get user's misconception history"""
    try:
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        misconceptions = MisconceptionDetector.get_user_misconceptions(
            user_id=int(user_id),
            resolved=resolved
        )
        
        return jsonify({
            'success': True,
            'data': {
                'misconceptions': misconceptions,
                'total': len(misconceptions)
            }
        })
    except Exception as e:
        logger.error(f"Error getting misconceptions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
