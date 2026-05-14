from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db import connect_db


def write_truth_eval(
    *,
    user_id: str,
    session_id: str | None,
    question: str,
    verification_track: str,
    life_evidence_confirmed: bool,
    discovery_triggered: bool,
) -> str:
    eval_id = f"te_{uuid4().hex}"
    now = datetime.now(timezone.utc).isoformat()
    with connect_db() as connection:
        connection.execute(
            """
            INSERT INTO truth_evals (
              id, user_id, session_id, question, verification_track,
              life_evidence_confirmed, discovery_triggered, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eval_id,
                user_id,
                session_id,
                question,
                verification_track,
                int(life_evidence_confirmed),
                int(discovery_triggered),
                now,
            ),
        )
        connection.commit()
    return eval_id
