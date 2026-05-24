import os
import jwt
from functools import wraps
from flask import request, jsonify, g


def require_auth(f):
    """Decorator that validates Bearer JWT and sets g.user_id / g.user_email."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET", "dev-jwt-secret"),
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {e}"}), 401

        g.user_id = payload["sub"]
        g.user_email = payload.get("email", "")
        g.user_name = payload.get("name", "")
        return f(*args, **kwargs)

    return decorated
