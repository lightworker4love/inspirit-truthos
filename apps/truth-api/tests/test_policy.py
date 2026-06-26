from app.routes import model_routes


def test_allowed_modes_case_client(client, monkeypatch):
    monkeypatch.setattr(
        model_routes,
        "get_current_user",
        lambda token: {
            "id": "usr_case_hank",
            "username": "hank",
            "role": "case_client",
            "displayName": "Hank",
            "email": None,
        },
    )

    response = client.get(
        "/models/allowed",
        headers={"Authorization": "Bearer session_test"},
    )
    assert response.status_code == 200
    data = response.json()
    keys = [m["key"] for m in data["modes"]]
    assert "spiritual_reflection" in keys
    assert "scripture_reflection" in keys
