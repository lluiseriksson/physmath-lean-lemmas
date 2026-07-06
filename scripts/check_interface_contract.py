#!/usr/bin/env python3
"""Check that the mother-facing interface contract matches this checkout."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "interface-contract.json"
DIGEST_PATH = ROOT / "docs" / "mother-interface-digest.md"
README_PATH = ROOT / "README.md"
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ci.yml"
INTERFACE_SMOKE_PATH = ROOT / "test" / "InterfaceSmoke.lean"
DIRECT_SOURCE_SMOKE_PATH = ROOT / "test" / "DirectSourceImportSmoke.lean"
EXPECTED_DIGEST_SCOPE_MARKERS = (
    "bookkeeping/interface",
    "source estimate",
    "continuum",
    "mass gap",
    "reconstruction",
    "Clay-adjacent",
)


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


def expect_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        fail(f"{label} drift: status={actual!r}, expected={expected!r}")


def expect_sha256_hex(value: str, label: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        fail(f"{label} must be a lowercase sha256 hex digest")


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


def mathlib_manifest_rev() -> str:
    manifest = load_json(ROOT / "lake-manifest.json")
    if not isinstance(manifest, dict):
        fail("lake-manifest.json root must be an object")
    packages = manifest.get("packages")
    if not isinstance(packages, list):
        fail("lake-manifest.json must contain a packages list")
    for package in packages:
        if isinstance(package, dict) and package.get("name") == "mathlib":
            rev = package.get("rev")
            if isinstance(rev, str) and rev:
                return rev
            fail("mathlib package is missing rev")
    fail("lake-manifest.json does not contain a mathlib package")


def lakefile_mathlib_rev() -> str:
    lakefile = read_text(ROOT / "lakefile.toml")
    match = re.search(r'(?m)^\s*rev\s*=\s*"([^"]+)"\s*$', lakefile)
    if not match:
        fail("lakefile.toml is missing a mathlib rev entry")
    return match.group(1)


def lakefile_direct_requirements() -> list[dict[str, str]]:
    try:
        lakefile = tomllib.loads(read_text(ROOT / "lakefile.toml"))
    except tomllib.TOMLDecodeError as err:
        fail(f"lakefile.toml is not valid TOML: {err}")

    requirements = lakefile.get("require")
    if requirements is None:
        return []
    if not isinstance(requirements, list):
        fail("lakefile.toml require entries must be a list")

    normalized: list[dict[str, str]] = []
    for requirement in requirements:
        if not isinstance(requirement, dict):
            fail("each lakefile.toml require entry must be an object")
        item: dict[str, str] = {}
        for key in ("name", "scope", "rev"):
            value = requirement.get(key)
            if not isinstance(value, str) or not value:
                fail(f"each lakefile.toml require entry needs a nonempty {key}")
            item[key] = value
        normalized.append(item)
    return normalized


def expect_digest_anchor(digest: str, label: str, needle: str) -> None:
    if needle not in digest:
        fail(f"mother-interface-digest.md is missing {label}: {needle}")


def digest_fully_qualified_api_names(digest: str) -> list[str]:
    match = re.search(
        r"(?ms)^Fully qualified public API names:\n\n"
        r"(?P<items>(?:- `[^`\n]+`\n)+)",
        digest,
    )
    if not match:
        fail("mother-interface-digest.md is missing the fully qualified API list")
    return re.findall(r"(?m)^- `([^`\n]+)`$", match.group("items"))


def readme_public_declaration_names(readme: str) -> list[str]:
    match = re.search(
        r"(?ms)^\| declaration \| content \|\n"
        r"\|---\|---\|\n"
        r"(?P<rows>(?:\| `[^`\n]+` \| [^\n]*\|\n)+)",
        readme,
    )
    if not match:
        fail("README.md is missing the public declaration table")
    return re.findall(r"(?m)^\| `([^`\n]+)` \|", match.group("rows"))


def digest_verification_commands(digest: str) -> list[str]:
    match = re.search(
        r"(?ms)^## Verification Gate\n.*?```bash\n(?P<commands>.*?)\n```",
        digest,
    )
    if not match:
        fail("mother-interface-digest.md is missing the verification command block")
    return [
        line.strip()
        for line in match.group("commands").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def ci_run_commands(ci_workflow: str) -> list[str]:
    commands: list[str] = []
    lines = ci_workflow.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^(?P<indent>\s*)run:\s*(?P<value>.*)$", line)
        if not match:
            index += 1
            continue

        value = match.group("value").strip()
        if value and value not in {"|", ">"}:
            commands.append(value)
            index += 1
            continue

        block_indent = len(match.group("indent")) + 2
        index += 1
        while index < len(lines):
            block_line = lines[index]
            actual_indent = len(block_line) - len(block_line.lstrip())
            if block_line.strip() and actual_indent < block_indent:
                break
            stripped = block_line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
            index += 1
    return commands


def lean_module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def source_imports(source_text: str) -> list[str]:
    return re.findall(r"(?m)^\s*import\s+([A-Za-z0-9_'.]+)\s*$", source_text)


def significant_lean_lines(source_text: str) -> list[str]:
    return [
        line.strip()
        for line in source_text.splitlines()
        if line.strip() and not line.strip().startswith("--")
    ]


def source_theorem_names(source_text: str) -> list[str]:
    return re.findall(r"(?m)^\s*theorem\s+([A-Za-z_][A-Za-z0-9_']*)\b", source_text)


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    if not isinstance(contract, dict):
        fail("docs/interface-contract.json root must be an object")

    if expect_string(contract, "schema") != "physmath-lean-lemmas.interface.v1":
        fail("unexpected schema")

    status_path = ROOT / expect_string(contract, "status_file")
    status = load_json(status_path)
    if not isinstance(status, dict):
        fail(f"{status_path.relative_to(ROOT)} root must be an object")
    if expect_string(status, "schema") != "physmath-lean-lemmas.status.v1":
        fail("unexpected status schema")

    source_file = ROOT / expect_string(contract, "source_file")
    source_text = read_text(source_file)
    source_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()
    if expect_string(contract, "source_file_sha256") != source_hash:
        fail(
            "source_file_sha256 does not match "
            f"{source_file.relative_to(ROOT)} ({source_hash})"
        )
    expect_equal(status.get("source_file_sha256"), source_hash, "STATUS source_file_sha256")
    release_zip_sha256 = expect_string(contract, "release_zip_sha256")
    expect_sha256_hex(release_zip_sha256, "release_zip_sha256")
    expect_equal(
        status.get("release_zip_sha256"),
        release_zip_sha256,
        "STATUS release_zip_sha256",
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
    expected_public_import = [f"import {source_module}"]
    actual_public_import = significant_lean_lines(import_text)
    if actual_public_import != expected_public_import:
        fail(
            f"{import_file.relative_to(ROOT)} must be a minimal public re-export: "
            f"expected={expected_public_import}, actual={actual_public_import}"
        )
    interface_smoke = read_text(INTERFACE_SMOKE_PATH)
    direct_source_smoke = read_text(DIRECT_SOURCE_SMOKE_PATH)
    if not re.search(rf"(?m)^\s*import\s+{re.escape(import_module)}\s*$", interface_smoke):
        fail(
            f"{INTERFACE_SMOKE_PATH.relative_to(ROOT)} must smoke-test "
            f"the public import {import_module!r}"
        )
    if not re.search(
        rf"(?m)^\s*import\s+{re.escape(source_module)}\s*$", direct_source_smoke
    ):
        fail(
            f"{DIRECT_SOURCE_SMOKE_PATH.relative_to(ROOT)} must smoke-test "
            f"the direct source import {source_module!r}"
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
    expect_equal(status.get("lean_toolchain"), toolchain, "STATUS lean_toolchain")

    mathlib_rev = expect_string(contract, "mathlib_rev")
    manifest_rev = mathlib_input_rev()
    lake_rev = lakefile_mathlib_rev()
    if mathlib_rev != manifest_rev or mathlib_rev != lake_rev:
        fail(
            "mathlib_rev drift: "
            f"contract={mathlib_rev}, manifest={manifest_rev}, lakefile={lake_rev}"
        )
    expect_equal(status.get("mathlib_rev"), mathlib_rev, "STATUS mathlib_rev")
    mathlib_package_rev = mathlib_manifest_rev()
    if expect_string(contract, "mathlib_manifest_rev") != mathlib_package_rev:
        fail(
            "mathlib_manifest_rev drift: "
            f"contract={expect_string(contract, 'mathlib_manifest_rev')}, "
            f"manifest={mathlib_package_rev}"
        )
    expect_equal(
        status.get("mathlib_manifest_rev"),
        mathlib_package_rev,
        "STATUS mathlib_manifest_rev",
    )

    direct_lake_requirements = contract.get("direct_lake_requirements")
    if not isinstance(direct_lake_requirements, list):
        fail("direct_lake_requirements must be a list")
    expected_requirements: list[dict[str, str]] = []
    for requirement in direct_lake_requirements:
        if not isinstance(requirement, dict):
            fail("each direct_lake_requirements entry must be an object")
        expected_requirements.append(
            {
                "name": expect_string(requirement, "name"),
                "scope": expect_string(requirement, "scope"),
                "rev": expect_string(requirement, "rev"),
            }
        )
    actual_requirements = lakefile_direct_requirements()
    if expected_requirements != actual_requirements:
        fail(
            "direct Lake requirements drift: "
            f"contract={expected_requirements}, lakefile={actual_requirements}"
        )

    for key in (
        "satellite",
        "node",
        "repository",
        "source_file",
        "consumption_rule",
    ):
        expect_equal(status.get(key), expect_string(contract, key), f"STATUS {key}")
    expect_equal(
        status.get("interface_contract"),
        str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "STATUS interface_contract",
    )
    expect_equal(
        status.get("mother_interface_digest"),
        str(DIGEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        "STATUS mother_interface_digest",
    )
    if expect_string(status, "status") != "green":
        fail("STATUS status must be 'green'")
    expect_string(status, "scope")

    digest = read_text(DIGEST_PATH)
    readme = read_text(README_PATH)
    ci_workflow = read_text(CI_WORKFLOW_PATH)
    for marker in EXPECTED_DIGEST_SCOPE_MARKERS:
        if marker not in digest:
            fail(f"mother-interface-digest.md is missing scope marker: {marker}")
    expect_digest_anchor(
        digest, "satellite", f"Satellite: `{expect_string(contract, 'satellite')}`"
    )
    expect_digest_anchor(digest, "node", f"Node: `{expect_string(contract, 'node')}`")
    expect_digest_anchor(digest, "repository", expect_string(contract, "repository"))
    expect_digest_anchor(digest, "source file", expect_string(contract, "source_file"))
    expect_digest_anchor(digest, "top-level import", f"import {import_module}")
    expect_digest_anchor(digest, "namespace", f"namespace {namespace}")
    expect_digest_anchor(digest, "interface contract path", "docs/interface-contract.json")
    expect_digest_anchor(digest, "status file path", expect_string(contract, "status_file"))
    expect_digest_anchor(digest, "source file sha256", source_hash)
    expect_digest_anchor(digest, "release zip sha256", release_zip_sha256)
    expect_digest_anchor(digest, "source imports field", "source_imports")
    for source_import in declared_imports:
        expect_digest_anchor(digest, f"source import {source_import}", source_import)
    expect_digest_anchor(digest, "direct Lake requirements field", "direct_lake_requirements")
    for requirement in expected_requirements:
        requirement_anchor = (
            f"{requirement['scope']}/{requirement['name']}@{requirement['rev']}"
        )
        expect_digest_anchor(
            digest,
            f"direct Lake requirement {requirement_anchor}",
            requirement_anchor,
        )
    expect_digest_anchor(digest, "Lean toolchain", toolchain)
    expect_digest_anchor(digest, "Mathlib rev", mathlib_rev)
    expect_digest_anchor(digest, "Mathlib manifest rev", mathlib_package_rev)
    expect_digest_anchor(
        digest, "consumption rule", expect_string(contract, "consumption_rule")
    )

    for label, needle in (
        ("source file", expect_string(contract, "source_file")),
        ("interface digest path", "docs/mother-interface-digest.md"),
        ("interface contract path", "docs/interface-contract.json"),
        ("status file path", expect_string(contract, "status_file")),
    ):
        if needle not in readme:
            fail(f"README.md is missing {label}: {needle}")

    verification = expect_object(contract, "verification")
    verification_commands = expect_string_list(verification, "commands")
    expected_digest_commands = ["lake exe cache get", *verification_commands]
    actual_digest_commands = digest_verification_commands(digest)
    if actual_digest_commands != expected_digest_commands:
        fail(
            "mother-interface-digest.md verification command block drift: "
            f"digest={actual_digest_commands}, expected={expected_digest_commands}"
        )
    ci_commands = ci_run_commands(ci_workflow)
    for command in verification_commands:
        expect_digest_anchor(digest, f"verification command {command}", command)
        if command not in ci_commands:
            fail(f"CI workflow is missing verification command: {command}")
    for axiom in expect_string_list(verification, "allowed_axioms"):
        expect_digest_anchor(digest, f"allowed axiom {axiom}", axiom)
    for token in expect_string_list(verification, "forbidden_tokens"):
        expect_digest_anchor(digest, f"forbidden token {token}", token)

    status_verification = expect_object(status, "verification")
    expect_equal(
        status_verification.get("ci_workflow"),
        str(CI_WORKFLOW_PATH.relative_to(ROOT)).replace("\\", "/"),
        "STATUS verification.ci_workflow",
    )
    expect_equal(
        status_verification.get("commands"),
        expect_string_list(verification, "commands"),
        "STATUS verification.commands",
    )
    expect_equal(
        status_verification.get("allowed_axioms"),
        expect_string_list(verification, "allowed_axioms"),
        "STATUS verification.allowed_axioms",
    )
    expect_equal(
        status_verification.get("forbidden_tokens"),
        expect_string_list(verification, "forbidden_tokens"),
        "STATUS verification.forbidden_tokens",
    )

    declarations = contract.get("public_declarations")
    if not isinstance(declarations, list) or not declarations:
        fail("public_declarations must be a nonempty list")
    seen_names: set[str] = set()
    qualified_names: list[str] = []
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
        qualified_names.append(qualified_name)
        if expect_string(declaration, "kind") != "theorem":
            fail(f"public declaration {name!r} must have kind 'theorem'")
        layer = expect_string(declaration, "layer")
        inputs = expect_string_list(declaration, "inputs")
        conclusion = expect_string(declaration, "conclusion")
        if not re.search(rf"\btheorem\s+{re.escape(name)}\b", source_text):
            fail(f"public declaration {name!r} is not a theorem in {source_file.name}")
        expect_digest_anchor(digest, f"public declaration {name}", name)
        expect_digest_anchor(
            digest, f"qualified public declaration {qualified_name}", qualified_name
        )
        expect_digest_anchor(
            digest,
            f"contract summary for {name}",
            f"- `{name}` (`{layer}`)",
        )
        for input_line in inputs:
            expect_digest_anchor(
                digest,
                f"contract input for {name}: {input_line}",
                f"  - input: `{input_line}`",
            )
        expect_digest_anchor(
            digest,
            f"contract conclusion for {name}",
            f"  - conclusion: `{conclusion}`",
        )
        for smoke_path, smoke_text in (
            (INTERFACE_SMOKE_PATH, interface_smoke),
            (DIRECT_SOURCE_SMOKE_PATH, direct_source_smoke),
        ):
            if qualified_name not in smoke_text:
                fail(
                    f"{smoke_path.relative_to(ROOT)} is missing smoke-test anchor "
                    f"for {qualified_name}"
                )
        if name not in readme:
            fail(f"README.md is missing public declaration {name!r}")

    expect_equal(
        status.get("public_declarations"),
        qualified_names,
        "STATUS public_declarations",
    )

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

    readme_theorem_order = readme_public_declaration_names(readme)
    if readme_theorem_order != contract_theorem_order:
        fail(
            "README.md public declaration table drift: "
            f"readme={readme_theorem_order}, contract={contract_theorem_order}"
        )

    source_theorems = set(source_theorem_order)
    missing_from_contract = sorted(source_theorems - seen_names)
    if missing_from_contract:
        fail(
            "source theorem declarations missing from public_declarations: "
            + ", ".join(missing_from_contract)
        )

    digest_api_names = digest_fully_qualified_api_names(digest)
    if digest_api_names != qualified_names:
        fail(
            "mother-interface-digest.md fully qualified API list drift: "
            f"digest={digest_api_names}, contract={qualified_names}"
        )

    print("INTERFACE CONTRACT CHECK OK")


if __name__ == "__main__":
    main()
