#!/usr/bin/env python3
# /// script
# dependencies = [
#   "anthropic>=0.75.0",
#   "numpy>=1.24.0",
#   "scipy>=1.10.0",
# ]
# ///
"""
Rubric-based evaluator for mapgpt-r2r harbor task.

Strategy:
  §3.A  Structural Modeling   (LLM per leaf)
  §3.B  Simulation Config     (LLM per leaf)
  §3.C  Numerical Match       (direct numerical comparison with ref NPZ)
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

from reward_scoring import coverage_gate, finalize_reward, metric_score, parse_judge_score

FROZEN_EVIDENCE_ROOT = Path("/logs/verifier/candidate_outputs")
SUBMISSION = Path(os.environ.get("EVIDENCE_ROOT", "/home/submission"))


def _require_frozen_evidence_root():
    raw_root = os.environ.get("EVIDENCE_ROOT")
    if not raw_root:
        raise RuntimeError("EVIDENCE_ROOT is required; direct /home/submission scoring is forbidden")
    try:
        supplied_root = Path(raw_root).resolve(strict=True)
        expected_root = FROZEN_EVIDENCE_ROOT.resolve(strict=True)
    except OSError as error:
        raise RuntimeError(f"frozen evidence root is unavailable: {error}") from error
    if supplied_root != expected_root:
        raise RuntimeError(
            f"EVIDENCE_ROOT must be {FROZEN_EVIDENCE_ROOT}, got {supplied_root}"
        )
    replay_record = supplied_root / "candidate_replay.json"
    try:
        record = json.loads(replay_record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError("frozen evidence lacks a valid candidate_replay.json") from error
    if (record.get("status") != "ok" or record.get("exit_code") != 0
            or record.get("source_unchanged") is not True):
        raise RuntimeError("frozen evidence is not from a successful unchanged clean replay")


def _raise_judge_infrastructure_failure(error):
    """Record transport/client failures separately from candidate evidence scores."""
    output = Path("/logs/verifier")
    output.mkdir(parents=True, exist_ok=True)
    reward = output / "reward.txt"
    if reward.exists():
        reward.unlink()
    payload = {
        "schema_version": 1,
        "kind": "infra",
        "stage": "judge_transport",
        "error_type": type(error).__name__,
        "message": str(error),
        "time_unix": time.time(),
    }
    (output / "infra_failure.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise RuntimeError(f"judge transport exhausted retries: {error}")
TESTS_DIR = Path(__file__).resolve().parent
REFS_DIR = TESTS_DIR / "refs"
PAPER_MD = Path("/home/paper/paper.md")
ADDENDUM_MD = TESTS_DIR / "config/public_contract.md"
JUDGE_PROMPT_MD = TESTS_DIR / "config/judge_prompt.md"
RUBRIC_JSON = TESTS_DIR / "rubric.json"
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-7")


# ─── OpenAI-compatible judge client ───────────────────────────────────────────

JUDGE_CHAT_BASE_URL = (os.environ.get("JUDGE_CHAT_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
                       or os.environ.get("JUDGE_BASE_URL") or "").rstrip("/")
JUDGE_CHAT_API_KEY = (os.environ.get("JUDGE_CHAT_API_KEY") or os.environ.get("OPENAI_API_KEY")
                      or os.environ.get("JUDGE_API_KEY") or "")
if JUDGE_CHAT_BASE_URL and not JUDGE_CHAT_BASE_URL.endswith("/v1"):
    JUDGE_CHAT_BASE_URL = JUDGE_CHAT_BASE_URL + "/v1"


def _chat_completion(system_prompt, user_content):
    import urllib.request
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    request = urllib.request.Request(
        JUDGE_CHAT_BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + JUDGE_CHAT_API_KEY},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        body = json.loads(response.read().decode("utf-8"))
    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("judge chat response has no choices")
    content = (choices[0].get("message") or {}).get("content")
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    if not content:
        raise RuntimeError("judge chat response has no content")
    return content


def get_client():
    if not JUDGE_CHAT_BASE_URL or not JUDGE_CHAT_API_KEY:
        return None
    return True


# ─── File helpers ──────────────────────────────────────────────────────────────

def _read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

def _read_json(path):
    txt = _read_text(path)
    if not txt:
        return None
    try:
        return json.loads(txt)
    except Exception:
        return None

def _read_npz(path):
    try:
        return np.load(str(path), allow_pickle=True)
    except Exception:
        return None

def _read_csv(path):
    try:
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


# ─── Evidence file reader ─────────────────────────────────────────────────────

def _read_evidence_file(path_str, kind):
    if path_str.startswith("papers/mapgpt-r2r/judge_only/refs/"):
        rel = path_str.replace("papers/mapgpt-r2r/judge_only/refs/", "")
        full = REFS_DIR / rel
    else:
        clean = path_str.removeprefix("submission/")
        full = SUBMISSION / clean

    if kind == "npz":
        data = _read_npz(full)
        if data is None:
            return f"[FILE NOT FOUND: {path_str}]"
        lines = [f"NPZ file: {path_str}", f"  Keys: {list(data.keys())}"]
        for k in data.keys():
            arr = data[k]
            if hasattr(arr, "shape"):
                lines.append(f"  {k}: shape={arr.shape}, dtype={arr.dtype}")
                if arr.ndim <= 1 and arr.size <= 10:
                    lines.append(f"    values={arr.tolist()}")
                elif arr.ndim == 1:
                    lines.append(f"    min={float(arr.min()):.4g}, max={float(arr.max()):.4g}")
        return "\n".join(lines)

    elif kind == "csv":
        rows = _read_csv(full)
        if rows is None:
            return f"[FILE NOT FOUND: {path_str}]"
        header = list(rows[0].keys()) if rows else []
        preview = rows[:5] if len(rows) > 5 else rows
        lines = [f"CSV file: {path_str}", f"  Columns: {header}", f"  Total rows: {len(rows)}", "  First rows:"]
        for r in preview:
            lines.append(f"    {dict(r)}")
        return "\n".join(lines)

    elif kind == "image":
        return f"[IMAGE FILE: {path_str} — visual content not evaluated here]"

    else:
        txt = _read_text(full)
        if txt is None:
            return f"[FILE NOT FOUND: {path_str}]"
        if len(txt) > 4000:
            txt = txt[:3800] + f"\n... [truncated] ..."
        return f"File: {path_str}\n```\n{txt}\n```"

# ─── §3.C Numerical checks — mapgpt-r2r (VLN metrics) ────────────────────────
#
# Recompute NE / OSR / SR / SPL from the agent's trajectories.json using the
# Matterport/R2R connectivity graphs (geodesic shortest path). Single-sided
# pass criteria: higher SR/SPL/OSR pass, lower NE passes. Thresholds derive
# from the task metric configuration.
#
# UUIDs MUST match rubric.json §3.C leaves (see config/judge_prompt.md §4).

import math
import collections

VLN_VARIANT = "r2r_val_unseen_subset"
SUCCESS_THRESHOLD_M = 3.0

C_LEAF_IDS = {
    "1acb1fdd-cd07-55bc-8a42-9bafb96020d8": "sr",
    "46f26dcb-6459-587b-8201-94a43a61c662": "spl",
    "44b66c5e-9f44-5e22-afbd-099f08357a21": "osr",
    "c0238ba1-96e0-5bc9-baa5-b7dcc6699278": "ne",
    "7c2f08ed-73db-503e-be71-55629e049abb": "behavior",
}

# Diagnostic defaults for behavior reporting.
_DEFAULT_BEHAVIOR_THRESHOLDS = {
    "CAP_HIT_RATE_MAX": 40.0, "OSR_SR_GAP_MAX": 25.0,
}


def _vln_refs_dir():
    return REFS_DIR / VLN_VARIANT


def _load_reported_metrics():
    data = _read_json(_vln_refs_dir() / "reported_metrics.json")
    if not data:
        return None, None
    return data, _DEFAULT_BEHAVIOR_THRESHOLDS


def _load_connectivity():
    """Load per-scan connectivity graphs into {scan: {vp: (x,y,z)}} + adjacency.

    Expected verifier reference layout:
      refs/r2r_val_unseen_subset/connectivity/<scan>_connectivity.json
    Each file: list of nodes with keys 'image_id', 'pose' (4x4 row-major, the
    translation is indices 3,7,11), and 'unobstructed' (bool list to other nodes)
    + 'included' flag — the standard Matterport3DSimulator connectivity format.
    """
    conn_dir = _vln_refs_dir() / "connectivity"
    if not conn_dir.exists():
        return None
    graphs = {}
    for f in conn_dir.glob("*_connectivity.json"):
        scan = f.name.replace("_connectivity.json", "")
        nodes = _read_json(f)
        if not nodes:
            continue
        pos = {}
        idx_to_id = []
        included = []
        for n in nodes:
            vp = n.get("image_id")
            pose = n.get("pose", [])
            idx_to_id.append(vp)
            included.append(bool(n.get("included", True)))
            if len(pose) >= 12:
                pos[vp] = (float(pose[3]), float(pose[7]), float(pose[11]))
        adj = collections.defaultdict(list)
        for i, n in enumerate(nodes):
            unob = n.get("unobstructed", [])
            vp_i = idx_to_id[i]
            for j, ok in enumerate(unob):
                if ok and included[i] and j < len(included) and included[j]:
                    vp_j = idx_to_id[j]
                    if vp_i in pos and vp_j in pos:
                        d = _euclid(pos[vp_i], pos[vp_j])
                        adj[vp_i].append((vp_j, d))
        graphs[scan] = {"pos": pos, "adj": adj}
    return graphs or None


def _euclid(a, b):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


def _geodesic(graph, src, dst):
    """Dijkstra shortest path length on a scan graph; inf if unreachable."""
    if src == dst:
        return 0.0
    pos, adj = graph["pos"], graph["adj"]
    if src not in pos or dst not in pos:
        return float("inf")
    import heapq
    dist = {src: 0.0}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            return d
        if d > dist.get(u, float("inf")):
            continue
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist.get(dst, float("inf"))


def _path_length(graph, traj):
    total = 0.0
    for a, b in zip(traj, traj[1:]):
        total += _geodesic(graph, a, b)
    return total


def _load_gt_paths():
    """{instr_id: {scan, goal_vp, start_vp, shortest_len}} from gt_paths.json."""
    return _read_json(_vln_refs_dir() / "gt_paths.json")


def _load_max_action_step():
    """Read the agent's declared max_action_step from meta.json (default 15)."""
    meta = _read_json(SUBMISSION / f"results/{VLN_VARIANT}/meta.json") or {}
    for k in ("max_action_step", "max_steps", "max_action_len"):
        if k in meta:
            try:
                return int(meta[k])
            except (TypeError, ValueError):
                pass
    return 15


