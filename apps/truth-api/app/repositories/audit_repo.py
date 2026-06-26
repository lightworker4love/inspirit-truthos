from app.core.db import get_db


def list_audit_logs(limit: int = 100):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM audit_logs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
