from flask import Blueprint, jsonify, request
from datetime import datetime
from app.extensions import db
from app.models import User, Lesson, Progress

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/map', methods=['GET', 'OPTIONS'])
def get_skill_map():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    # For demo, use a hardcoded user or get from session
    # In production, use @login_required
    user_id = request.args.get('user_id', 'demo_user')
    user = User.query.filter_by(user_id=user_id).first()
    
    if not user:
        # Create demo user if not exists
        user = User(user_id=user_id, username="CodeExplorer")
        db.session.add(user)
        db.session.commit()

    lessons = Lesson.query.order_by(Lesson.order).all()
    
    # Calculate unlock status for each lesson
    lesson_data = []
    for lesson in lessons:
        data = lesson.to_dict(user.user_id)
        # Add mock visual position for the frontend map
        # In a real app, this might be stored in the DB or calculated layout
        data['position'] = {'x': (lesson.order % 2) * 100, 'y': lesson.order * 100}
        lesson_data.append(data)

    return jsonify({
        'user': user.to_dict(),
        'nodes': lesson_data
    })

@progress_bp.route('/unlock', methods=['POST'])
def unlock_node():
    data = request.json
    user_id = data.get('user_id')
    lesson_id = data.get('lesson_id')
    
    # Logic to unlock would go here
    # For now, the 'is_unlocked_for_user' method in models handles dynamic checking
    return jsonify({'status': 'checked'})

@progress_bp.route('/complete', methods=['POST'])
def complete_node():
    data = request.json
    user_id = data.get('user_id')
    lesson_id = data.get('lesson_id')
    stars = data.get('stars', 1)
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    progress = Progress.query.filter_by(user_id=user.id, lesson_id=lesson_id).first()
    
    if not progress:
        progress = Progress(user_id=user.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    progress.completed = True
    progress.stars = max(progress.stars, stars)
    progress.completed_at = datetime.utcnow()
    
    # Update User XP/Stars
    user.total_stars += stars
    user.update_level()
    user.check_and_award_badges()
    
    db.session.commit()
    
    return jsonify({
        'status': 'completed',
        'user': user.to_dict(),
        'badges': [b.to_dict() for b in user.badges]
    })