def _compute_vln_metrics():
    """Return (metrics_dict, note) or (None, reason). metrics in percent / metres.

    In addition to SR/OSR/SPL/NE, computes stop-behavior-health signals from
    the per-case ``stopped`` flag + trajectory length vs. max_action_step:
      * HIT_CAP_RATE   -- % of cases that exhausted the step budget
                          (len(traj)-1 >= max_action_step). A healthy MapGPT
                          run rarely runs out of budget; a high rate means the
                          nav LLM almost never emits "A. stop".
      * ACTIVE_STOP_RATE -- % that stopped within budget (report-only; the
                          stopped flag cannot distinguish a genuine arrival
                          stop from any forced/loop-guard stop, so this is
                          surfaced for transparency but not gated on).
      * OSR_SR_GAP     -- OSR - SR (pts). A large gap = the agent passes the
                          goal but fails to stop there (broken stop decision).
    """
    traj_data = _read_json(SUBMISSION / f"results/{VLN_VARIANT}/trajectories.json")
    if not traj_data:
        return None, "trajectories.json not found or unparseable"
    graphs = _load_connectivity()
    if graphs is None:
        return None, "connectivity refs not found (expected refs/r2r_val_unseen_subset/connectivity)"
    gt = _load_gt_paths()
    if gt is None:
        return None, "Required gt_paths.json not found in the task references"

    max_action_step = _load_max_action_step()

    n = 0
    sr = osr = spl = 0.0
    ne_sum = 0.0
    n_hit_cap = 0
    n_active_stop = 0
    for instr_id, ref in gt.items():
        scan = ref.get("scan")
        goal = ref.get("goal_vp")
        shortest = float(ref.get("shortest_len", 0.0) or 0.0)
        graph = graphs.get(scan)
        if graph is None:
            n += 1
            ne_sum += float("inf") if False else 0.0  # missing graph -> count as fail, NE unknown
            continue
        pred = traj_data.get(instr_id)
        n += 1
        if not pred or not pred.get("trajectory"):
            ne_sum += _geodesic(graph, ref.get("start_vp", goal), goal)
            continue
        traj = pred["trajectory"]
        # Stop-behavior tally (independent of GT): a "move" is each edge in the
        # trajectory; len(traj)-1 == number of action steps taken.
        n_moves = max(len(traj) - 1, 0)
        if n_moves >= max_action_step:
            n_hit_cap += 1
        elif pred.get("stopped"):
            n_active_stop += 1
        final_ne = _geodesic(graph, traj[-1], goal)
        ne_sum += final_ne
        success = 1.0 if final_ne <= SUCCESS_THRESHOLD_M else 0.0
        sr += success
        oracle = 1.0 if any(_geodesic(graph, vp, goal) <= SUCCESS_THRESHOLD_M for vp in traj) else 0.0
        osr += oracle
        plen = _path_length(graph, traj)
        if success and plen > 0:
            spl += shortest / max(plen, shortest)
        elif success and shortest == 0:
            spl += 1.0

    if n == 0:
        return None, "no cases in gt_paths.json"
    sr_pct = 100.0 * sr / n
    osr_pct = 100.0 * osr / n
    return {
        "n": n,
        "SR": sr_pct,
        "OSR": osr_pct,
        "SPL": 100.0 * spl / n,
        "NE": ne_sum / n,
        "HIT_CAP_RATE": 100.0 * n_hit_cap / n,
        "ACTIVE_STOP_RATE": 100.0 * n_active_stop / n,
        "OSR_SR_GAP": osr_pct - sr_pct,
        "max_action_step": max_action_step,
    }, f"computed over {n} cases"


