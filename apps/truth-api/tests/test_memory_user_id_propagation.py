"""
tests/test_memory_user_id_propagation.py
Phase 1/2 scaffolding — identity governance tests.

Ensures that memory_policy.resolve_user_id() always prefers the
auth-derived identity and only falls through to proxy identity when
all trust conditions are explicitly satisfied.

No network calls.  No live settings.
"""

from unittest.mock import patch

from app.services import memory_policy


def _make_settings(**overrides):
    defaults = {
        "memory_user_id_source": "auth",
        "memory_trust_proxy_user_id": False,
    }
    defaults.update(overrides)

    class Fake:
        pass

    obj = Fake()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# Default: auth mode
# ---------------------------------------------------------------------------

def test_auth_mode_always_returns_auth_user_id():
    s = _make_settings(memory_user_id_source="auth")
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="proxy-user-xyz",
        )
    assert result == "auth-user-123"


def test_auth_mode_ignores_proxy_user_id_even_if_trust_flag_true():
    s = _make_settings(memory_user_id_source="auth", memory_trust_proxy_user_id=True)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="proxy-user-xyz",
        )
    assert result == "auth-user-123"


# ---------------------------------------------------------------------------
# Proxy mode (only when explicitly configured)
# ---------------------------------------------------------------------------

def test_proxy_mode_returns_proxy_id_when_trust_flag_true():
    s = _make_settings(memory_user_id_source="proxy", memory_trust_proxy_user_id=True)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="proxy-user-xyz",
        )
    assert result == "proxy-user-xyz"


def test_proxy_mode_falls_back_to_auth_when_trust_flag_false():
    s = _make_settings(memory_user_id_source="proxy", memory_trust_proxy_user_id=False)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="proxy-user-xyz",
        )
    assert result == "auth-user-123"


def test_proxy_mode_falls_back_when_proxy_id_empty():
    s = _make_settings(memory_user_id_source="proxy", memory_trust_proxy_user_id=True)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="",
        )
    assert result == "auth-user-123"


def test_proxy_mode_falls_back_when_proxy_id_none():
    s = _make_settings(memory_user_id_source="proxy", memory_trust_proxy_user_id=True)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id=None,
        )
    assert result == "auth-user-123"


def test_proxy_mode_falls_back_when_proxy_id_whitespace():
    s = _make_settings(memory_user_id_source="proxy", memory_trust_proxy_user_id=True)
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_user_id(
            auth_user_id="auth-user-123",
            proxy_user_id="   ",
        )
    assert result == "auth-user-123"


# ---------------------------------------------------------------------------
# assert_scope_valid helper
# ---------------------------------------------------------------------------

def test_assert_scope_valid_passes_for_known_scope():
    s = _make_settings()
    # Set memory_allowed_scopes on the fake settings
    s.memory_allowed_scopes = "default,none,session,experiment"
    with patch("app.services.memory_policy.settings", s):
        memory_policy.assert_scope_valid("default")  # should not raise


def test_assert_scope_valid_raises_for_unknown_scope():
    import pytest
    s = _make_settings()
    s.memory_allowed_scopes = "default,none,session,experiment"
    with patch("app.services.memory_policy.settings", s):
        with pytest.raises(ValueError, match="not in MEMORY_ALLOWED_SCOPES"):
            memory_policy.assert_scope_valid("rogue_scope")
