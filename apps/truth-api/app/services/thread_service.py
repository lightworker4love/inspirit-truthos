from fastapi import HTTPException, status

from app.repositories.thread_repo import create_thread, get_thread_by_id, list_entries, add_entry


def create_role_bound_thread(current_user: dict, resolved_mode: dict, title: str | None):
    thread_id = create_thread(
        case_user_id=current_user["id"],
        created_by_user_id=current_user["id"],
        mode_key=resolved_mode["mode"],
        mode_label=resolved_mode["label"],
        resolved_model_id=resolved_mode["model_id"],
        title=title,
    )
    return thread_id


def get_accessible_thread(current_user: dict, thread_id: str):
    row = get_thread_by_id(thread_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    if current_user["role"] == "case_client" and row["case_user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Thread access denied")

    return row


def append_message(thread_id: str, speaker: str, content: str):
    return add_entry(thread_id, speaker, content)


def get_thread_with_entries(thread_id: str):
    thread = get_thread_by_id(thread_id)
    entries = list_entries(thread_id)
    return thread, entries
