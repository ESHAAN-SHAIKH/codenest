"""
Authentication API endpoints for CodeNest
Handles registration, login, and user profile
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
import logging
import re

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Valid email is required')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')

        if errors:
            return jsonify({'error': '; '.join(errors)}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Create user
        user = User(
            user_id=username.lower().replace(' ', '_'),
            username=username,
            email=email,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate token
        access_token = create_access_token(identity=str(user.id))

        logger.info(f"New user registered: {username} ({email})")

        return jsonify({
            'success': True,
            'token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Update streak
        user.update_streak()
        db.session.commit()

        # Generate token
        access_token = create_access_token(identity=str(user.id))

        logger.info(f"User logged in: {user.username}")

        return jsonify({
            'success': True,
            'token': access_token,
            'user': user.to_dict()
        })

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    except Exception as e:
        logger.error(f"Get me error: {e}")
        return jsonify({'error': 'Failed to get user profile'}), 500


@auth_bp.route('/onboarding', methods=['POST'])
@jwt_required()
def complete_onboarding():
    """Complete user onboarding — sets skill level and creates initial mastery records"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json or {}
        skill_level = data.get('skill_level', 'beginner')
        preferred_language = data.get('preferred_language', 'python')
        interests = data.get('interests', [])  # list of concept category names

        # Update user profile
        user.skill_level = skill_level
        user.preferred_language = preferred_language
        user.onboarding_completed = True

        # Create initial concept mastery records based on skill level
        _seed_user_mastery(user, skill_level, interests)

        # Initialise all 5 archetype progress records so the dashboard loads correctly
        from app.services.archetype_engine import ArchetypeEngine
        ArchetypeEngine.initialize_archetypes(user.id)

        db.session.commit()

        logger.info(f"Onboarding completed for {user.username} (level={skill_level})")

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Onboarding error: {e}")
        return jsonify({'error': 'Onboarding failed'}), 500


def _seed_user_mastery(user, skill_level, interests):
    """Create initial ConceptMastery records for a new user based on their skill level"""
    from app.cognitive_models.cognitive import Concept, ConceptMastery
    from datetime import datetime

    # Base mastery scores by skill level
    score_map = {
        'beginner': {'base': 0.1, 'variance': 0.1},
        'intermediate': {'base': 0.4, 'variance': 0.15},
        'advanced': {'base': 0.7, 'variance': 0.15},
    }
    config = score_map.get(skill_level, score_map['beginner'])

    concepts = Concept.query.all()
    import random
    random.seed()

    for concept in concepts:
        # Higher initial mastery for interested categories
        boost = 0.1 if concept.category in interests else 0.0
        base_score = min(1.0, config['base'] + boost)
        score = min(1.0, max(0.05, base_score + random.uniform(-config['variance'], config['variance'])))

        mastery = ConceptMastery(
            user_id=user.id,
            concept_id=concept.id,
            mastery_score=round(score, 3),
            confidence_score=round(score * 0.8, 3),
            practice_count=0,
            total_attempts=0,
            successful_attempts=0,
            last_practiced_at=datetime.utcnow(),
            spaced_repetition_due_date=datetime.utcnow(),
        )
        db.session.add(mastery)
