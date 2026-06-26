from app.core.audit import write_audit_log


def log_event(actor_user_id: str | None, action: str, result: str, target_type: str | None = None, target_id: str | None = None, resolved_model_id: str | None = None, metadata: dict | None = None):
    write_audit_log(
        actor_user_id=actor_user_id,
        action=action,
        result=result,
        target_type=target_type,
        target_id=target_id,
        resolved_model_id=resolved_model_id,
        metadata=metadata,
    )
