from flask import Flask, abort, request, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
import hmac
import secrets

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'device_booking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session cookie hardening (behind nginx + https: set FLASK_ENV=production)
    env = (os.environ.get('FLASK_ENV') or os.environ.get('ENV') or '').lower()
    is_production = env == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get(
        'SESSION_COOKIE_SECURE',
        '1' if is_production else '0'
    ).lower() in {'1', 'true', 'yes', 'on'}

    # Persist remembered user for up to 7 days
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # CSRF protection for HTML form POSTs
    def _get_csrf_token() -> str:
        token = session.get('_csrf_token')
        if not token:
            token = secrets.token_urlsafe(32)
            session['_csrf_token'] = token
        return token

    @app.context_processor
    def _inject_csrf_token():
        return {'csrf_token': _get_csrf_token}

    @app.before_request
    def _csrf_protect():
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            submitted = request.form.get('_csrf_token') or request.headers.get('X-CSRFToken')
            expected = session.get('_csrf_token')
            if not expected or not submitted or not hmac.compare_digest(expected, submitted):
                abort(400)

    @app.after_request
    def _set_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), camera=(), microphone=()')
        # With nginx+https you can also enable HSTS at the proxy layer.
        if os.environ.get('ENABLE_HSTS', '').lower() in {'1', 'true', 'yes', 'on'}:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    @app.before_request
    def _make_session_permanent_if_user_set():
        if session.get('user_name'):
            session.permanent = True
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes import admin_bp, user_bp, status_bp, log_bp, main_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(main_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
