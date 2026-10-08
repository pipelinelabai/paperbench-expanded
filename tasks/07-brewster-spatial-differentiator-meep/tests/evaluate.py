#!/usr/bin/env python3
"""Harbor verifier entrypoint for Meep v2 LLM-only rubric scoring.

The clean replay is performed by test.sh.  This wrapper only runs the
tool-augmented all-LLM scorer and publishes Harbor-compatible result files.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
TESTS = Path(os.environ.get("PBX_TESTS_DIR", str(HERE)))
sys.path.insert(0, str(TESTS / "src"))
TASK_ROOT = TESTS.parent if TESTS.parent != Path("/") else TESTS
LOGS = Path(os.environ.get("PBX_LOGS_DIR", "/logs/verifier"))
EVIDENCE = Path(
    os.environ.get(
        "PBX_EVIDENCE_ROOT",
        os.environ.get("PBX_CANDIDATE_EVIDENCE_ROOT", "/logs/verifier/candidate_outputs"),
    )
)


def env_int(name: str, default: int) -> str:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return str(default)
    return str(max(1, int(value)))


def env_float(name: str, default: float) -> str:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return str(default)
    return str(float(value))


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copy2(src, dst)


def main() -> int:
    from meep_score_publication import block_disabled_scoring

    if block_disabled_scoring(TESTS, LOGS):
        return 78
    scorer = TESTS / "src/rubric_tool_llm_regrade.py"
    if not scorer.is_file():
        raise SystemExit(f"missing LLM scorer: {scorer}")
    if not EVIDENCE.exists():
        raise SystemExit(f"missing evidence root: {EVIDENCE}")

    LOGS.mkdir(parents=True, exist_ok=True)
    out = LOGS / "llm_regrade"
    resume = env_bool("PBX_LLM_RESUME", False) and (out / "manifest.json").is_file()
    if env_bool("PBX_LLM_RESUME", False) and not resume:
        print(
            f"NOTE: PBX_LLM_RESUME is set but {out / 'manifest.json'} does not exist; "
            "scoring fresh instead.",
            file=sys.stderr,
        )
    if out.exists() and not resume:
        shutil.rmtree(out)

    model = os.environ.get("JUDGE_MODEL", "gpt-5.5")
    transport = os.environ.get("PBX_LLM_TRANSPORT") or os.environ.get("JUDGE_TRANSPORT") or "auto"
    cmd = [
        sys.executable,
        str(scorer),
        "--task-root",
        str(TASK_ROOT),
        "--evidence-root",
        str(EVIDENCE),
        "--out",
        str(out),
        "--model",
        model,
        "--transport",
        transport,
        "--max-workers",
        env_int("PBX_LLM_MAX_WORKERS", 8),
        "--max-tokens",
        env_int("PBX_LLM_MAX_TOKENS", 8192),
        "--http-timeout",
        env_float("PBX_LLM_HTTP_TIMEOUT", 300.0),
        "--retries",
        env_int("PBX_LLM_RETRIES", 4),
        "--retry-sleep",
        env_float("PBX_LLM_RETRY_SLEEP", 8.0),
        "--max-tool-rounds",
        env_int("PBX_LLM_MAX_TOOL_ROUNDS", 16),
        "--final-parse-retries",
        env_int("PBX_LLM_FINAL_PARSE_RETRIES", 2),
        "--max-total-tool-chars",
        env_int("PBX_LLM_MAX_TOTAL_TOOL_CHARS", 400000),
        "--max-tool-result-chars",
        env_int("PBX_LLM_MAX_TOOL_RESULT_CHARS", 65000),
        "--min-tool-result-chars",
        env_int("PBX_LLM_MIN_TOOL_RESULT_CHARS", 4000),
        "--fail-loud-threshold",
        env_float("PBX_LLM_FAIL_LOUD_THRESHOLD", 0.02),
    ]
    if resume:
        cmd.append("--resume")
    only_leaves = os.environ.get("PBX_LLM_ONLY_LEAVES", "").strip()
    if only_leaves:
        cmd += ["--only-leaves", only_leaves]
    if env_bool("PBX_LLM_FAIL_LOUD", False):
        cmd.append("--fail-loud-on-judge-errors")
    else:
        cmd.append("--no-fail-loud-on-judge-errors")
    if os.environ.get("PBX_LLM_DRY_RUN") == "1":
        cmd.append("--dry-run")

    # Exit 4 means "scored, but judge errors exceeded the fail-loud threshold".
    # Result files still exist and must be published, so do not use check=True.
    proc = subprocess.run(cmd)
    if proc.returncode not in (0, 4):
        raise SystemExit(f"LLM scorer failed with exit code {proc.returncode}")
    scorer_rc = proc.returncode

    if os.environ.get("PBX_LLM_DRY_RUN") == "1":
        result = {
            "status": "dry_run",
            "score": None,
            "judge_model": model,
            "evidence_root": str(EVIDENCE),
            "llm_regrade_dir": str(out),
            "note": "PBX_LLM_DRY_RUN=1 only builds leaf packets; it is not a real grade.",
        }
        (LOGS / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        (LOGS / "reward.txt").unlink(missing_ok=True)
        return 0

    result_path = out / "result.json"
    reward_path = out / "reward.txt"
    rubric_path = out / "rubric_results.json"
    if not result_path.is_file() or not rubric_path.is_file():
        raise SystemExit(f"LLM scorer did not produce expected result files under {out}")
    if not reward_path.is_file():
        raise SystemExit(
            "LLM scorer produced a PARTIAL score and deliberately wrote no reward.txt "
            f"(subset total is in {out / 'reward_partial.txt'}). Set PBX_LLM_RESUME=1 so "
            "the remaining leaves are reused, or clear PBX_LLM_ONLY_LEAVES for a full run."
        )

    from meep_score_publication import InvalidGrade, withhold_invalid_score

    try:
        withhold_invalid_score(result_path, TESTS / "rubric.json", rubric_path, LOGS)
    except InvalidGrade as error:
        print(f"Score withheld: {error}", file=sys.stderr)
        return 75

    copy_if_exists(result_path, LOGS / "result.json")
    copy_if_exists(reward_path, LOGS / "reward.txt")
    copy_if_exists(rubric_path, LOGS / "rubric_results.json")
    copy_if_exists(out / "manifest.json", LOGS / "llm_regrade_manifest.json")

    copy_if_exists(out / "judge_errors.json", LOGS / "judge_errors.json")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    score = float(result.get("score", 0.0))
    (LOGS / "reward.txt").write_text(f"{score:.6f}\n", encoding="utf-8")

    resume_info = result.get("resume") or {}
    if resume_info.get("enabled"):
        print(
            f"RESUME: {resume_info.get('n_rescored')} leaf/leaves re-scored, "
            f"{resume_info.get('n_reused')} reused from the prior run "
            f"(re-scored: {resume_info.get('rescored_leaf_indices')}).",
            file=sys.stderr,
        )
    n_errors = int(result.get("n_judge_errors", 0) or 0)
    if n_errors:
        lost = float(result.get("judge_error_weight_lost", 0.0) or 0.0)
        frac = float(result.get("judge_error_fraction_of_possible", 0.0) or 0.0)
        print(
            f"JUDGE ERRORS: {n_errors} leaf/leaves fail-closed to 0 inside the judge; "
            f"{lost:.4f} weight lost ({frac * 100:.2f}% of possible). "
            f"reward={score:.6f} is a LOWER BOUND. See judge_errors.json.",
            file=sys.stderr,
        )
    return scorer_rc


if __name__ == "__main__":
    raise SystemExit(main())
