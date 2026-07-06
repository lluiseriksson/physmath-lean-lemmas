#!/usr/bin/env python3
"""Reject forbidden Lean proof tokens in proof-bearing Lean files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"
STATIC_TARGETS = [ROOT / "PhysmathLemmas", ROOT / "test"]


def fail(message: str) -> None:
    print(f"FORBIDDEN TOKEN CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_contract() -> dict[str, object]:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required file: {CONTRACT_PATH.relative_to(ROOT)}")
    except json.JSONDecodeError as err:
        fail(f"{CONTRACT_PATH.relative_to(ROOT)} is not valid JSON: {err}")
    if not isinstance(contract, dict):
        fail(f"{CONTRACT_PATH.relative_to(ROOT)} root must be an object")
    return contract


def expect_string(contract: dict[str, object], key: str) -> str:
    value = contract.get(key)
    if not isinstance(value, str) or not value:
        fail(f"contract field {key!r} must be a nonempty string")
    return value


def forbidden_tokens(contract: dict[str, object]) -> list[str]:
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


def scan_targets(contract: dict[str, object]) -> list[Path]:
    source_file = ROOT / expect_string(contract, "source_file")
    import_file = ROOT / f"{expect_string(contract, 'import').replace('.', '/')}.lean"
    for path in (source_file, import_file):
        if not path.is_file():
            fail(f"contract Lean target does not exist: {path.relative_to(ROOT)}")
    return [source_file, import_file, *STATIC_TARGETS]


def lean_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".lean" else []
    if path.is_dir():
        return sorted(path.rglob("*.lean"))
    return []


def main() -> None:
    contract = load_contract()
    token_pattern = "|".join(re.escape(token) for token in forbidden_tokens(contract))
    pattern = re.compile(rf"(?<![A-Za-z0-9_'])({token_pattern})(?![A-Za-z0-9_'])")
    hits: list[str] = []
    seen_paths: set[Path] = set()
    for target in scan_targets(contract):
        for path in lean_files(target):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            rel = path.relative_to(ROOT)
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in pattern.finditer(line):
                    hits.append(f"{rel}:{lineno}:{match.start() + 1}: {line.strip()}")

    if hits:
        print("FORBIDDEN TOKEN DETECTED", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        raise SystemExit(1)

    print("FORBIDDEN TOKEN CHECK OK")


if __name__ == "__main__":
    main()
