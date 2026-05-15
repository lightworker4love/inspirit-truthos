from __future__ import annotations

import json

from app.db import connect_db


class SQLiteBeliefLogClient:
    def get_evidence_for_principle(self, user_id: str, principle_id: str) -> list[dict]:
        with connect_db() as connection:
            rows = connection.execute(
                """
                SELECT id, session_id, belief_statement, created_at
                  FROM belief_logs
                 WHERE user_id = ?
                   AND belief_statement LIKE ?
                 ORDER BY created_at DESC
                 LIMIT 5
                """,
                (user_id, f"%{principle_id}%"),
            ).fetchall()
        return [dict(row) for row in rows]


class SQLiteSoulMapClient:
    def get_patterns(self, user_id: str) -> list:
        with connect_db() as connection:
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if "soulmaps" not in tables and "soul_maps" not in tables:
                return []
            if "soulmaps" in tables:
                rows = connection.execute(
                    """
                    SELECT recurringpatternsjson AS patterns
                      FROM soulmaps
                     WHERE userid = ?
                     ORDER BY updatedat DESC
                     LIMIT 1
                    """,
                    (user_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT recurring_patterns_json AS patterns
                      FROM soul_maps
                     WHERE user_id = ?
                     ORDER BY updated_at DESC
                     LIMIT 1
                    """,
                    (user_id,),
                ).fetchall()
        if not rows:
            return []
        try:
            value = json.loads(rows[0]["patterns"] or "[]")
        except json.JSONDecodeError:
            return []
        return value if isinstance(value, list) else []
