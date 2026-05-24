from flask import Blueprint, request, jsonify, g

from app.auth.middleware import require_auth
from app.db import get_supabase
from app.email_service import (
    notify_task_assigned,
    notify_task_completed,
)

tasks_bp = Blueprint("tasks", __name__)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

def _get_user(user_id: str):

    result = (
        get_supabase()
        .table("users")
        .select("id,name,email")
        .eq("id", user_id)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        return None

    return result.data[0]


# ───────────────────────────────────────────────────────────────────────────────
# List Tasks
# ───────────────────────────────────────────────────────────────────────────────

@tasks_bp.get("")
@require_auth
def list_tasks():

    db = get_supabase()

    result = (
        db.table("tasks")
        .select("""
            *,
            creator:users!creator_id(
                id,
                name,
                email,
                avatar_url
            ),
            assignee:users!assignee_id(
                id,
                name,
                email,
                avatar_url
            )
        """)
        .or_(f"creator_id.eq.{g.user_id},assignee_id.eq.{g.user_id}")
        .order("created_at", desc=True)
        .execute()
    )

    return jsonify(result.data)


# ───────────────────────────────────────────────────────────────────────────────
# Create Task
# ───────────────────────────────────────────────────────────────────────────────

@tasks_bp.post("")
@require_auth
def create_task():

    body = request.get_json(silent=True) or {}

    title = (body.get("title") or "").strip()

    if not title:
        return jsonify({
            "error": "title is required"
        }), 400

    description = body.get("description", "")
    status = body.get("status", "todo")
    priority = body.get("priority", "medium")
    due_date = body.get("due_date")
    assignee_id = body.get("assignee_id")

    db = get_supabase()

    insert_data = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "due_date": due_date,
        "creator_id": g.user_id,
        "assignee_id": assignee_id,
    }

    # Insert task
    insert_result = (
        db.table("tasks")
        .insert(insert_data)
        .execute()
    )

    if not insert_result.data:
        return jsonify({
            "error": "Failed to create task"
        }), 500

    task_id = insert_result.data[0]["id"]

    # Fetch full task with relations
    task_result = (
        db.table("tasks")
        .select("""
            *,
            creator:users!creator_id(
                id,
                name,
                email,
                avatar_url
            ),
            assignee:users!assignee_id(
                id,
                name,
                email,
                avatar_url
            )
        """)
        .eq("id", task_id)
        .execute()
    )

    if not task_result.data:
        return jsonify({
            "error": "Failed to fetch created task"
        }), 500

    task = task_result.data[0]

    # Log assignment
    if assignee_id:

        (
            db.table("task_assignments")
            .insert({
                "task_id": task["id"],
                "assigned_to": assignee_id,
                "assigned_by": g.user_id,
            })
            .execute()
        )

        # Notify assignee
        if assignee_id != g.user_id and task.get("assignee"):

            assignee = task["assignee"]
            creator = task["creator"] or {}

            notify_task_assigned(
                assignee_email=assignee["email"],
                assignee_name=assignee.get("name", ""),
                creator_name=creator.get("name", g.user_email),
                task_title=title,
                task_description=description,
                task_id=task["id"],
                priority=priority,
                due_date=due_date,
            )

    return jsonify(task), 201


# ───────────────────────────────────────────────────────────────────────────────
# Get Task
# ───────────────────────────────────────────────────────────────────────────────

@tasks_bp.get("/<task_id>")
@require_auth
def get_task(task_id: str):

    db = get_supabase()

    result = (
        db.table("tasks")
        .select("""
            *,
            creator:users!creator_id(
                id,
                name,
                email,
                avatar_url
            ),
            assignee:users!assignee_id(
                id,
                name,
                email,
                avatar_url
            )
        """)
        .eq("id", task_id)
        .or_(f"creator_id.eq.{g.user_id},assignee_id.eq.{g.user_id}")
        .execute()
    )

    if not result.data:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(result.data[0])


# ───────────────────────────────────────────────────────────────────────────────
# Update Task
# ───────────────────────────────────────────────────────────────────────────────

@tasks_bp.patch("/<task_id>")
@require_auth
def update_task(task_id: str):

    db = get_supabase()

    existing_result = (
        db.table("tasks")
        .select("""
            *,
            creator:users!creator_id(
                id,
                name,
                email,
                avatar_url
            ),
            assignee:users!assignee_id(
                id,
                name,
                email,
                avatar_url
            )
        """)
        .eq("id", task_id)
        .or_(f"creator_id.eq.{g.user_id},assignee_id.eq.{g.user_id}")
        .execute()
    )

    if not existing_result.data:
        return jsonify({
            "error": "Task not found or access denied"
        }), 404

    existing = existing_result.data[0]

    body = request.get_json(silent=True) or {}

    allowed = [
        "title",
        "description",
        "status",
        "priority",
        "due_date",
        "assignee_id",
    ]

    updates = {
        k: v
        for k, v in body.items()
        if k in allowed
    }

    if not updates:
        return jsonify({
            "error": "No valid fields to update"
        }), 400

    # Update task
    (
        db.table("tasks")
        .update(updates)
        .eq("id", task_id)
        .execute()
    )

    # Fetch updated task
    updated_result = (
        db.table("tasks")
        .select("""
            *,
            creator:users!creator_id(
                id,
                name,
                email,
                avatar_url
            ),
            assignee:users!assignee_id(
                id,
                name,
                email,
                avatar_url
            )
        """)
        .eq("id", task_id)
        .execute()
    )

    task = updated_result.data[0]

    # Assignee changed
    if (
        "assignee_id" in updates
        and updates["assignee_id"] != existing.get("assignee_id")
    ):

        new_assignee_id = updates["assignee_id"]

        if new_assignee_id:

            (
                db.table("task_assignments")
                .insert({
                    "task_id": task_id,
                    "assigned_to": new_assignee_id,
                    "assigned_by": g.user_id,
                })
                .execute()
            )

            assignee = task.get("assignee") or {}
            creator = task.get("creator") or {}

            if assignee and new_assignee_id != g.user_id:

                notify_task_assigned(
                    assignee_email=assignee["email"],
                    assignee_name=assignee.get("name", ""),
                    creator_name=creator.get("name", g.user_email),
                    task_title=task["title"],
                    task_description=task.get("description", ""),
                    task_id=task_id,
                    priority=task.get("priority", "medium"),
                    due_date=task.get("due_date"),
                )

    # Task completed
    if (
        updates.get("status") == "done"
        and existing.get("status") != "done"
        and existing.get("creator_id") != g.user_id
    ):

        creator = task.get("creator") or {}

        if creator:

            notify_task_completed(
                creator_email=creator["email"],
                creator_name=creator.get("name", ""),
                completer_name=g.user_name or g.user_email,
                task_title=task["title"],
                task_id=task_id,
            )

    return jsonify(task)


# ───────────────────────────────────────────────────────────────────────────────
# Delete Task
# ───────────────────────────────────────────────────────────────────────────────

@tasks_bp.delete("/<task_id>")
@require_auth
def delete_task(task_id: str):

    db = get_supabase()

    existing = (
        db.table("tasks")
        .select("id,creator_id")
        .eq("id", task_id)
        .eq("creator_id", g.user_id)
        .execute()
    )

    if not existing.data:
        return jsonify({
            "error": "Task not found or you are not the creator"
        }), 404

    (
        db.table("tasks")
        .delete()
        .eq("id", task_id)
        .execute()
    )

    return jsonify({
        "message": "Task deleted"
    }), 200