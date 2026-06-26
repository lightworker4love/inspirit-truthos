import json
from uuid import uuid4

from app.core.db import get_db
from app.core.security import utcnow_iso


def write_audit_log(
    actor_user_id: str | None,
    action: str,
    result: str,
    target_type: str | None = None,
    target_id: str | None = None,
    resolved_model_id: str | None = None,
    metadata: dict | None = None,
):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO audit_logs (
                id, actor_user_id, action, target_type, target_id,
                resolved_model_id, result, metadata_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"audit_{uuid4().hex}",
                actor_user_id,
                action,
                target_type,
                target_id,
                resolved_model_id,
                result,
                json.dumps(metadata or {}, ensure_ascii=False),
                utcnow_iso(),
            ),
        )
