"""
AI Assistant API endpoints for Code Nest
Powered by LLMService for intelligent code tutoring
"""

from flask import Blueprint, jsonify, request
from ..services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__)

# Initialize LLM service
llm_service = LLMService()


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """General chat endpoint for AI assistant"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '')
        code = data.get('code', '')
        context = data.get('context', 'general')
        user_level = data.get('user_level', 'beginner')
        language = data.get('language', 'python')
        
        if not message and not code:
            return jsonify({'error': 'Please provide a message or code'}), 400
        
        # If code is provided, use explain_code
        if code:
            result = llm_service.explain_code(
                code=code,
                context=context,
                question=message or 'Explain this code',
                user_level=user_level,
                language=language
            )
        else:
            # For general chat, treat as concept explanation
            result = llm_service.get_concept_explanation(
                concept=message,
                user_level=user_level,
                language=language
            )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }), 500


@ai_bp.route('/explain', methods=['POST'])
def explain_code():
    """Explain code endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        code = data.get('code')
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        context = data.get('context', 'general')
        question = data.get('question', 'Explain this code')
        user_level = data.get('user_level', 'beginner')
        language = data.get('language', 'python')
        
        result = llm_service.explain_code(
            code=code,
            context=context,
            question=question,
            user_level=user_level,
            language=language
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Explain endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred explaining the code',
            'details': str(e)
        }), 500


@ai_bp.route('/hint', methods=['POST'])
def get_hint():
    """Generate hint for struggling user"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        lesson_id = data.get('lesson_id')
        user_code = data.get('user_code', '')
        expected_output = data.get('expected_output', '')
        language = data.get('language', 'python')
        
        if lesson_id is None:
            return jsonify({'error': 'lesson_id is required'}), 400
        
        result = llm_service.generate_hint(
            lesson_id=lesson_id,
            user_code=user_code,
            expected_output=expected_output,
            language=language
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Hint endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred generating hint',
            'details': str(e)
        }), 500


@ai_bp.route('/feedback', methods=['POST'])
def get_feedback():
    """Generate feedback for challenge submission"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_code = data.get('user_code')
        expected_output = data.get('expected_output')
        actual_output = data.get('actual_output')
        language = data.get('language', 'python')
        
        if not user_code or expected_output is None or actual_output is None:
            return jsonify({
                'error': 'user_code, expected_output, and actual_output are required'
            }), 400
        
        result = llm_service.generate_challenge_feedback(
            user_code=user_code,
            expected_output=expected_output,
            actual_output=actual_output,
            language=language
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Feedback endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred generating feedback',
            'details': str(e)
        }), 500


@ai_bp.route('/concept', methods=['POST'])
def explain_concept():
    """Explain a programming concept"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        concept = data.get('concept')
        if not concept:
            return jsonify({'error': 'concept is required'}), 400
        
        user_level = data.get('user_level', 'beginner')
        language = data.get('language', 'python')
        
        result = llm_service.get_concept_explanation(
            concept=concept,
            user_level=user_level,
            language=language
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Concept endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred explaining the concept',
            'details': str(e)
        }), 500
