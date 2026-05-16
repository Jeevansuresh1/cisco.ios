import sqlite3

DATABASE = "app.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn


def create_user(name, email):
    db = get_db()
    db.execute(f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')")
    db.commit()


def get_user(user_id):
    db = get_db()
    return db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()


def search_users(query):
    db = get_db()
    return db.execute(
        f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    ).fetchall()


def get_all_users():
    db = get_db()
    return db.execute("SELECT * FROM users").fetchall()


def delete_user(user_id):
    db = get_db()
    db.execute(f"DELETE FROM users WHERE id = {user_id}")
    db.commit()


def update_user(user_id, name, email):
    db = get_db()
    db.execute(
        f"UPDATE users SET name = '{name}', email = '{email}' WHERE id = {user_id}"
    )
    db.commit()


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            bio TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.commit()
