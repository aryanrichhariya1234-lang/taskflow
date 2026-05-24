from flask import Blueprint, jsonify, g
from app.auth.middleware import require_auth
from app.db import get_supabase

users_bp = Blueprint("users", __name__)


@users_bp.get("")
@require_auth
def list_users():
    """Return all registered users (for assignee picker).
    Excludes the requesting user's sensitive fields.
    """
    db = get_supabase()
    result = (
        db.table("users")
        .select("id,name,email,avatar_url,created_at")
        .order("name")
        .execute()
    )
    return jsonify(result.data)


@users_bp.get("/<user_id>")
@require_auth
def get_user(user_id: str):
    db = get_supabase()
    result = (
        db.table("users")
        .select("id,name,email,avatar_url,created_at")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify(result.data)
