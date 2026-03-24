from flask import Flask, jsonify, request
import os
from config import Config
from .extensions import db, migrate, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Import ALL models here so SQLAlchemy can resolve relationships
    # before any blueprint imports them (prevents mapper conflicts)
    with app.app_context():
        from .models import User, Lesson, Challenge, Progress, Badge, Analytics  # noqa
        from .cognitive_models.cognitive import Concept, ConceptMastery, MisconceptionTag  # noqa
        from .cognitive_models.learning import CodeIteration, DebuggingSession  # noqa
        from .cognitive_models.progression import ArchetypeProgress  # noqa
        from .cognitive_models.arena import ArenaMatch, ArenaRating  # noqa

    
    # Manual CORS - Intercept OPTIONS requests BEFORE routing
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_response(('', 204))
            frontend_url = os.environ.get('FRONTEND_URL', '*')
            response.headers['Access-Control-Allow-Origin'] = frontend_url
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        frontend_url = os.environ.get('FRONTEND_URL', '*')
        response.headers['Access-Control-Allow-Origin'] = frontend_url
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    # ── JWT error handlers — must include CORS headers manually because
    # Flask-JWT-Extended error responses bypass the after_request hook. ────────
    def _cors_json(body, status):
        from flask import make_response
        resp = make_response(jsonify(body), status)
        frontend_url = os.environ.get('FRONTEND_URL', '*')
        resp.headers['Access-Control-Allow-Origin'] = frontend_url
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return resp

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return _cors_json({'error': 'Token has expired', 'code': 'token_expired'}, 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return _cors_json({'error': 'Invalid token', 'code': 'invalid_token'}, 422)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return _cors_json({'error': 'Missing authorization token', 'code': 'authorization_required'}, 401)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_data):
        return _cors_json({'error': 'Fresh token required', 'code': 'fresh_token_required'}, 401)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return _cors_json({'error': 'Token has been revoked', 'code': 'token_revoked'}, 401)

    # Register Blueprints
    from .api import api_bp, progress_bp, execution_bp, ai_bp
    from .api.auth import auth_bp
    from .api.cognitive import cognitive_bp
    from .api.debugging import debugging_bp
    from .api.archetypes import archetypes_bp
    
    # Import new route blueprints
    from .routes.iteration_routes import iteration_bp
    from .routes.analytics_routes import analytics_bp
    from .routes.arena_routes import arena_bp
    from .routes.beginner_routes import beginner_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(execution_bp, url_prefix='/api/execute')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # New cognitive training blueprints
    app.register_blueprint(cognitive_bp, url_prefix='/api/cognitive')
    app.register_blueprint(debugging_bp, url_prefix='/api/debugging')
    app.register_blueprint(archetypes_bp, url_prefix='/api/archetypes')
    
    # Register new routes
    app.register_blueprint(iteration_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(arena_bp, url_prefix='/api')
    app.register_blueprint(beginner_bp, url_prefix='/api/beginner')

    # Root route for health check / backend info
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CodeNest Backend API',
            'status': 'running',
            'version': '2.0.0'
        })
    
    # Test endpoint for CORS
    @app.route('/test', methods=['GET', 'OPTIONS'])
    def test():
        return jsonify({'message': 'CORS test successful!'})

    return app
