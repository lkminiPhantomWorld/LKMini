#!/usr/bin/env python3
"""
verify_lkmini.py — LKMini seed_v0 exact-boundary verifier
Author: ky46738-ops
A_EQUALS_A=true
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "LKMini.svg",
    "PUBLIC_PRIVATE_BOUNDARY.md",
    "SHA256SUMS",
    ".github/workflows/gatekeeper.yml",
    "tools/verify_lkmini.py",
}

HASHED_FILES = REQUIRED_FILES - {"SHA256SUMS"}

PRIVATE_MARKERS = {
    "PRIVATE_ENGINE",
    "ENGINE_REGISTRY_PRIVATE",
}

# 邊界說明必須能描述被禁止項目；驗證器也必須能定義待掃描標記。
ALLOWED_MARKERS_BY_FILE = {
    "PUBLIC_PRIVATE_BOUNDARY.md": PRIVATE_MARKERS,
    "tools/verify_lkmini.py": PRIVATE_MARKERS,
}


def relative_files() -> set[str]:
    found: set[str] = set()
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        root_path = Path(root)
        for filename in sorted(files):
            path = root_path / filename
            found.add(path.relative_to(REPO_ROOT).as_posix())
    return found


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_exact_file_set() -> bool:
    found = relative_files()
    missing = sorted(REQUIRED_FILES - found)
    extra = sorted(found - REQUIRED_FILES)
    if missing:
        print(f"FAIL: Missing required files: {missing}")
    if extra:
        print(f"FAIL: Extra files outside public seed boundary: {extra}")
    if missing or extra:
        return False
    print("PASS: Exact eight-file public seed boundary")
    return True


def check_a_equals_a() -> bool:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    if "A_EQUALS_A=true" not in content:
        print("FAIL: A=A marker missing in README.md")
        return False
    print("PASS: A=A marker found")
    return True


def parse_sha256sums() -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw_line in (REPO_ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed SHA256SUMS line: {raw_line!r}")
        expected, rel = parts
        if rel in entries:
            raise ValueError(f"Duplicate SHA256SUMS path: {rel}")
        if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
            raise ValueError(f"Invalid SHA256 value for {rel}")
        entries[rel] = expected
    return entries


def check_sha256sums() -> bool:
    try:
        entries = parse_sha256sums()
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return False

    if set(entries) != HASHED_FILES:
        print(
            "FAIL: SHA256SUMS paths must equal the seven hashed public files; "
            f"expected={sorted(HASHED_FILES)} actual={sorted(entries)}"
        )
        return False

    ok = True
    for rel in sorted(entries):
        actual = sha256_file(REPO_ROOT / rel)
        if actual != entries[rel]:
            print(f"FAIL: {rel} hash mismatch expected={entries[rel]} actual={actual}")
            ok = False
        else:
            print(f"OK: {rel}")
    if ok:
        print("PASS: All seven hashes match")
    return ok


def check_no_private_leak() -> bool:
    ok = True
    for rel in sorted(REQUIRED_FILES):
        path = REPO_ROOT / rel
        if path.suffix.lower() not in {".md", ".json", ".txt", ".py", ".yml", ".yaml"}:
            continue
        content = path.read_text(encoding="utf-8", errors="strict")
        allowed = ALLOWED_MARKERS_BY_FILE.get(rel, set())
        for marker in PRIVATE_MARKERS:
            if marker in content and marker not in allowed:
                print(f"FAIL: Private marker {marker!r} in {rel}")
                ok = False
    if ok:
        print("PASS: No private marker outside the explicit boundary description")
    return ok


def main() -> int:
    results = [
        check_exact_file_set(),
        check_a_equals_a(),
        check_sha256sums(),
        check_no_private_leak(),
    ]
    if all(results):
        print("\nPASS: A=A — exact public seed boundary is locked.")
        return 0
    print("\nFAIL: public seed boundary is not locked.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
