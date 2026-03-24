"""
Database models for Code Nest Backend
"""

from app.extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json



class User(db.Model):
    """User model for storing user information and progress"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)

    # Onboarding
    onboarding_completed = db.Column(db.Boolean, default=False)
    skill_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    preferred_language = db.Column(db.String(20), default='python')

    # Beginner mode
    is_beginner_mode = db.Column(db.Boolean, default=True)
    beginner_phase = db.Column(db.String(20), default='scaffolded')
    # phase values: 'scaffolded' -> 'guided' -> 'freeform' -> 'complete'

    # Progress tracking
    total_stars = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    # User level based on stars
    level = db.Column(db.Integer, default=1)
    
    # Cognitive metrics
    engineering_maturity_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    debugging_efficiency_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    hint_dependency_ratio = db.Column(db.Float, default=0.0)  # hints used / attempts
    cognitive_load_variance = db.Column(db.Float, default=0.0)  # variance in attempt times

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = db.relationship('Progress', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('Badge', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # New cognitive relationships
    concept_mastery = db.relationship('ConceptMastery', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='ConceptMastery.user_id')
    misconceptions = db.relationship('MisconceptionTag', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='MisconceptionTag.user_id')
    code_iterations = db.relationship('CodeIteration', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='CodeIteration.user_id')
    debugging_sessions = db.relationship('DebuggingSession', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='DebuggingSession.user_id')
    archetype_progress = db.relationship('ArchetypeProgress', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='ArchetypeProgress.user_id')
    arena_ratings = db.relationship('ArenaRating', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='ArenaRating.user_id')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def update_streak(self):
        """Update user's learning streak"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        if self.last_activity:
            if self.last_activity.date() == yesterday.date():
                # Consecutive day
                self.current_streak += 1
            elif self.last_activity.date() < yesterday.date():
                # Streak broken
                self.current_streak = 1
            # If same day, don't change streak
        else:
            # First activity
            self.current_streak = 1

        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_activity = now
        self.update_level()

    def update_level(self):
        """Update user level based on total stars"""
        # Level formula: level = floor(stars / 20) + 1
        new_level = min((self.total_stars // 20) + 1, 50)  # Cap at level 50
        self.level = new_level

    def check_and_award_badges(self):
        """Check if user qualifies for new badges and award them"""
        from config import Config

        badge_requirements = Config.BADGE_REQUIREMENTS
        existing_badges = {badge.badge_type for badge in self.badges}

        # Check each badge type
        for badge_type, requirements in badge_requirements.items():
            if badge_type in existing_badges:
                continue

            if self._meets_badge_requirements(badge_type, requirements):
                self._award_badge(badge_type)

    def _meets_badge_requirements(self, badge_type, requirements):
        """Check if user meets requirements for a specific badge"""
        completed_lessons = len([p for p in self.progress if p.completed])

        if 'lessons_completed' in requirements:
            return completed_lessons >= requirements['lessons_completed']
        elif 'total_stars' in requirements:
            return self.total_stars >= requirements['total_stars']
        elif 'streak_days' in requirements:
            return self.current_streak >= requirements['streak_days']

        return False

    def _award_badge(self, badge_type):
        """Award a badge to the user"""
        badge_info = {
            'first_lesson': {'name': 'First Steps', 'description': 'Completed your first lesson!', 'icon': '🌟'},
            'getting_started': {'name': 'Getting Started', 'description': 'Completed 3 lessons', 'icon': '🚀'},
            'loop_master': {'name': 'Loop Master', 'description': 'Mastered loops and repetition', 'icon': '🔄'},
            'math_genius': {'name': 'Math Genius', 'description': 'Solved complex math challenges', 'icon': '🧮'},
            'streak_keeper': {'name': 'Streak Keeper', 'description': 'Learned for 7 days in a row!', 'icon': '🔥'},
            'star_collector': {'name': 'Star Collector', 'description': 'Collected 50 stars!', 'icon': '⭐'},
            'challenge_champion': {'name': 'Challenge Champion', 'description': 'Completed 10 challenges', 'icon': '🏆'}
        }

        if badge_type in badge_info:
            info = badge_info[badge_type]
            badge = Badge(
                user_id=self.id,
                badge_type=badge_type,
                name=info['name'],
                description=info['description'],
                icon=info['icon'],
                earned_at=datetime.utcnow()
            )
            db.session.add(badge)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'total_stars': self.total_stars,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'level': self.level,
            'skill_level': self.skill_level,
            'preferred_language': self.preferred_language,
            'onboarding_completed': self.onboarding_completed,
            'is_beginner_mode': self.is_beginner_mode,
            'beginner_phase': self.beginner_phase,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class Lesson(db.Model):
    """Lesson model for storing lesson information"""

    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    order = db.Column(db.Integer, nullable=False)

    # Lesson content (stored as JSON)
    content = db.Column(db.JSON)  # task, expected_output, hints, etc.

    # Prerequisites
    prerequisite_lessons = db.Column(db.JSON)  # List of lesson IDs

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = db.relationship('Progress', backref='lesson', lazy=True)

    def is_unlocked_for_user(self, user_id):
        """Check if lesson is unlocked for a specific user"""
        if self.order == 1:  # First lesson is always unlocked
            return True

        if not self.prerequisite_lessons:
            # If no prerequisites defined, use order-based unlocking
            previous_lesson = Lesson.query.filter_by(order=self.order - 1).first()
            if previous_lesson:
                user = User.query.filter_by(user_id=user_id).first()
                if user:
                    progress = Progress.query.filter_by(
                        user_id=user.id,
                        lesson_id=previous_lesson.id
                    ).first()
                    return progress and progress.completed
            return False

        # Check if all prerequisite lessons are completed
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return False

        for prereq_id in self.prerequisite_lessons:
            progress = Progress.query.filter_by(
                user_id=user.id,
                lesson_id=prereq_id
            ).first()
            if not progress or not progress.completed:
                return False

        return True

    def to_dict(self, user_id=None):
        """Convert lesson to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'order': self.order,
            'content': self.content,
            'unlocked': self.is_unlocked_for_user(user_id) if user_id else False,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Challenge(db.Model):
    """Challenge model for coding challenges"""

    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='easy')  # easy, medium, hard
    category = db.Column(db.String(50))  # loops, math, logic, etc.

    # Challenge details
    points = db.Column(db.Integer, default=10)
    expected_output = db.Column(db.Text)
    hints = db.Column(db.JSON)  # List of hints
    test_cases = db.Column(db.JSON)  # List of test cases

    # Scaffolding
    challenge_mode = db.Column(db.String(20), default='freeform')
    # values: 'scaffolded', 'guided', 'freeform'
    scaffold_data = db.Column(db.JSON, nullable=True)
    # type: 'fill_in_blank' | 'predict_output' | 'error_spotting'
    # See UnifiedSubmissionService for field spec per type

    # Requirements
    min_level = db.Column(db.Integer, default=1)
    prerequisite_lessons = db.Column(db.JSON)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_unlocked_for_user(self, user_id):
        """Check if challenge is unlocked for a specific user"""
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return False

        # Check level requirement
        if user.level < self.min_level:
            return False

        # Check prerequisite lessons
        if self.prerequisite_lessons:
            for lesson_id in self.prerequisite_lessons:
                progress = Progress.query.filter_by(
                    user_id=user.id,
                    lesson_id=lesson_id
                ).first()
                if not progress or not progress.completed:
                    return False

        return True

    def to_dict(self, user_id=None):
        """Convert challenge to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'category': self.category,
            'points': self.points,
            'expected_output': self.expected_output,
            'hints': self.hints or [],
            'test_cases': self.test_cases or [],
            'min_level': self.min_level,
            'challenge_mode': self.challenge_mode,
            'scaffold_data': self.scaffold_data,
            'unlocked': self.is_unlocked_for_user(user_id) if user_id else False,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Progress(db.Model):
    """Progress tracking for lessons and challenges"""

    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)

    # Progress details
    completed = db.Column(db.Boolean, default=False)
    stars = db.Column(db.Integer, default=0)  # 1-3 stars based on performance
    attempts = db.Column(db.Integer, default=0)

    # Code submission
    last_code = db.Column(db.Text)  # User's last submitted code
    completion_time = db.Column(db.Integer)  # Time taken to complete (seconds)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),)

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'stars': self.stars,
            'attempts': self.attempts,
            'completion_time': self.completion_time,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Badge(db.Model):
    """Badge model for user achievements"""

    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Badge details
    badge_type = db.Column(db.String(50), nullable=False)  # first_lesson, streak_keeper, etc.
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))  # Emoji or icon identifier

    # Timestamps
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_type', name='unique_user_badge'),)

    def to_dict(self):
        """Convert badge to dictionary"""
        return {
            'id': self.id,
            'badge_type': self.badge_type,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }


class Analytics(db.Model):
    """Analytics model for tracking user behavior"""

    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # code_run, lesson_start, etc.
    event_data = db.Column(db.JSON)  # Additional event data

    # Context
    session_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert analytics event to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }