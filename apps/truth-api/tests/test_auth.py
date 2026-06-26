from app.routes import auth_routes


def test_login_route_success(client, monkeypatch):
    monkeypatch.setattr(
        auth_routes,
        "login",
        lambda request, username, password: {
            "user": {
                "id": "usr_case_hank",
                "username": username,
                "role": "case_client",
                "displayName": "Hank",
                "email": None,
            },
            "session": {
                "token": "session_test",
                "expiresAt": "2026-03-23T00:00:00+00:00",
            },
        },
    )

    response = client.post(
        "/auth/login",
        json={"username": "hank", "password": "secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "hank"
    assert data["user"]["role"] == "case_client"
    assert data["session"]["token"] == "session_test"
