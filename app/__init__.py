import os
from datetime import datetime, timezone
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig, config
from sqlalchemy import text

# --- Instantiate Extensions ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()


# --- Rate limiting ---
# Use Flask-Limiter when available; otherwise fall back to a no-op shim so the
# app still runs in environments where the optional dependency is absent.
try:
    from flask_limiter import Limiter as _Limiter
    from flask_limiter.util import get_remote_address as _get_remote_address

    limiter = _Limiter(key_func=_get_remote_address, default_limits=[])
    _LIMITER_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when dependency missing
    _LIMITER_AVAILABLE = False

    class _NoopLimiter:
        """Minimal stand-in that makes @limiter.limit(...) a passthrough."""

        def init_app(self, app):
            return None

        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    limiter = _NoopLimiter()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    from app.models.user import User
    return db.session.get(User, int(user_id))

def create_app(config_name=None):
    import logging
    from datetime import datetime

    app = Flask(__name__, instance_relative_config=True)

    # Add format_date filter for templates
    def format_datetime(value, format='%b %d, %Y'):
        if value is None:
            return ""
        return value.strftime(format)
    
    app.jinja_env.filters['format_date'] = format_datetime


    if config_name is None:
        # FLASK_CONFIG takes precedence; otherwise fall back to FLASK_ENV
        # (production/development/testing) so a single FLASK_ENV var selects
        # the right Config class. Defaults to development.
        config_name = os.environ.get('FLASK_CONFIG') or os.environ.get('FLASK_ENV') or 'default'

    if isinstance(config_name, str):
        config_class = config.get(config_name, Config)
    else:
        config_class = config_name
    app.config.from_object(config_class)

    # Fail fast in production if the SECRET_KEY is missing or still the insecure
    # development default — a known key allows session/CSRF/token forgery.
    from config import INSECURE_DEFAULT_SECRET_KEY
    is_production = not app.config.get('DEBUG') and not app.config.get('TESTING')
    if is_production and (not os.environ.get('SECRET_KEY')
                          or app.config.get('SECRET_KEY') == INSECURE_DEFAULT_SECRET_KEY):
        raise RuntimeError(
            "SECRET_KEY must be set to a strong, unique value in production. "
            "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    # Trust Nginx's X-Forwarded-* headers so url_for(_external=True) uses https
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


    import logging
    if app.config.get('TESTING'):
        print(f"!!! Setting Logger Level to INFO for Testing !!!")
        log_level = logging.INFO


    else:
        log_level = logging.INFO # Or your default production level

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(funcName)s:%(lineno)d]')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.propagate = False

    app.logger.setLevel(log_level)


    app.logger.critical("Flask App Logger Initialized with Level: %s", app.logger.getEffectiveLevel())

    # Validate required environment variables
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
        app.logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")


    import click
    from flask.cli import with_appcontext
    from app.utils.db import get_db
    
    @click.command('update-schema')
    @with_appcontext
    def update_schema_command():
        """Update database schema for new features."""
        try:
            # Check if draft_data column exists in assessments table
            result = db.session.execute(text("PRAGMA table_info(assessments)"))
            columns = [row[1] for row in result.fetchall()]  # Column names are in index 1
            has_draft_data = 'draft_data' in columns

            if not has_draft_data:
                # Add draft_data column
                db.session.execute(text("""
                    ALTER TABLE assessments 
                    ADD COLUMN draft_data TEXT
                """))
                print("Added draft_data column to assessments table")

            # Check if response_text and notes columns exist in sdg_scores table
            result = db.session.execute(text("PRAGMA table_info(sdg_scores)"))
            columns = [row[1] for row in result.fetchall()]  # Column names are in index 1
            has_response_text = 'response_text' in columns

            if not has_response_text:
                # Add response_text and notes columns
                db.session.execute(text("""
                    ALTER TABLE sdg_scores 
                    ADD COLUMN response_text TEXT,
                    ADD COLUMN notes TEXT
                """))
                print("Added response_text and notes columns to sdg_scores table")

                # Copy data from score_text to response_text
                db.session.execute(text("""
                    UPDATE sdg_scores 
                    SET response_text = score_text 
                    WHERE score_text IS NOT NULL
                """))
                print("Copied data from score_text to response_text")

            db.session.commit()
            print("Schema update completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating schema: {e}")
            raise

    app.cli.add_command(update_schema_command)


    # --- Database URI Configuration ---
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # SQLAlchemy prefers postgresql:// over postgres://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    # Otherwise, config class fallback is used

    # --- Initialize Extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Initialize mail only if MAIL_USERNAME is configured
    if app.config.get('MAIL_USERNAME'):
        mail.init_app(app)
        app.logger.info("Flask-Mail initialized")
    else:
        app.logger.warning("MAIL_USERNAME not configured, email features disabled")

    csrf.init_app(app)

    # --- Initialize Cache ---
    # Configure cache based on environment
    redis_url = os.environ.get('REDIS_URL')
    if redis_url and not app.config.get('TESTING'):
        # Use Redis for production/development
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = redis_url
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes default
        app.config['CACHE_KEY_PREFIX'] = 'sdg_'
    elif app.config.get('TESTING'):
        # Use simple cache for testing (in-memory)
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = 60
    else:
        # Fallback to simple cache for development without Redis
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300
        app.logger.warning("Redis not configured, using SimpleCache (in-memory)")

    cache.init_app(app)
    app.logger.info(f"Cache initialized: {app.config['CACHE_TYPE']}")

    # --- Initialize rate limiter ---
    if _LIMITER_AVAILABLE:
        # Use Redis for shared limits across Gunicorn workers when available;
        # otherwise per-process in-memory storage (fine for single worker/dev).
        if redis_url and not app.config.get('TESTING'):
            app.config.setdefault('RATELIMIT_STORAGE_URI', redis_url)
        # Disable enforcement in tests to keep the suite deterministic.
        app.config.setdefault('RATELIMIT_ENABLED', not app.config.get('TESTING', False))
        limiter.init_app(app)
        app.logger.info("Rate limiter initialized")
    else:
        app.logger.warning("Flask-Limiter not installed, rate limiting disabled")

    @app.before_request
    def check_db_connection():
        """Verify database connection before each request."""
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            app.logger.error(f"Database connection error: {str(e)}")
            db.session.rollback()
            db.session.remove()

    # Register filters (if filters.py exists)
    try:
        from . import filters
        filters.register_filters(app)
    except ImportError:
        pass


    from . import models


    def format_date(value, format='%Y-%m-%d'):
        """Format a date using specified format."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format) if value else ""
    app.jinja_env.filters['format_date'] = format_date

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    # Expose url_for_project_routes() to all templates (used by profile.html
    # and others). This was previously defined but never registered.
    from app.utils.context_processors import utility_processor
    app.context_processor(utility_processor)


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()


    if hasattr(app, 'before_serving'):
        @app.before_serving
        def init_db():
            pass
    else:
        pass


    # Register blueprints
    from app.routes import main_bp, auth_bp, projects_bp, assessments_bp, questionnaire_bp, api_bp, dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(assessments_bp, url_prefix='/assessments')
    app.register_blueprint(questionnaire_bp, url_prefix='/questionnaire')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)

    return app
