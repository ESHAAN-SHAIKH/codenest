"""
Misconception Detection Service
AI-powered detection and classification of common coding misconceptions
"""

from app.extensions import db
from app.cognitive_models.cognitive import MisconceptionTag, Concept, ConceptMastery
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class MisconceptionDetector:
    """Service for detecting and tracking coding misconceptions"""
    
    # Common misconception patterns with regex
    PATTERNS = {
        'off_by_one': {
            'regex': [
                r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\([^\)]+\)\s*\+\s*1\s*\)',  # range(len(x) + 1)
                r'while\s+\w+\s*<=\s*len\s*\(',  # while i <= len()
            ],
            'description': 'Off-by-one error in loop bounds',
            'concept_keywords': ['loops', 'iteration', 'indexing']
        },
        'infinite_loop': {
            'regex': [
                r'while\s+True\s*:(?!.*break)',  # while True without break
                r'while\s+\d+\s*:',  # while 1:
            ],
            'description': 'Potential infinite loop without exit condition',
            'concept_keywords': ['loops', 'control_flow']
        },
        'null_handling': {
            'regex': [
                r'if\s+\w+\s*==\s*None',  # Should use 'is None'
                r'if\s+not\s+\w+\s*:(?!.*is None)',  # Risky None check
            ],
            'description': 'Improper null/None handling',
            'concept_keywords': ['conditionals', 'null_safety']
        },
        'list_modification_during_iteration': {
            'regex': [
                r'for\s+\w+\s+in\s+(\w+)\s*:.*\1\.remove\(',  # Modifying list while iterating
                r'for\s+\w+\s+in\s+(\w+)\s*:.*\1\.append\(',
            ],
            'description': 'Modifying list during iteration',
            'concept_keywords': ['loops', 'data_structures', 'lists']
        },
        'mutable_default_argument': {
            'regex': [
                r'def\s+\w+\s*\([^)]*=\s*\[\s*\]',  # def func(x=[])
                r'def\s+\w+\s*\([^)]*=\s*\{\s*\}',  # def func(x={})
            ],
            'description': 'Mutable default argument in function',
            'concept_keywords': ['functions', 'scope', 'mutability']
        },
        'string_concatenation_in_loop': {
            'regex': [
                r'for\s+\w+\s+in.*:\s*\n\s*\w+\s*\+=\s*["\']',  # string += in loop
            ],
            'description': 'Inefficient string concatenation in loop',
            'concept_keywords': ['loops', 'performance', 'strings']
        },
        'variable_scope_confusion': {
            'regex': [
                r'global\s+\w+',  # Using global unnecessarily
            ],
            'description': 'Variable scope misunderstanding',
            'concept_keywords': ['scope', 'variables']
        }
    }
    
    @staticmethod
    def analyze_code_for_misconceptions(
        user_id: int,
        code: str,
        challenge_id: int = None,
        lesson_id: int = None,
        language: str = 'python'
    ) -> List[Dict]:
        """
        Analyze code for common misconceptions
        
        Args:
            user_id: User ID
            code: Code to analyze
            challenge_id: Optional challenge ID
            lesson_id: Optional lesson ID
            language: Programming language (only Python supported currently)
            
        Returns:
            List of detected misconceptions
        """
        if language != 'python':
            logger.warning(f"Misconception detection not yet supported for {language}")
            return []
        
        detected = []
        
        for misconception_type, pattern_data in MisconceptionDetector.PATTERNS.items():
            for regex_pattern in pattern_data['regex']:
                if re.search(regex_pattern, code, re.MULTILINE | re.DOTALL):
                    # Find related concept
                    concept = MisconceptionDetector._find_related_concept(
                        pattern_data['concept_keywords']
                    )
                    
                    # Check if this misconception already exists for user
                    existing = MisconceptionTag.query.filter_by(
                        user_id=user_id,
                        misconception_type=misconception_type,
                        resolved=False
                    ).first()
                    
                    if existing:
                        # Mark recurrence
                        existing.mark_recurrence(code)
                    else:
                        # Create new misconception tag
                        misconception = MisconceptionTag(
                            user_id=user_id,
                            concept_id=concept.id if concept else None,
                            misconception_type=misconception_type,
                            description=pattern_data['description'],
                            code_snippet=code[:500],  # Store first 500 chars
                            challenge_id=challenge_id,
                            lesson_id=lesson_id
                        )
                        db.session.add(misconception)
                    
                    detected.append({
                        'type': misconception_type,
                        'description': pattern_data['description'],
                        'severity': 'medium',  # Could be enhanced with ML
                        'concept_keywords': pattern_data['concept_keywords']
                    })
                    
                    break  # Only count once per misconception type
        
        db.session.commit()
        
        return detected
    
    @staticmethod
    def _find_related_concept(keywords: List[str]) -> Optional[Concept]:
        """Find a concept related to given keywords"""
        for keyword in keywords:
            concept = Concept.query.filter(
                Concept.name.ilike(f'%{keyword}%')
            ).first()
            if concept:
                return concept
        return None
    
    @staticmethod
    def classify_error_type(error_message: str, code: str) -> str:
        """
        Classify error into categories
        
        Args:
            error_message: Error message from code execution
            code: Source code that caused error
            
        Returns:
            Error classification
        """
        error_lower = error_message.lower()
        
        # Syntax errors
        if 'syntaxerror' in error_lower or 'invalid syntax' in error_lower:
            return 'syntax'
        
        # Logic errors
        elif 'indexerror' in error_lower:
            return 'logic_indexing'
        elif 'keyerror' in error_lower:
            return 'logic_dictionary'
        elif 'typeerror' in error_lower:
            return 'logic_type'
        elif 'valueerror' in error_lower:
            return 'logic_value'
        elif 'attributeerror' in error_lower:
            return 'logic_attribute'
        
        # Runtime errors
        elif 'zerodivisionerror' in error_lower:
            return 'runtime_division'
        elif 'nameerror' in error_lower:
            return 'runtime_undefined'
        elif 'recursionerror' in error_lower or 'maximum recursion' in error_lower:
            return 'runtime_recursion'
        
        # Conceptual errors (detected from code patterns)
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            if re.search(r'while.*:', code):
                return 'conceptual_infinite_loop'
            return 'conceptual_efficiency'
        
        return 'unknown'
    
    @staticmethod
    def tag_misconception(
        user_id: int,
        concept_id: int,
        misconception_type: str,
        description: str,
        code_snippet: str,
        challenge_id: int = None,
        lesson_id: int = None
    ) -> MisconceptionTag:
        """
        Manually tag a misconception (e.g., from AI analysis)
        
        Args:
            user_id: User ID
            concept_id: Related concept ID
            misconception_type: Type of misconception
            description: Description of the misconception
            code_snippet: Code exhibiting the misconception
            challenge_id: Optional challenge ID
            lesson_id: Optional lesson ID
            
        Returns:
            MisconceptionTag instance
        """
        # Check for existing unresolved misconception
        existing = MisconceptionTag.query.filter_by(
            user_id=user_id,
            concept_id=concept_id,
            misconception_type=misconception_type,
            resolved=False
        ).first()
        
        if existing:
            existing.mark_recurrence(code_snippet)
            db.session.commit()
            return existing
        
        misconception = MisconceptionTag(
            user_id=user_id,
            concept_id=concept_id,
            misconception_type=misconception_type,
            description=description,
            code_snippet=code_snippet,
            challenge_id=challenge_id,
            lesson_id=lesson_id
        )
        
        db.session.add(misconception)
        db.session.commit()
        
        return misconception
    
    @staticmethod
    def check_recurrence(user_id: int, misconception_type: str) -> Dict:
        """
        Check if a misconception is recurring for a user
        
        Args:
            user_id: User ID
            misconception_type: Type of misconception to check
            
        Returns:
            Dictionary with recurrence information
        """
        misconception = MisconceptionTag.query.filter_by(
            user_id=user_id,
            misconception_type=misconception_type,
            resolved=False
        ).first()
        
        if not misconception:
            return {
                'recurring': False,
                'count': 0
            }
        
        return {
            'recurring': True,
            'count': misconception.recurrence_count,
            'first_detected': misconception.detected_at.isoformat() if misconception.detected_at else None,
            'last_occurred': misconception.last_occurred_at.isoformat() if misconception.last_occurred_at else None,
            'severity': 'high' if misconception.recurrence_count >= 3 else 'medium'
        }
    
    @staticmethod
    def get_user_misconceptions(user_id: int, resolved: bool = False) -> List[Dict]:
        """
        Get all misconceptions for a user
        
        Args:
            user_id: User ID
            resolved: Whether to include resolved misconceptions
            
        Returns:
            List of misconception dictionaries
        """
        query = MisconceptionTag.query.filter_by(user_id=user_id)
        
        if not resolved:
            query = query.filter_by(resolved=False)
        
        misconceptions = query.order_by(MisconceptionTag.recurrence_count.desc()).all()
        
        return [m.to_dict() for m in misconceptions]
    
    @staticmethod
    def resolve_misconception(misconception_id: int):
        """
        Mark a misconception as resolved
        
        Args:
            misconception_id: Misconception ID
        """
        misconception = MisconceptionTag.query.get(misconception_id)
        
        if misconception:
            misconception.mark_resolved()
            db.session.commit()
            
            logger.info(f"Resolved misconception {misconception_id} for user {misconception.user_id}")
