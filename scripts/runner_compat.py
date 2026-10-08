"""Check the local Harbor version and its numeric-setting log-scrub fix."""

import argparse
import ast
from importlib import metadata
from pathlib import Path


VERSION = "0.21.0"


def compatible_source(source, apply_fix=False):
    expected = ast.dump(ast.parse("value and not value.isdigit()", mode="eval").body)
    guards = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.If):
            continue
        for statement in node.body:
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == "secrets" and call.func.attr == "add" and len(call.args) == 1 and isinstance(call.args[0], ast.Name) and call.args[0].id == "value":
                    guards.append(node.test)
    if len(guards) != 1:
        raise ValueError("The expected Harbor log-scrub guard was not found exactly once.")
    if ast.dump(guards[0]) == expected:
        return source
    if not isinstance(guards[0], ast.Name) or guards[0].id != "value":
        raise ValueError("Harbor's numeric-setting log-scrub guard is not recognized.")
    if not apply_fix:
        raise ValueError("The local numeric-setting fix is missing; run scripts/runner_compat.py --apply.")
    before = "                        if value:\n                            secrets.add(value)"
    after = "                        if value and not value.isdigit():\n                            secrets.add(value)"
    if source.count(before) != 1:
        raise ValueError("The expected Harbor log-scrub guard was not found exactly once.")
    result = source.replace(before, after, 1)
    compatible_source(result)
    return result


def check_runner(apply_fix=False):
    package = metadata.distribution("harbor")
    if package.version != VERSION:
        raise ValueError(f"Harbor {VERSION} is required; found {package.version}.")
    path = Path(package.locate_file("harbor/trial/trial.py"))
    source = path.read_text()
    result = compatible_source(source, apply_fix)
    if result != source:
        path.write_text(result)
    return f"Harbor {VERSION}: numeric-setting log-scrub guard is compatible."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply only the recognized upstream-to-local fix.")
    args = parser.parse_args()
    try:
        print(check_runner(args.apply))
    except (ValueError, OSError, metadata.PackageNotFoundError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
