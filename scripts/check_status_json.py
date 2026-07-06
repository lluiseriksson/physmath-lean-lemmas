#!/usr/bin/env python3
"""Check that STATUS.json is a usable consumer heartbeat."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "STATUS.json"
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"
DIGEST_PATH = ROOT / "docs" / "mother-interface-digest.md"
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ci.yml"
EXPECTED_SCOPE_MARKERS = (
    "bookkeeping/interface",
    "no source-estimate",
    "continuum",
    "mass-gap",
    "reconstruction",
    "Clay-adjacent",
)


def fail(message: str) -> None:
    print(f"STATUS JSON CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as err:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {err}")


def expect_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def expect_string(mapping: dict[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        fail(f"{key!r} must be a nonempty string")
    return value


def expect_string_list(mapping: dict[str, object], key: str) -> list[str]:
    value = mapping.get(key)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        fail(f"{key!r} must be a nonempty list of strings")
    return value


def expect_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        fail(f"{label} drift: status={actual!r}, expected={expected!r}")


def expect_sha256_hex(value: str, label: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        fail(f"{label} must be a lowercase sha256 hex digest")


def main() -> None:
    status = expect_object(load_json(STATUS_PATH), "STATUS.json")
    contract = expect_object(load_json(CONTRACT_PATH), "docs/interface-contract.json")

    if expect_string(status, "schema") != "physmath-lean-lemmas.status.v1":
        fail("unexpected STATUS schema")
    if expect_string(status, "status") != "green":
        fail("STATUS status must be 'green'")
    scope = expect_string(status, "scope")
    for marker in EXPECTED_SCOPE_MARKERS:
        if marker not in scope:
            fail(f"scope is missing required disclaimer marker: {marker}")

    for key in (
        "satellite",
        "node",
        "repository",
        "source_file",
        "lean_toolchain",
        "mathlib_rev",
        "mathlib_manifest_rev",
        "consumption_rule",
    ):
        expect_equal(status.get(key), expect_string(contract, key), key)
    expect_equal(
        expect_string(contract, "status_file"),
        str(STATUS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "contract.status_file",
    )

    source_file = ROOT / expect_string(status, "source_file")
    source_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()
    expect_equal(status.get("source_file_sha256"), source_hash, "source_file_sha256")
    release_zip_sha256 = expect_string(status, "release_zip_sha256")
    expect_sha256_hex(release_zip_sha256, "release_zip_sha256")
    expect_equal(
        release_zip_sha256,
        expect_string(contract, "release_zip_sha256"),
        "release_zip_sha256",
    )

    digest_path = ROOT / expect_string(status, "mother_interface_digest")
    if not digest_path.is_file():
        fail(f"mother_interface_digest does not exist: {digest_path.relative_to(ROOT)}")
    expect_equal(
        status.get("mother_interface_digest"),
        str(DIGEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        "mother_interface_digest",
    )
    expect_equal(
        status.get("interface_contract"),
        str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "interface_contract",
    )

    qualified_declarations: list[str] = []
    declarations = contract.get("public_declarations")
    if not isinstance(declarations, list) or not declarations:
        fail("contract public_declarations must be a nonempty list")
    namespace = expect_string(contract, "namespace")
    for declaration in declarations:
        declaration_obj = expect_object(declaration, "public declaration")
        name = expect_string(declaration_obj, "name")
        qualified_declarations.append(f"{namespace}.{name}")
    expect_equal(
        status.get("public_declarations"),
        qualified_declarations,
        "public_declarations",
    )

    verification = expect_object(status.get("verification"), "verification")
    expect_equal(
        verification.get("ci_workflow"),
        str(CI_WORKFLOW_PATH.relative_to(ROOT)).replace("\\", "/"),
        "verification.ci_workflow",
    )
    ci_workflow = read_text(CI_WORKFLOW_PATH)
    for command in expect_string_list(verification, "commands"):
        if command not in ci_workflow:
            fail(f"CI workflow is missing verification command: {command}")

    contract_verification = expect_object(contract.get("verification"), "contract verification")
    for key in ("commands", "allowed_axioms", "forbidden_tokens"):
        expect_equal(
            verification.get(key),
            expect_string_list(contract_verification, key),
            f"verification.{key}",
        )

    print("STATUS JSON CHECK OK")


if __name__ == "__main__":
    main()
