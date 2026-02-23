#!/usr/bin/env python3
"""Lightweight helper to surface common technical debt signals in a codebase."""

import argparse
import ast
import os
from pathlib import Path
from typing import Dict, Iterable, List


DebtReport = Dict[str, List[str]]


def iter_files(root: Path) -> Iterable[Path]:
    """Yield files under root, skipping .git directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            yield Path(dirpath, name)


def find_todos(files: Iterable[Path]) -> List[str]:
    findings: List[str] = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    if "TODO" in line or "FIXME" in line:
                        snippet = line.rstrip()
                        findings.append(f"{path}:{idx}: {snippet}")
        except (OSError, UnicodeDecodeError):
            continue
    return findings


def missing_module_docstrings(files: Iterable[Path]) -> List[str]:
    findings: List[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        try:
            module = ast.parse(source)
        except SyntaxError as exc:
            findings.append(f"{path}: unable to parse ({exc.msg})")
            continue
        if ast.get_docstring(module, clean=False) is None:
            findings.append(f"{path}: missing module docstring")
    return findings


def find_unpinned_requirements(files: Iterable[Path]) -> List[str]:
    findings: List[str] = []
    for path in files:
        if path.name != "requirements.txt":
            continue
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if stripped.startswith(("-", "--", "git+", "https://", "http://")):
                        continue
                    if "==" not in stripped:
                        findings.append(f"{path}:{idx}: {stripped or '<blank line>'}")
        except OSError:
            continue
    return findings


def build_report(root: Path) -> DebtReport:
    all_files = list(iter_files(root))
    return {
        "TODO/FIXME": find_todos(all_files),
        "Missing module docstrings": missing_module_docstrings(all_files),
        "Unpinned requirements": find_unpinned_requirements(all_files),
    }


def print_report(report: DebtReport) -> None:
    for title, items in report.items():
        print(f"== {title} ==")
        if not items:
            print("None found.\n")
            continue
        for item in items:
            print(f"- {item}")
        print()


def parse_args() -> Path:
    parser = argparse.ArgumentParser(
        description="Scan a directory for common technical debt markers."
    )
    parser.add_argument(
        "path", metavar="PATH", type=str, help="Root directory to scan recursively."
    )
    args = parser.parse_args()
    return Path(args.path).resolve()


def main() -> None:
    root = parse_args()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Path does not exist or is not a directory: {root}")

    report = build_report(root)
    print_report(report)


if __name__ == "__main__":
    main()
