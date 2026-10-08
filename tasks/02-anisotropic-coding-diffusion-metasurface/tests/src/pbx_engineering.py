#!/usr/bin/env python3
"""Versioned replay preparation, diagnostics, and publication policy."""

import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid


VERSION = "engineering-v1"
RECEIPTS = ("candidate_replay.json", "safe_replay.json", "replay_receipt.json", "replay_state.json")


def read_json(path):
    try:
        value = json.loads(Path(path).read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_replay(logs):
    logs = Path(logs)
    for name in RECEIPTS:
        value = read_json(logs / name)
        if value and ("exit_code" in value or "status" in value):
            return value, name
    try:
        return {"exit_code": int((logs / "replay_exit_code.txt").read_text().strip())}, "replay_exit_code.txt"
    except (OSError, ValueError):
        return {}, ""


def agent_termination(logs):
    boundary = read_json(Path(logs).parent / "pbx_phase_boundary.json")
    if boundary.get("owner") == "paperbench-expanded_host_phase_boundary" and boundary.get("status") == "completed":
        termination = boundary.get("agent_termination", "")
        if termination != "completed":
            return termination
    termination = os.environ.get("PBX_AGENT_TERMINATION", "")
    if termination and termination != "completed":
        return termination
    path = Path(logs).parent / "agent/claude-code.txt"
    try:
        with path.open("rb") as handle:
            handle.seek(max(0, path.stat().st_size - 262144))
            lines = handle.read().decode(errors="replace").splitlines()
        for line in reversed(lines):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict) and event.get("type") == "result":
                return event.get("terminal_reason") or event.get("subtype") or ""
    except OSError:
        pass
    return ""


def replay_integrity(logs, replay):
    before = replay.get("input_before_manifest_sha256")
    after = replay.get("input_after_manifest_sha256")
    if before and before == after and replay.get("source_unchanged") is not False:
        return True
    receipt = read_json(Path(logs) / "private/replay_receipt.json")
    return bool(receipt.get("owner") == "paperbench-expanded_verifier"
                and receipt.get("source_only_inputs_verified") is True
                and receipt.get("exit_code") == replay.get("exit_code")
                and receipt.get("input_sha256_before")
                and receipt.get("input_sha256_before") == receipt.get("input_sha256_after"))


def raw_score(logs, fallback=None):
    logs = Path(logs)
    result = read_json(logs / "result.json")
    candidates = [result.get("score"), result.get("raw_rubric_score")]
    try:
        candidates.append(float((logs / "reward.txt").read_text().strip()))
    except (OSError, ValueError):
        pass
    candidates.append(fallback)
    for value in candidates:
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1:
            return float(value)
    return None