_VLN_CACHE = {}

def _vln_metrics_cached():
    if "m" not in _VLN_CACHE:
        _VLN_CACHE["m"] = _compute_vln_metrics()
    return _VLN_CACHE["m"]


def _grade_c_leaf_numerically(leaf_key):
    reported, defaults = _load_reported_metrics()
    if reported is None:
        return 0.0, "reported_metrics.json not found in refs"
    defaults = defaults or _DEFAULT_BEHAVIOR_THRESHOLDS
    metrics, note = _vln_metrics_cached()
    if metrics is None:
        return 0.0, note

    if leaf_key == "sr":
        return metric_score(reported, "SR", metrics["SR"], 0.0, 47.7)
    if leaf_key == "spl":
        return metric_score(reported, "SPL", metrics["SPL"], 0.0, 38.1)
    if leaf_key == "osr":
        return metric_score(reported, "OSR", metrics["OSR"], 0.0, 57.9)
    if leaf_key == "ne":
        return metric_score(reported, "NE", metrics["NE"], 10.03, 5.62, direction="lower")
    if leaf_key == "behavior":
        # Stop-behavior health: both gates must pass. Thresholds come from
        # reported_metrics.json["behavior_thresholds"]; fall back to defaults.
        bt = reported.get("behavior_thresholds") if isinstance(reported, dict) else None
        bt = bt or {}
        cap_max = float(bt.get("cap_hit_rate_max", defaults.get("CAP_HIT_RATE_MAX", 40.0)))
        gap_max = float(bt.get("osr_sr_gap_max", defaults.get("OSR_SR_GAP_MAX", 25.0)))
        cap = float(metrics.get("HIT_CAP_RATE", 100.0))
        gap = float(metrics.get("OSR_SR_GAP", 100.0))
        active = float(metrics.get("ACTIVE_STOP_RATE", 0.0))
        mas = metrics.get("max_action_step", 15)
        cap_ok = cap <= cap_max
        gap_ok = gap <= gap_max
        ok = cap_ok and gap_ok
        msg = (
            f"stop-behavior: HIT_CAP_RATE={cap:.1f}% (need <= {cap_max:.0f}%, "
            f"{'OK' if cap_ok else 'FAIL'}; max_action_step={mas}); "
            f"OSR_SR_GAP={gap:.1f}pt (need <= {gap_max:.0f}pt, "
            f"{'OK' if gap_ok else 'FAIL'}); "
            f"ACTIVE_STOP_RATE={active:.1f}% (report-only). "
            f"A high cap-rate or gap means the nav LLM rarely emits 'A. stop' "
            f"or passes the goal without stopping. NOTE: any non-paper forced-"
            f"stop crutch (loop guard, repeat-vp break) artificially deflates "
            f"these — cross-check §3.A code audit."
        )
        return (1.0 if ok else 0.0), msg

    return 0.0, "unknown leaf key"


