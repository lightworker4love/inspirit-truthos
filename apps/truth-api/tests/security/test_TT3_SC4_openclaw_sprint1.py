from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from app.gateway_check import _validated_gateway_base_url


REPO_ROOT = Path(__file__).resolve().parents[4]


def _load_openclaw_bridge_module():
    module_path = REPO_ROOT / "scripts" / "openclaw_bridge.py"
    spec = importlib.util.spec_from_file_location("openclaw_bridge_security_test", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vulnerability_exists_before_fix_gateway_base_url():
    # This test documents the vulnerable pattern. It should fail if validation is removed.
    with pytest.raises(ValueError):
        _validated_gateway_base_url("http://169.254.169.254/latest/meta-data")


def test_fix_prevents_gateway_credential_exfiltration_url():
    with pytest.raises(ValueError):
        _validated_gateway_base_url("https://token@example.com/v1")


def test_fix_allows_known_embedding_gateway_hosts():
    assert _validated_gateway_base_url("http://host.docker.internal:11434/v1") == "http://host.docker.internal:11434/v1"
    assert _validated_gateway_base_url("https://api.openai.com/v1/") == "https://api.openai.com/v1"


def test_vulnerability_exists_before_fix_truthos_internal_url():
    # This test documents the vulnerable pattern. It should fail if validation is removed.
    bridge = _load_openclaw_bridge_module()
    with pytest.raises(ValueError):
        bridge._validated_truthos_internal_url("http://evil.example/api")


def test_fix_prevents_truthos_internal_credential_exfiltration_url():
    bridge = _load_openclaw_bridge_module()
    with pytest.raises(ValueError):
        bridge._validated_truthos_internal_url("http://user:pass@localhost:18000")


def test_fix_allows_local_truthos_internal_url():
    bridge = _load_openclaw_bridge_module()
    assert bridge._validated_truthos_internal_url("http://localhost:18000/") == "http://localhost:18000"


def test_vulnerability_exists_before_fix_dependency_floor():
    # This test documents vulnerable dependency floors. It should fail if floors regress.
    pyproject = (REPO_ROOT / "apps" / "truth-api" / "pyproject.toml").read_text()
    requirements = (REPO_ROOT / "apps" / "truth-api" / "requirements.txt").read_text()
    assert "setuptools>=68" not in pyproject
    assert "pyarrow>=14.0.0" not in requirements


def test_fix_pins_patched_dependency_floors():
    pyproject = (REPO_ROOT / "apps" / "truth-api" / "pyproject.toml").read_text()
    requirements = (REPO_ROOT / "apps" / "truth-api" / "requirements.txt").read_text()
    assert 'setuptools>=78.1.1' in pyproject
    assert "pyarrow>=17.0.0" in requirements
