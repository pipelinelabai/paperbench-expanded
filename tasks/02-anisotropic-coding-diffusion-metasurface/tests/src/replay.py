#!/usr/bin/env python3
"""Clean, verifier-owned replay with immutable-input and output receipts."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SUBMISSION = Path(os.environ.get("SUBMISSION_DIR", "/home/submission"))
LOGS = Path(os.environ.get("VERIFIER_LOG_DIR", "/logs/verifier"))
GENERATED = (
    "results", "hfss", "views", "work", "logs", ".tmp_views", ".solver-tmp",
    "calibration.md", "calibration_log.csv", "calibration_parameters.json",
    "batch.log", "batch_main.log", "session.log", "reproduce.log",
    "replay.log", "final_replay.log", "reproduce_main.log", "build_run.log", "hfss_solve.log",
    "pipeline.log", "build_log.txt", "solve_log.json", "replay_report.json",
    "replay_receipt.json",
    "aedt_temp", ".aedt_temp", "aedt_work",
    "cbfreq.stdout.log", "pecfreq.stdout.log",
    "cbmono.stdout.log", "pecmono.stdout.log",
    "pipeline_run.log", "pipeline_variants.log", "clean_run_outer.log",
    "pipeline_run_attempt1.log", "pipeline_run_attempt2.log",
    "pipeline_run_attempt3.log", "pipeline_run_attempt4.log",
)
RUNTIME_ROOT_NAMES = {
    ".run_home", ".ansys", ".cache", "Ansoft",
    ".mpl_cache", ".solver-tmp",
}
RUNTIME_ANYWHERE_DIR_NAMES = {"__pycache__"}
RUNTIME_FILE_NAMES = {
    "batch.log", "batch_main.log", "session.log", "reproduce.log",
    "license.log", "ansysli_client.log",
    "replay.log", "reproduce_console.log", "reproduce_console.txt",
    "calibration_history.json", "validation.log",
}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}
NATIVE_SUFFIXES = {".aedt", ".asol", ".msh", ".prof", ".profile"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def is_runtime_path(relative: Path) -> bool:
    return (
        bool(relative.parts and relative.parts[0] in RUNTIME_ROOT_NAMES)
        or any(part in RUNTIME_ANYWHERE_DIR_NAMES for part in relative.parts)
        or (len(relative.parts) == 1 and relative.name in RUNTIME_FILE_NAMES)
        or relative.suffix.lower() in RUNTIME_SUFFIXES
        or (
            len(relative.parts) == 1
            and "license" in relative.name.lower()
            and relative.suffix.lower() in {".log", ".out"}
        )
    )


def inventory_inputs() -> dict:
    result = {}
    for path in SUBMISSION.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(SUBMISSION)
        if relative.parts and relative.parts[0] in set(GENERATED):
            continue
        if is_runtime_path(relative):
            continue
        result[relative.as_posix()] = digest(path)
    return result


def validate_source_only_inputs(inputs: dict[str, str]) -> None:
    cached = []
    for name in inputs:
        relative = Path(name)
        lower = name.lower()
        if (
            relative.suffix.lower() in NATIVE_SUFFIXES
            or ".aedtresults/" in lower
            or re.fullmatch(r"\.s\d+p", relative.suffix.lower())
        ):
            cached.append(name)
    if cached:
        raise RuntimeError(
            "cached HFSS result artifacts are forbidden outside replay-generated roots: "
            + ", ".join(sorted(cached)[:20])
        )


def inventory_outputs() -> dict:
    result = {}
    for name in (*GENERATED, *sorted(RUNTIME_ROOT_NAMES)):
        path = SUBMISSION / name
        if path.is_file() and not path.is_symlink():
            result[name] = digest(path)
        elif path.is_dir() and not path.is_symlink():
            for item in path.rglob("*"):
                if item.is_file() and not item.is_symlink():
                    result[item.relative_to(SUBMISSION).as_posix()] = digest(item)
    return result


def output_metadata() -> dict[str, tuple[int, int]]:
    result = {}
    for name in (*GENERATED, *sorted(RUNTIME_ROOT_NAMES)):
        path = SUBMISSION / name
        if path.is_file() and not path.is_symlink():
            info = path.stat()
            result[name] = (info.st_size, info.st_mtime_ns)
        elif path.is_dir() and not path.is_symlink():
            for item in path.rglob("*"):
                if item.is_file() and not item.is_symlink():
                    info = item.stat()
                    result[item.relative_to(SUBMISSION).as_posix()] = (
                        info.st_size,
                        info.st_mtime_ns,
                    )
    return result


def wait_for_stable_outputs(timeout: float = 15.0, interval: float = 0.5) -> bool:
    """Require three consecutive identical output metadata snapshots."""
    deadline = time.monotonic() + timeout
    previous = None
    stable_intervals = 0
    while time.monotonic() < deadline:
        current = output_metadata()
        if current == previous:
            stable_intervals += 1
            if stable_intervals >= 2:
                return True
        else:
            stable_intervals = 0
        previous = current
        time.sleep(interval)
    return False


def solver_process_ids() -> set[int]:
    patterns = ("ansysedt", "ansyscl", "hf3d", "electra")
    text = subprocess.check_output(["ps", "-eo", "pid=,comm="], text=True, errors="replace")
    result = set()
    for line in text.splitlines():
        fields = line.strip().split(None, 1)
        if len(fields) != 2:
            continue
        if any(fields[1].lower().startswith(pattern) for pattern in patterns):
            result.add(int(fields[0]))
    return result


def monitor(stop: threading.Event, observed: list[bool], baseline: set[int]) -> None:
    while not stop.wait(0.25):
        try:
            if solver_process_ids() - baseline:
                observed[0] = True
        except Exception:
            pass


def main() -> int:
    private = LOGS / "private"
    private.mkdir(parents=True, exist_ok=True)
    (private / "replay_receipt.json").unlink(missing_ok=True)
    # Remove generated roots and runtime caches before inventorying candidate
    # source. In particular, do not let a pre-seeded .run_home/.ansys cache
    # survive into verifier-owned replay.
    for name in GENERATED:
        path = SUBMISSION / name
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()
    runtime_dirs = sorted(
        (
            path for path in SUBMISSION.rglob("*")
            if (
                path.name in RUNTIME_ANYWHERE_DIR_NAMES
                or (path.parent == SUBMISSION and path.name in RUNTIME_ROOT_NAMES)
            )
        ),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in runtime_dirs:
        if path.is_symlink():
            path.unlink()
        elif path.exists() and path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for name in ("results", "hfss", "views"):
        (SUBMISSION / name).mkdir(parents=True, exist_ok=True)
    before = inventory_inputs()
    source_only_inputs_verified = True
    source_error = None
    try:
        validate_source_only_inputs(before)
    except RuntimeError as exc:
        source_only_inputs_verified = False
        source_error = str(exc)

    started = datetime.now(timezone.utc).isoformat()
    observed = [False]
    stop = threading.Event()
    try:
        baseline_solver_pids = solver_process_ids()
    except Exception:
        baseline_solver_pids = set()
    thread = threading.Thread(
        target=monitor, args=(stop, observed, baseline_solver_pids), daemon=True
    )
    thread.start()
    script = SUBMISSION / "reproduce.sh"
    execution = {"status": "candidate_missing_entrypoint", "exit_code": 127}
    if source_error:
        exit_code = 126
        execution = {"status": "source_validation_failed", "exit_code": exit_code}
    elif script.is_file() and not script.is_symlink():
        completed = subprocess.run(["python3", str(Path(__file__).resolve().parent / "safe_replay.py"), str(script)], cwd=SUBMISSION, check=False)
        exit_code = completed.returncode
        try:
            execution = json.loads((LOGS / "safe_replay.json").read_text())
        except (OSError, ValueError):
            execution = {"status": "missing_execution_receipt", "exit_code": exit_code}
    else:
        exit_code = 127
    stop.set()
    thread.join(timeout=2)
    outputs_stable = wait_for_stable_outputs()
    if not outputs_stable and exit_code == 0:
        exit_code = 125
    after = inventory_inputs()
    outputs = inventory_outputs()
    receipt = {
        "schema_version": 1,
        "owner": "paperbench-expanded_verifier",
        "status": "completed" if exit_code == 0 else "partial",
        "exit_code": exit_code,
        "execution": execution,
        "input_sha256_before": before,
        "input_sha256_after": after,
        "output_sha256": outputs,
        "solver_process_observed": observed[0],
        "source_only_inputs_verified": source_only_inputs_verified,
        "source_validation_error": source_error,
        "outputs_stable": outputs_stable,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    (private / "replay_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
