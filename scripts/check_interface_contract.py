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
DIGEST_PATH = ROOT / "docs" / "mother-interface-digest.md"
README_PATH = ROOT / "README.md"


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


def expect_string_list(mapping: dict[str, object], key: str) -> list[str]:
    value = mapping.get(key)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        fail(f"contract field {key!r} must be a nonempty list of strings")
    return value


def expect_object(mapping: dict[str, object], key: str) -> dict[str, object]:
    value = mapping.get(key)
    if not isinstance(value, dict):
        fail(f"contract field {key!r} must be an object")
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


def expect_digest_anchor(digest: str, label: str, needle: str) -> None:
    if needle not in digest:
        fail(f"mother-interface-digest.md is missing {label}: {needle}")


def lean_module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def source_imports(source_text: str) -> list[str]:
    return re.findall(r"(?m)^\s*import\s+([A-Za-z0-9_'.]+)\s*$", source_text)


def source_theorem_names(source_text: str) -> list[str]:
    return re.findall(r"(?m)^\s*theorem\s+([A-Za-z_][A-Za-z0-9_']*)\b", source_text)


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

    import_module = expect_string(contract, "import")
    import_file = ROOT / f"{import_module.replace('.', '/')}.lean"
    import_text = read_text(import_file)
    source_module = lean_module_name(source_file)
    if not re.search(rf"(?m)^\s*import\s+{re.escape(source_module)}\s*$", import_text):
        fail(
            f"contract import {import_module!r} does not re-export "
            f"{source_module!r}"
        )

    namespace = expect_string(contract, "namespace")
    if not re.search(rf"(?m)^\s*namespace\s+{re.escape(namespace)}\s*$", source_text):
        fail(f"source file is missing namespace {namespace!r}")

    declared_imports = expect_string_list(contract, "source_imports")
    actual_imports = source_imports(source_text)
    if declared_imports != actual_imports:
        fail(
            "source_imports drift: "
            f"contract={declared_imports}, source={actual_imports}"
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

    digest = read_text(DIGEST_PATH)
    readme = read_text(README_PATH)
    expect_digest_anchor(
        digest, "satellite", f"Satellite: `{expect_string(contract, 'satellite')}`"
    )
    expect_digest_anchor(digest, "node", f"Node: `{expect_string(contract, 'node')}`")
    expect_digest_anchor(digest, "repository", expect_string(contract, "repository"))
    expect_digest_anchor(digest, "source file", expect_string(contract, "source_file"))
    expect_digest_anchor(digest, "top-level import", f"import {import_module}")
    expect_digest_anchor(digest, "namespace", f"namespace {namespace}")
    expect_digest_anchor(digest, "interface contract path", "docs/interface-contract.json")
    expect_digest_anchor(digest, "source file sha256", source_hash)
    expect_digest_anchor(digest, "source imports field", "source_imports")
    for source_import in declared_imports:
        expect_digest_anchor(digest, f"source import {source_import}", source_import)
    expect_digest_anchor(digest, "Lean toolchain", toolchain)
    expect_digest_anchor(digest, "Mathlib rev", mathlib_rev)
    expect_digest_anchor(
        digest, "consumption rule", expect_string(contract, "consumption_rule")
    )

    for label, needle in (
        ("source file", expect_string(contract, "source_file")),
        ("interface digest path", "docs/mother-interface-digest.md"),
        ("interface contract path", "docs/interface-contract.json"),
    ):
        if needle not in readme:
            fail(f"README.md is missing {label}: {needle}")

    verification = expect_object(contract, "verification")
    for command in expect_string_list(verification, "commands"):
        expect_digest_anchor(digest, f"verification command {command}", command)
    for axiom in expect_string_list(verification, "allowed_axioms"):
        expect_digest_anchor(digest, f"allowed axiom {axiom}", axiom)
    for token in expect_string_list(verification, "forbidden_tokens"):
        expect_digest_anchor(digest, f"forbidden token {token}", token)

    declarations = contract.get("public_declarations")
    if not isinstance(declarations, list) or not declarations:
        fail("public_declarations must be a nonempty list")
    seen_names: set[str] = set()
    for declaration in declarations:
        if not isinstance(declaration, dict):
            fail("each public declaration must be an object")
        name = expect_string(declaration, "name")
        if name in seen_names:
            fail(f"duplicate public declaration {name!r}")
        seen_names.add(name)
        qualified_name = expect_string(declaration, "qualified_name")
        expected_qualified_name = f"{namespace}.{name}"
        if qualified_name != expected_qualified_name:
            fail(
                f"public declaration {name!r} has qualified_name "
                f"{qualified_name!r}, expected {expected_qualified_name!r}"
            )
        if expect_string(declaration, "kind") != "theorem":
            fail(f"public declaration {name!r} must have kind 'theorem'")
        expect_string(declaration, "layer")
        expect_string_list(declaration, "inputs")
        expect_string(declaration, "conclusion")
        if not re.search(rf"\btheorem\s+{re.escape(name)}\b", source_text):
            fail(f"public declaration {name!r} is not a theorem in {source_file.name}")
        expect_digest_anchor(digest, f"public declaration {name}", name)
        expect_digest_anchor(
            digest, f"qualified public declaration {qualified_name}", qualified_name
        )
        if name not in readme:
            fail(f"README.md is missing public declaration {name!r}")

    source_theorem_order = source_theorem_names(source_text)
    contract_theorem_order = [
        declaration["name"]
        for declaration in declarations
        if isinstance(declaration, dict)
    ]
    if contract_theorem_order != source_theorem_order:
        fail(
            "public_declarations order drift: "
            f"contract={contract_theorem_order}, source={source_theorem_order}"
        )

    source_theorems = set(source_theorem_order)
    missing_from_contract = sorted(source_theorems - seen_names)
    if missing_from_contract:
        fail(
            "source theorem declarations missing from public_declarations: "
            + ", ".join(missing_from_contract)
        )

    print("INTERFACE CONTRACT CHECK OK")


if __name__ == "__main__":
    main()
