#!/usr/bin/env python3
"""Reject forbidden Lean proof tokens in public source files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"
TARGETS = [ROOT / "PhysmathLemmas", ROOT / "PhysmathLemmas.lean"]


def fail(message: str) -> None:
    print(f"FORBIDDEN TOKEN CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def forbidden_tokens() -> list[str]:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required file: {CONTRACT_PATH.relative_to(ROOT)}")
    except json.JSONDecodeError as err:
        fail(f"{CONTRACT_PATH.relative_to(ROOT)} is not valid JSON: {err}")
    if not isinstance(contract, dict):
        fail(f"{CONTRACT_PATH.relative_to(ROOT)} root must be an object")
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        fail("verification must be an object")
    tokens = verification.get("forbidden_tokens")
    if (
        not isinstance(tokens, list)
        or not tokens
        or not all(isinstance(item, str) and item for item in tokens)
    ):
        fail("verification.forbidden_tokens must be a nonempty list of strings")
    return tokens


def lean_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".lean" else []
    if path.is_dir():
        return sorted(path.rglob("*.lean"))
    return []


def main() -> None:
    pattern = re.compile("|".join(re.escape(token) for token in forbidden_tokens()))
    hits: list[str] = []
    for target in TARGETS:
        for path in lean_files(target):
            rel = path.relative_to(ROOT)
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    hits.append(f"{rel}:{lineno}: {line.strip()}")

    if hits:
        print("FORBIDDEN TOKEN DETECTED", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        raise SystemExit(1)

    print("FORBIDDEN TOKEN CHECK OK")


if __name__ == "__main__":
    main()
