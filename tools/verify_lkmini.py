#!/usr/bin/env python3
"""
verify_lkmini.py — LKMini seed_v0 integrity verifier
Author: ky46738-ops
A_EQUALS_A=true
"""
from pathlib import Path
import hashlib
import sys

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "LKMini.svg",
    "PUBLIC_PRIVATE_BOUNDARY.md",
    "SHA256SUMS",
    ".github/workflows/gatekeeper.yml",
    "tools/verify_lkmini.py",
]

PRIVATE_PATH_MARKERS = [
    "🥃永恆核心",
    "🎩大管家",
    "PRIVATE_ENGINE_FLEET",
    "ENGINE_REGISTRY_PRIVATE",
]

CONTENT_SCAN_EXCLUDES = {
    "PUBLIC_PRIVATE_BOUNDARY.md",
    ".github/workflows/gatekeeper.yml",
    "tools/verify_lkmini.py",
}

SECRET_MARKERS = [
    "BEGIN PRIVATE KEY",
    "ghp_",
    "github_pat_",
    "sk-",
]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def repository_files():
    return sorted(
        str(path.as_posix())
        for path in Path(".").rglob("*")
        if path.is_file() and ".git" not in path.parts
    )

def check_required_files():
    actual = repository_files()
    missing = [path for path in REQUIRED_FILES if path not in actual]
    extra = [path for path in actual if path not in REQUIRED_FILES]
    if missing:
        print(f"FAIL: Missing files: {missing}")
    if extra:
        print(f"FAIL: Unexpected public files: {extra}")
    if missing or extra:
        return False
    print("PASS: Exactly eight public seed files exist")
    return True

def check_a_equals_a():
    content = Path("README.md").read_text(encoding="utf-8")
    if "A_EQUALS_A=true" not in content:
        print("FAIL: A=A marker missing")
        return False
    print("PASS: A=A marker found")
    return True

def check_sha256sums():
    ok = True
    for raw_line in Path("SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            print(f"FAIL: Invalid SHA256SUMS line: {raw_line}")
            ok = False
            continue
        expected, path = parts
        if not Path(path).is_file():
            print(f"FAIL: {path} not found")
            ok = False
            continue
        actual = sha256_file(path)
        if actual != expected:
            print(f"FAIL: {path} hash mismatch")
            ok = False
        else:
            print(f"OK: {path}")
    if ok:
        print("PASS: All hashes match")
    return ok

def check_no_private_leak():
    actual = repository_files()
    for path in actual:
        if any(marker in path for marker in PRIVATE_PATH_MARKERS):
            print(f"FAIL: Private path marker found: {path}")
            return False
        if path in CONTENT_SCAN_EXCLUDES:
            continue
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        for marker in PRIVATE_PATH_MARKERS + SECRET_MARKERS:
            if marker in content:
                print(f"FAIL: Prohibited marker found in {path}")
                return False
    print("PASS: Public/private boundary is clean")
    return True

if __name__ == "__main__":
    results = [
        check_required_files(),
        check_a_equals_a(),
        check_sha256sums(),
        check_no_private_leak(),
    ]
    if all(results):
        print("\n✅ A=A — All checks passed. Gate is locked.")
        sys.exit(0)
    print("\n❌ FAIL — Gate is NOT locked.")
    sys.exit(1)
