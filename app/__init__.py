import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(config=None):
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=str(root / "templates"), static_folder=str(root / "static"))

    # --- Core config ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///:memory:'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Cookie security ---
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['WTF_CSRF_ENABLED'] = True

    # Override with test config if provided
    if config:
        app.config.update(config)

    # --- Extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Only enable Talisman in production
    if os.environ.get('FLASK_ENV') == 'production':
        csp = {
            'default-src': "'self'",
            'style-src': ["'self'", 'https://fonts.googleapis.com'],
            'font-src': ["'self'", 'https://fonts.gstatic.com'],
            'script-src': "'self'",
            'img-src': "'self' data:",
        }
        Talisman(app, content_security_policy=csp, force_https=True)

    login_manager.login_view = 'auth.signin'
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    # --- Blueprints ---
    from app.auth.routes import auth_bp
    from app.vehicles.routes import vehicles_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(main_bp)

    # --- Error handlers ---
    from app.main.routes import page_not_found
    app.register_error_handler(404, page_not_found)

    with app.app_context():
        db.create_all()

    return app
