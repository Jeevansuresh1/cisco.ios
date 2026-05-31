from flask import Blueprint, request, jsonify
from models import get_db

profiles_bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")

@profiles_bp.route("/", methods=["GET"])
def list_profiles():
    """List all profiles with pagination."""

@profiles_bp.route("/", methods=["GET"])
def list_profiles():
    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 25, type=int), 100)
    offset = (page - 1) * per_page

    users = db.execute(
        "SELECT id, name, email, bio, created_at FROM users LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    profiles = [
        {
            "id": u[0],
            "name": u[1],
            "email": u[2],
            "bio": u[3] or "",
            "created_at": u[4],
        }
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "data": profiles,
        "pagination": {
            "total_pages": (total + per_page - 1) // per_page,
            "has_next": page * per_page < total,
            "has_prev": page > 1,
        },
    })
    ]

    return jsonify({
        "data": profiles,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "has_next": page * per_page < total,
            "has_prev": page > 1,
        },
    })


@profiles_bp.route("/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    db = get_db()
    user = db.execute(
        "SELECT id, name, email, bio, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    if not user:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify({
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "bio": user[3] or "",
        "created_at": user[4],
    })


@profiles_bp.route("/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "Profile not found"}), 404
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    allowed_fields = {"name", "email", "bio"}
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    db.commit()

    updated = db.execute(
        "SELECT id, name, email, bio, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    return jsonify({
        "id": updated[0],
        "name": updated[1],
        "email": updated[2],
        "bio": updated[3] or "",
        "created_at": updated[4],
    })


@profiles_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_profile(user_id):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return jsonify({"message": "Profile deleted successfully"}), 200
