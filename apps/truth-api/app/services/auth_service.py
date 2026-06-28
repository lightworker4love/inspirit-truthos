from fastapi import HTTPException, Request, status

from app.core.audit import write_audit_log
from app.core.security import verify_password, create_session_token, utcnow_iso, expires_in_days
from app.repositories.user_repo import get_user_by_username, get_case_profile_by_user_id, get_user_by_id
from app.repositories.session_repo import create_session, get_session, revoke_session


def logout(session_token: str):
    session = get_session(session_token)
    if not session or session["revoked_at"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    revoke_session(session_token, utcnow_iso())
    write_audit_log(session["user_id"], "logout", "success")


def login(request: Request, username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        write_audit_log(None, "login_failure", "failure", metadata={"username": username})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user["status"] != "active":
        write_audit_log(user["id"], "login_failure", "denied", metadata={"reason": "inactive"})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

    session_id = create_session_token()
    issued_at = utcnow_iso()
    expires_at = expires_in_days(7)

    create_session(
        session_id=session_id,
        user_id=user["id"],
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        issued_at=issued_at,
        expires_at=expires_at,
    )

    display_name = user["username"]
    profile = get_case_profile_by_user_id(user["id"])
    if profile and profile["display_name"]:
        display_name = profile["display_name"]

    write_audit_log(user["id"], "login_success", "success")
    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "displayName": display_name,
            "email": user["email"],
        },
        "session": {
            "token": session_id,
            "expiresAt": expires_at,
        },
    }


def get_current_user(session_token: str):
    session = get_session(session_token)
    if not session or session["revoked_at"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = get_user_by_id(session["user_id"])
    if not user or user["status"] != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not available")

    profile = get_case_profile_by_user_id(user["id"])
    display_name = profile["display_name"] if profile and profile["display_name"] else user["username"]

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "displayName": display_name,
        "email": user["email"],
    }
