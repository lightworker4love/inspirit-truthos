"""
tests/test_memory_hooks_chat_flow.py
Phase 1/2 scaffolding — memory service no-op behavior when flags are disabled.

These tests verify that:
1. memory_service.retrieve() returns skipped=True when flags are off.
2. memory_service.store() returns skipped=True when flags are off.
3. Neither function raises or makes network calls when disabled.
4. format_context_block() returns empty string when memories list is empty.

No live network connections.  Settings are patched to safe defaults.
"""

from unittest.mock import patch, MagicMock

from app.services import memory_service
from app.services.memory_types import MemoryReadRequest, MemoryWriteRequest


def _disabled_settings():
    class Fake:
        memory_longterm_enabled = False
        memory_read_enabled = False
        memory_write_enabled = False
        memory_allowed_scopes = "default,none,session,experiment"
        memory_default_scope = "default"
        memory_experiment_scope_enabled = False
        memory_session_scope_write_enabled = False
        memory_write_min_chars = 24
        memory_fail_open_read = True
        memory_fail_open_write = True
        mem0_base_url = ""
        mem0_api_key = ""
    return Fake()


def _enabled_no_url_settings():
    class Fake:
        memory_longterm_enabled = True
        memory_read_enabled = True
        memory_write_enabled = True
        memory_allowed_scopes = "default,none,session,experiment"
        memory_default_scope = "default"
        memory_experiment_scope_enabled = False
        memory_session_scope_write_enabled = False
        memory_write_min_chars = 24
        memory_fail_open_read = True
        memory_fail_open_write = True
        mem0_base_url = ""  # not configured
        mem0_api_key = ""
    return Fake()


# ---------------------------------------------------------------------------
# retrieve() — disabled flags
# ---------------------------------------------------------------------------

def test_retrieve_skips_when_globally_disabled():
    s = _disabled_settings()
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
    ):
        req = MemoryReadRequest(
            user_id="user-123",
            thread_id="thread-abc",
            query="test message",
            scope="default",
        )
        result = memory_service.retrieve(req)
    assert result.skipped is True
    assert result.memories == []


def test_retrieve_skips_when_scope_is_none():
    s = _disabled_settings()
    s.memory_longterm_enabled = True  # enabled but scope=none
    s.memory_read_enabled = True
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
    ):
        req = MemoryReadRequest(
            user_id="user-123",
            thread_id="thread-abc",
            query="test message",
            scope="none",
        )
        result = memory_service.retrieve(req)
    assert result.skipped is True


def test_retrieve_skips_when_base_url_not_configured():
    s = _enabled_no_url_settings()
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
    ):
        req = MemoryReadRequest(
            user_id="user-123",
            thread_id="thread-abc",
            query="test message",
            scope="default",
        )
        result = memory_service.retrieve(req)
    assert result.skipped is True
    assert result.error is not None


def test_retrieve_does_not_call_client_when_disabled():
    s = _disabled_settings()
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
        patch("app.services.memory_service.memory_clients.mem0_search") as mock_search,
    ):
        req = MemoryReadRequest(
            user_id="user-123",
            thread_id="thread-abc",
            query="test message",
            scope="default",
        )
        memory_service.retrieve(req)
    mock_search.assert_not_called()


# ---------------------------------------------------------------------------
# store() — disabled flags
# ---------------------------------------------------------------------------

def test_store_skips_when_globally_disabled():
    s = _disabled_settings()
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
    ):
        req = MemoryWriteRequest(
            user_id="user-123",
            thread_id="thread-abc",
            user_message="Hello",
            assistant_reply="A response that is long enough to pass min_chars check.",
            scope="default",
        )
        result = memory_service.store(req)
    assert result.skipped is True
    assert result.stored is False


def test_store_does_not_call_client_when_disabled():
    s = _disabled_settings()
    with (
        patch("app.services.memory_policy.settings", s),
        patch("app.services.memory_service.settings", s),
        patch("app.services.memory_service.memory_clients.mem0_add") as mock_add,
    ):
        req = MemoryWriteRequest(
            user_id="user-123",
            thread_id="thread-abc",
            user_message="Hello",
            assistant_reply="A response that is long enough.",
            scope="default",
        )
        memory_service.store(req)
    mock_add.assert_not_called()


# ---------------------------------------------------------------------------
# format_context_block()
# ---------------------------------------------------------------------------

def test_format_context_block_empty_on_no_memories():
    result = memory_service.format_context_block([])
    assert result == ""


def test_format_context_block_produces_section_header():
    result = memory_service.format_context_block(["User prefers concise answers."])
    assert "## Relevant Memory Context" in result
    assert "User prefers concise answers." in result


def test_format_context_block_multiple_memories():
    memories = ["fact one", "fact two", "fact three"]
    result = memory_service.format_context_block(memories)
    for m in memories:
        assert m in result


def test_format_context_block_skips_empty_strings():
    result = memory_service.format_context_block(["", "  ", "real fact"])
    assert "real fact" in result
    # Should not produce bullet for empty lines
    lines = [ln for ln in result.splitlines() if ln.strip().startswith("-")]
    assert len(lines) == 1
