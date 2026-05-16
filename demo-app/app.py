from flask import Flask, request, jsonify, render_template
import sqlite3
import requests

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
        f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    ).fetchall()
    return jsonify(results)


@app.route("/users")
def list_users():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return jsonify(users)


@app.route("/api/external-data")
def get_external_data():
    resp = requests.get("https://api.example.com/data")
    return jsonify(resp.json())


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
        f"SELECT * FROM users WHERE name = '{username}'"
    ).fetchone()
    bio = user[3] if user and len(user) > 3 else ""
    return render_template("profile.html", username=username, user_bio=bio)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
