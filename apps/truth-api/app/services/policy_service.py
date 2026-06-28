from fastapi import HTTPException, status

from app.repositories.policy_repo import get_allowed_modes_by_role, get_policy_by_role_and_mode, get_active_prompt_by_audience


def list_allowed_modes(role: str):
    rows = get_allowed_modes_by_role(role)
    return [
        {
            "key": row["mode_key"],
            "label": row["mode_label"],
            "default": bool(row["is_default"]),
        }
        for row in rows
    ]


def resolve_model(role: str, mode_key: str):
    row = get_policy_by_role_and_mode(role, mode_key)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mode is not allowed for this role",
        )
    return {
        "mode": row["mode_key"],
        "label": row["mode_label"],
        "model_id": row["model_id"],
    }


def load_active_prompt(role: str) -> str:
    audience = "case_client" if role == "case_client" else "admin_builder"
    row = get_active_prompt_by_audience(audience)
    if not row:
        return "You are a safe and helpful assistant."
    return row["content_body"]
