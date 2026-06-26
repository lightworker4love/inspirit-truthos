from app.core.db import get_db


def get_allowed_modes_by_role(role: str):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM model_policies
            WHERE role = ? AND enabled = 1
            ORDER BY is_default DESC, mode_label ASC
            """,
            (role,),
        ).fetchall()


def get_policy_by_role_and_mode(role: str, mode_key: str):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM model_policies
            WHERE role = ? AND mode_key = ? AND enabled = 1
            LIMIT 1
            """,
            (role, mode_key),
        ).fetchone()


def get_active_prompt_by_audience(audience: str):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM prompt_versions
            WHERE audience = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (audience,),
        ).fetchone()