# ─── LLM grading ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = JUDGE_PROMPT_MD.read_text().partition('\n\n## Task-specific judging rules\n\n')[0]


def _call_llm_for_leaf(criterion, evidence_text, paper_md, addendum, judge_addendum, retries=2):
    client = get_client()
    if client is None:
        _raise_judge_infrastructure_failure("LLM client unavailable")

    user_content = f"""## Paper
{paper_md[:8000]}

## Task Addendum
{addendum[:3000]}

## Judge Addendum (contains ground truth tolerances)
{judge_addendum[:4000]}

## Submission Evidence Files
{evidence_text}

## Criterion to Grade
{criterion}

Do not assign 0 solely because one requested evidence file is missing or unreadable. Use all available evidence and award partial credit when the criterion is partially supported.

Now evaluate the submission for this criterion. Give SCORE: 0, 0.25, 0.5, 0.75, or 1."""

    for attempt in range(retries + 1):
        try:
            content = _chat_completion(SYSTEM_PROMPT, user_content)
            return parse_judge_score(content), content[:500]
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            _raise_judge_infrastructure_failure(e)
    _raise_judge_infrastructure_failure("judge transport exhausted retries")


# ─── Rubric helpers ───────────────────────────────────────────────────────────

def _load_rubric():
    return _read_json(RUBRIC_JSON)

