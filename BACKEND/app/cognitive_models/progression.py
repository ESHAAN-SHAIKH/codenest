"""
Identity-based progression models
Tracks archetype development and skill-based identity
"""

from app.extensions import db
from datetime import datetime


class ArchetypeProgress(db.Model):
    """Tracks user progression across 5 skill archetypes"""
    
    __tablename__ = 'archetype_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Archetype type
    archetype_type = db.Column(db.String(50), nullable=False)
    # Types: architect, debugger, optimizer, refactorer, guardian
    
    # Progression
    rank_level = db.Column(db.Integer, default=1)  # 1-10 ranks
    experience_points = db.Column(db.Integer, default=0)
    
    # Behavior metrics (JSON storing specific metrics)
    behavior_metrics = db.Column(db.JSON, default=dict)
    """
    Example behavior_metrics structure:
    {
        "architect": {
            "system_design_quality": 0.8,
            "code_organization_score": 0.75,
            "abstraction_usage": 0.6
        },
        "debugger": {
            "bug_identification_speed": 0.7,
            "explanation_quality": 0.85,
            "debug_success_rate": 0.9
        },
        "optimizer": {
            "performance_improvements": 12,
            "complexity_reductions": 8,
            "avg_optimization_impact": 0.65
        },
        "refactorer": {
            "code_quality_improvements": 15,
            "readability_score": 0.8,
            "refactor_frequency": 0.7
        },
        "guardian": {
            "security_awareness_score": 0.75,
            "edge_case_coverage": 0.8,
            "error_handling_quality": 0.85
        }
    }
    """
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'archetype_type', name='unique_user_archetype'),)
    
    # Rank thresholds (XP needed for each rank)
    RANK_THRESHOLDS = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000,
        6: 2000,
        7: 4000,
        8: 7000,
        9: 12000,
        10: 20000
    }
    
    def add_experience(self, xp: int):
        """
        Add experience points and check for rank up
        
        Args:
            xp: Experience points to add
        
        Returns:
            dict: Information about rank up if occurred
        """
        old_rank = self.rank_level
        self.experience_points += xp
        
        # Check for rank up
        new_rank = old_rank
        for rank, threshold in self.RANK_THRESHOLDS.items():
            if self.experience_points >= threshold:
                new_rank = rank
        
        self.rank_level = min(10, new_rank)
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        ranked_up = new_rank > old_rank
        
        return {
            'ranked_up': ranked_up,
            'old_rank': old_rank,
            'new_rank': self.rank_level,
            'total_xp': self.experience_points,
            'next_rank_xp': self.RANK_THRESHOLDS.get(self.rank_level + 1, None)
        }
    
    def update_metrics(self, metrics: dict):
        """
        Update behavior metrics for this archetype
        
        Args:
            metrics: Dictionary of metrics to update
        """
        if not self.behavior_metrics:
            self.behavior_metrics = {}
        
        self.behavior_metrics.update(metrics)
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_progress_to_next_rank(self):
        """Calculate progress percentage to next rank"""
        if self.rank_level >= 10:
            return 100  # Max rank
        
        current_threshold = self.RANK_THRESHOLDS[self.rank_level]
        next_threshold = self.RANK_THRESHOLDS[self.rank_level + 1]
        
        xp_in_current_rank = self.experience_points - current_threshold
        xp_needed_for_next = next_threshold - current_threshold
        
        progress = (xp_in_current_rank / xp_needed_for_next) * 100
        return round(min(100, max(0, progress)), 1)
    
    def to_dict(self):
        """Convert archetype progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'archetype_type': self.archetype_type,
            'rank_level': self.rank_level,
            'experience_points': self.experience_points,
            'progress_to_next_rank': self.get_progress_to_next_rank(),
            'next_rank_xp': self.RANK_THRESHOLDS.get(self.rank_level + 1),
            'behavior_metrics': self.behavior_metrics or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