def assess(logs, state="done", fallback_score=None, exception_type=""):
    logs = Path(logs)
    replay, receipt_source = read_replay(logs)
    score = raw_score(logs, fallback_score)
    result = read_json(logs / "result.json")
    validity = read_json(logs / "validity.json")
    failure = read_json(logs / "failure.json")
    candidate_failure = read_json(logs / "candidate_failure.json")
    termination = "timeout" if exception_type == "AgentTimeoutError" else agent_termination(logs)
    budget_exhausted = termination in {"timeout", "max_turns", "error_max_turns"}
    delivery = read_json(logs / "delivery_status.json").get("delivery")
    infra_records = [read_json(logs / name) for name in ("infra_failure.json", "private/infrastructure_error.json", "private/harness_failure.json")]
    status = "unknown"
    reason = "No complete, recognized replay and judge record."
    publishable = False
    ranking_score = None
    exit_code = replay.get("exit_code")
    judge_bad = (
        result.get("judge_ok") is False
        or bool(result.get("n_judge_errors"))
        or bool(validity.get("judge_failures"))
        or result.get("status") in {"scored_with_judge_errors", "infrastructure_error", "judge_unavailable", "judge_unavailable_partial", "judge_error"}
        or "judge_unavailable" in str(result.get("status", ""))
    )
    infra_bad = (failure.get("kind") == "infra" or any(infra_records)
                 or result.get("status") in {"task_error", "verifier_config_error", "verifier_internal_error"}
                 or replay.get("status") in {"isolation_error", "post_replay_isolation_error", "infrastructure_error"})
    if state == "superseded":
        status, reason = "superseded", "Superseded trials are diagnostic only."
    elif state == "running":
        status, reason = "running", "The trial has not finished."
    elif infra_bad or (exception_type in {"UnknownApiError", "EnvironmentStartTimeoutError", "AgentSetupTimeoutError"} and not budget_exhausted):
        status, reason = "infra_error", "Infrastructure or agent transport failed; no scientific zero is inferred."
    elif budget_exhausted and delivery == "starter_only":
        status, reason = "agent_budget_exhausted", "The agent exhausted its budget without delivery; no scientific score is inferred."
    elif delivery == "starter_only":
        status, reason = "no_delivery", "Only starter files remain; this alone does not establish an infrastructure failure."
    elif result.get("status") == "dry_run":
        status, reason = "dry_run", "Packet generation is not a scientific evaluation."
    elif judge_bad:
        status, reason = "judge_error", "The judge did not complete; the raw score is diagnostic only."
    elif result.get("status") == "invalid_evidence":
        status, reason = "invalid_evidence", "Trusted replay integrity failed; no scientific score is published."
    elif (result.get("scoring_policy") == "leaf-local-replay-v1"
          and result.get("status") in {"scored", "scored_replay_partial"}
          and result.get("provenance_verified") is True
          and result.get("partial") is False
          and result.get("unknown_leaf_ids") == []
          and score is not None and replay_integrity(logs, replay)):
        status = "valid" if result.get("replay_completed") else "partial"
        reason = "All leaves assessed under the leaf-local policy; execution completion is reported separately."
        publishable, ranking_score = True, score
    elif failure.get("kind") == "candidate" or candidate_failure or exit_code in {125, 127}:
        status, reason = "candidate_failed", "Replay failure alone does not determine the scientific score; retain the leaf-level review."
        if score is not None and replay_integrity(logs, replay):
            status, reason = "partial", "The judge assessed verified partial evidence independently of replay completion."
            publishable, ranking_score = True, score
    elif exit_code == 126:
        status, reason = "unknown", "Exit 126 alone does not distinguish submission rejection from workspace/isolation failure."
    elif validity.get("validity") in {"invalid", "unknown"}:
        status, reason = "candidate_invalid", "The task validity gate rejected the evidence."
        if validity.get("validity") == "invalid":
            ranking_score = 0.0
    elif exit_code == 0 and replay.get("source_unchanged") is not False and score is not None and (
        replay.get("status") not in {"failed", "not_attempted"}
        or (receipt_source == "candidate_replay.json" and replay.get("status") == "failed"
            and "candidate_receipt_sha256" in replay and replay.get("candidate_receipt_sha256") is None
            and replay.get("stdout_log_sha256") and replay.get("exec_trace_sha256")
            and replay_integrity(logs, replay))
    ):
        status, reason = "valid", "Replay and judge completed without a recorded infrastructure or integrity failure."
        publishable, ranking_score = True, score
    elif isinstance(exit_code, int) and exit_code != 0 and score is not None and float(replay.get("elapsed_seconds") or 0) > 0:
        if replay_integrity(logs, replay):
            status, reason = "partial", "A completed judge scored genuine partial replay evidence; the failed attempt is retained."
            publishable, ranking_score = True, score
        else:
            status, reason = "candidate_failed", "Replay failed; partial evidence integrity is not established."
    return {
        "schema_version": 1,
        "policy_version": VERSION,
        "status": status,
        "reason": reason,
        "replay_exit": exit_code,
        "receipt_source": receipt_source,
        "agent_termination": termination,
        "agent_budget_exhausted": budget_exhausted,
        "raw_score": score,
        "publishable": publishable,
        "scientific_score": score if publishable else None,
        "ranking_score": ranking_score,
        "eligible_for_ranking": ranking_score is not None,
    }


def record_failure(logs, kind, stage, reason_code, message, path=None):
    record = {"schema_version": 1, "policy_version": VERSION, "kind": kind, "stage": stage,
              "reason_code": reason_code, "message": message, "path": str(path) if path else None}
    atomic_json(Path(logs) / "failure.json", record)
    return record


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