def _walk_leaves(node):
    if not node.get("sub_tasks"):
        return [node]
    leaves = []
    for c in node["sub_tasks"]:
        leaves.extend(_walk_leaves(c))
    return leaves

def _compute_weight(rubric, target_id):
    def _find(node, target, acc):
        if node.get("id") == target:
            return acc
        children = node.get("sub_tasks", [])
        if not children:
            return None
        total = sum(c.get("weight", 1) for c in children)
        for c in children:
            r = _find(c, target, acc * c.get("weight", 1) / total)
            if r is not None:
                return r
        return None
    return _find(rubric, target_id, 1.0) or 0.0

# ─── Main evaluation ──────────────────────────────────────────────────────────

def evaluate():
    _require_frozen_evidence_root()
    rubric = _load_rubric()
    if rubric is None:
        print("[ERROR] rubric.json not found", file=sys.stderr)
        return {"total_score": 0.0, "leaf_results": {}}

    paper_md = _read_text(PAPER_MD) or "(paper.md not found)"
    addendum = _read_text(ADDENDUM_MD) or "(addendum not found)"
    judge_addendum = JUDGE_PROMPT_MD.read_text().split('\n\n## Task-specific judging rules\n\n', 1)[1]

    leaves = _walk_leaves(rubric)
    print(f"Found {len(leaves)} leaf nodes in rubric")

    leaf_weights = {}
    total_weight = 0.0
    for leaf in leaves:
        w = _compute_weight(rubric, leaf["id"])
        leaf_weights[leaf["id"]] = w
        total_weight += w

    leaf_results = {}
    weighted_sum = 0.0

    for i, leaf in enumerate(leaves):
        lid = leaf["id"]
        criterion = leaf.get("requirements", "")
        evidence_inputs = leaf.get("evidence_inputs", [])
        weight = leaf_weights[lid]

        print(f"\n[{i+1}/{len(leaves)}] {lid[:8]}  w={weight:.4f}")
        print(f"  {criterion[:100]}...")

        if lid in C_LEAF_IDS:
            leaf_key = C_LEAF_IDS[lid]
            score, explanation = _grade_c_leaf_numerically(leaf_key)
            method = "numerical"
            print(f"  [numerical] score={score}  {explanation}")
        else:
            parts = []
            for ei in evidence_inputs:
                parts.append(_read_evidence_file(ei.get("path", ""), ei.get("kind", "text")))
            evidence_text = "\n\n---\n\n".join(parts) if parts else "(no evidence)"
            score_int, explanation = _call_llm_for_leaf(
                criterion=criterion,
                evidence_text=evidence_text,
                paper_md=paper_md,
                addendum=addendum,
                judge_addendum=judge_addendum,
            )
            score = float(score_int)
            method = "llm"
            print(f"  [llm] score={score}")

        leaf_results[lid] = {
            "criterion": criterion[:120],
            "weight": weight,
            "score": score,
            "method": method,
            "explanation": str(explanation)[:500],
        }
        weighted_sum += weight * score

    raw_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    total_score, scoring = finalize_reward(raw_score, leaf_results, C_LEAF_IDS)
    return {"total_score": total_score, "raw_score": raw_score, "total_weight": total_weight,
            "weighted_score_sum": weighted_sum, "scoring": scoring,
            "leaf_results": leaf_results}


