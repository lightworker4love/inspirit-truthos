from app.core.db import get_db


def get_user_by_username(username: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ? LIMIT 1",
            (username,),
        ).fetchone()


def get_user_by_id(user_id: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ? LIMIT 1",
            (user_id,),
        ).fetchone()


def get_case_profile_by_user_id(user_id: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM case_profiles WHERE user_id = ? LIMIT 1",
            (user_id,),
        ).fetchone()
