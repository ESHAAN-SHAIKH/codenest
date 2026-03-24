"""
Arena competitive system models
Tracks matches, ratings, and competitive gameplay
"""

from app.extensions import db
from datetime import datetime


class ArenaMatch(db.Model):
    """Competitive arena matches between users"""
    
    __tablename__ = 'arena_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Match type
    match_type = db.Column(db.String(50), nullable=False)
    # Types: debug_duel, refactor_race, optimization_battle, speed_challenge
    
    # Players
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Results
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    player1_score = db.Column(db.Integer, default=0)
    player2_score = db.Column(db.Integer, default=0)
    
    # Match data
    match_data = db.Column(db.JSON)
    """
    Example match_data structure:
    {
        "challenge_id": 123,
        "time_limit": 600,
        "player1_submission": {"code": "...", "time": 450},
        "player2_submission": {"code": "...", "time": 520},
        "player1_rating_before": 1500,
        "player2_rating_before": 1480,
        "rating_change": 15
    }
    """
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, abandoned
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert match to dictionary"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'match_type': self.match_type,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'winner_id': self.winner_id,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'match_data': self.match_data,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ArenaRating(db.Model):
    """Elo rating system for arena competitions"""
    
    __tablename__ = 'arena_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_type = db.Column(db.String(50), nullable=False)
    
    # Elo rating
    rating = db.Column(db.Integer, default=1500)  # Starting Elo
    peak_rating = db.Column(db.Integer, default=1500)
    lowest_rating = db.Column(db.Integer, default=1500)
    
    # Match statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    
    # Streaks
    current_win_streak = db.Column(db.Integer, default=0)
    best_win_streak = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_match_at = db.Column(db.DateTime)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'match_type', name='unique_user_match_type'),)
    
    def calculate_elo_change(self, opponent_rating: int, result: str, k_factor: int = 32):
        """
        Calculate Elo rating change based on match result
        
        Args:
            opponent_rating: Opponent's current rating
            result: 'win', 'loss', or 'draw'
            k_factor: K-factor for Elo calculation (default 32)
        
        Returns:
            int: Rating change (positive or negative)
        """
        # Expected score
        expected_score = 1 / (1 + 10 ** ((opponent_rating - self.rating) / 400))
        
        # Actual score
        if result == 'win':
            actual_score = 1.0
        elif result == 'loss':
            actual_score = 0.0
        else:  # draw
            actual_score = 0.5
        
        # Rating change
        rating_change = int(k_factor * (actual_score - expected_score))
        
        return rating_change
    
    def update_rating(self, opponent_rating: int, result: str, k_factor: int = 32):
        """
        Update rating after a match
        
        Args:
            opponent_rating: Opponent's rating
            result: 'win', 'loss', or 'draw'
            k_factor: K-factor for calculation
        
        Returns:
            dict: Information about rating change
        """
        old_rating = self.rating
        rating_change = self.calculate_elo_change(opponent_rating, result, k_factor)
        
        self.rating += rating_change
        self.matches_played += 1
        
        # Update win/loss counts
        if result == 'win':
            self.wins += 1
            self.current_win_streak += 1
            if self.current_win_streak > self.best_win_streak:
                self.best_win_streak = self.current_win_streak
        elif result == 'loss':
            self.losses += 1
            self.current_win_streak = 0
        else:
            self.draws += 1
        
        # Update peak/lowest ratings
        if self.rating > self.peak_rating:
            self.peak_rating = self.rating
        if self.rating < self.lowest_rating:
            self.lowest_rating = self.rating
        
        self.last_match_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        return {
            'old_rating': old_rating,
            'new_rating': self.rating,
            'rating_change': rating_change,
            'result': result
        }
    
    def get_win_rate(self):
        """Calculate win rate percentage"""
        if self.matches_played == 0:
            return 0.0
        return round((self.wins / self.matches_played) * 100, 1)
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'match_type': self.match_type,
            'rating': self.rating,
            'peak_rating': self.peak_rating,
            'lowest_rating': self.lowest_rating,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': self.get_win_rate(),
            'current_win_streak': self.current_win_streak,
            'best_win_streak': self.best_win_streak,
            'last_match_at': self.last_match_at.isoformat() if self.last_match_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
