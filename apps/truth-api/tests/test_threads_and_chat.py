from app.routes import thread_routes, chat_routes


def test_create_thread_success(client, monkeypatch):
    monkeypatch.setattr(
        thread_routes,
        "get_current_user",
        lambda token: {
            "id": "usr_case_hank",
            "username": "hank",
            "role": "case_client",
            "displayName": "Hank",
            "email": None,
        },
    )
    monkeypatch.setattr(
        thread_routes,
        "resolve_model",
        lambda role, mode: {
            "mode": "spiritual_reflection",
            "label": "靜心陪伴模式",
            "model_id": "custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit",
        },
    )
    monkeypatch.setattr(
        thread_routes,
        "create_role_bound_thread",
        lambda user, resolved, title: "thr_test_001",
    )
    monkeypatch.setattr(
        thread_routes,
        "log_event",
        lambda *args, **kwargs: None,
    )

    response = client.post(
        "/threads",
        headers={"Authorization": "Bearer session_test"},
        json={"mode": "spiritual_reflection", "title": "March reflection"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["threadId"] == "thr_test_001"
    assert data["resolvedModelId"] == "custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit"


def test_chat_success(client, monkeypatch):
    monkeypatch.setattr(
        chat_routes,
        "get_current_user",
        lambda token: {
            "id": "usr_case_hank",
            "username": "hank",
            "role": "case_client",
            "displayName": "Hank",
            "email": None,
        },
    )
    monkeypatch.setattr(
        chat_routes,
        "get_accessible_thread",
        lambda user, thread_id: {
            "id": thread_id,
            "selected_mode_key": "spiritual_reflection",
            "resolved_model_id": "custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit",
        },
    )
    monkeypatch.setattr(
        chat_routes,
        "resolve_model",
        lambda role, mode: {
            "mode": "spiritual_reflection",
            "label": "靜心陪伴模式",
            "model_id": "custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit",
        },
    )
    monkeypatch.setattr(
        chat_routes,
        "load_active_prompt",
        lambda role: "You are a safe spiritual dialogue assistant.",
    )
    monkeypatch.setattr(
        chat_routes,
        "append_message",
        lambda thread_id, speaker, content: None,
    )
    monkeypatch.setattr(
        chat_routes,
        "upstream_chat",
        lambda payload: {"content": "我在，先陪你一起呼吸。"},
    )
    monkeypatch.setattr(
        chat_routes,
        "log_event",
        lambda *args, **kwargs: None,
    )

    response = client.post(
        "/chat",
        headers={"Authorization": "Bearer session_test"},
        json={
            "threadId": "thr_test_001",
            "message": "我今天很焦慮。",
            "mode": "spiritual_reflection",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["threadId"] == "thr_test_001"
    assert data["resolvedModelId"] == "custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit"
    assert "呼吸" in data["reply"]
