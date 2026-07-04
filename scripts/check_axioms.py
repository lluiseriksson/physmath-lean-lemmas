#!/usr/bin/env python3
"""Portable axiom audit for the public Lean interface."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"


def fail(message: str) -> None:
    print(f"AXIOM CHECK FAILED: {message}", file=sys.stderr)
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


def load_public_declarations(contract: dict[str, object]) -> list[str]:

    declarations = contract.get("public_declarations")
    if not isinstance(declarations, list) or not declarations:
        fail("public_declarations must be a nonempty list")

    names: list[str] = []
    for declaration in declarations:
        if not isinstance(declaration, dict):
            fail("each public declaration must be an object")
        name = declaration.get("name")
        if not isinstance(name, str) or not name:
            fail("each public declaration needs a nonempty name")
        names.append(name)
    return names


def load_allowed_axioms(contract: dict[str, object]) -> set[str]:
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        fail("verification must be an object")
    allowed = verification.get("allowed_axioms")
    if (
        not isinstance(allowed, list)
        or not allowed
        or not all(isinstance(item, str) and item for item in allowed)
    ):
        fail("verification.allowed_axioms must be a nonempty list of strings")
    return set(allowed)


def lean_axiom_query(names: list[str]) -> str:
    lines = ["import PhysmathLemmas", "open PhysmathLemmas"]
    lines.extend(f"#print axioms {name}" for name in names)
    return "\n".join(lines) + "\n"


def parse_axioms(stdout: str, names: list[str]) -> dict[str, set[str]]:
    expected = {f"PhysmathLemmas.{name}" for name in names}
    found: dict[str, set[str]] = {}
    depends_pattern = re.compile(r"^'([^']+)' depends on axioms: \[(.*)\]$")
    none_pattern = re.compile(r"^'([^']+)' does not depend on any axioms$")

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        depends_match = depends_pattern.match(line)
        if depends_match:
            full_name, axiom_text = depends_match.groups()
            axioms = {
                item.strip()
                for item in axiom_text.split(",")
                if item.strip()
            }
        else:
            none_match = none_pattern.match(line)
            if not none_match:
                continue
            full_name = none_match.group(1)
            axioms = set()

        if full_name in expected:
            found[full_name] = axioms

    missing = sorted(expected - found.keys())
    if missing:
        fail("missing axiom output for " + ", ".join(missing))
    return found


def main() -> None:
    contract = load_contract()
    names = load_public_declarations(contract)
    allowed_axioms = load_allowed_axioms(contract)
    query = lean_axiom_query(names)
    result = subprocess.run(
        ["lake", "env", "lean", "--stdin"],
        cwd=ROOT,
        input=query,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        fail(f"lean axiom query exited with status {result.returncode}")

    observed = parse_axioms(result.stdout, names)
    unexpected: list[str] = []
    for full_name, axioms in observed.items():
        extra = axioms - allowed_axioms
        if extra:
            unexpected.append(f"{full_name}: {', '.join(sorted(extra))}")

    if unexpected:
        fail("unexpected axioms detected: " + "; ".join(unexpected))

    allowed = " / ".join(sorted(allowed_axioms))
    print(f"AXIOM CHECK OK: only {allowed}")


if __name__ == "__main__":
    main()