def prepare_workspace(submission, logs, generated_roots, owner=None):
    submission, logs = Path(submission), Path(logs)
    roots = set(generated_roots) | {"__pycache__"}
    if any(Path(name).name != name or name in {"", ".", ".."} for name in roots):
        raise ValueError("Generated roots must be top-level names.")
    try:
        regular_tree(submission)
    except ValueError as error:
        record_failure(logs, "candidate", "source_scan", "unsafe_entry", str(error))
        return 126
    snapshot = logs / "source_submission"
    try:
        if snapshot.exists():
            shutil.rmtree(snapshot)
        snapshot.mkdir(parents=True)
        for entry in submission.iterdir():
            if entry.name in roots:
                continue
            destination = snapshot / entry.name
            if entry.is_dir():
                shutil.copytree(entry, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(entry, destination)
        for entry in submission.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        shutil.copytree(snapshot, submission, dirs_exist_ok=True)
        if owner:
            import pwd
            identity = pwd.getpwnam(owner)
            for current, directories, files in os.walk(submission):
                os.chown(current, identity.pw_uid, identity.pw_gid)
                os.chmod(current, 0o755)
                for name in files:
                    path = Path(current) / name
                    os.chown(path, identity.pw_uid, identity.pw_gid)
                    path.chmod(path.stat().st_mode | 0o600)
            subprocess.run(["runuser", "-u", owner, "--", "env", "-i", "PATH=/usr/bin:/bin", "/bin/sh", "-eu", "-c",
                            "cd \"$1\"; probe=$(mktemp .pbx-write-check.XXXXXX); trap 'rm -f \"$probe\"' EXIT; printf ready > \"$probe\"; test \"$(cat \"$probe\")\" = ready",
                            "sh", str(submission)], check=True)
        return 0
    except (OSError, subprocess.CalledProcessError) as error:
        record_failure(logs, "infra", "workspace_prepare", "filesystem_error", str(error), getattr(error, "filename", None))
        return 126


def begin(logs, tests):
    logs, tests = Path(logs), Path(tests)
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid.uuid4().hex[:8]
    entries = [entry for entry in logs.iterdir() if entry.name != ".history"]
    if entries:
        history = logs / ".history" / stamp
        history.parent.mkdir(mode=0o700, exist_ok=True)
        history.parent.chmod(0o700)
        history.mkdir(mode=0o700)
        for entry in entries:
            os.replace(entry, history / entry.name)
    records = {}
    for root in (tests, Path("/home/paper")):
        if root.is_dir():
            for path in sorted(root.rglob("*")):
                if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts and path.suffix in {".py", ".sh", ".json", ".toml", ".yaml", ".md"}:
                    records[str(path)] = sha256(path)
    atomic_json(logs / "execution_manifest.json", {
        "schema_version": 1, "policy_version": VERSION, "execution_id": stamp,
        "input_sha256": records, "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "declared_cpus": os.environ.get("CONTAINER_CPUS"),
        "image_digest": os.environ.get("PBX_IMAGE_DIGEST"),
        "judge_model": os.environ.get("JUDGE_MODEL"),
        "solver_python": sys.version,
    })


def finalize(logs):
    logs = Path(logs)
    assessment = assess(logs)
    atomic_json(logs / "publication.json", assessment)
    reward = logs / "reward.txt"
    if not assessment["publishable"]:
        reward.unlink(missing_ok=True)
        if assessment["status"] == "candidate_invalid":
            reward.write_text("0.000000\n")
        return 1 if assessment["status"] in {"infra_error", "judge_error", "unknown", "invalid_evidence"} else 0
    return 0


def preflight(logs, solver):
    modules = {"hfss": ("ansys.aedt.core", "openai"), "meep": ("meep",), "qe": (), "biology": ()}
    try:
        missing = [name for name in modules.get(solver, ()) if importlib.util.find_spec(name) is None]
        if solver in {"meep", "qe", "biology"}:
            missing.extend(name for name in ("iptables", "ip6tables", "runuser", "setpriv", "strace") if not shutil.which(name))
        if solver == "qe" and not shutil.which("pw.x"):
            missing.append("pw.x")
        if solver == "hfss" and not any(name.startswith(("ANSYSEM_ROOT", "AWP_ROOT")) and Path(value).is_dir()
                                         for name, value in os.environ.items()):
            missing.append("AEDT installation discovery environment")
        if missing:
            raise RuntimeError("Missing replay prerequisites: " + ", ".join(missing))
    except (ImportError, RuntimeError, ValueError) as error:
        record_failure(logs, "infra", "environment_preflight", "missing_runtime", str(error))
        return 1
    atomic_json(Path(logs) / "environment_preflight.json", {"schema_version": 1, "solver": solver, "status": "passed",
                                                           "solver_smoke_test": "not_performed"})
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("begin", "prepare", "check", "finalize", "failure", "preflight"))
    parser.add_argument("--logs", default="/logs/verifier")
    parser.add_argument("--tests", default="/tests")
    parser.add_argument("--submission", default="/home/submission")
    parser.add_argument("--generated-root", action="append", default=[])
    parser.add_argument("--owner")
    parser.add_argument("--solver", default="")
    parser.add_argument("--kind", choices=("candidate", "infra"), default="infra")
    parser.add_argument("--stage", default="replay")
    parser.add_argument("--reason", default="unknown")
    parser.add_argument("--message", default="")
    args = parser.parse_args()
    if args.command == "begin":
        begin(args.logs, args.tests)
    elif args.command == "prepare":
        return prepare_workspace(args.submission, args.logs, args.generated_root, args.owner)
    elif args.command == "check":
        regular_tree(args.submission)
        print("Source filesystem preflight passed; execution and source-mutation checks still require clean replay.")
    elif args.command == "failure":
        record_failure(args.logs, args.kind, args.stage, args.reason, args.message)
    elif args.command == "preflight":
        return preflight(args.logs, args.solver)
    else:
        return finalize(args.logs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
