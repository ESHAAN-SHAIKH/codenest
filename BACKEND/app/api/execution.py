"""
Code Execution API for Code Nest
Uses MultiLanguageSandbox for secure, multi-language code execution
"""

from flask import Blueprint, jsonify, request
from ..services.sandbox import MultiLanguageSandbox
import logging

logger = logging.getLogger(__name__)
execution_bp = Blueprint('execution', __name__)

# Initialize sandbox
sandbox = MultiLanguageSandbox(timeout=15, max_memory_mb=100)


@execution_bp.route('/', methods=['POST'])
def execute_code():
    """Execute code in a secure sandbox"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        code = data.get('code')
        language = data.get('language', 'python')
        
        if not code or not code.strip():
            return jsonify({
                'success': False,
                'error': 'No code provided',
                'output': ''
            }), 400
        
        # Validate language
        supported_languages = sandbox.get_supported_languages()
        language_lower = language.lower()
       
        if language_lower not in supported_languages:
            return jsonify({
                'success': False,
                'error': f'Language "{language}" is not supported. Supported languages: {", ".join(supported_languages.keys())}',
                'output': ''
            }), 400
        
        # Check if language is available
        if not supported_languages[language_lower]:
            return jsonify({
                'success': False,
                'error': f'{language} runtime/compiler not available on this server',
                'output': ''
            }), 503
        
        # Execute code
        logger.info(f"Executing {language} code (length: {len(code)} chars)")
        result = sandbox.execute_code(code=code, language=language_lower)
        
        # Log result
        if result.get('success'):
            logger.info(f"Execution successful in {result.get('execution_time', 0):.2f}s")
        else:
            logger.warning(f"Execution failed: {result.get('error', 'Unknown error')}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Execution endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during code execution',
            'details': str(e),
            'output': ''
        }), 500


@execution_bp.route('/validate', methods=['POST'])
def validate_lesson():
    """Validate lesson output against expected output"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_output = data.get('user_output', '')
        expected_output = data.get('expected_output', '')
        
        if expected_output is None:
            return jsonify({'error': 'expected_output is required'}), 400
        
        # Use sandbox validation
        result = sandbox.validate_lesson_output(
            user_output=user_output,
            expected_output=expected_output
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Validation endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred during validation',
            'details': str(e)
        }), 500


@execution_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported programming languages"""
    try:
        languages = sandbox.get_supported_languages()
        return jsonify({
            'languages': languages,
            'available': [lang for lang, available in languages.items() if available]
        })
    
    except Exception as e:
        logger.error(f"Languages endpoint error: {str(e)}")
        return jsonify({
            'error': 'An error occurred fetching supported languages',
            'details': str(e)
        }), 500
