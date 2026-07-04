#!/usr/bin/env python3
"""Check that the mother-facing interface contract matches this checkout."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"


def fail(message: str) -> None:
    print(f"INTERFACE CONTRACT CHECK FAILED: {message}", file=sys.stderr)
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


def expect_string(mapping: dict[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        fail(f"contract field {key!r} must be a nonempty string")
    return value


def mathlib_input_rev() -> str:
    manifest = load_json(ROOT / "lake-manifest.json")
    if not isinstance(manifest, dict):
        fail("lake-manifest.json root must be an object")
    packages = manifest.get("packages")
    if not isinstance(packages, list):
        fail("lake-manifest.json must contain a packages list")
    for package in packages:
        if isinstance(package, dict) and package.get("name") == "mathlib":
            input_rev = package.get("inputRev")
            if isinstance(input_rev, str) and input_rev:
                return input_rev
            fail("mathlib package is missing inputRev")
    fail("lake-manifest.json does not contain a mathlib package")


def lakefile_mathlib_rev() -> str:
    lakefile = read_text(ROOT / "lakefile.toml")
    match = re.search(r'(?m)^\s*rev\s*=\s*"([^"]+)"\s*$', lakefile)
    if not match:
        fail("lakefile.toml is missing a mathlib rev entry")
    return match.group(1)


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    if not isinstance(contract, dict):
        fail("docs/interface-contract.json root must be an object")

    if expect_string(contract, "schema") != "physmath-lean-lemmas.interface.v1":
        fail("unexpected schema")

    source_file = ROOT / expect_string(contract, "source_file")
    source_text = read_text(source_file)
    source_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()
    if expect_string(contract, "source_file_sha256") != source_hash:
        fail(
            "source_file_sha256 does not match "
            f"{source_file.relative_to(ROOT)} ({source_hash})"
        )

    toolchain = read_text(ROOT / "lean-toolchain").strip()
    if expect_string(contract, "lean_toolchain") != toolchain:
        fail(f"lean_toolchain does not match lean-toolchain ({toolchain})")

    mathlib_rev = expect_string(contract, "mathlib_rev")
    manifest_rev = mathlib_input_rev()
    lake_rev = lakefile_mathlib_rev()
    if mathlib_rev != manifest_rev or mathlib_rev != lake_rev:
        fail(
            "mathlib_rev drift: "
            f"contract={mathlib_rev}, manifest={manifest_rev}, lakefile={lake_rev}"
        )

    declarations = contract.get("public_declarations")
    if not isinstance(declarations, list) or not declarations:
        fail("public_declarations must be a nonempty list")
    for declaration in declarations:
        if not isinstance(declaration, dict):
            fail("each public declaration must be an object")
        name = expect_string(declaration, "name")
        if not re.search(rf"\btheorem\s+{re.escape(name)}\b", source_text):
            fail(f"public declaration {name!r} is not a theorem in {source_file.name}")

    print("INTERFACE CONTRACT CHECK OK")


if __name__ == "__main__":
    main()
