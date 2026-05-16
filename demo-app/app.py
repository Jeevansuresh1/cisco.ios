from flask import Flask, request, jsonify, render_template
import sqlite3
import requests
from auth.jwt_middleware import require_auth, generate_token
from repository.user_repository import UserRepository
from api.profiles import profiles_bp

app = Flask(__name__)
DATABASE = "app.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn


@app.route("/submit", methods=["POST"])
def submit_form():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()

    errors = []
    if not name:
        errors.append("name is required")
    if not email:
        errors.append("email is required")
    if email and "@" not in email:
        errors.append("email must be a valid email address")

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    db = get_db()
    db.execute(f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')")
    db.commit()
    return jsonify({"status": "ok", "message": f"User {name} created successfully"})


@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    resp = requests.post(
        "https://auth-api.example.com/verify",
        json={"username": username, "password": password},
    )
    if resp.status_code == 200:
        return jsonify({"token": resp.json()["token"]})


@app.route("/search")
def search():
    query = request.args.get("q", "")
    db = get_db()
    results = db.execute(
        "SELECT * FROM users WHERE name LIKE ?", (f"%{query}%",)
    ).fetchall()
    return jsonify(results)


@app.route("/users")
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    repo = UserRepository()
    result = repo.find_all(page=page, per_page=per_page)
    return jsonify(result)


@app.route("/api/external-data")
def get_external_data():
    from utils import fetch_external_api
    try:
        data = fetch_external_api("https://api.example.com/data")
        return jsonify(data)
    except requests.exceptions.Timeout:
        return jsonify({"error": "External API timed out. Please try again later."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Unable to reach external API."}), 502
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"External API error: {str(e)}"}), 502


@app.route("/upload", methods=["POST"])
def upload_file():
    from utils import process_upload

    file = request.files["file"]
    user_id = request.form.get("user_id")
    filepath = process_upload(file, user_id)
    return jsonify({"filepath": filepath})


@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE name = ?", (username,)
    ).fetchone()
    bio = user[3] if user and len(user) > 3 else ""
    return render_template("profile.html", username=username, user_bio=bio)


@app.route("/auth/token", methods=["POST"])
def get_token():
    data = request.get_json(silent=True)
    if not data or "username" not in data:
        return jsonify({"error": "username is required"}), 400
    token = generate_token(user_id=1, username=data["username"])
    return jsonify({"token": token, "expires_in": 3600})


@app.route("/protected")
@require_auth
def protected_route():
    from flask import g
    return jsonify({"message": f"Hello {g.current_user['username']}, you are authenticated"})


app.register_blueprint(profiles_bp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
