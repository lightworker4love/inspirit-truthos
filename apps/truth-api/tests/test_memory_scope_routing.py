"""
tests/test_memory_scope_routing.py
Phase 1/2 scaffolding — scope resolution logic tests.

All tests run without any live external services or network calls.
They verify that memory_policy.resolve_scope() applies the correct
policy logic from settings, and that unknown or disallowed scopes
are safely handled.
"""

import pytest

# Override settings before importing anything else to prevent .env reads
# from polluting the test environment with a real MEMORY_LONGTERM_ENABLED=true.
import importlib
from unittest.mock import patch

from app.services import memory_policy


def _make_settings(**overrides):
    """Return a mock settings-like object for policy tests."""
    defaults = {
        "memory_longterm_enabled": False,
        "memory_read_enabled": False,
        "memory_write_enabled": False,
        "memory_allowed_scopes": "default,none,session,experiment",
        "memory_default_scope": "default",
        "memory_experiment_scope_enabled": False,
        "memory_session_scope_write_enabled": False,
        "memory_write_min_chars": 24,
        "memory_user_id_source": "auth",
        "memory_trust_proxy_user_id": False,
    }
    defaults.update(overrides)

    class FakeSettings:
        pass

    obj = FakeSettings()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# resolve_scope
# ---------------------------------------------------------------------------

def test_resolve_scope_returns_none_when_globally_disabled():
    s = _make_settings(memory_longterm_enabled=False)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.resolve_scope("default") == "none"


def test_resolve_scope_respects_requested_scope():
    s = _make_settings(memory_longterm_enabled=True)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.resolve_scope("session") == "session"


def test_resolve_scope_falls_back_for_unknown_scope():
    s = _make_settings(memory_longterm_enabled=True, memory_default_scope="default")
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_scope("unknown_scope_xyz")
    assert result == "default"


def test_resolve_scope_none_is_always_allowed():
    s = _make_settings(memory_longterm_enabled=True)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.resolve_scope("none") == "none"


def test_resolve_scope_experiment_gated_by_flag():
    # experiment scope requested but flag is off
    s = _make_settings(
        memory_longterm_enabled=True,
        memory_experiment_scope_enabled=False,
        memory_default_scope="default",
    )
    with patch("app.services.memory_policy.settings", s):
        result = memory_policy.resolve_scope("experiment")
    assert result == "default"


def test_resolve_scope_experiment_allowed_when_flag_on():
    s = _make_settings(
        memory_longterm_enabled=True,
        memory_experiment_scope_enabled=True,
    )
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.resolve_scope("experiment") == "experiment"


# ---------------------------------------------------------------------------
# is_read_permitted / is_write_permitted
# ---------------------------------------------------------------------------

def test_read_not_permitted_when_scope_none():
    s = _make_settings(memory_read_enabled=True)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_read_permitted("none") is False


def test_read_not_permitted_when_flag_off():
    s = _make_settings(memory_read_enabled=False)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_read_permitted("default") is False


def test_read_permitted_when_all_conditions_met():
    s = _make_settings(memory_read_enabled=True)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_read_permitted("default") is True


def test_write_not_permitted_when_scope_none():
    s = _make_settings(memory_write_enabled=True)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_write_permitted("none", 1000) is False


def test_write_not_permitted_when_flag_off():
    s = _make_settings(memory_write_enabled=False)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_write_permitted("default", 1000) is False


def test_write_not_permitted_below_min_chars():
    s = _make_settings(memory_write_enabled=True, memory_write_min_chars=100)
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_write_permitted("default", 50) is False


def test_write_not_permitted_session_scope_when_flag_off():
    s = _make_settings(
        memory_write_enabled=True,
        memory_session_scope_write_enabled=False,
        memory_write_min_chars=10,
    )
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_write_permitted("session", 100) is False


def test_write_permitted_when_all_conditions_met():
    s = _make_settings(
        memory_write_enabled=True,
        memory_write_min_chars=10,
    )
    with patch("app.services.memory_policy.settings", s):
        assert memory_policy.is_write_permitted("default", 100) is True
