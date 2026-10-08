#!/usr/bin/env python3
"""Read-only public filesystem preflight; no grading or publication policy."""

import argparse
import os
from pathlib import Path
import stat


def regular_tree(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"not a regular submission directory: {root}")
    for current, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError(f"nonregular entry: {path.relative_to(root)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--submission", default="/home/submission")
    args = parser.parse_args()
    try:
        regular_tree(args.submission)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Filesystem preflight failed: {error}\n")
    print("Source filesystem preflight passed; execution and source-mutation checks still require clean replay.")


if __name__ == "__main__":
    main()
