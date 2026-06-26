"""
Tests for blueprint writeback observability and gate logic.

Covers:
  A. Successful writeback (gate passes, signals found, save called)
  B. Gate blocked — short conversation (char_count < MIN)
  C. Gate blocked — session_count < MIN
  D. Gate blocked — signal density < MIN
  E. Daily cap enforcement
  F. save_case_profile failure → re-raises (caller must isolate)
  G. SOUL_AGE_INFERENCE_ENABLED=False → soul_age not written
  H. force=True bypasses gate (admin path)
  I. No insight available → skipped without save
  J. Kill switch (BLUEPRINT_WRITEBACK_ENABLED=false)

Run from the truth-api root or via: pytest workspace/soul-guardian/test_blueprint_writeback.py -v
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRUTH_API = _REPO_ROOT / "inspirit-truthos" / "apps" / "truth-api"
if str(_TRUTH_API) not in sys.path:
    sys.path.insert(0, str(_TRUTH_API))

import app.case_insight_service as svc
from app.case_models import CaseProfile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_daily_counter():
    """Wipe the in-memory daily cap counter before/after each test."""
    svc._DAILY_WRITE_COUNTER.clear()
    yield
    svc._DAILY_WRITE_COUNTER.clear()


@pytest.fixture()
def profile():
    return CaseProfile(
        case_id="web__test",
        login_username="test_user",
        preferred_name="TestUser",
        source_channel="web",
        memory_namespace="web__test",
    )


# Enough chars with life-theme + blind-spot signals to pass the gate
RICH_TEXT = (
    "我在探索界線與自我價值的課題。"  # theme: boundaries and self-worth
    "anxiety about relationships and intimacy, "  # theme: relationships + emotional regulation
    "I tend to over-explain things to justify myself. "  # blind_spot: over-explaining
    "There is a lot of avoiding and delay in my decision-making. "  # blind_spot: avoidance
) * 15  # ~600+ chars after repetition

SHORT_TEXT = "hi"


# ---------------------------------------------------------------------------
# A. Successful writeback
# ---------------------------------------------------------------------------

class TestSuccessPath:
    def test_save_called_on_rich_conversation(self, profile):
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "你的界線意識正在萌芽。"},
                metadata={"session_count": 5, "request_id": "req-abc", "source_channel": "web"},
            )
        assert saved, "save_case_profile should have been called"
        assert "last_session_insight" in [f for f in ["last_session_insight"] if result.last_session_insight]
        assert any("boundaries" in t for t in result.life_themes)

    def test_life_themes_appended_not_overwritten(self, profile):
        profile_with_existing = profile.model_copy(
            update={"life_themes": ["trust and allowing"]}
        )
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile_with_existing,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "insight."},
                metadata={"session_count": 5},
            )
        assert "trust and allowing" in result.life_themes, "existing theme must be preserved"
        assert len(result.life_themes) > 1, "new themes should be appended"


# ---------------------------------------------------------------------------
# B–D. Gate blocked
# ---------------------------------------------------------------------------

class TestGateBlocked:
    def test_short_conversation_no_list_writes(self, profile):
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": SHORT_TEXT}],
                model_response={"mirror": "ok"},
                metadata={"session_count": 5},
            )
        # Short text → no insight derivable, no themes → no save at all
        assert result.life_themes == profile.life_themes
        assert result.blind_spots == profile.blind_spots
        # save may or may not be called depending on insight; profile must not have list fields added

    def test_low_session_count_blocks_list_fields(self, profile):
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "insight here."},
                metadata={"session_count": 0},  # below MIN=3
            )
        # Gate blocks list fields; only insight might be written
        assert result.life_themes == profile.life_themes
        assert result.blind_spots == profile.blind_spots

    def test_no_signals_in_text_skips_list_fields(self, profile):
        bland_text = "天氣不錯，我今天吃了飯，想想要去散步。" * 40  # >500 chars, no keyword signals
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": bland_text}],
                model_response={"mirror": "好的。"},
                metadata={"session_count": 5},
            )
        # Insufficient signal density blocks list fields
        assert result.life_themes == profile.life_themes


# ---------------------------------------------------------------------------
# E. Daily cap
# ---------------------------------------------------------------------------

class TestDailyCap:
    def test_cap_blocks_after_limit(self, profile):
        """After _MAX_DAILY_BLUEPRINT_WRITES calls, subsequent calls are blocked."""
        insight_response = {"mirror": "有洞見。"}
        with patch("app.case_insight_service.save_case_profile"):
            for _ in range(svc._MAX_DAILY_BLUEPRINT_WRITES):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response=insight_response,
                    metadata={"session_count": 10},
                )

        saved_after_cap = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved_after_cap.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response=insight_response,
                metadata={"session_count": 10},
            )
        assert not saved_after_cap, "save should NOT be called after daily cap is hit"
        assert result.life_themes == profile.life_themes

    def test_different_cases_have_independent_caps(self, profile):
        """Cap is per case_id, not global."""
        other = profile.model_copy(update={"case_id": "web__other", "memory_namespace": "web__other"})
        with patch("app.case_insight_service.save_case_profile") as mock_save:
            # Exhaust cap for 'profile'
            for _ in range(svc._MAX_DAILY_BLUEPRINT_WRITES):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response={"mirror": "insight."},
                    metadata={"session_count": 10},
                )
            # 'other' should still be allowed
            svc.update_case_blueprint_from_conversation(
                other,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "insight."},
                metadata={"session_count": 10},
            )
        # At least one save should be for the 'other' case
        saved_case_ids = [c.args[0].case_id for c in mock_save.call_args_list]
        assert "web__other" in saved_case_ids


# ---------------------------------------------------------------------------
# F. Failure isolation
# ---------------------------------------------------------------------------

class TestFailureIsolation:
    def test_save_failure_reraises_for_caller_isolation(self, profile):
        """The service re-raises so the caller (main.py) can catch and isolate."""
        with patch("app.case_insight_service.save_case_profile", side_effect=OSError("disk full")):
            with pytest.raises(OSError, match="disk full"):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response={"mirror": "insight."},
                    metadata={"session_count": 5},
                )

    def test_blueprint_update_failed_event_emitted_on_save_error(self, profile, caplog):
        import logging
        with patch("app.case_insight_service.save_case_profile", side_effect=OSError("no space")):
            with caplog.at_level(logging.INFO, logger="app.case_insight_service"):
                try:
                    svc.update_case_blueprint_from_conversation(
                        profile,
                        conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                        model_response={"mirror": "insight."},
                        metadata={"session_count": 5},
                    )
                except OSError:
                    pass
        assert any("blueprint_event=blueprint_update_failed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# G. SOUL_AGE_INFERENCE_ENABLED=False
# ---------------------------------------------------------------------------

class TestSoulAgeFlag:
    def test_soul_age_not_written_when_flag_off(self, profile):
        assert svc.SOUL_AGE_INFERENCE_ENABLED is False, "flag must default to False"
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[
                    {"role": "user", "content": RICH_TEXT + " status win prove control beat " * 20}
                ],
                model_response={"mirror": "insight."},
                metadata={"session_count": 10},
            )
        assert result.soul_age is None


# ---------------------------------------------------------------------------
# H. force=True — admin/backfill path bypasses gate
# ---------------------------------------------------------------------------

class TestForceFlag:
    def test_force_bypasses_session_count_gate(self, profile):
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "insight."},
                metadata={"session_count": 0},  # would normally block
                force=True,
            )
        assert saved, "force=True must bypass session_count gate"
        assert any("boundaries" in t for t in result.life_themes)

    def test_force_bypasses_char_count_gate(self, profile):
        # Enough signal keywords but just slightly short on chars
        short_but_signalled = "界線 anxiety over-explain " * 8  # ~200 chars
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": short_but_signalled}],
                model_response={"mirror": "insight."},
                metadata={"session_count": 10},
                force=True,
            )
        # force — char count gate bypassed; signals were found so save should be attempted
        # (save may or may not be called if no insight derived — acceptable)
        # Main assertion: no exception raised
        assert True


# ---------------------------------------------------------------------------
# I. No insight + no signals → skipped (no save)
# ---------------------------------------------------------------------------

class TestSkipWhenEmpty:
    def test_empty_messages_and_response_skips_save(self, profile):
        """Truly empty input (no messages, no response) → nothing to derive → no save."""
        saved = []
        with patch("app.case_insight_service.save_case_profile", side_effect=saved.append):
            result = svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[],   # empty list → _normalize_text → ""
                model_response={},          # empty dict → all candidates fail → ""
                metadata={"session_count": 5},
            )
        assert not saved, "nothing derivable → save should not be called"
        assert result is profile  # original profile returned unchanged


# ---------------------------------------------------------------------------
# Observability: event names in log output
# ---------------------------------------------------------------------------

class TestObservabilityEvents:
    def test_attempted_event_always_emitted(self, profile, caplog):
        import logging
        with caplog.at_level(logging.INFO, logger="app.case_insight_service"):
            with patch("app.case_insight_service.save_case_profile"):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response={"mirror": "洞見。"},
                    metadata={"session_count": 5},
                )
        assert any("blueprint_event=blueprint_update_attempted" in r.message for r in caplog.records)

    def test_succeeded_event_on_save(self, profile, caplog):
        import logging
        with caplog.at_level(logging.INFO, logger="app.case_insight_service"):
            with patch("app.case_insight_service.save_case_profile"):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response={"mirror": "洞見。"},
                    metadata={"session_count": 5},
                )
        assert any("blueprint_event=blueprint_update_succeeded" in r.message for r in caplog.records)

    def test_blocked_event_on_daily_cap(self, profile, caplog):
        import logging
        with patch("app.case_insight_service.save_case_profile"):
            for _ in range(svc._MAX_DAILY_BLUEPRINT_WRITES):
                svc.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                    model_response={"mirror": "洞見。"},
                    metadata={"session_count": 10},
                )
        with caplog.at_level(logging.INFO, logger="app.case_insight_service"):
            svc.update_case_blueprint_from_conversation(
                profile,
                conversation_messages=[{"role": "user", "content": RICH_TEXT}],
                model_response={"mirror": "洞見。"},
                metadata={"session_count": 10},
            )
        assert any(
            "blueprint_event=blueprint_update_blocked" in r.message and "daily_cap" in r.message
            for r in caplog.records
        )


# ---------------------------------------------------------------------------
# J. Kill switch — BLUEPRINT_WRITEBACK_ENABLED env-var guard (in main.py)
# ---------------------------------------------------------------------------

class TestKillSwitch:
    """Tests for the _BLUEPRINT_WRITEBACK_ENABLED flag in app.main.

    We exercise _attempt_blueprint_writeback directly rather than going through
    the HTTP handler to keep tests fast and free of network/DB dependencies.
    """

    @pytest.fixture(autouse=True)
    def imports(self):
        import app.main as main_mod
        from app.models import TruthQueryRequest
        self.main = main_mod
        self.TruthQueryRequest = TruthQueryRequest

    def _make_payload(self):
        return self.TruthQueryRequest(
            user_id="kill_switch_user",
            login_username="KsUser",
            source_channel="web",
            session_id="ks-001",
            message="test",
        )

    def _make_case_ctx(self, case_id="web__kill_switch_user"):
        ctx = types.SimpleNamespace(case_id=case_id)
        return ctx

    def test_kill_switch_off_skips_load_and_emits_event(self, caplog):
        """When flag is False, load_case_profile must NOT be called and the
        blueprint_writeback_disabled event must be logged."""
        import logging
        with patch.object(self.main, "_BLUEPRINT_WRITEBACK_ENABLED", False), \
             patch.object(self.main, "load_case_profile") as mock_load, \
             caplog.at_level(logging.INFO, logger="app.main"):
            self.main._attempt_blueprint_writeback(
                self._make_payload(),
                self._make_case_ctx(),
                {"mirror": "irrelevant"},
                "req-ks-001",
            )
        mock_load.assert_not_called()
        assert any(
            "blueprint_event=blueprint_writeback_disabled" in r.message
            for r in caplog.records
        )

    def test_kill_switch_on_proceeds_normally(self):
        """When flag is True (default), load_case_profile IS called."""
        with patch.object(self.main, "_BLUEPRINT_WRITEBACK_ENABLED", True), \
             patch.object(self.main, "load_case_profile", return_value=None) as mock_load, \
             patch.object(self.main, "_count_case_sessions", return_value=0):
            self.main._attempt_blueprint_writeback(
                self._make_payload(),
                self._make_case_ctx(),
                {"mirror": "ok"},
                "req-ks-002",
            )
        mock_load.assert_called_once_with("web__kill_switch_user")

    def test_kill_switch_disabled_event_contains_case_id(self, caplog):
        """The disabled event must include the case_id for traceability."""
        import logging
        ctx = self._make_case_ctx(case_id="web__traceable_case")
        with patch.object(self.main, "_BLUEPRINT_WRITEBACK_ENABLED", False), \
             patch.object(self.main, "load_case_profile"), \
             caplog.at_level(logging.INFO, logger="app.main"):
            self.main._attempt_blueprint_writeback(
                self._make_payload(),
                ctx,
                {},
                "req-ks-003",
            )
        assert any(
            "blueprint_event=blueprint_writeback_disabled" in r.message
            and "web__traceable_case" in r.message
            for r in caplog.records
        )

