#!/usr/bin/env python3
"""Public, read-only artifact preflight. Does not run candidate code or HFSS."""

import argparse
import csv
import itertools
import json
import math
import os
import stat
from pathlib import Path

def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON: {value}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def read_csv(path, reference=False):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        lines = stream
        if reference:
            lines = (line for line in stream if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(lines, skipinitialspace=True, strict=True)
        fields = [name.strip() for name in reader.fieldnames or []]
        if not fields or any(not name for name in fields) or len(set(fields)) != len(fields):
            raise ValueError(f"invalid CSV header: {path}")
        reader.fieldnames = fields
        rows = list(reader)
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    for row in rows:
        if None in row and reference and fields[-1].lower() in {"note", "notes", "flag", "flags", "comment", "comments"}:
            extras = row.pop(None) or []
            row[fields[-1]] = ",".join([row.get(fields[-1]) or "", *extras])
        if None in row or set(row) != set(fields):
            raise ValueError(f"ragged CSV: {path}")
        for name in fields:
            value = "" if row[name] is None else row[name].strip()
            if not value and not reference:
                raise ValueError(f"blank CSV cell: {path}:{name}")
            row[name] = value
            try:
                number = float(value)
            except ValueError:
                continue
            if not math.isfinite(number):
                raise ValueError(f"nonfinite CSV value: {path}:{name}")
    return fields, rows


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


def safe_path(root, name, directory=False):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("expected a submission-relative path")
    path = root / relative
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError("symlinks are not supported")
    path.resolve(strict=True).relative_to(root)
    if directory:
        if not path.is_dir() or not any(path.iterdir()):
            raise ValueError("required directory is empty or missing")
    elif not path.is_file() or path.stat().st_size == 0:
        raise ValueError("required file is empty or missing")
    return path


def axis_values(axis):
    if "values" in axis:
        return axis["values"]
    count = round((axis["stop"] - axis["start"]) / axis["step"]) + 1
    return [axis["start"] + index * axis["step"] for index in range(count)]


def check_csv(path, rule):
    fields, rows = read_csv(path)
    missing = sorted(set(rule["columns"]) - set(fields))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    for row in rows:
        for name in rule["columns"]:
            if name != "plane" and not math.isfinite(float(row[name])):
                raise ValueError(f"expected finite numeric column: {name}")
    grid = rule["grid"]
    if grid["type"] == "linear":
        expected = axis_values(grid)
        actual = [float(row[grid["column"]]) for row in rows]
        if len(actual) != len(expected) or any(
            abs(actual_value - expected_value) > grid.get("tolerance", 1e-8)
            for actual_value, expected_value in zip(actual, expected)
        ):
            raise ValueError(f"expected ordered {grid['column']} grid: {grid['start']}..{grid['stop']} step {grid['step']}")
    elif grid["type"] == "cartesian_values":
        axes = grid["axes"]
        values = [axis_values(axis) for axis in axes]
        expected = set(itertools.product(*values))
        actual = []
        for row in rows:
            point = []
            for axis, allowed in zip(axes, values):
                value = row[axis["column"]]
                if isinstance(allowed[0], str):
                    point.append(value)
                else:
                    matches = [entry for entry in allowed if abs(float(value) - entry) <= 1e-8]
                    if len(matches) != 1:
                        raise ValueError(f"off-grid {axis['column']}: {value}")
                    point.append(matches[0])
            actual.append(tuple(point))
        if len(actual) != len(expected) or set(actual) != expected:
            raise ValueError("missing or duplicate Cartesian grid points")
    else:
        raise ValueError(f"unsupported public grid: {grid['type']}")


def check(root, contract, variant=None):
    root = root.resolve(strict=True)
    issues = []
    checked = 0
    for name in contract["required_paths"]:
        parts = Path(name).parts
        if variant and len(parts) > 2 and parts[0] in {"results", "views"}:
            if parts[1] in contract["variants"] and parts[1] != variant:
                continue
        checked += 1
        try:
            path = safe_path(root, name, directory=name.endswith("/"))
            if path.suffix == ".json":
                payload = read_json(path)
                if not isinstance(payload, dict):
                    raise ValueError("expected a JSON object")
                if path.name == "meta.json" and parts[1] in contract["hfss_variants"]:
                    if not isinstance(payload.get("setup_names"), list) or not payload["setup_names"]:
                        raise ValueError("meta.json requires a nonempty setup_names list")
                    if not payload.get("result_source"):
                        raise ValueError("meta.json requires an explicit result_source")
            elif path.suffix == ".csv":
                rule = contract["csv_contracts"].get(name)
                if rule:
                    check_csv(path, rule)
                else:
                    read_csv(path)
        except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
            issues.append({"path": name, "error": str(error), "requirement": "addendum.md: Required data products / Output Schemas"})
    return {"status": "ok" if not issues else "incomplete", "checked_paths": checked, "issues": issues,
            "scope": "Public filenames, text schemas and grids only; not scientific credit or native provenance verification.",
            "candidate_code_executed": False, "files_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("check",))
    parser.add_argument("--submission", type=Path, default=Path("/home/submission"))
    parser.add_argument("--variant")
    arguments = parser.parse_args()
    if arguments.command == "check":
        if arguments.variant:
            parser.error("--variant is not supported by filesystem checks")
        try:
            regular_tree(arguments.submission)
        except (OSError, ValueError) as error:
            parser.exit(1, f"Filesystem preflight failed: {error}\n")
        print("Source filesystem preflight passed; execution and source-mutation checks still require clean replay.")
        return 0
    contract = read_json(Path(__file__).resolve().with_name("submission_contract.json"))
    if arguments.variant and arguments.variant not in contract["variants"]:
        parser.error(f"unknown variant: {arguments.variant}")
    try:
        result = check(arguments.submission, contract, arguments.variant)
    except (OSError, ValueError) as error:
        result = {"status": "incomplete", "issues": [{"path": str(arguments.submission), "error": str(error)}]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
