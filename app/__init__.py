from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from os import path
from dotenv import load_dotenv, find_dotenv
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    load_dotenv(find_dotenv())
    # Config settings
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY') or 'default_secret_key_for_development'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate = Migrate(app, db)

    # Import blueprints
    from .views import bp as views_bp
    from .auth import bp as auth_bp

    # Register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
