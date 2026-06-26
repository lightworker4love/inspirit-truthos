from uuid import uuid4

from app.core.db import get_db
from app.core.security import utcnow_iso


def create_thread(case_user_id: str, created_by_user_id: str, mode_key: str, mode_label: str, resolved_model_id: str, title: str | None):
    thread_id = f"thr_{uuid4().hex}"
    now = utcnow_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO case_threads (
                id, case_user_id, created_by_user_id, selected_mode_key,
                selected_mode_label, resolved_model_id, title, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                thread_id,
                case_user_id,
                created_by_user_id,
                mode_key,
                mode_label,
                resolved_model_id,
                title,
                now,
                now,
            ),
        )
    return thread_id


def get_thread_by_id(thread_id: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM case_threads WHERE id = ? LIMIT 1",
            (thread_id,),
        ).fetchone()


def list_entries(thread_id: str):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM case_entries
            WHERE thread_id = ?
            ORDER BY created_at ASC
            """,
            (thread_id,),
        ).fetchall()


def add_entry(thread_id: str, speaker: str, content: str, content_type: str = "text"):
    entry_id = f"entry_{uuid4().hex}"
    now = utcnow_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO case_entries (
                id, thread_id, speaker, content, content_type, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entry_id, thread_id, speaker, content, content_type, now),
        )
    return entry_id
