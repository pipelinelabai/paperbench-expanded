"""Freeze original inputs without mistaking newly generated files for mutations."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat


GENERATED_ROOTS = {"config", "geometry", "results", "views", "report.md", "replay_receipt.json"}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else hashlib.sha256(stream.read()).hexdigest()


def safe_file(root, relative):
    parsed = PurePosixPath(relative)
    if not relative or parsed.is_absolute() or ".." in parsed.parts or str(parsed) != relative:
        raise ValueError("Invalid frozen input path")
    current = root
    for component in parsed.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("Frozen input traverses a symlink")
    if not current.is_file() or not stat.S_ISREG(current.stat().st_mode):
        raise ValueError("Frozen input missing or nonregular")
    return current


def inventory_path(source, inventory):
    source, inventory = Path(source).resolve(), Path(inventory)
    if inventory.is_symlink() or inventory.resolve().is_relative_to(source):
        raise ValueError("Frozen inventory must be outside the submission")
    return source, inventory


def freeze(source, inventory):
    source, inventory = inventory_path(source, inventory)
    inputs = {}
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if relative.parts[0] in GENERATED_ROOTS or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError("Source inputs cannot contain symlinks")
        if path.is_dir():
            continue
        inputs[relative.as_posix()] = digest(safe_file(source, relative.as_posix()))
    if "reproduce.sh" not in inputs:
        raise ValueError("A regular no-argument replay entry point is required")
    descriptor = os.open(inventory, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump({"schema_version": 1, "inputs": inputs}, stream, sort_keys=True, indent=2)
        stream.write("\n")
    return inputs


def fingerprint(source, inventory):
    source, inventory = inventory_path(source, inventory)
    metadata = inventory.stat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid() or metadata.st_mode & 0o077:
        raise ValueError("Frozen inventory must be private to the trusted runner")
    if metadata.st_size > 2 * 1024 * 1024:
        raise ValueError("Frozen inventory exceeds the size limit")
    document = json.loads(inventory.read_text())
    inputs = document.get("inputs")
    if document.get("schema_version") != 1 or not isinstance(inputs, dict) or "reproduce.sh" not in inputs:
        raise ValueError("Invalid frozen input inventory")
    return {relative: digest(safe_file(source, relative)) for relative in sorted(inputs)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("freeze", "fingerprint"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    args = parser.parse_args()
    result = (freeze if args.operation == "freeze" else fingerprint)(args.source, args.inventory)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
