from flask import Blueprint

# Import blueprints to make them available when importing app.api
from .routes import api_bp
from .progress import progress_bp
from .execution import execution_bp
from .ai import ai_bp
