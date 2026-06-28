from app.core.db import get_db


def create_session(session_id: str, user_id: str, ip_address: str | None, user_agent: str | None, issued_at: str, expires_at: str):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO auth_sessions (
                id, user_id, ip_address, user_agent, issued_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_id, ip_address, user_agent, issued_at, expires_at),
        )


def get_session(session_id: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM auth_sessions WHERE id = ? LIMIT 1",
            (session_id,),
        ).fetchone()


def revoke_session(session_id: str, revoked_at: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE auth_sessions SET revoked_at = ? WHERE id = ?",
            (revoked_at, session_id),
        )
