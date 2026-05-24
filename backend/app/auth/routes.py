import os
import jwt
import datetime

from flask import Blueprint, redirect, jsonify, session, g
from authlib.integrations.flask_client import OAuth

from app.db import get_supabase
from app.auth.middleware import require_auth

# ───────────────────────────────────────────────────────────────────────────────
# Blueprint
# ───────────────────────────────────────────────────────────────────────────────

auth_bp = Blueprint("auth", __name__)

# ───────────────────────────────────────────────────────────────────────────────
# OAuth Setup
# ───────────────────────────────────────────────────────────────────────────────

oauth = OAuth()

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

# ───────────────────────────────────────────────────────────────────────────────
# JWT Helper
# ───────────────────────────────────────────────────────────────────────────────

def _make_jwt(user_id: str, email: str, name: str) -> str:

    expiry = datetime.datetime.utcnow() + datetime.timedelta(
        hours=int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    )

    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": expiry,
        "iat": datetime.datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET", "dev-jwt-secret"),
        algorithm="HS256",
    )

# ───────────────────────────────────────────────────────────────────────────────
# Routes
# ───────────────────────────────────────────────────────────────────────────────

@auth_bp.get("/google")
def google_login():
    """
    Redirect user to Google OAuth.
    """

    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/auth/callback"
    )

    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.get("/callback")
def google_callback():
    """
    Handle Google OAuth callback.
    """

    try:
        token = oauth.google.authorize_access_token()

    except Exception as e:
        return jsonify({
            "error": f"OAuth failed: {e}"
        }), 400

    userinfo = token.get("userinfo")

    if not userinfo:
        return jsonify({
            "error": "Could not retrieve user info from Google"
        }), 400

    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    name = userinfo.get("name", "")
    avatar_url = userinfo.get("picture", "")

    if not google_id or not email:
        return jsonify({
            "error": "Missing Google account information"
        }), 400

    supabase = get_supabase()

    try:

        # ───────────────────────────────────────────────────────────────────────
        # Find existing user
        # ───────────────────────────────────────────────────────────────────────

        existing = (
            supabase.table("users")
            .select("*")
            .eq("google_id", google_id)
            .execute()
        )

        user = None

        # ───────────────────────────────────────────────────────────────────────
        # Existing User
        # ───────────────────────────────────────────────────────────────────────

        if existing.data and len(existing.data) > 0:

            user = existing.data[0]

            (
                supabase.table("users")
                .update({
                    "name": name,
                    "avatar_url": avatar_url,
                })
                .eq("id", user["id"])
                .execute()
            )

        # ───────────────────────────────────────────────────────────────────────
        # New User
        # ───────────────────────────────────────────────────────────────────────

        else:

            (
                supabase.table("users")
                .insert({
                    "email": email,
                    "name": name,
                    "avatar_url": avatar_url,
                    "google_id": google_id,
                })
                .execute()
            )

        # ───────────────────────────────────────────────────────────────────────
        # Fetch final user
        # ───────────────────────────────────────────────────────────────────────

        final_user = (
            supabase.table("users")
            .select("*")
            .eq("google_id", google_id)
            .execute()
        )

        if not final_user.data or len(final_user.data) == 0:
            return jsonify({
                "error": "Failed to retrieve user"
            }), 500

        user = final_user.data[0]

    except Exception as e:

        print("SUPABASE ERROR:", str(e))

        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500

    # ───────────────────────────────────────────────────────────────────────────
    # Create JWT
    # ───────────────────────────────────────────────────────────────────────────

    access_token = _make_jwt(
        user["id"],
        email,
        name,
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Redirect to frontend
    # ───────────────────────────────────────────────────────────────────────────

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    return redirect(
        f"{frontend_url}/auth/callback?token={access_token}"
    )


@auth_bp.get("/me")
@require_auth
def me():
    """
    Return current authenticated user.
    """

    supabase = get_supabase()

    try:

        result = (
            supabase.table("users")
            .select("*")
            .eq("id", g.user_id)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify(result.data[0])

    except Exception as e:

        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500


@auth_bp.post("/logout")
def logout():
    """
    Clear Flask session.
    """

    session.clear()

    return jsonify({
        "message": "Logged out"
    })