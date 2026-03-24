"""
Debugging Engine Service
Generates debugging challenges with injected bugs and evaluates solutions
"""

from app.extensions import db
from app.cognitive_models.learning import DebuggingSession
from app.cognitive_models.cognitive import Concept
from typing import Dict, List, Optional
import random
import re
from datetime import datetime

class DebuggingEngine:
    """Service for generating and evaluating debugging challenges"""
    
    # Bug injection templates
    BUG_TEMPLATES = {
        'off_by_one': {
            'description': 'Off-by-one error in loop bounds',
            'difficulty': 'easy',
            'inject': lambda code: code.replace('range(len(', 'range(len('),  # Placeholder - actual implementation would be more complex
            'concept_keywords': ['loops', 'indexing']
        },
        'infinite_loop': {
            'description': 'Missing loop exit condition',
            'difficulty': 'medium',
            'concept_keywords': ['loops', 'control_flow']
        },
        'null_error': {
            'description': 'Null/None reference error',
            'difficulty': 'easy',
            'concept_keywords': ['variables', 'conditionals']
        },
        'type_error': {
            'description': 'Type mismatch error',
            'difficulty': 'easy',
            'concept_keywords': ['data types']
        },
        'logic_error': {
            'description': 'Incorrect logic in condition',
            'difficulty': 'medium',
            'concept_keywords': ['conditionals', 'logic']
        },
        'boundary_error': {
            'description': 'Incorrect boundary condition',
            'difficulty': 'medium',
            'concept_keywords': ['edge cases', 'conditionals']
        }
    }
    
    @staticmethod
    def generate_debug_challenge(difficulty: str = 'medium', bug_type: str = None) -> Dict:
        """
        Generate a debugging challenge with injected bug
        
        Args:
            difficulty: Challenge difficulty
            bug_type: Specific bug type to inject (optional)
            
        Returns:
            Dictionary with challenge data
        """
        # Select bug type
        if not bug_type:
            suitable_bugs = [
                bt for bt, data in DebuggingEngine.BUG_TEMPLATES.items() 
                if data['difficulty'] == difficulty
            ]
            bug_type = random.choice(suitable_bugs) if suitable_bugs else 'off_by_one'
        
        bug_template = DebuggingEngine.BUG_TEMPLATES.get(bug_type, DebuggingEngine.BUG_TEMPLATES['logic_error'])
        
        # Get sample code for bug type
        code_with_bug = DebuggingEngine._get_sample_buggy_code(bug_type)
        expected_output = DebuggingEngine._get_expected_output(bug_type)
        buggy_output = DebuggingEngine._get_buggy_output(bug_type)
        
        return {
            'bug_type': bug_type,
            'difficulty': difficulty,
            'description': bug_template['description'],
            'code_with_bug': code_with_bug,
            'expected_output': expected_output,
            'actual_buggy_output': buggy_output,
            'hint': DebuggingEngine._get_bug_hint(bug_type)
        }
    
    @staticmethod
    def _get_sample_buggy_code(bug_type: str) -> str:
        """Get sample code with specific bug type"""
        samples = {
            'off_by_one': """def print_numbers(n):
    # Print numbers from 1 to n
    for i in range(1, n):  # Bug: should be range(1, n + 1)
        print(i)
    
print_numbers(5)""",
            
            'infinite_loop': """def count_down(n):
    # Count down from n to 1
    while n > 0:
        print(n)
        # Bug: Missing n -= 1
    print("Done!")

count_down(3)""",
            
            'null_error': """def get_first_item(items):
    # Return first item or default
    first = items[0]  # Bug: No check if items is empty
    return first

result = get_first_item([])
print(result)""",
            
            'type_error': """def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: str in list causes TypeError

average = calculate_average([1, 2, "3", 4])
print(average)""",
            
            'logic_error': """def is_even(number):
    # Check if number is even
    if number % 2 == 1:  # Bug: Logic inverted
        return True
    return False

print(is_even(4))  # Should print True, prints False""",
            
            'boundary_error': """def find_max(numbers):
    # Find maximum in list
    max_num = 0  # Bug: Fails for negative numbers
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

print(find_max([-5, -2, -10]))  # Should print -2, prints 0"""
        }
        
        return samples.get(bug_type, samples['logic_error'])
    
    @staticmethod
    def _get_expected_output(bug_type: str) -> str:
        """Get expected correct output"""
        outputs = {
            'off_by_one': "1\n2\n3\n4\n5",
            'infinite_loop': "3\n2\n1\nDone!",
            'null_error': "None (or default value)",
            'type_error': "2.5",
            'logic_error': "True",
            'boundary_error': "-2"
        }
        return outputs.get(bug_type, "")
    
    @staticmethod
    def _get_buggy_output(bug_type: str) -> str:
        """Get actual buggy output"""
        outputs = {
            'off_by_one': "1\n2\n3\n4",
            'infinite_loop': "3\n3\n3\n... (infinite)",
            'null_error': "IndexError: list index out of range",
            'type_error': "TypeError: unsupported operand type(s)",
            'logic_error': "False",
            'boundary_error': "0"
        }
        return outputs.get(bug_type, "Error or unexpected output")
   
    @staticmethod
    def _get_bug_hint(bug_type: str) -> str:
        """Get hint for bug type"""
        hints = {
            'off_by_one': "Check your loop bounds carefully. Are you including all numbers?",
            'infinite_loop': "Make sure your loop has a way to exit. What changes each iteration?",
            'null_error': "What happens if the list is empty? Should you check first?",
            'type_error': "Check the types of all values. Can they all be used in this operation?",
            'logic_error': "Double-check your condition. What does it actually test for?",
            'boundary_error': "Consider edge cases. What if all numbers are negative?"
        }
        return hints.get(bug_type, "Carefully trace through the code line by line.")
    
    @staticmethod
    def start_debugging_session(user_id: int, difficulty: str = 'medium', bug_type: str = None) -> DebuggingSession:
        """
        Start a new debugging session for a user
        
        Args:
            user_id: User ID
            difficulty: Challenge difficulty
            bug_type: Optional specific bug type
            
        Returns:
            DebuggingSession instance
        """
        challenge = DebuggingEngine.generate_debug_challenge(difficulty, bug_type)
        
        session = DebuggingSession(
            user_id=user_id,
            bug_type=challenge['bug_type'],
            difficulty=difficulty,
            code_with_bug=challenge['code_with_bug'],
            expected_output=challenge['expected_output'],
            actual_buggy_output=challenge['actual_buggy_output']
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def evaluate_explanation(explanation: str, bug_type: str) -> float:
        """
        Evaluate the quality of a bug explanation
        Uses keyword matching and completeness heuristics
        
        Args:
            explanation: User's bug explanation
            bug_type: Type of bug
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        explanation_lower = explanation.lower()
        score = 0.0
        
        # Keywords to look for based on bug type
        key_terms = {
            'off_by_one': ['range', 'bound', 'index', '+1', 'inclusive', 'exclusive'],
            'infinite_loop': ['exit', 'condition', 'increment', 'decrement', 'break', 'loop'],
            'null_error': ['empty', 'none', 'check', 'validate', 'null'],
            'type_error': ['type', 'string', 'integer', 'convert', 'cast'],
            'logic_error': ['condition', 'logic', 'inverse', 'opposite', 'should'],
            'boundary_error': ['edge', 'negative', 'initial', 'minimum', 'maximum']
        }
        
        relevant_terms = key_terms.get(bug_type, [])
        
        # Check for relevant keywords (40%)
        terms_found = sum(1 for term in relevant_terms if term in explanation_lower)
        keyword_score = min(0.4, (terms_found / max(len(relevant_terms), 1)) * 0.4)
        score += keyword_score
        
        # Check explanation length (30%)
        word_count = len(explanation.split())
        if word_count >= 20:
            score += 0.3
        elif word_count >= 10:
            score += 0.2
        elif word_count >= 5:
            score += 0.1
        
        # Check for solution mention (30%)
        solution_keywords = ['fix', 'correct', 'should', 'change', 'modify', 'update']
        has_solution = any(keyword in explanation_lower for keyword in solution_keywords)
        if has_solution:
            score += 0.3
        
        return round(min(1.0, score), 3)
    
    @staticmethod
    def submit_debugging_solution(
        session_id: int,
        user_explanation: str,
        corrected_code: str,
        bug_location_line: int = None
    ) -> Dict:
        """
        Submit and evaluate a debugging solution
        
        Args:
            session_id: Debugging session ID
            user_explanation: User's explanation of the bug
            corrected_code: User's corrected code
            bug_location_line: Line number where bug was identified
            
        Returns:
            Dictionary with evaluation results
        """
        session = DebuggingSession.query.get(session_id)
        
        if not session:
            return {'error': 'Session not found'}
        
        if session.completed:
            return {'error': 'Session already completed'}
        
        # Calculate time taken
        time_taken = int((datetime.utcnow() - session.started_at).total_seconds())
        
        # Evaluate explanation quality
        explanation_score = DebuggingEngine.evaluate_explanation(user_explanation, session.bug_type)
        
        # TODO: Actually execute corrected code and compare output
        # For now, simple heuristic based on code differences
        correctness_score = 0.8 if corrected_code != session.code_with_bug else 0.0
        
        # Update session
        session.user_explanation = user_explanation
        session.user_corrected_code = corrected_code
        session.bug_location_line = bug_location_line
        session.explanation_quality_score = explanation_score
        session.correctness_score = correctness_score
        session.time_to_identify = time_taken
        session.time_to_fix = time_taken
        session.completed = True
        session.passed = correctness_score >= 0.7 and explanation_score >= 0.5
        session.completed_at = datetime.utcnow()
        
        # AI evaluation (simplified - would use LLM in production)
        session.ai_evaluation = {
            'explanation_strengths': 'Good identification of the issue' if explanation_score > 0.6 else 'Could be more detailed',
            'explanation_weaknesses': 'Explain why this causes the bug' if explanation_score < 0.7 else None,
            'code_feedback': 'Correct fix applied' if correctness_score > 0.7 else 'Code still has issues'
        }
        
        db.session.commit()
        
        # Calculate overall debugging skill
        skill_score = session.calculate_debugging_skill()
        
        return {
            'passed': session.passed,
            'explanation_quality': explanation_score,
            'correctness': correctness_score,
            'debugging_skill': skill_score,
            'time_taken': time_taken,
            'ai_evaluation': session.ai_evaluation
        }
    
    @staticmethod
    def get_debugging_skill_metrics(user_id: int) -> Dict:
        """
        Get aggregate debugging skill metrics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with skill metrics
        """
        sessions = DebuggingSession.query.filter_by(
            user_id=user_id,
            completed=True
        ).all()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'pass_rate': 0.0,
                'average_skill': 0.0,
                'average_time': 0,
                'bug_type_proficiency': {}
            }
        
        total_skill = sum(s.calculate_debugging_skill() for s in sessions)
        passed_sessions = sum(1 for s in sessions if s.passed)
        total_time = sum(s.time_to_identify or 0 for s in sessions)
        
        # Bug type breakdown
        bug_types = {}
        for session in sessions:
            if session.bug_type not in bug_types:
                bug_types[session.bug_type] = {'count': 0, 'skill': 0}
            bug_types[session.bug_type]['count'] += 1
            bug_types[session.bug_type]['skill'] += session.calculate_debugging_skill()
        
        bug_type_proficiency = {
            bt: round(data['skill'] / data['count'], 3)
            for bt, data in bug_types.items()
        }
        
        return {
            'total_sessions': len(sessions),
            'pass_rate': round(passed_sessions / len(sessions), 3),
            'average_skill': round(total_skill / len(sessions), 3),
            'average_time': int(total_time / len(sessions)),
            'bug_type_proficiency': bug_type_proficiency,
            'strongest_area': max(bug_type_proficiency, key=bug_type_proficiency.get) if bug_type_proficiency else None,
            'weakest_area': min(bug_type_proficiency, key=bug_type_proficiency.get) if bug_type_proficiency else None
        }
