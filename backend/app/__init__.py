import os

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ───────────────────────────────────────────────────────────────────────────
    # Secret Key
    # ───────────────────────────────────────────────────────────────────────────

    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-secret"
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Session Config
    # ───────────────────────────────────────────────────────────────────────────

    app.config["SESSION_COOKIE_NAME"] = "taskflow_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

    # ───────────────────────────────────────────────────────────────────────────
    # CORS
    # ───────────────────────────────────────────────────────────────────────────

    CORS(
        app,
        origins=[
            os.getenv(
                "FRONTEND_URL",
                "http://localhost:3000"
            )
        ],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Import Blueprints + OAuth
    # ───────────────────────────────────────────────────────────────────────────

    from app.auth.routes import auth_bp, oauth
    from app.tasks.routes import tasks_bp
    from app.users.routes import users_bp

    # ───────────────────────────────────────────────────────────────────────────
    # Initialize OAuth ONCE
    # ───────────────────────────────────────────────────────────────────────────

    oauth.init_app(app)

    # ───────────────────────────────────────────────────────────────────────────
    # Register Blueprints
    # ───────────────────────────────────────────────────────────────────────────

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(users_bp, url_prefix="/users")

    # ───────────────────────────────────────────────────────────────────────────
    # Health Route
    # ───────────────────────────────────────────────────────────────────────────

    @app.get("/health")
    def health():
        return {
            "status": "ok"
        }

    return app