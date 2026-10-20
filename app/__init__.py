from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def create_app():
    """Create and configure the Flask application."""
    # Get the directory containing this file (app/)
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Parent directory is the project root
    project_root = os.path.dirname(basedir)

    app = Flask(__name__,
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DB_PATH'] = os.getenv('DB_PATH', 'instance/shruti.db')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'instance/uploads')
    app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', 'instance/audio')

    # Initialize database
    from app.db import init_db
    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes_student import student_bp
    app.register_blueprint(student_bp)

    return app
