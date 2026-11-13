"""Verify that NFD filenames cannot bypass NFC MANIFEST.in exclusions."""
from __future__ import annotations

import importlib.metadata
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unicodedata

version = importlib.metadata.version("setuptools")
assert tuple(map(int, version.split(".")[:2])) >= (83, 0), version
with tempfile.TemporaryDirectory(prefix="truthos-setuptools-") as directory:
    root = Path(directory)
    (root / "setup.py").write_text(
        "from setuptools import setup\nsetup(name='truthos-unicode-fixture', version='0.0.0', py_modules=['fixture'])\n",
        encoding="utf-8",
    )
    (root / "fixture.py").write_text("# Synthetic packaging fixture\n", encoding="utf-8")
    (root / "public.txt").write_text("public synthetic fixture\n", encoding="utf-8")
    secret = "secret_café.txt"
    (root / unicodedata.normalize("NFD", secret)).write_text(
        "synthetic marker, not a credential\n", encoding="utf-8"
    )
    (root / "MANIFEST.in").write_text(
        f"global-include *.txt\nglobal-exclude {secret}\n", encoding="utf-8"
    )
    subprocess.run(
        [sys.executable, "setup.py", "sdist"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    archives = list((root / "dist").glob("*.tar.gz"))
    assert len(archives) == 1
    with tarfile.open(archives[0]) as archive:
        names = [unicodedata.normalize("NFC", member.name) for member in archive]
    assert any(name.endswith("/public.txt") for name in names), names
    assert not any(name.endswith("/" + secret) for name in names), names
print(f"PASS setuptools {version}: NFD fixture excluded by NFC manifest; public control retained")
