from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'device_booking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes import admin_bp, user_bp, status_bp, log_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(log_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
