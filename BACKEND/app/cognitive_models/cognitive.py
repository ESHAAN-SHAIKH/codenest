"""
Cognitive modeling database models
Tracks concept mastery, misconceptions, and spaced repetition
"""

from app.extensions import db
from datetime import datetime, timedelta
import math


class Concept(db.Model):
    """Master concept taxonomy for programming concepts"""
    
    __tablename__ = 'concepts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # variables, control_flow, data_structures, etc.
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.Integer, default=1)  # 1-10 scale
    
    # Prerequisite relationships (stored as JSON array of concept IDs)
    prerequisite_concepts = db.Column(db.JSON, default=list)
    
    # Tags for categorization
    tags = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mastery_records = db.relationship('ConceptMastery', backref='concept', lazy=True, cascade='all, delete-orphan')
    misconceptions = db.relationship('MisconceptionTag', backref='concept', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert concept to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'difficulty_level': self.difficulty_level,
            'prerequisite_concepts': self.prerequisite_concepts or [],
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConceptMastery(db.Model):
    """Tracks user mastery levels for each concept with spaced repetition"""
    
    __tablename__ = 'concept_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    
    # Mastery metrics
    mastery_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    confidence_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    
    # Spaced repetition data
    last_practiced_at = db.Column(db.DateTime, default=datetime.utcnow)
    practice_count = db.Column(db.Integer, default=0)
    decay_factor = db.Column(db.Float, default=0.95)  # How quickly mastery decays
    spaced_repetition_due_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance tracking
    total_attempts = db.Column(db.Integer, default=0)
    successful_attempts = db.Column(db.Integer, default=0)
    average_time_seconds = db.Column(db.Float, default=0.0)
    hint_usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'concept_id', name='unique_user_concept'),)
    
    def calculate_decay(self):
        """
        Calculate current mastery with decay based on time since last practice
        Uses spaced repetition algorithm: M(t) = M0 * e^(-t/τ)
        """
        if not self.last_practiced_at:
            return self.mastery_score
        
        days_since_practice = (datetime.utcnow() - self.last_practiced_at).days
        
        if days_since_practice == 0:
            return self.mastery_score
        
        # Decay constant (tau) based on mastery level - higher mastery = slower decay
        tau = 30 * (1 + self.mastery_score)  # 30-60 days depending on mastery
        
        # Exponential decay
        decayed_score = self.mastery_score * math.exp(-days_since_practice / tau)
        
        return max(0.0, min(1.0, decayed_score))
    
    def update_mastery(self, success: bool, time_taken: int, hints_used: int):
        """
        Update mastery score based on performance
        
        Args:
            success: Whether the attempt was successful
            time_taken: Time taken in seconds
            hints_used: Number of hints used
        """
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
        
        self.hint_usage_count += hints_used
        
        # Update average time
        if self.average_time_seconds == 0:
            self.average_time_seconds = time_taken
        else:
            self.average_time_seconds = (self.average_time_seconds + time_taken) / 2
        
        # Calculate new mastery score
        # Base score on success rate
        success_rate = self.successful_attempts / self.total_attempts
        
        # Penalize hint usage (each hint reduces score)
        hint_penalty = min(0.3, hints_used * 0.1)
        
        # Time efficiency factor (faster = better, but capped)
        # Assume 300 seconds is baseline
        time_factor = min(1.0, 300 / max(time_taken, 30))
        
        # Calculate new mastery
        new_mastery = (success_rate * 0.6) + (time_factor * 0.3) + (0.1 if hints_used == 0 else 0)
        new_mastery = max(0.0, min(1.0, new_mastery - hint_penalty))
        
        # Smooth transition (weighted average with previous mastery)
        self.mastery_score = (self.mastery_score * 0.7) + (new_mastery * 0.3)
        
        # Update confidence based on consistency
        if success:
            self.confidence_score = min(1.0, self.confidence_score + 0.1)
        else:
            self.confidence_score = max(0.0, self.confidence_score - 0.15)
        
        # Update spaced repetition schedule
        self.last_practiced_at = datetime.utcnow()
        self.practice_count += 1
        
        # Calculate next review date based on mastery
        # Higher mastery = longer intervals
        days_until_next = int(1 + (self.mastery_score * 14))  # 1-15 days
        self.spaced_repetition_due_date = datetime.utcnow() + timedelta(days=days_until_next)
        
        self.updated_at = datetime.utcnow()
    
    def is_due_for_review(self):
        """Check if this concept is due for spaced repetition review"""
        return datetime.utcnow() >= self.spaced_repetition_due_date
    
    def to_dict(self):
        """Convert mastery record to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'concept_id': self.concept_id,
            'mastery_score': round(self.mastery_score, 3),
            'confidence_score': round(self.confidence_score, 3),
            'current_mastery': round(self.calculate_decay(), 3),
            'last_practiced_at': self.last_practiced_at.isoformat() if self.last_practiced_at else None,
            'practice_count': self.practice_count,
            'total_attempts': self.total_attempts,
            'successful_attempts': self.successful_attempts,
            'success_rate': round(self.successful_attempts / self.total_attempts, 3) if self.total_attempts > 0 else 0,
            'average_time_seconds': round(self.average_time_seconds, 1),
            'hint_usage_count': self.hint_usage_count,
            'due_for_review': self.is_due_for_review(),
            'next_review_date': self.spaced_repetition_due_date.isoformat() if self.spaced_repetition_due_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MisconceptionTag(db.Model):
    """Records detected misconceptions for targeted remediation"""
    
    __tablename__ = 'misconception_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    
    # Misconception details
    misconception_type = db.Column(db.String(100), nullable=False)  # off_by_one, null_handling, etc.
    description = db.Column(db.Text)
    code_snippet = db.Column(db.Text)  # The code that exhibited the misconception
    
    # Tracking
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    recurrence_count = db.Column(db.Integer, default=1)
    last_occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    
    # Context
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    def mark_recurrence(self, code_snippet: str = None):
        """Mark that this misconception occurred again"""
        self.recurrence_count += 1
        self.last_occurred_at = datetime.utcnow()
        self.resolved = False
        self.resolved_at = None
        
        if code_snippet:
            self.code_snippet = code_snippet
    
    def mark_resolved(self):
        """Mark misconception as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert misconception to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'concept_id': self.concept_id,
            'misconception_type': self.misconception_type,
            'description': self.description,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'recurrence_count': self.recurrence_count,
            'last_occurred_at': self.last_occurred_at.isoformat() if self.last_occurred_at else None,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'challenge_id': self.challenge_id,
            'lesson_id': self.lesson_id
        }
