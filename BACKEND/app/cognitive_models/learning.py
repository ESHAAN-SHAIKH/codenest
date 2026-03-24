"""
Learning-focused database models
Tracks debugging sessions and code iterations
"""

from app.extensions import db
from datetime import datetime


class CodeIteration(db.Model):
    """Tracks iterative code improvements for enforced refinement"""
    
    __tablename__ = 'code_iterations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    
    # Iteration tracking
    iteration_number = db.Column(db.Integer, default=1)
    stage = db.Column(db.String(50), nullable=False)  # functional, quality, performance, edge_cases
    
    # Code snapshot
    code_snapshot = db.Column(db.Text, nullable=False)
    
    # Quality metrics
    quality_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    complexity_score = db.Column(db.Integer, default=0)  # Cyclomatic complexity
    time_complexity = db.Column(db.String(50))  # O(n), O(n^2), etc.
    space_complexity = db.Column(db.String(50))
    
    # Improvement tracking
    improvement_delta = db.Column(db.Float, default=0.0)  # Change from previous iteration
    
    # AI Feedback
    ai_feedback = db.Column(db.JSON)  # Structured feedback from LLM
    
    # Status
    passed_stage = db.Column(db.Boolean, default=False)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert iteration to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'iteration_number': self.iteration_number,
            'stage': self.stage,
            'code_snapshot': self.code_snapshot,
            'quality_score': round(self.quality_score, 3),
            'complexity_score': self.complexity_score,
            'time_complexity': self.time_complexity,
            'space_complexity': self.space_complexity,
            'improvement_delta': round(self.improvement_delta, 3),
            'ai_feedback': self.ai_feedback,
            'passed_stage': self.passed_stage,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class DebuggingSession(db.Model):
    """Tracks debugging simulator sessions for skill development"""
    
    __tablename__ = 'debugging_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Bug details
    bug_type = db.Column(db.String(50), nullable=False)  # off_by_one, infinite_loop, null_error, etc.
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    
    # Challenge code
    code_with_bug = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text)
    actual_buggy_output = db.Column(db.Text)
    
    # User response
    user_explanation = db.Column(db.Text)  # User's explanation of the bug
    user_corrected_code = db.Column(db.Text)
    bug_location_line = db.Column(db.Integer)  # Line number where bug was identified
    
    # Evaluation
    explanation_quality_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0, scored by AI
    correctness_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    time_to_identify = db.Column(db.Integer)  # Seconds taken to identify bug
    time_to_fix = db.Column(db.Integer)  # Seconds taken to fix
    
    # AI Evaluation
    ai_evaluation = db.Column(db.JSON)  # Detailed feedback from LLM
    
    # Status
    completed = db.Column(db.Boolean, default=False)
    passed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def calculate_debugging_skill(self):
        """Calculate overall debugging skill score for this session"""
        if not self.completed:
            return 0.0
        
        # Weight factors
        explanation_weight = 0.4
        correctness_weight = 0.4
        speed_weight = 0.2
        
        # Time efficiency (faster = better, diminishing returns)
        time_factor = 0.0
        if self.time_to_identify:
            # Assume 180 seconds (3 min) is baseline
            time_factor = min(1.0, 180 / max(self.time_to_identify, 30))
        
        skill_score = (
            self.explanation_quality_score * explanation_weight +
            self.correctness_score * correctness_weight +
            time_factor * speed_weight
        )
        
        return round(min(1.0, max(0.0, skill_score)), 3)
    
    def to_dict(self):
        """Convert debugging session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bug_type': self.bug_type,
            'difficulty': self.difficulty,
            'code_with_bug': self.code_with_bug,
            'expected_output': self.expected_output,
            'user_explanation': self.user_explanation,
            'user_corrected_code': self.user_corrected_code,
            'bug_location_line': self.bug_location_line,
            'explanation_quality_score': round(self.explanation_quality_score, 3) if self.explanation_quality_score else 0.0,
            'correctness_score': round(self.correctness_score, 3) if self.correctness_score else 0.0,
            'time_to_identify': self.time_to_identify,
            'time_to_fix': self.time_to_fix,
            'debugging_skill_score': self.calculate_debugging_skill(),
            'ai_evaluation': self.ai_evaluation,
            'completed': self.completed,
            'passed': self.passed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
