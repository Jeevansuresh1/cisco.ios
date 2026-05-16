from models import get_db


class UploadRepository:
    def __init__(self):
        self.db = get_db()

    def create(self, filename, user_id, status="pending"):
        cursor = self.db.execute(
            "INSERT INTO uploads (filename, user_id, status) VALUES (?, ?, ?)",
            (filename, user_id, status),
        )
        self.db.commit()
        return {"id": cursor.lastrowid, "filename": filename, "status": status}

    def find_by_user(self, user_id):
        rows = self.db.execute(
            "SELECT * FROM uploads WHERE user_id = ?", (user_id,)
        ).fetchall()
        return [self._to_dict(r) for r in rows]

    def update_status(self, upload_id, status):
        self.db.execute(
            "UPDATE uploads SET status = ? WHERE id = ?", (status, upload_id)
        )
        self.db.commit()

    @staticmethod
    def _to_dict(row):
        if not row:
            return None
        return {
            "id": row[0],
            "filename": row[1],
            "user_id": row[2],
            "status": row[3],
        }
