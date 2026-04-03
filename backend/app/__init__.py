from flask import Flask

from .bootstrap import initialize_database
from .config import Config
from .extensions import cors, db, jwt, migrate
from .routes.auth import auth_bp
from .routes.investors import investors_bp
from .routes.notifications import notifications_bp
from .routes.startups import startups_bp


def _validate_database_dependencies(app):
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("mysql+pymysql://"):
        try:
            import cryptography  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: install 'cryptography' for MySQL accounts using "
                "sha256_password or caching_sha2_password auth."
            ) from exc


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    _validate_database_dependencies(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(startups_bp, url_prefix="/api/startups")
    app.register_blueprint(investors_bp, url_prefix="/api/investors")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    if not app.config.get("TESTING") and app.config.get("AUTO_INIT_DB", True):
        with app.app_context():
            initialize_database(seed_admin=app.config.get("SEED_ADMIN_ON_STARTUP", False))

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    return app
