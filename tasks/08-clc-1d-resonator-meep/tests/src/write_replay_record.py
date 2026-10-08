#!/usr/bin/env python3
"""Write the runner-owned record for one candidate clean replay."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    if not path.exists() or path.is_symlink():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--exec-trace", type=Path, required=True)
    parser.add_argument("--inputs-before", type=Path, required=True)
    parser.add_argument("--inputs-after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--nonce", required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--elapsed-seconds", type=float, required=True)
    args = parser.parse_args()
    receipt = args.submission / "replay_receipt.json"
    before_hash = sha(args.inputs_before)
    after_hash = sha(args.inputs_after)
    intact_inputs = before_hash is not None and before_hash == after_hash
    completed = args.exit_code == 0 and intact_inputs and sha(args.log) is not None and sha(args.exec_trace) is not None
    value = {
        "schema_version": 1,
        "status": "completed" if completed else "failed",
        "replay_nonce": args.nonce,
        "exit_code": args.exit_code,
        "started_at": args.started_at,
        "elapsed_seconds": args.elapsed_seconds,
        "candidate_receipt_required": False,
        "candidate_receipt_sha256": sha(receipt),
        "source_integrity_verified": intact_inputs,
        "stdout_log_sha256": sha(args.log),
        "exec_trace_sha256": sha(args.exec_trace),
        "input_before_manifest_sha256": sha(args.inputs_before),
        "input_after_manifest_sha256": sha(args.inputs_after),
    }
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
