from models import get_db


class UserRepository:
    def __init__(self):
        self.db = get_db()

    def find_all(self, page=1, per_page=25):
        offset = (page - 1) * per_page
        users = self.db.execute(
            "SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset)
        ).fetchall()
        total = self.db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return {
            "data": [self._to_dict(u) for u in users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            },
        }

    def find_by_id(self, user_id):
        row = self.db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return self._to_dict(row) if row else None

    def find_by_name(self, name):
        row = self.db.execute(
            "SELECT * FROM users WHERE name = ?", (name,)
        ).fetchone()
        return self._to_dict(row) if row else None

    def search(self, query, page=1, per_page=25):
        offset = (page - 1) * per_page
        rows = self.db.execute(
            "SELECT * FROM users WHERE name LIKE ? LIMIT ? OFFSET ?",
            (f"%{query}%", per_page, offset),
        ).fetchall()
        return [self._to_dict(r) for r in rows]

    def create(self, name, email):
        cursor = self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)", (name, email)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)

    def update(self, user_id, **fields):
        allowed = {"name", "email", "bio"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.find_by_id(user_id)
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        self.db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        self.db.commit()
        return self.find_by_id(user_id)

    def delete(self, user_id):
        self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.db.commit()

    @staticmethod
    def _to_dict(row):
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "bio": row[3] if len(row) > 3 else "",
            "created_at": row[4] if len(row) > 4 else None,
        }