def main():
    print("=" * 60)
    print("mapgpt-r2r Evaluator (LLM + numerical)")
    print("=" * 60)
    print(f"  JUDGE_MODEL: {JUDGE_MODEL}")
    print(f"  JUDGE_CHAT_BASE_URL: {JUDGE_CHAT_BASE_URL or '(unset)'}")
    print()

    results = evaluate()

    print("\n--- Leaf Results ---")
    for lid, r in results["leaf_results"].items():
        status = "PASS" if r["score"] >= 0.99 else ("PARTIAL" if r["score"] > 0.01 else "FAIL")
        print(f"  {lid[:8]}  w={r['weight']:.4f}  score={r['score']:.2f}  [{status}]  ({r['method']})")
        print(f"    {r['criterion'][:80]}")

    total = results["total_score"]
    print(f"\n{'='*60}")
    print(f"  TOTAL SCORE: {total:.4f}")
    print(f"{'='*60}")

    reward_path = Path("/logs/verifier/reward.txt")
    reward_path.parent.mkdir(parents=True, exist_ok=True)
    reward_path.write_text(f"{total:.6f}\n")
    print(f"\nReward written: {total:.6f}")

    results_path = Path("/logs/verifier/rubric_results.json")
    results_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Detailed results: {results_path}")


if __name__ == "__main__":
    main()
