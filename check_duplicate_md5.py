#!/usr/bin/env python3
"""
Scan a repository for duplicate files by MD5 checksum.

Output format:
3 files of <checksum> found:
1. path/to/file1
2. path/to/file2
3. path/to/file3
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from typing import DefaultDict, Iterable, List, Tuple


DEFAULT_EXCLUDE_DIRS = {".git"}


def iter_files(root: str, exclude_dirs: Iterable[str], follow_symlinks: bool) -> Iterable[str]:
    exclude_set = set(exclude_dirs)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        # Prevent walking into excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_set]

        for name in filenames:
            path = os.path.join(dirpath, name)
            # Skip symlinked files by default to avoid surprises/cycles
            if not follow_symlinks and os.path.islink(path):
                continue
            yield path


def md5sum(path: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def format_rel(path: str, root: str) -> str:
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        # Different drive on Windows, etc.
        rel = path
    return rel.replace(os.sep, "/")


def find_duplicates(root: str, exclude_dirs: Iterable[str], follow_symlinks: bool) -> List[Tuple[str, List[str]]]:
    groups: DefaultDict[str, List[str]] = defaultdict(list)

    for path in iter_files(root=root, exclude_dirs=exclude_dirs, follow_symlinks=follow_symlinks):
        try:
            digest = md5sum(path)
        except (OSError, PermissionError):
            # Unreadable file; skip rather than fail the whole run
            continue
        groups[digest].append(path)

    duplicates: List[Tuple[str, List[str]]] = []
    for digest, paths in groups.items():
        if len(paths) > 1:
            duplicates.append((digest, sorted(paths)))

    duplicates.sort(key=lambda x: x[0])  # stable, deterministic output
    return duplicates


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check MD5 checksums of all files in a repo and report duplicates."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude (can be used multiple times). Default excludes: .git",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symlinks (directories and files). Off by default.",
    )
    args = parser.parse_args(argv)

    root = os.path.abspath(args.path)
    exclude_dirs = DEFAULT_EXCLUDE_DIRS | set(args.exclude_dir)

    duplicates = find_duplicates(root=root, exclude_dirs=exclude_dirs, follow_symlinks=args.follow_symlinks)

    if not duplicates:
        return 0

    for digest, paths in duplicates:
        rel_paths = [format_rel(p, root=root) for p in paths]
        print(f"{len(rel_paths)} files of {digest} found:")
        for i, p in enumerate(rel_paths, start=1):
            print(f"{i}. {p}")
        print()

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

