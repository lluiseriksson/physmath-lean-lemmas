#!/usr/bin/env python3
"""Reject forbidden Lean proof tokens in public source files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "PhysmathLemmas", ROOT / "PhysmathLemmas.lean"]
PATTERN = re.compile(r"sorry|admit|native_decide")


def lean_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".lean" else []
    if path.is_dir():
        return sorted(path.rglob("*.lean"))
    return []


def main() -> None:
    hits: list[str] = []
    for target in TARGETS:
        for path in lean_files(target):
            rel = path.relative_to(ROOT)
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if PATTERN.search(line):
                    hits.append(f"{rel}:{lineno}: {line.strip()}")

    if hits:
        print("FORBIDDEN TOKEN DETECTED", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        raise SystemExit(1)

    print("FORBIDDEN TOKEN CHECK OK")


if __name__ == "__main__":
    main()
