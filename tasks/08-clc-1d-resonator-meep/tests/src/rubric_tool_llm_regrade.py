#!/usr/bin/env python3
"""Tool-augmented all-LLM regrade for Meep v2 outputs.

This script is the task's grading engine.  evaluate.py is only a thin Harbor
wrapper around it.

Contract:
- This task directory's rubric.json is the scoring authority.
- This task directory's config/judge_prompt.md, config/public_contract.md, and refs/ are
  supplied to the judge.
- Leaf IDs, hierarchy-derived effective weights, and pass conditions are
  preserved.
- Python tools are read-only evidence tools.  They may summarize/recompute NPZ,
  inspect images, and read text/JSON, but they never assign the final score.
- The LLM must return the final binary score for each leaf.

Default evidence root is a clean replay output tree such as:
  .../trajectory_trial/verifier/candidate_outputs

Example dry run:
  python3 tests/src/rubric_tool_llm_regrade.py \\
    --evidence-root /path/to/verifier/candidate_outputs \\
    --out /tmp/meep_tool_llm_dry --dry-run

Actual run:
  export OPENAI_API_KEY=...
  export OPENAI_BASE_URL=http://.../v1
  python3 tests/src/rubric_tool_llm_regrade.py \\
    --evidence-root /path/to/verifier/candidate_outputs \\
    --out /tmp/meep_tool_llm_gpt55 \\
    --model gpt-5.5 --max-workers 8
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import csv
import dataclasses
import hashlib
import json
import math
import mimetypes
import os
import random
import re
import sys
import textwrap
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np

from structured_evidence_readers import read_json_evidence, read_text_evidence
from meep_evidence_formats import FORMAT_POLICY, NumericEvidence, convert_units
from meep_scientific_bridge import BINDING_SCHEMA, describe_metrics, derive_metrics, tree_digest


THIS_TESTS_DIR = Path(__file__).resolve().parents[1]
THIS_TASK = THIS_TESTS_DIR.parent if THIS_TESTS_DIR.parent != Path("/") else THIS_TESTS_DIR
DEFAULT_TASK_ROOT = THIS_TASK
LOCAL_TESTS = THIS_TESTS_DIR
DEFAULT_JUDGE_PROMPT = LOCAL_TESTS / "config/judge_prompt.md"


def instruction_file(task_root: Path, filename: str) -> Path:
    """Resolve evaluator instruction files for either task-root or tests-only layout."""
    candidates = [
        task_root / "evaluator" / filename,
        task_root / "tests" / filename,
        LOCAL_TESTS / filename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def resolve_refs_dir(task_root: Path) -> Path:
    candidates = [
        task_root / "evaluator" / "refs",
        task_root / "tests" / "refs",
        LOCAL_TESTS / "refs",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_SUFFIXES = {".txt", ".md", ".py", ".sh", ".log", ".csv", ".toml", ".yaml", ".yml"}
NP_SUFFIXES = {".npz", ".npy"}
GENERIC_NPZ_TOOLS = {
    "inspect_npz",
    "inspect_numeric",
    "numeric_array_convert_units",
    "derive_scientific_metrics",
    "npz_list_arrays",
    "npz_array_stats",
    "npz_array_slice",
    "npz_array_histogram",
    "npz_downsample_2d",
    "npz_compare_arrays",
    "npz_check_linear_relation",
}





@dataclasses.dataclass(frozen=True)
class Leaf:
    index: int
    leaf_id: str
    weight: float
    effective_weight: float
    requirements: str
    title: str
    evidence_inputs: list[dict[str, Any]]
    ancestors: list[str]
    metric_operation: str | None = None


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path, max_chars: int) -> str:
    try:
        text = path.read_bytes().decode("utf-8", errors="replace")
    except Exception as exc:
        return f"<<READ_ERROR {type(exc).__name__}: {exc}>>"
    return truncate_judge_text(text, max_chars)


def truncate_judge_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head = max_chars // 2
    tail = max_chars - head
    return text[:head] + f"\n\n<<TRUNCATED {len(text) - max_chars} CHARS FROM MIDDLE>>\n\n" + text[-tail:]


def read_judge_prompt(prompt_path: Path, rules_path: Path, prompt_limit: int, rules_limit: int) -> tuple[str, str]:
    separator = "\n\n## Task-specific judging rules\n\n"
    rules_document = rules_path.read_text(encoding="utf-8")
    _, marker, rules = rules_document.partition(separator)
    if not marker:
        raise ValueError(f"Missing task-specific judging rules: {rules_path}")
    prompt = prompt_path.read_text(encoding="utf-8").partition(separator)[0]
    return truncate_judge_text(prompt, prompt_limit), truncate_judge_text(rules, rules_limit)


def flatten_rubric(root: dict[str, Any]) -> list[Leaf]:
    leaves: list[Leaf] = []

    def visit(node: dict[str, Any], inherited: float, ancestors: list[str]) -> None:
        children = node.get("sub_tasks") or []
        if not children:
            idx = len(leaves) + 1
            leaves.append(
                Leaf(
                    index=idx,
                    leaf_id=str(node.get("id", "")),
                    weight=float(node.get("weight", 0.0)),
                    effective_weight=inherited,
                    requirements=str(node.get("requirements", "")),
                    title=str(node.get("title", node.get("name", ""))),
                    evidence_inputs=list(node.get("evidence_inputs") or []),
                    ancestors=ancestors,
                    metric_operation=node.get("metric_operation"),
                )
            )
            return
        denom = sum(float(child.get("weight", 1.0)) for child in children) or 1.0
        next_ancestors = ancestors + [str(node.get("requirements", ""))]
        for child in children:
            visit(child, inherited * float(child.get("weight", 1.0)) / denom, next_ancestors)

    visit(root, 1.0, [])
    return leaves


def safe_rel(path: Path) -> str:
    return str(path).replace("\\", "/").lstrip("/")


class EvidenceTools:
    def __init__(self, task_root: Path, evidence_root: Path, args: argparse.Namespace):
        self.task_root = task_root
        self.evidence_root = evidence_root
        self.args = args
        self.allowed_roots = [
            evidence_root.resolve(strict=False),
            (task_root / "evaluator" / "refs").resolve(strict=False),
            (task_root / "evaluator").resolve(strict=False),
            (task_root / "solver").resolve(strict=False),
            (task_root / "environment" / "paper").resolve(strict=False),
            LOCAL_TESTS.resolve(strict=False),
        ]

    def _is_allowed(self, path: Path) -> bool:
        resolved = path.resolve(strict=False)
        for root in self.allowed_roots:
            try:
                resolved.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _candidates(self, logical_path: str) -> list[Path]:
        raw = logical_path.strip()
        raw = raw.split("\x00", 1)[0]
        p = Path(raw)
        parts = p.parts
        no_submission = Path(*parts[1:]) if parts and parts[0] == "submission" else p

        candidates: list[Path] = []
        if not p.is_absolute():
            candidates.extend(
                [
                    self.evidence_root / p,
                    self.evidence_root / no_submission,
                    self.evidence_root / "submission" / no_submission,
                    self.evidence_root / "candidate_outputs" / p,
                    self.evidence_root / "candidate_outputs" / no_submission,
                    self.evidence_root / "verifier" / "candidate_outputs" / p,
                    self.evidence_root / "verifier" / "candidate_outputs" / no_submission,
                ]
            )
            if raw.startswith("papers/") and "/judge/refs/" in raw:
                rel = raw.split("/judge/", 1)[1]
                candidates.append(self.task_root / "evaluator" / rel)
                candidates.append(self.task_root / "tests" / rel)
                candidates.append(LOCAL_TESTS / rel)
            if raw.startswith("refs/"):
                candidates.append(self.task_root / "evaluator" / raw)
                candidates.append(self.task_root / "tests" / raw)
                candidates.append(LOCAL_TESTS / raw)
            if raw.startswith("config/"):
                candidates.append(self.task_root / "tests" / raw)
                candidates.append(LOCAL_TESTS / raw)
            if raw.startswith("solver/"):
                candidates.append(self.task_root / raw)
            if raw.startswith("paper_image/"):
                candidates.append(self.task_root / "solver" / raw)
            if raw in {"judge_addendum.md", "evaluator/judge_addendum.md", "tests/judge_addendum.md"}:
                candidates.append(self.task_root / "evaluator" / "config/judge_prompt.md")
                candidates.append(self.task_root / "tests" / "config/judge_prompt.md")
                candidates.append(LOCAL_TESTS / "config/judge_prompt.md")
            if raw in {"rubric.json", "evaluator/rubric.json", "tests/rubric.json"}:
                candidates.append(self.task_root / "evaluator" / "rubric.json")
                candidates.append(self.task_root / "tests" / "rubric.json")
                candidates.append(LOCAL_TESTS / "rubric.json")
        else:
            candidates.append(p)

        seen: set[str] = set()
        out: list[Path] = []
        for c in candidates:
            key = str(c.resolve(strict=False))
            if key not in seen:
                seen.add(key)
                out.append(c)
        return out

    def resolve(self, logical_path: str) -> Path:
        for candidate in self._candidates(logical_path):
            if candidate.exists() and self._is_allowed(candidate):
                if candidate.is_symlink():
                    raise ValueError(f"symlink evidence is not allowed: {logical_path}")
                return candidate
        searched = [str(x) for x in self._candidates(logical_path)[:12]]
        raise FileNotFoundError(f"could not resolve allowed evidence path {logical_path!r}; searched={searched}")

    def list_evidence_files(self, root_kind: str = "submission", max_entries: int = 300, offset: int = 0) -> dict[str, Any]:
        if root_kind not in {"submission", "refs", "paper"}:
            raise ValueError("Unknown evidence root kind")
        if not isinstance(offset, int) or offset < 0 or not isinstance(max_entries, int) or not 1 <= max_entries <= 1000:
            raise ValueError("Use a nonnegative offset and 1 to 1000 entries per page")
        if root_kind == "refs":
            roots = [self.task_root / "evaluator" / "refs", self.task_root / "tests" / "refs", LOCAL_TESTS / "refs"]
        elif root_kind == "paper":
            roots = [self.task_root / "solver", self.task_root / "environment" / "paper"]
        else:
            roots = [self.evidence_root]
        paths = []
        seen = set()
        for root in roots:
            if not root.exists() or not self._is_allowed(root):
                continue
            for path in sorted(root.rglob("*")):
                identity = str(path.absolute())
                if identity in seen or (not path.is_symlink() and not path.is_file()):
                    continue
                seen.add(identity)
                paths.append((root, path))
        rows: list[dict[str, Any]] = []
        for root, path in paths[offset:offset + max_entries]:
                if path.is_symlink():
                    rows.append({"path": str(path), "type": "symlink_rejected"})
                    continue
                if path.is_file():
                    rows.append(
                        {
                            "path": str(path),
                            "relative": str(path.relative_to(root)),
                            "size_bytes": path.stat().st_size,
                            "suffix": path.suffix.lower(),
                            "sha256": sha256_file(path),
                        }
                    )
        end = min(offset + len(rows), len(paths))
        return {"root_kind": root_kind, "files": rows, "offset": offset,
                "returned": len(rows), "total_files": len(paths),
                "next_offset": end if end < len(paths) else None}

    def read_text_file(self, path: str, max_chars: int | None = None, offset: int = 0) -> dict[str, Any]:
        resolved = self.resolve(path)
        if not resolved.is_file():
            raise ValueError(f"not a regular file: {path}")
        maximum = min(max_chars or self.args.max_tool_text_chars, self.args.max_tool_text_chars)
        return read_text_evidence(resolved, maximum, offset)

    def read_json_file(self, path: str, max_chars: int | None = None, pointer: str = "", offset: int = 0) -> dict[str, Any]:
        resolved = self.resolve(path)
        maximum = min(max_chars or self.args.max_tool_text_chars, self.args.max_tool_text_chars)
        return read_json_evidence(resolved, maximum, pointer, offset)

    def inspect_npz(self, path: str, arrays: list[str] | None = None, max_samples: int | None = None) -> dict[str, Any]:
        resolved = self.resolve(path)
        max_samples = min(max_samples or self.args.npz_samples, self.args.npz_samples)
        result = {"path": str(resolved), "sha256": sha256_file(resolved),
                  "size_bytes": resolved.stat().st_size, "format": resolved.suffix.lower(), "arrays": {}}
        try:
            with NumericEvidence(resolved) as evidence:
                keys = evidence.keys()
                result["keys"] = keys
                result["metadata"] = evidence.metadata
                result["rejected_fields"] = dict(evidence.rejected)
                result["missing_requested_arrays"] = [key for key in (arrays or []) if key not in keys]
                for key in (arrays if arrays is not None else keys):
                    if key not in keys:
                        continue
                    try:
                        result["arrays"][key] = self._array_summary(evidence.get(key), max_samples)
                    except (ValueError, TypeError) as error:
                        result["rejected_fields"][key] = str(error)
                if not result["arrays"]:
                    result["error"] = "No requested numeric data could be inspected; investigate evidence mapping before scoring."
        except Exception as error:
            result["error"] = f"{type(error).__name__}: {error}"
        return result

    def _load_np_array(self, path: str, array: str | None = None) -> tuple[Path, str, np.ndarray]:
        resolved = self.resolve(path)
        with NumericEvidence(resolved) as evidence:
            keys = evidence.keys()
            if array is None:
                if len(keys) != 1:
                    raise ValueError("An exact dataset name is required when the file has multiple datasets")
                array = keys[0]
            return resolved, array, np.asarray(evidence.get(array))

    def numeric_array_convert_units(self, path: str, array: str, source_unit: str, target_unit: str) -> dict[str, Any]:
        resolved, key, values = self._load_np_array(path, array)
        converted = convert_units(values, source_unit, target_unit)
        return {"path": str(resolved), "sha256": sha256_file(resolved), "array": key,
                "source_unit": source_unit, "target_unit": target_unit,
                "unit_provenance": "Judge must verify declared units from the original evidence; no units were inferred.",
                "summary": self._array_summary(converted, self.args.npz_samples)}

    def _numeric_view(self, arr: np.ndarray, value_mode: str) -> np.ndarray:
        a = np.asarray(arr)
        mode = value_mode or "auto"
        if mode == "auto":
            mode = "abs" if np.iscomplexobj(a) else "value"
        if mode == "abs":
            return np.abs(a)
        if mode == "real":
            return np.real(a)
        if mode == "imag":
            return np.imag(a)
        if mode == "complex":
            return a
        if mode == "value":
            if np.iscomplexobj(a):
                raise ValueError("value_mode='value' cannot serialize complex arrays; use abs/real/imag")
            return a
        raise ValueError(f"unsupported value_mode: {value_mode}")

    def _jsonable_value(self, x: Any) -> Any:
        if isinstance(x, np.generic):
            x = x.item()
        if isinstance(x, complex):
            return {"real": float(x.real), "imag": float(x.imag)}
        if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
            return str(x)
        if isinstance(x, (str, int, float, bool)) or x is None:
            return x
        return str(x)

    def _jsonable_array_limited(self, arr: np.ndarray, max_items: int) -> Any:
        a = np.asarray(arr)
        if a.size > max_items:
            raise ValueError(f"requested slice has {a.size} items, exceeds max_items={max_items}")
        return np.vectorize(self._jsonable_value, otypes=[object])(a).tolist()

    def npz_list_arrays(self, path: str) -> dict[str, Any]:
        inspected = self.inspect_npz(path)
        inspected["arrays"] = [{"name": key, **summary} for key, summary in inspected["arrays"].items()]
        return inspected

    def npz_array_stats(
        self,
        path: str,
        array: str,
        value_mode: str = "auto",
        percentiles: list[float] | None = None,
    ) -> dict[str, Any]:
        p, key, arr = self._load_np_array(path, array)
        vals = np.asarray(self._numeric_view(arr, value_mode))
        out: dict[str, Any] = {
            "path": str(p),
            "array": key,
            "sha256": sha256_file(p),
            "dtype": str(arr.dtype),
            "shape": list(arr.shape),
            "size": int(arr.size),
            "value_mode": value_mode,
        }
        try:
            if np.iscomplexobj(vals):
                out["complex_stats_interpretation"] = "statistics computed on absolute values because value_mode produced complex values"
                vals = np.abs(vals)
            finite = np.isfinite(vals)
            out["finite_count"] = int(finite.sum())
            out["nonfinite_count"] = int((~finite).sum())
            out["nonzero_count"] = int(np.count_nonzero(vals[finite])) if finite.any() else 0
            if finite.any():
                vf = vals[finite].astype(float)
                out.update(
                    {
                        "min": float(np.min(vf)),
                        "max": float(np.max(vf)),
                        "mean": float(np.mean(vf)),
                        "std": float(np.std(vf)),
                        "rms": float(np.sqrt(np.mean(vf**2))),
                        "l1_mean_abs": float(np.mean(np.abs(vf))),
                    }
                )
                pct = percentiles if percentiles is not None else [0, 1, 5, 25, 50, 75, 95, 99, 100]
                pct = [float(x) for x in pct if 0 <= float(x) <= 100][:21]
                out["percentiles"] = {str(x): float(np.percentile(vf, x)) for x in pct}
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def npz_array_slice(
        self,
        path: str,
        array: str,
        value_mode: str = "auto",
        slices: list[dict[str, int | None]] | None = None,
        flat_start: int | None = None,
        flat_count: int = 20,
        max_items: int = 400,
    ) -> dict[str, Any]:
        p, key, arr = self._load_np_array(path, array)
        vals = np.asarray(self._numeric_view(arr, value_mode))
        max_items = min(int(max_items), int(self.args.max_npz_slice_items))
        out: dict[str, Any] = {
            "path": str(p),
            "array": key,
            "sha256": sha256_file(p),
            "dtype": str(arr.dtype),
            "shape": list(arr.shape),
            "value_mode": value_mode,
        }
        try:
            if slices is not None:
                spec = []
                for dim in range(vals.ndim):
                    item = slices[dim] if dim < len(slices) else {}
                    spec.append(slice(item.get("start"), item.get("stop"), item.get("step")))
                view = vals[tuple(spec)]
                out["selection"] = {"slices": slices}
            else:
                start = int(flat_start or 0)
                count = min(max(0, int(flat_count)), max_items)
                view = vals.reshape(-1)[start : start + count]
                out["selection"] = {"flat_start": start, "flat_count": count}
            out["selected_shape"] = list(np.asarray(view).shape)
            out["values"] = self._jsonable_array_limited(np.asarray(view), max_items)
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def npz_array_histogram(
        self,
        path: str,
        array: str,
        value_mode: str = "auto",
        bins: int = 20,
        range_min: float | None = None,
        range_max: float | None = None,
    ) -> dict[str, Any]:
        p, key, arr = self._load_np_array(path, array)
        vals = np.asarray(self._numeric_view(arr, value_mode)).reshape(-1)
        complex_hist = bool(np.iscomplexobj(vals))
        if complex_hist:
            vals = np.abs(vals)
        bins = min(max(1, int(bins)), 100)
        out: dict[str, Any] = {
            "path": str(p),
            "array": key,
            "sha256": sha256_file(p),
            "shape": list(arr.shape),
            "value_mode": value_mode,
            "bins": bins,
        }
        try:
            finite = vals[np.isfinite(vals)].astype(float)
            if finite.size == 0:
                raise ValueError("no finite values")
            if complex_hist:
                out["complex_histogram_interpretation"] = "histogram computed on absolute values because value_mode produced complex values"
            hist_range = None
            if range_min is not None or range_max is not None:
                lo = float(range_min) if range_min is not None else float(np.min(finite))
                hi = float(range_max) if range_max is not None else float(np.max(finite))
                hist_range = (lo, hi)
            counts, edges = np.histogram(finite, bins=bins, range=hist_range)
            out["finite_count"] = int(finite.size)
            out["counts"] = [int(x) for x in counts.tolist()]
            out["edges"] = [float(x) for x in edges.tolist()]
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def npz_downsample_2d(
        self,
        path: str,
        array: str,
        value_mode: str = "auto",
        max_rows: int = 32,
        max_cols: int = 32,
    ) -> dict[str, Any]:
        p, key, arr = self._load_np_array(path, array)
        vals = np.asarray(self._numeric_view(arr, value_mode))
        max_rows = min(max(1, int(max_rows)), 80)
        max_cols = min(max(1, int(max_cols)), 80)
        out: dict[str, Any] = {
            "path": str(p),
            "array": key,
            "sha256": sha256_file(p),
            "dtype": str(arr.dtype),
            "shape": list(arr.shape),
            "value_mode": value_mode,
        }
        try:
            if vals.ndim != 2:
                raise ValueError(f"npz_downsample_2d requires a 2-D array, got shape {vals.shape}")
            row_idx = np.unique(np.linspace(0, vals.shape[0] - 1, min(max_rows, vals.shape[0])).round().astype(int))
            col_idx = np.unique(np.linspace(0, vals.shape[1] - 1, min(max_cols, vals.shape[1])).round().astype(int))
            sampled = vals[np.ix_(row_idx, col_idx)]
            out["row_indices"] = [int(x) for x in row_idx.tolist()]
            out["col_indices"] = [int(x) for x in col_idx.tolist()]
            out["sampled_shape"] = list(sampled.shape)
            out["values"] = self._jsonable_array_limited(sampled, max_rows * max_cols)
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def npz_compare_arrays(
        self,
        path_a: str,
        array_a: str,
        path_b: str,
        array_b: str,
        value_mode: str = "auto",
        rtol: float = 1e-7,
        atol: float = 0.0,
    ) -> dict[str, Any]:
        pa, ka, aa = self._load_np_array(path_a, array_a)
        pb, kb, bb = self._load_np_array(path_b, array_b)
        va = np.asarray(self._numeric_view(aa, value_mode))
        vb = np.asarray(self._numeric_view(bb, value_mode))
        out: dict[str, Any] = {
            "path_a": str(pa),
            "array_a": ka,
            "sha256_a": sha256_file(pa),
            "path_b": str(pb),
            "array_b": kb,
            "sha256_b": sha256_file(pb),
            "shape_a": list(va.shape),
            "shape_b": list(vb.shape),
            "value_mode": value_mode,
            "rtol": rtol,
            "atol": atol,
        }
        try:
            if va.shape != vb.shape:
                out["same_shape"] = False
                return out
            out["same_shape"] = True
            diff = va - vb
            finite = np.isfinite(diff)
            out["finite_diff_count"] = int(finite.sum())
            if finite.any():
                d_abs = np.abs(diff[finite]).astype(float)
                out["max_abs_diff"] = float(np.max(d_abs))
                out["mean_abs_diff"] = float(np.mean(d_abs))
                out["rms_diff"] = float(np.sqrt(np.mean(d_abs**2)))
                out["allclose"] = bool(np.allclose(va, vb, rtol=float(rtol), atol=float(atol)))
                a_flat = np.abs(va.reshape(-1)) if np.iscomplexobj(va) else va.reshape(-1)
                b_flat = np.abs(vb.reshape(-1)) if np.iscomplexobj(vb) else vb.reshape(-1)
                mask = np.isfinite(a_flat) & np.isfinite(b_flat)
                if mask.sum() >= 2 and np.std(a_flat[mask]) > 0 and np.std(b_flat[mask]) > 0:
                    out["pearson_corr"] = float(np.corrcoef(a_flat[mask].astype(float), b_flat[mask].astype(float))[0, 1])
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def npz_check_linear_relation(
        self,
        path: str,
        terms: list[dict[str, Any]],
        value_mode: str = "auto",
        rtol: float = 1e-7,
        atol: float = 1e-10,
    ) -> dict[str, Any]:
        if not terms:
            raise ValueError("terms must be nonempty")
        p = self.resolve(path)
        out: dict[str, Any] = {
            "path": str(p),
            "sha256": sha256_file(p),
            "terms": terms,
            "value_mode": value_mode,
            "rtol": rtol,
            "atol": atol,
        }
        try:
            arrays: list[np.ndarray] = []
            coeffs: list[float] = []
            use_raw_complex = value_mode == "complex" or (value_mode == "auto")
            for term in terms:
                arr_name = str(term["array"])
                coeff = float(term.get("coefficient", 1.0))
                _, _, arr = self._load_np_array(str(p), arr_name)
                if use_raw_complex:
                    arrays.append(np.asarray(arr))
                else:
                    arrays.append(np.asarray(self._numeric_view(arr, value_mode)))
                coeffs.append(coeff)
            shapes = [a.shape for a in arrays]
            out["shapes"] = [list(s) for s in shapes]
            if len(set(shapes)) != 1:
                out["same_shape"] = False
                return out
            total = np.zeros_like(arrays[0], dtype=np.result_type(*arrays, float))
            for coeff, arr in zip(coeffs, arrays):
                total = total + coeff * arr
            residual_abs = np.abs(total)
            finite = np.isfinite(residual_abs)
            out["same_shape"] = True
            out["finite_count"] = int(finite.sum())
            if finite.any():
                vals = residual_abs[finite].astype(float)
                out["max_abs_residual"] = float(np.max(np.abs(vals)))
                out["mean_abs_residual"] = float(np.mean(np.abs(vals)))
                out["rms_residual"] = float(np.sqrt(np.mean(vals**2)))
                out["allclose_zero"] = bool(np.allclose(total, 0.0, rtol=float(rtol), atol=float(atol)))
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    def _array_summary(self, arr: Any, max_samples: int) -> dict[str, Any]:
        a = np.asarray(arr)
        out: dict[str, Any] = {"dtype": str(a.dtype), "shape": list(a.shape), "size": int(a.size), "nbytes": int(a.nbytes)}
        if a.size == 0:
            return out
        flat = a.reshape(-1)
        if np.iscomplexobj(a):
            vals = np.abs(flat)
            out["complex"] = True
            out["sample"] = [{"real": float(np.real(x)), "imag": float(np.imag(x))} for x in flat[:max_samples]]
        else:
            vals = flat
            out["sample"] = [self._scalar(x) for x in flat[:max_samples]]
        try:
            finite = np.isfinite(vals)
            out["finite_count"] = int(finite.sum())
            out["nonfinite_count"] = int((~finite).sum())
            if finite.any():
                vf = vals[finite].astype(float)
                out["min"] = float(np.min(vf))
                out["max"] = float(np.max(vf))
                out["mean"] = float(np.mean(vf))
                out["std"] = float(np.std(vf))
                out["nonzero_count"] = int(np.count_nonzero(vf))
        except Exception as exc:
            out["stats_error"] = f"{type(exc).__name__}: {exc}"
        return out

    def _scalar(self, x: Any) -> Any:
        if isinstance(x, np.generic):
            x = x.item()
        if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
            return str(x)
        if isinstance(x, (str, int, float, bool)) or x is None:
            return x
        return str(x)

    def inspect_image(self, path: str) -> dict[str, Any]:
        p = self.resolve(path)
        out: dict[str, Any] = {
            "path": str(p),
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "suffix": p.suffix.lower(),
        }
        try:
            from PIL import Image

            with Image.open(p) as im:
                out.update({"width": im.width, "height": im.height, "mode": im.mode, "format": im.format})
        except Exception as exc:
            out["image_probe_error"] = f"{type(exc).__name__}: {exc}"
        return out

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "describe_scientific_metrics":
            return describe_metrics(instruction_file(self.task_root, "src/scientific_metrics.py"))
        if name == "derive_scientific_metrics":
            return derive_metrics(self, instruction_file(self.task_root, "src/scientific_metrics.py"), **arguments)
        if name == "inspect_numeric":
            return self.inspect_npz(**arguments)
        if name == "numeric_array_convert_units":
            return self.numeric_array_convert_units(**arguments)
        if name == "list_evidence_files":
            return self.list_evidence_files(**arguments)
        if name == "read_text_file":
            return self.read_text_file(**arguments)
        if name == "read_json_file":
            return self.read_json_file(**arguments)
        if name == "inspect_npz":
            return self.inspect_npz(**arguments)
        if name == "npz_list_arrays":
            return self.npz_list_arrays(**arguments)
        if name == "npz_array_stats":
            return self.npz_array_stats(**arguments)
        if name == "npz_array_slice":
            return self.npz_array_slice(**arguments)
        if name == "npz_array_histogram":
            return self.npz_array_histogram(**arguments)
        if name == "npz_downsample_2d":
            return self.npz_downsample_2d(**arguments)
        if name == "npz_compare_arrays":
            return self.npz_compare_arrays(**arguments)
        if name == "npz_check_linear_relation":
            return self.npz_check_linear_relation(**arguments)
        if name == "inspect_image":
            return self.inspect_image(**arguments)
        raise ValueError(f"unknown tool: {name}")


def read_refs_text(task_root: Path, max_chars: int) -> str:
    refs_root = resolve_refs_dir(task_root)
    blocks: list[str] = []
    for path in sorted(refs_root.rglob("*")) if refs_root.exists() else []:
        if not path.is_file() or path.suffix.lower() in IMAGE_SUFFIXES:
            continue
        blocks.append(f"### refs/{path.relative_to(refs_root)}\n{read_text(path, max_chars)}")
    local_refs = LOCAL_TESTS / "refs"
    if local_refs.exists():
        for path in sorted(local_refs.rglob("*")):
            if not path.is_file() or path.suffix.lower() in IMAGE_SUFFIXES:
                continue
            blocks.append(f"### local tests/refs/{path.relative_to(local_refs)}\n{read_text(path, max_chars)}")
    text = "\n\n".join(blocks)
    if len(text) <= max_chars:
        return text
    return text[: max_chars // 2] + "\n<<REFS_TRUNCATED>>\n" + text[-max_chars // 2 :]


def tool_specs() -> list[dict[str, Any]]:
    def tool(name: str, description: str, props: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": props, "required": required or [], "additionalProperties": False},
            },
        }

    return [
        tool(
            "describe_scientific_metrics",
            "Describe reviewed task-specific numerical operations and their required quantities/units. This reads private evaluator code, not candidate code.",
            {},
        ),
        tool(
            "derive_scientific_metrics",
            "Recompute a reviewed scientific operation from explicit candidate array bindings across NPZ/NPY/JSON/CSV/TSV/HDF5. Every quantity binding needs path, array, source_unit, target_unit and unit_evidence (a path/quote in candidate text, or an exact numeric metadata_key). Context supplies documented geometry/analysis choices, never invented result arrays. Returns computed metrics plus hashes, not an assumed model score.",
            {"operation": {"type": "string"}, "bindings": {"type": "object", "additionalProperties": BINDING_SCHEMA}, "context": {"type": "object"}},
            ["operation", "bindings"],
        ),
        tool(
            "inspect_numeric",
            "Inspect numeric evidence in NPZ, NPY, JSON, CSV, TSV or HDF5. Lists exact dataset keys and metadata without changing input files. Nested JSON keys use JSON pointers; never guess a variant from a terminal key.",
            {"path": {"type": "string"}, "arrays": {"type": "array", "items": {"type": "string"}},
             "max_samples": {"type": "integer", "minimum": 1, "maximum": 20}},
            ["path"],
        ),
        tool(
            "numeric_array_convert_units",
            "Summarize an array after explicit dimension-compatible unit conversion. Verify source units in evidence first; no phase, normalization or dimensionless Meep unit is inferred.",
            {"path": {"type": "string"}, "array": {"type": "string"},
             "source_unit": {"type": "string"}, "target_unit": {"type": "string"}},
            ["path", "array", "source_unit", "target_unit"],
        ),
        tool(
            "list_evidence_files",
            "List allowed files with pagination. Follow next_offset until null before concluding submission evidence is absent.",
            {
                "root_kind": {"type": "string", "enum": ["submission", "refs", "paper"]},
                "max_entries": {"type": "integer", "minimum": 1, "maximum": 1000},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        tool(
            "read_text_file",
            "Read text with explicit character-offset pagination. Follow next_offset to inspect remaining content.",
            {"path": {"type": "string"}, "max_chars": {"type": "integer", "minimum": 1, "maximum": 120000},
             "offset": {"type": "integer", "minimum": 0, "maximum": 67108864}},
            ["path"],
        ),
        tool(
            "read_json_file",
            "Parse bounded JSON completely; select a subtree with an exact JSON pointer. Oversized subtrees return child pointers, not invalid truncated JSON. Follow next_offset for remaining children.",
            {"path": {"type": "string"}, "max_chars": {"type": "integer", "minimum": 1, "maximum": 120000},
             "pointer": {"type": "string"}, "offset": {"type": "integer", "minimum": 0}},
            ["path"],
        ),
        tool(
            "inspect_npz",
            "Inspect a numeric file (NPZ/NPY/JSON/CSV/TSV/HDF5): keys, dtype, shape, finite stats, and a small sample. Does not return full arrays.",
            {
                "path": {"type": "string"},
                "arrays": {"type": "array", "items": {"type": "string"}},
                "max_samples": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            ["path"],
        ),
        tool(
            "npz_list_arrays",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): list arrays with dtype, shape, size, byte size, and complex flag.",
            {"path": {"type": "string"}},
            ["path"],
        ),
        tool(
            "npz_array_stats",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): compute finite counts, min/max/mean/std/RMS/nonzero count and percentiles for one array. For complex arrays choose value_mode abs, real, or imag.",
            {
                "path": {"type": "string"},
                "array": {"type": "string"},
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "percentiles": {"type": "array", "items": {"type": "number"}, "maxItems": 21},
            },
            ["path", "array"],
        ),
        tool(
            "npz_array_slice",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): return a small slice or flat window from one array. Output is capped; use this for exact local values, heads, tails, and small grids.",
            {
                "path": {"type": "string"},
                "array": {"type": "string"},
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "slices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": ["integer", "null"]},
                            "stop": {"type": ["integer", "null"]},
                            "step": {"type": ["integer", "null"]},
                        },
                        "additionalProperties": False,
                    },
                },
                "flat_start": {"type": "integer", "minimum": 0},
                "flat_count": {"type": "integer", "minimum": 0, "maximum": 2000},
                "max_items": {"type": "integer", "minimum": 1, "maximum": 2000},
            },
            ["path", "array"],
        ),
        tool(
            "npz_array_histogram",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): compute a bounded histogram for one array, using value/abs/real/imag view.",
            {
                "path": {"type": "string"},
                "array": {"type": "string"},
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "bins": {"type": "integer", "minimum": 1, "maximum": 100},
                "range_min": {"type": ["number", "null"]},
                "range_max": {"type": ["number", "null"]},
            },
            ["path", "array"],
        ),
        tool(
            "npz_downsample_2d",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): downsample a 2-D array to a small grid for LLM inspection without returning the full array.",
            {
                "path": {"type": "string"},
                "array": {"type": "string"},
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "max_rows": {"type": "integer", "minimum": 1, "maximum": 80},
                "max_cols": {"type": "integer", "minimum": 1, "maximum": 80},
            },
            ["path", "array"],
        ),
        tool(
            "npz_compare_arrays",
            "Generic numeric-file tool (NPZ/NPY/JSON/CSV/TSV/HDF5): compare two arrays from same or different files using max/RMS difference, allclose, and correlation when possible.",
            {
                "path_a": {"type": "string"},
                "array_a": {"type": "string"},
                "path_b": {"type": "string"},
                "array_b": {"type": "string"},
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "rtol": {"type": "number"},
                "atol": {"type": "number"},
            },
            ["path_a", "array_a", "path_b", "array_b"],
        ),
        tool(
            "npz_check_linear_relation",
            "Generic NPZ tool: check whether a linear relation among arrays in one file is approximately zero, e.g. hz_total - hz_incident - hz_scattered = 0.",
            {
                "path": {"type": "string"},
                "terms": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "properties": {
                            "array": {"type": "string"},
                            "coefficient": {"type": "number"},
                        },
                        "required": ["array"],
                        "additionalProperties": False,
                    },
                },
                "value_mode": {"type": "string", "enum": ["auto", "value", "abs", "real", "imag", "complex"]},
                "rtol": {"type": "number"},
                "atol": {"type": "number"},
            },
            ["path", "terms"],
        ),
        tool(
            "inspect_image",
            "Inspect image metadata for an allowed candidate, reference, or paper image.",
            {"path": {"type": "string"}},
            ["path"],
        ),
    ]


def likely_required_tools(leaf: Leaf) -> set[str]:
    paths = " ".join(str(x.get("path", "")) for x in leaf.evidence_inputs).lower()
    req = leaf.requirements.lower()
    needed: set[str] = set()
    if any(suffix in paths for suffix in NP_SUFFIXES):
        needed.add("inspect_npz")
    if any(suffix in paths for suffix in IMAGE_SUFFIXES):
        needed.add("inspect_image")
    if ".json" in paths:
        needed.add("read_json_file")
    if any(suffix in paths for suffix in [".py", ".md", ".log", ".csv", ".sh", ".txt", ".toml", ".yaml", ".yml"]):
        needed.add("read_text_file")
    # Require NPZ inspection only for explicit NPZ evidence/requirements.
    # Do not infer it from generic words like "array"; e.g. "array_size"
    # structure leaves and "uniform-array" run logs are JSON/text evidence.
    if "npz" in req:
        needed.add("inspect_npz")
    # Do not infer an image requirement only from rubric words such as
    # "field map", "plot", or "figure".  Many leaves use those words for
    # raw NPZ arrays or structural/log evidence.  Image inspection is enforced
    # above only when the routed evidence explicitly names an image file.
    return needed


def image_attachment(path: Path, label: str, max_bytes: int, tools: EvidenceTools) -> dict[str, Any] | None:
    try:
        if not path.is_file() or path.is_symlink() or not tools._is_allowed(path):
            return None
        data = path.read_bytes()
    except Exception:
        return None
    if len(data) > max_bytes:
        return None
    return {
        "label": label,
        "path": str(path),
        "media_type": mimetypes.guess_type(str(path))[0] or ("image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"),
        "b64": base64.b64encode(data).decode("ascii"),
        "sha256": sha256_file(path),
        "bytes": len(data),
    }


def collect_image_attachments(leaf: Leaf, tools: EvidenceTools, args: argparse.Namespace) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    leaf_has_image = any(
        Path(str(item.get("path", ""))).suffix.lower() in IMAGE_SUFFIXES or str(item.get("kind", "")).lower() == "image"
        for item in leaf.evidence_inputs
    )
    if args.attach_candidate_images:
        for item in leaf.evidence_inputs:
            logical = str(item.get("path", ""))
            if Path(logical).suffix.lower() in IMAGE_SUFFIXES or str(item.get("kind", "")).lower() == "image":
                try:
                    p = tools.resolve(logical)
                    img = image_attachment(p, f"candidate:{logical}", args.max_image_bytes, tools)
                    if img:
                        images.append(img)
                except Exception:
                    continue
    if args.attach_ref_images and (leaf_has_image or args.attach_images_for_all):
        ref_roots = [tools.task_root / "evaluator" / "refs", LOCAL_TESTS / "refs"]
        for root in ref_roots:
            if root.exists():
                for p in sorted(root.rglob("*")):
                    if p.suffix.lower() in IMAGE_SUFFIXES:
                        img = image_attachment(p, f"evaluator_ref:{p.name}", args.max_image_bytes, tools)
                        if img:
                            images.append(img)
    if args.attach_paper_images and (leaf_has_image or args.attach_images_for_all):
        for p in sorted((tools.task_root / "solver" / "paper_image").glob("*"))[: args.max_paper_images]:
            if p.suffix.lower() in IMAGE_SUFFIXES:
                img = image_attachment(p, f"paper_image:{p.name}", args.max_image_bytes, tools)
                if img:
                    images.append(img)
    # Deduplicate by sha256.
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for img in images:
        key = str(img.get("sha256") or img.get("path"))
        if key not in seen:
            seen.add(key)
            out.append(img)
    return out[: args.max_attached_images_per_leaf]


def build_initial_prompt(
    leaf: Leaf,
    task_root: Path,
    evidence_root: Path,
    judge_addendum: str,
    refs_text: str,
    judge_prompt_text: str,
    args: argparse.Namespace,
) -> str:
    paper_candidates = [
        task_root / "environment" / "paper" / "paper.md",
        task_root / "solver" / "paper.md",
        task_root / "paper.md",
    ]
    addendum_candidates = [
        task_root / "environment" / "paper" / "addendum.md",
        task_root / "solver" / "addendum.md",
        task_root / "addendum.md",
    ]
    paper_md = next((p for p in paper_candidates if p.exists()), paper_candidates[0])
    solver_addendum = next((p for p in addendum_candidates if p.exists()), addendum_candidates[0])
    required_tools = sorted(likely_required_tools(leaf))
    return textwrap.dedent(
        f"""
        You are an independent PaperBench High-Difficulty and Expanded Tasks Meep judge. Score exactly one Meep v2 rubric leaf.

        Format-invariance policy (also applies to every example path in the leaf):
        {FORMAT_POLICY}

        Non-negotiable rules:
        - The rubric leaf and pass condition below are the scoring authority.
        - config/judge_prompt.md, config/public_contract.md, and refs/ below are private evaluator instructions from this task's tests directory.
        - Use tool calls to inspect cited evidence. Do not infer file contents from paths.
        - For numeric-result leaves, inspect actual arrays with inspect_numeric or the generic numeric tools before scoring:
          inspect_npz, npz_list_arrays, npz_array_stats, npz_array_slice, npz_array_histogram,
          npz_downsample_2d, npz_compare_arrays, or npz_check_linear_relation.  Use multiple NPZ/CSV/JSON/image tools when needed; never return or request entire large arrays.
        - For spatial/plot leaves, inspect the actual image OR equivalent raw spatial data with coordinates and interpretation. Missing PNG alone is never a failure. Metadata or a nonempty file alone is insufficient.
        - Use describe_scientific_metrics and derive_scientific_metrics for reviewed numerical operations. Bind only candidate arrays and verify units/variant mappings from source evidence. For documented split real/imaginary arrays in one file, use array plus imaginary_array and cite complex_evidence (path/quote or real_plus_i_imag metadata); never guess absent phase. For metric_operation leaves, a passing verdict requires the specified operation to have actually succeeded. Tools recompute values; the final verdict must also check the leaf scientific requirements.
        - If scientific evidence is genuinely absent after discovery, contradictory, or incorrect, score the affected leaf accordingly. An evaluator format/read error is a judge error, not a model failure.
        - If replay did not execute, no real Meep evidence exists, or the candidate appears to read evaluator refs/targets, close affected leaves to 0, but do not globally zero unrelated leaves.
        - Return final JSON only after tool use is complete.

        Required output JSON:
        {{
          "score": 0 or 1,
          "confidence": "low|medium|high",
          "tool_calls_used": ["tool_name", "..."],
          "evidence_summary": "specific files/arrays/images/logs actually inspected",
          "fatal_flags": ["..."],
          "evidence_access": "ok|missing|tool_error",
          "reason": "short strict reason tied to the scientific leaf pass condition, never cosmetic layout"
        }}

        Rubric leaf:
        - index: {leaf.index}
        - id: {leaf.leaf_id}
        - title: {leaf.title}
        - effective_weight: {leaf.effective_weight:.12f}
        - requirement/pass condition: {leaf.requirements}
        - ancestors: {json.dumps(leaf.ancestors, ensure_ascii=False, indent=2)}
        - evidence_inputs: {json.dumps(leaf.evidence_inputs, ensure_ascii=False, indent=2)}
        - tools expected for this leaf: {json.dumps(required_tools, ensure_ascii=False)}
        - required scientific metric operation, if any: {leaf.metric_operation}

        Evidence root:
        {evidence_root}

        Local config/judge_prompt.md:
        {judge_prompt_text[: args.max_judge_prompt_chars]}

        Task-specific rules from config/judge_prompt.md:
        {judge_addendum}

        Frozen public contract for tests-only layouts:
        {read_text(instruction_file(task_root, "config/public_contract.md"), args.max_solver_addendum_chars)}

        Local refs/:
        {refs_text}

        Paper text excerpt:
        {read_text(paper_md, args.max_paper_chars) if paper_md.exists() else "<<paper.md missing>>"}

        Solver addendum excerpt:
        {read_text(solver_addendum, args.max_solver_addendum_chars) if solver_addendum.exists() else "<<solver addendum missing>>"}
        """
    ).strip()



FORCE_FINAL_INSTRUCTION = (
    "TOOL BUDGET EXHAUSTED. You have now used the full tool-call budget for this "
    "leaf. Do not request any more tools. Decide now, using only the evidence you "
    "have already inspected, and return the final JSON object only. If what you "
    "inspected does satisfy the leaf pass condition, return score 1. If the "
    "evidence you gathered is genuinely insufficient or contradicts the pass "
    "condition, return score 0 and say exactly why in `reason`. Never return an "
    "empty message."
)

REASK_FINAL_JSON = (
    "Your previous message could not be parsed as JSON. Return the final verdict "
    "again as a single raw JSON object and nothing else: no prose, no explanation "
    "outside the object, no markdown fences, no tool calls. Required keys: score "
    "(0 or 1), confidence, tool_calls_used, evidence_summary, fatal_flags, reason."
)

EVIDENCE_BUDGET_NOTE = (
    "NOTE: the cumulative evidence budget for this leaf is nearly exhausted, so "
    "further tool results will be heavily truncated. Inspect only what you still "
    "strictly need, then emit the final JSON."
)

RETRYABLE_HTTP_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524}


class ToolBudget:
    """Bound cumulative tool-result bytes so deep leaves cannot blow the context.

    Per-call truncation stays generous; only once the whole-leaf budget is
    spent do results get squeezed to the floor, and the judge is told so.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.total = max(0, int(args.max_total_tool_chars))
        self.per_call = max(1, int(args.max_tool_result_chars))
        self.floor = max(1, min(int(args.min_tool_result_chars), self.per_call))
        self.spent = 0
        self.squeezed = False

    def render(self, result: Any) -> str:
        text = json.dumps(result, ensure_ascii=False, default=str)
        cap = self.per_call
        if self.total:
            if self.spent >= self.total:
                cap = self.floor
                self.squeezed = True
            elif self.spent + cap > self.total:
                cap = max(self.floor, self.total - self.spent)
                self.squeezed = True
        if len(text) > cap:
            text = text[:cap] + f"\n<<truncated: {len(text)} chars total, cap {cap}>>"
        self.spent += len(text)
        return text


def retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    try:
        value = exc.headers.get("Retry-After")
    except Exception:
        return None
    if not value:
        return None
    try:
        return float(str(value).strip())
    except Exception:
        return None


def retry_delay(args: argparse.Namespace, attempt: int, retry_after: float | None) -> float:
    if retry_after is not None and retry_after >= 0:
        return min(retry_after, 120.0)
    base = float(args.retry_sleep) * attempt
    return base + random.uniform(0.0, min(base, 8.0))


def blank_content(message: Any) -> bool:
    if not isinstance(message, dict):
        return True
    return not content_to_text(message.get("content", "")).strip()




def parse_final_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(x.get("text", "")) for x in content if isinstance(x, dict))
    return str(content)


def call_openai_tool_judge(
    packet: dict[str, Any],
    tools_runner: EvidenceTools,
    args: argparse.Namespace,
    trace_sink: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    api_key = args.api_key or os.environ.get("JUDGE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base = args.api_base or os.environ.get("JUDGE_BASE_URL") or os.environ.get("JUDGE_API_BASE") or os.environ.get("OPENAI_BASE_URL")
    if not base:
        raise RuntimeError("Missing explicitly configured judge endpoint; refusing silent fallback routing")
    if not api_key:
        raise RuntimeError("missing API key: set OPENAI_API_KEY/JUDGE_API_KEY or pass --api-key")

    prompt = packet["prompt"]
    images = packet["attached_images"]
    user_content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for img in images:
        user_content.append({"type": "text", "text": f"Attached image: {img['label']} path={img['path']} sha256={img['sha256']}"})
        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['media_type']};base64,{img['b64']}",
                    "detail": args.image_detail,
                },
            }
        )
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are a strict Meep paper-reproduction judge. Use tools when evidence must be read. Final score is binary.",
        },
        {"role": "user", "content": user_content},
    ]
    tool_trace: list[dict[str, Any]] = trace_sink if trace_sink is not None else []
    tool_names_used: list[str] = []
    budget_notes: list[str] = []
    budget = ToolBudget(args)
    last_assistant_text = ""
    rounds_used = 0
    parse_retries_left = max(0, int(args.final_parse_retries))
    forced_final = False
    budget_warned = False
    max_iterations = int(args.max_tool_rounds) + parse_retries_left + 4

    for _ in range(max_iterations):
        payload = {
            "model": args.model,
            "messages": messages,
            "tools": tool_specs(),
            "tool_choice": "none" if forced_final else "auto",
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
        try:
            data = post_chat(base, api_key, payload, args)
        except Exception:
            if not forced_final:
                raise
            # Some gateways reject tool_choice="none"; ask again with no tools.
            payload.pop("tools", None)
            payload.pop("tool_choice", None)
            budget_notes.append("tool_choice=none rejected; retried without tools")
            data = post_chat(base, api_key, payload, args)
        message = data["choices"][0]["message"]
        last_assistant_text = content_to_text(message.get("content", ""))
        tool_calls = message.get("tool_calls") or []
        if forced_final and tool_calls:
            # Provider ignored tool_choice=none.  Dropping the calls would leave
            # unanswered tool_call ids in history, so strip them from the turn.
            message = {k: v for k, v in message.items() if k != "tool_calls"}
            budget_notes.append("provider returned tool calls after final-answer instruction; ignored")
            tool_calls = []
        messages.append(message)
        if not tool_calls:
            try:
                final = parse_final_json(last_assistant_text)
            except Exception as exc:
                if parse_retries_left > 0:
                    parse_retries_left -= 1
                    forced_final = True
                    budget_notes.append(f"final JSON parse failed ({type(exc).__name__}); re-asked")
                    if blank_content(messages[-1]):
                        messages[-1] = {**messages[-1], "content": "(empty response)"}
                    messages.append({"role": "user", "content": REASK_FINAL_JSON})
                    continue
                raise
            final["_judge_text"] = last_assistant_text
            final["_tool_trace"] = tool_trace
            final["_tool_names_used"] = tool_names_used
            final["_rounds_used"] = rounds_used
            final["_forced_final"] = forced_final
            final["_budget_notes"] = budget_notes
            final["_tool_chars_used"] = budget.spent
            final["_transport"] = "openai_chat_completions"
            return final
        for call in tool_calls:
            fn = call.get("function", {})
            name = fn.get("name", "")
            try:
                arguments = json.loads(fn.get("arguments") or "{}")
            except Exception:
                arguments = {}
            try:
                result = tools_runner.execute(name, arguments)
            except Exception as exc:
                result = {"tool_error": f"{type(exc).__name__}: {exc}"}
            tool_names_used.append(name)
            rendered = budget.render(result)
            tool_trace.append({"round": rounds_used + 1, "tool": name, "arguments": arguments, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "name": name,
                    "content": rendered,
                }
            )
        rounds_used += 1
        if rounds_used >= int(args.max_tool_rounds):
            forced_final = True
            budget_notes.append(f"tool-round cap {args.max_tool_rounds} reached; forced final answer")
            messages.append({"role": "user", "content": FORCE_FINAL_INSTRUCTION})
        elif budget.squeezed and not budget_warned:
            budget_warned = True
            budget_notes.append(f"evidence budget {budget.total} chars exhausted; tool results truncated")
            messages.append({"role": "user", "content": EVIDENCE_BUDGET_NOTE})
    raise RuntimeError("tool loop ended without final JSON")


def anthropic_base_url(args: argparse.Namespace) -> str:
    base = args.api_base or os.environ.get("JUDGE_BASE_URL") or os.environ.get("JUDGE_API_BASE") or os.environ.get("ANTHROPIC_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    if not base:
        raise RuntimeError("Missing explicitly configured judge endpoint; refusing silent fallback routing")
    base = base.rstrip("/")
    if base.endswith("/v1"):
        return base
    return base + "/v1"


def anthropic_tools() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for spec in tool_specs():
        fn = spec["function"]
        out.append(
            {
                "name": fn["name"],
                "description": fn["description"],
                "input_schema": fn["parameters"],
            }
        )
    return out


def call_anthropic_tool_judge(
    packet: dict[str, Any],
    tools_runner: EvidenceTools,
    args: argparse.Namespace,
    trace_sink: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    api_key = args.api_key or os.environ.get("JUDGE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("missing API key: set OPENAI_API_KEY/ANTHROPIC_API_KEY/JUDGE_API_KEY or pass --api-key")

    prompt = packet["prompt"]
    images = packet["attached_images"]
    user_content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for img in images:
        user_content.append({"type": "text", "text": f"Attached image: {img['label']} path={img['path']} sha256={img['sha256']}"})
        user_content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img["media_type"],
                    "data": img["b64"],
                },
            }
        )
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_content}]
    tool_trace: list[dict[str, Any]] = trace_sink if trace_sink is not None else []
    tool_names_used: list[str] = []
    budget_notes: list[str] = []
    budget = ToolBudget(args)
    last_text = ""
    rounds_used = 0
    parse_retries_left = max(0, int(args.final_parse_retries))
    forced_final = False
    budget_warned = False
    max_iterations = int(args.max_tool_rounds) + parse_retries_left + 4

    for _ in range(max_iterations):
        payload = {
            "model": args.model,
            "system": "You are a strict Meep paper-reproduction judge. Use tools when evidence must be read. Final score is binary.",
            "messages": messages,
            "tools": anthropic_tools(),
            "max_tokens": args.max_tokens,
        }
        if forced_final:
            payload["tool_choice"] = {"type": "none"}
        if "fable" not in args.model.lower():
            payload["temperature"] = args.temperature
        try:
            data = post_anthropic(anthropic_base_url(args), api_key, payload, args)
        except Exception:
            if not forced_final:
                raise
            payload.pop("tools", None)
            payload.pop("tool_choice", None)
            budget_notes.append("tool_choice=none rejected; retried without tools")
            data = post_anthropic(anthropic_base_url(args), api_key, payload, args)
        content = data.get("content") or []
        text_parts = [part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text"]
        last_text = "\n".join(text_parts)
        tool_uses = [part for part in content if isinstance(part, dict) and part.get("type") == "tool_use"]
        if forced_final and tool_uses:
            content = [part for part in content if not (isinstance(part, dict) and part.get("type") == "tool_use")]
            budget_notes.append("provider returned tool calls after final-answer instruction; ignored")
            tool_uses = []
        if not content:
            content = [{"type": "text", "text": "(empty response)"}]
        messages.append({"role": "assistant", "content": content})
        if not tool_uses:
            try:
                final = parse_final_json(last_text)
            except Exception as exc:
                if parse_retries_left > 0:
                    parse_retries_left -= 1
                    forced_final = True
                    budget_notes.append(f"final JSON parse failed ({type(exc).__name__}); re-asked")
                    messages.append({"role": "user", "content": REASK_FINAL_JSON})
                    continue
                raise
            final["_judge_text"] = last_text
            final["_tool_trace"] = tool_trace
            final["_tool_names_used"] = tool_names_used
            final["_rounds_used"] = rounds_used
            final["_forced_final"] = forced_final
            final["_budget_notes"] = budget_notes
            final["_tool_chars_used"] = budget.spent
            final["_transport"] = "anthropic_messages"
            return final
        tool_results: list[dict[str, Any]] = []
        for call in tool_uses:
            name = str(call.get("name", ""))
            arguments = call.get("input") or {}
            if not isinstance(arguments, dict):
                arguments = {}
            try:
                result = tools_runner.execute(name, arguments)
            except Exception as exc:
                result = {"tool_error": f"{type(exc).__name__}: {exc}"}
            tool_names_used.append(name)
            tool_trace.append({"round": rounds_used + 1, "tool": name, "arguments": arguments, "result": result})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.get("id"),
                    "content": budget.render(result),
                }
            )
        follow_up: list[dict[str, Any]] = []
        rounds_used += 1
        if rounds_used >= int(args.max_tool_rounds):
            forced_final = True
            budget_notes.append(f"tool-round cap {args.max_tool_rounds} reached; forced final answer")
            follow_up.append({"type": "text", "text": FORCE_FINAL_INSTRUCTION})
        elif budget.squeezed and not budget_warned:
            budget_warned = True
            budget_notes.append(f"evidence budget {budget.total} chars exhausted; tool results truncated")
            follow_up.append({"type": "text", "text": EVIDENCE_BUDGET_NOTE})
        messages.append({"role": "user", "content": tool_results + follow_up})
    raise RuntimeError("tool loop ended without final JSON")


def post_chat(base: str, api_key: str, payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    url = base.rstrip("/") + "/chat/completions"
    body_bytes = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last: Exception | None = None
    for attempt in range(1, args.retries + 2):
        retry_after: float | None = None
        try:
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=args.http_timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            if not parsed.get("choices"):
                raise RuntimeError(f"judge returned no choices: {body[:500]}")
            return parsed
        except urllib.error.HTTPError as exc:
            retry_after = retry_after_seconds(exc)
            detail = exc.read().decode("utf-8", errors="replace")[:1200]
            last = RuntimeError(f"HTTP {exc.code}: {detail}")
            if exc.code not in RETRYABLE_HTTP_STATUS:
                raise last from exc
        except Exception as exc:
            last = exc
        if attempt <= args.retries:
            time.sleep(retry_delay(args, attempt, retry_after))
    raise RuntimeError(f"judge call failed after {args.retries + 1} attempts: {last}")


def post_anthropic(base: str, api_key: str, payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    url = base.rstrip("/") + "/messages"
    body_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    last: Exception | None = None
    for attempt in range(1, args.retries + 2):
        retry_after: float | None = None
        try:
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=args.http_timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            if parsed.get("type") == "error" or parsed.get("error"):
                raise RuntimeError(f"judge returned error: {body[:1200]}")
            return parsed
        except urllib.error.HTTPError as exc:
            retry_after = retry_after_seconds(exc)
            detail = exc.read().decode("utf-8", errors="replace")[:1200]
            last = RuntimeError(f"HTTP {exc.code}: {detail}")
            if exc.code not in RETRYABLE_HTTP_STATUS:
                raise last from exc
        except Exception as exc:
            last = exc
        if attempt <= args.retries:
            time.sleep(retry_delay(args, attempt, retry_after))
    raise RuntimeError(f"judge call failed after {args.retries + 1} attempts: {last}")


def validate_judgment(leaf: Leaf, judgment: dict[str, Any], packet: dict[str, Any], args: argparse.Namespace) -> tuple[int, list[str]]:
    notes: list[str] = []
    raw_score = judgment.get("score")
    if raw_score not in (0, 1, "0", "1"):
        raise ValueError("final JSON score must be exactly 0 or 1, without rounding")
    score = int(raw_score)
    access = judgment.get("evidence_access")
    if access not in {"ok", "missing", "tool_error"}:
        raise ValueError("Invalid evidence_access classification")
    if access == "tool_error":
        raise ValueError("Evaluator could not inspect equivalent evidence; rejudge the same frozen submission")
    trace = judgment.get("_tool_trace") or []
    evidence_root = Path(packet["evidence_root"]).resolve() if packet.get("evidence_root") else None
    candidate_inspected = False
    used = set()
    for entry in trace:
        result = entry.get("result")
        if not isinstance(result, dict) or result.get("error") or result.get("parse_error") or result.get("tool_error"):
            continue
        used.add(entry.get("tool"))
        if evidence_root is not None:
            paths = []
            if entry.get("tool") in ({"read_text_file", "read_json_file"} | GENERIC_NPZ_TOOLS):
                paths.extend(result.get(key) for key in ("path", "path_a", "path_b") if isinstance(result.get(key), str))
            if entry.get("tool") == "derive_scientific_metrics" and result.get("status") == "recomputed_from_candidate_arrays":
                paths.extend(binding.get("path") for binding in result.get("bindings", {}).values()
                             if isinstance(binding, dict) and isinstance(binding.get("path"), str))
            candidate_inspected |= any(Path(path).resolve().is_relative_to(evidence_root) for path in paths)
    if evidence_root is not None:
        candidate_inspected |= any(image.get("b64") and isinstance(image.get("path"), str)
                                   and Path(image["path"]).resolve().is_relative_to(evidence_root)
                                   for image in packet.get("attached_images", []))
    pages = [entry["result"] for entry in trace
             if entry.get("tool") == "list_evidence_files"
             and isinstance(entry.get("result"), dict)
             and entry["result"].get("root_kind") == "submission"
             and not any(entry["result"].get(key) for key in ("error", "parse_error", "tool_error"))]
    covered = 0
    totals = {page.get("total_files") for page in pages}
    for page in sorted(pages, key=lambda item: item.get("offset", -1)):
        offset, returned = page.get("offset", -1), page.get("returned", 0)
        if 0 <= offset <= covered:
            covered = max(covered, offset + returned)
    discovered = len(totals) == 1 and next(iter(totals), None) == covered
    if access == "missing":
        if score != 0 or not discovered:
            raise ValueError("Missing scientific evidence requires a complete paginated submission listing and a zero judgment")
        if args.enforce_required_tools and evidence_root is not None and covered and not candidate_inspected:
            raise ValueError("A nonempty submission requires content inspection, not filename-only absence inference")
        return score, notes
    if args.enforce_required_tools and evidence_root is not None and not candidate_inspected:
        raise ValueError("No actual candidate evidence was inspected; private targets or tool-free guesses cannot establish a grade")
    if score == 1 and leaf.metric_operation:
        recomputed = any(
            entry.get("tool") == "derive_scientific_metrics"
            and isinstance(entry.get("result"), dict)
            and entry["result"].get("status") == "recomputed_from_candidate_arrays"
            and entry["result"].get("operation") == leaf.metric_operation
            and entry["result"].get("bindings")
            for entry in trace
        )
        if not recomputed:
            raise ValueError("Passing this leaf requires its reviewed scientific metric operation; no score may be published yet")
    required = likely_required_tools(leaf)
    if args.enforce_required_tools:
        missing = set()
        for requirement in required:
            if requirement == "inspect_npz" and (GENERIC_NPZ_TOOLS & used):
                continue
            if requirement == "inspect_image" and ((GENERIC_NPZ_TOOLS & used) or "inspect_image" in used or packet.get("attached_images")):
                continue
            if requirement in {"read_text_file", "read_json_file"} and ({"read_text_file", "read_json_file"} | GENERIC_NPZ_TOOLS) & used:
                continue
            if requirement not in used:
                missing.add(requirement)
        if missing:
            raise ValueError(f"Judge did not successfully inspect required evidence kinds: {sorted(missing)}; do not publish as model failure")
    return score, notes


def score_one(packet_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    leaf = Leaf(**packet["leaf"])
    task_root = Path(packet.get("task_root", packet.get("task_root", "")))
    evidence_root = Path(packet["evidence_root"])
    tools_runner = EvidenceTools(task_root, evidence_root, args)
    trace_sink: list[dict[str, Any]] = []
    raw = None
    try:
        if args.dry_run:
            return {
                "leaf_index": leaf.index,
                "leaf_id": leaf.leaf_id,
                "title": leaf.title,
                "score": 0,
                "method": "dry_run_not_scored",
                "effective_weight": leaf.effective_weight,
            }
        transport = args.transport
        if transport == "auto":
            transport = "anthropic" if args.model.startswith("anthropic-") or "claude" in args.model.lower() else "openai"
        if transport == "anthropic":
            raw = call_anthropic_tool_judge(packet, tools_runner, args, trace_sink=trace_sink)
        else:
            raw = call_openai_tool_judge(packet, tools_runner, args, trace_sink=trace_sink)
        score, validation_notes = validate_judgment(leaf, raw, packet, args)
        return {
            "leaf_index": leaf.index,
            "leaf_id": leaf.leaf_id,
            "title": leaf.title,
            "weight": leaf.weight,
            "effective_weight": leaf.effective_weight,
            "score": score,
            "method": "meep_v2_tool_augmented_llm",
            "judge_error": False,
            "rounds_used": raw.get("_rounds_used"),
            "forced_final": bool(raw.get("_forced_final")),
            "budget_notes": raw.get("_budget_notes") or [],
            "tool_chars_used": raw.get("_tool_chars_used"),
            "judge_json": raw,
            "validation_notes": validation_notes,
            "evidence_inputs": leaf.evidence_inputs,
            "attached_images": [{k: v for k, v in img.items() if k != "b64"} for img in packet.get("attached_images", [])],
        }
    except Exception as exc:
        if not args.fail_closed_on_error:
            raise
        return {
            "leaf_index": leaf.index,
            "leaf_id": leaf.leaf_id,
            "title": leaf.title,
            "weight": leaf.weight,
            "effective_weight": leaf.effective_weight,
            "score": 0,
            "method": "meep_v2_tool_augmented_llm_error_fail_closed",
            "judge_error": True,
            "error_class": type(exc).__name__,
            "judge_json": raw,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc()[-5000:],
            "rounds_observed": max([int(t.get("round", 0)) for t in trace_sink], default=0),
            "tool_calls_observed": len(trace_sink),
            "tool_names_observed": [str(t.get("tool")) for t in trace_sink],
            "tool_calls_tail": [
                {"round": t.get("round"), "tool": t.get("tool"), "arguments": t.get("arguments"), "result": t.get("result")}
                for t in trace_sink[-8:]
            ],
            "evidence_inputs": leaf.evidence_inputs,
        }



RESUME_HARD_KEYS = (
    "task_root",
    "evidence_root",
    "rubric_sha256",
    "judge_addendum_sha256",
    "model",
    "enforce_required_tools",
    "script_sha256",
    "judge_prompt_sha256",
    "evidence_reader_sha256",
    "evidence_tree_sha256",
    "refs_tree_sha256",
    "public_contract_sha256",
    "scientific_module_sha256",
    "scientific_bridge_sha256",
)
RESUME_SOFT_KEYS = ()


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception as exc:
        return f"<<unreadable:{type(exc).__name__}>>"


def build_resume_fingerprint(
    task_root: Path,
    evidence_root: Path,
    rubric_path: Path,
    addendum_path: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "task_root": str(task_root),
        "evidence_root": str(evidence_root),
        "rubric_sha256": sha256_file(rubric_path),
        "judge_addendum_sha256": sha256_file(addendum_path),
        "judge_prompt_sha256": sha256_file(args.judge_prompt) if args.judge_prompt.is_file() else None,
        "model": args.model,
        "enforce_required_tools": bool(args.enforce_required_tools),
        "script_sha256": sha256_file(Path(__file__)),
        "evidence_reader_sha256": sha256_file(Path(__file__).with_name("meep_evidence_formats.py")),
        "evidence_tree_sha256": tree_digest(evidence_root),
        "refs_tree_sha256": tree_digest(resolve_refs_dir(task_root)),
        "public_contract_sha256": {
            (str(path.relative_to(task_root)) if path.is_relative_to(task_root) else path.name): sha256_file(path)
            for path in (task_root / "instruction.md", task_root / "environment/paper/addendum.md",
                         instruction_file(task_root, "config/public_contract.md"))
            if path.is_file()
        },
        "scientific_module_sha256": sha256_file(instruction_file(task_root, "src/scientific_metrics.py")),
        "scientific_bridge_sha256": sha256_file(Path(__file__).with_name("meep_scientific_bridge.py")),
    }


def check_resume_fingerprint(
    prior_manifest: dict[str, Any],
    current: dict[str, Any],
    args: argparse.Namespace,
) -> list[str]:
    """Return human-readable notes, or SystemExit if reuse would be unsound."""
    prior = prior_manifest.get("resume_fingerprint")
    if not isinstance(prior, dict):
        raise SystemExit(
            "--resume refused: the prior run in this output directory predates resume "
            "support (manifest.json has no resume_fingerprint), so its judgments cannot "
            "be validated. Score fresh into an empty --out."
        )
    hard = [k for k in RESUME_HARD_KEYS if prior.get(k) != current.get(k)]
    if hard:
        detail = "; ".join(f"{k}: prior={prior.get(k)!r} now={current.get(k)!r}" for k in hard)
        raise SystemExit(
            f"--resume refused: {len(hard)} fingerprint field(s) changed, so reusing the "
            f"prior judgments would produce a wrong grade -> {detail}"
        )
    notes: list[str] = []
    soft = [k for k in RESUME_SOFT_KEYS if prior.get(k) != current.get(k)]
    if soft:
        text = f"resumed across a change in {', '.join(soft)}"
        if not args.resume_allow_script_change:
            raise SystemExit(f"--resume refused: {text} (pass --resume-allow-script-change to permit)")
        notes.append(text + "; reused verdicts were produced by the earlier version")
    return notes


def parse_leaf_selection(spec: str | None, valid: set[int]) -> set[int] | None:
    if spec is None or not str(spec).strip():
        return None
    wanted: set[int] = set()
    for chunk in re.split(r"[,\s]+", str(spec).strip()):
        if not chunk:
            continue
        span = re.fullmatch(r"(\d+)\s*-\s*(\d+)", chunk)
        if span:
            lo, hi = int(span.group(1)), int(span.group(2))
            if lo > hi:
                lo, hi = hi, lo
            wanted.update(range(lo, hi + 1))
            continue
        if not chunk.isdigit():
            raise SystemExit(f"--only-leaves: cannot parse {chunk!r}")
        wanted.add(int(chunk))
    if not wanted:
        raise SystemExit("--only-leaves matched no leaves")
    unknown = sorted(wanted - valid)
    if unknown:
        hi = max(valid) if valid else 0
        raise SystemExit(f"--only-leaves: no such leaf index {unknown} (valid 1..{hi})")
    return wanted


def load_prior_judgments(out: Path) -> dict[int, dict[str, Any]]:
    found: dict[int, dict[str, Any]] = {}
    judgments_dir = out / "leaf_judgments"
    if not judgments_dir.is_dir():
        return found
    for path in sorted(judgments_dir.glob("*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(row, dict):
            continue
        if any(k not in row for k in ("leaf_index", "leaf_id", "effective_weight", "score")):
            continue
        try:
            idx = int(row["leaf_index"])
        except Exception:
            continue
        row["reused_from_prior_run"] = True
        found[idx] = row
    return found


def aggregate(judgments: list[dict[str, Any]]) -> float:
    total = sum(float(judgment["effective_weight"]) * float(judgment["score"]) for judgment in judgments)
    return total


def summarize_stages(rubric: dict[str, Any], judgments: list[dict[str, Any]]) -> dict[str, Any]:
    weights = {leaf.leaf_id: leaf.effective_weight for leaf in flatten_rubric(rubric)}
    scored = {row["leaf_id"]: row for row in judgments}
    stages = {}
    for stage in rubric.get("sub_tasks") or []:
        leaf_ids = [leaf.leaf_id for leaf in flatten_rubric(stage)]
        possible = sum(weights[leaf_id] for leaf_id in leaf_ids)
        earned = sum(weights[leaf_id] * float(scored[leaf_id]["score"]) for leaf_id in leaf_ids if leaf_id in scored)
        stages[str(stage["id"])] = {
            "title": stage["title"],
            "earned": earned,
            "possible": possible,
            "score": earned / possible if possible else 0.0,
            "evaluated_weight": sum(weights[leaf_id] for leaf_id in leaf_ids if leaf_id in scored),
            "leaf_ids": leaf_ids,
        }
    return stages




def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
    ap.add_argument("--task-root", type=Path, default=DEFAULT_TASK_ROOT)
    ap.add_argument("--judge-prompt", type=Path, default=DEFAULT_JUDGE_PROMPT)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default=os.environ.get("JUDGE_MODEL", "gpt-5.5"))
    ap.add_argument("--transport", choices=["auto", "openai", "anthropic"],
                    default=os.environ.get("PBX_LLM_TRANSPORT") or os.environ.get("JUDGE_TRANSPORT") or "auto")
    ap.add_argument("--api-base", default=None)
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-empty-out", action="store_true", help="allow existing empty output directory")
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--max-paper-chars", type=int, default=40000)
    ap.add_argument("--max-solver-addendum-chars", type=int, default=25000)
    ap.add_argument("--max-judge-addendum-chars", type=int, default=50000)
    ap.add_argument("--max-refs-chars", type=int, default=30000)
    ap.add_argument("--max-judge-prompt-chars", type=int, default=18000)
    ap.add_argument("--max-tool-text-chars", type=int, default=50000)
    ap.add_argument("--max-tool-result-chars", type=int, default=65000)  # per call; whole-leaf cap is --max-total-tool-chars
    ap.add_argument("--npz-samples", type=int, default=10)
    ap.add_argument("--max-npz-slice-items", type=int, default=400)
    ap.add_argument("--attach-candidate-images", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--attach-ref-images", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--attach-paper-images", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--attach-images-for-all", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--max-paper-images", type=int, default=20)
    ap.add_argument("--max-attached-images-per-leaf", type=int, default=24)
    ap.add_argument("--max-image-bytes", type=int, default=2_000_000)
    ap.add_argument("--image-detail", choices=["low", "high", "auto"], default="high")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--max-tool-rounds", type=int, default=16)
    ap.add_argument("--http-timeout", type=float, default=300.0)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--retry-sleep", type=float, default=8.0)
    ap.add_argument("--final-parse-retries", type=int, default=2)
    ap.add_argument("--max-total-tool-chars", type=int, default=400000)
    ap.add_argument("--min-tool-result-chars", type=int, default=4000)
    ap.add_argument("--fail-loud-on-judge-errors", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--fail-loud-threshold", type=float, default=0.02)
    ap.add_argument("--fail-closed-on-error", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--enforce-required-tools", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument(
        "--resume",
        action="store_true",
        help="reuse the judgments already in --out and only re-score leaves that are "
        "missing or that failed inside the judge; requires a matching prior manifest",
    )
    ap.add_argument(
        "--only-leaves",
        default=None,
        help="comma/space separated leaf indices, ranges allowed (e.g. '5,10,27' or '5-9'). "
        "With --resume the remaining leaves are reused; without it the run is PARTIAL "
        "and writes reward_partial.txt instead of reward.txt",
    )
    ap.add_argument(
        "--resume-allow-script-change",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="allow --resume when only the scorer script or judge prompt changed "
        "(evidence root, rubric, addendum and model must still match exactly)",
    )
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()

    task_root = args.task_root.resolve(strict=False)
    from meep_score_publication import block_disabled_scoring

    if block_disabled_scoring(instruction_file(task_root, "rubric.json").parent, args.out):
        return 78
    evidence_root = args.evidence_root.resolve(strict=False)
    if args.out.resolve(strict=False).is_relative_to(evidence_root):
        raise SystemExit("Judge output must not be inside frozen candidate evidence")
    rubric_path = instruction_file(task_root, "rubric.json")
    addendum_path = instruction_file(task_root, "config/judge_prompt.md")
    if not rubric_path.is_file():
        raise SystemExit(f"missing rubric: {rubric_path}")
    if not addendum_path.is_file():
        raise SystemExit(f"missing judge addendum: {addendum_path}")
    if not evidence_root.exists():
        raise SystemExit(f"missing evidence root: {evidence_root}")
    prior_manifest: dict[str, Any] = {}
    if args.out.exists() and any(args.out.iterdir()) and not args.resume:
        raise SystemExit(
            f"output directory exists and is not empty; refusing to overwrite: {args.out}\n"
            "(pass --resume to keep those judgments and only re-score the failed leaves)"
        )
    if args.resume:
        prior_manifest_path = args.out / "manifest.json"
        if not prior_manifest_path.is_file():
            raise SystemExit(f"--resume needs a prior manifest to validate against: {prior_manifest_path}")
        try:
            prior_manifest = json.loads(prior_manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"--resume could not read prior manifest {prior_manifest_path}: {exc}")
        if not isinstance(prior_manifest, dict):
            raise SystemExit(f"--resume found a malformed prior manifest: {prior_manifest_path}")
    args.out.mkdir(parents=True, exist_ok=True)
    packets_dir = args.out / "leaf_packets"
    judgments_dir = args.out / "leaf_judgments"
    packets_dir.mkdir(exist_ok=True)
    judgments_dir.mkdir(exist_ok=True)

    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    leaves = flatten_rubric(rubric)
    judge_prompt_text, judge_addendum = read_judge_prompt(
        args.judge_prompt, addendum_path, args.max_judge_prompt_chars, args.max_judge_addendum_chars)
    refs_text = read_refs_text(task_root, args.max_refs_chars)
    tools_runner = EvidenceTools(task_root, evidence_root, args)

    manifest = {
        "script": str(Path(__file__).resolve()),
        "mode": "meep_v2_tool_augmented_all_llm",
        "task_root": str(task_root),
        "rubric": str(rubric_path),
        "judge_addendum": str(addendum_path),
        "refs": str(resolve_refs_dir(task_root)),
        "judge_prompt": str(args.judge_prompt),
        "evidence_root": str(evidence_root),
        "out": str(args.out),
        "model": args.model,
        "dry_run": args.dry_run,
        "n_leaves": len(leaves),
        "notes": [
            "Leaf scores are final LLM 0/1 judgments.",
            "Tools are read-only evidence readers/recomputers and never assign score.",
            "NPZ is accessed through bounded generic NPZ tools; full large arrays are never injected into prompts.",
            "Candidate/ref/paper images are attached as visual inputs when enabled.",
        ],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "resume_fingerprint": build_resume_fingerprint(
            task_root, evidence_root, rubric_path, addendum_path, args
        ),
    }

    resume_notes: list[str] = []
    reused: dict[int, dict[str, Any]] = {}
    if args.resume:
        resume_notes = check_resume_fingerprint(prior_manifest, manifest["resume_fingerprint"], args)
        reused = load_prior_judgments(args.out)
    valid_indices = {int(leaf.index) for leaf in leaves}
    selection = parse_leaf_selection(args.only_leaves, valid_indices)
    if args.resume:
        if selection is not None:
            # An explicit selection wins: --only-leaves means "judge exactly these
            # again", even if a prior verdict for them already looks fine.
            redo = set(selection)
        else:
            broken = {
                i
                for i, j in reused.items()
                if j.get("judge_error") or int(j.get("score") or 0) not in (0, 1)
            }
            redo = (valid_indices - set(reused)) | broken
    else:
        redo = set(selection) if selection is not None else set(valid_indices)
    for idx in list(reused):
        if idx in redo or idx not in valid_indices:
            reused.pop(idx, None)
    partial = (set(reused) | redo) != valid_indices
    if args.resume:
        print(
            f"resume: reusing {len(reused)} prior judgment(s), re-scoring {len(redo)} "
            f"of {len(valid_indices)} leaves: {sorted(redo)}",
            flush=True,
        )
        for note in resume_notes:
            print(f"resume note: {note}", flush=True)

    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    packet_paths: list[Path] = []
    for leaf in leaves:
        if int(leaf.index) not in redo:
            continue
        prompt = build_initial_prompt(leaf, task_root, evidence_root, judge_addendum, refs_text, judge_prompt_text, args)
        images = collect_image_attachments(leaf, tools_runner, args)
        packet = {
            "leaf": dataclasses.asdict(leaf),
            "task_root": str(task_root),
            "evidence_root": str(evidence_root),
            "prompt": prompt,
            "attached_images": images,
            "required_tools_inferred": sorted(likely_required_tools(leaf)),
        }
        packet_path = packets_dir / f"{leaf.index:03d}_{leaf.leaf_id}.json"
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        packet_paths.append(packet_path)

    if args.dry_run:
        print(f"dry-run complete: wrote {len(packet_paths)} packets to {packets_dir}")
        return 0

    judgments: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as ex:
        futures = {ex.submit(score_one, packet, args): packet for packet in packet_paths}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            judgments.append(result)
            out_path = judgments_dir / futures[future].name
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(
                f"leaf {int(result['leaf_index']):03d} score={result['score']} "
                f"title={result.get('title')}",
                flush=True,
            )

    n_rescored = len(judgments)
    judgments.extend(reused.values())
    judgments.sort(key=lambda x: int(x["leaf_index"]))
    total = aggregate(judgments)

    possible_weight = sum(float(j["effective_weight"]) for j in judgments)
    error_rows = [j for j in judgments if j.get("judge_error")]
    error_weight = sum(float(j["effective_weight"]) for j in error_rows)
    error_fraction = (error_weight / possible_weight) if possible_weight else 0.0
    error_classes: dict[str, int] = {}
    for j in error_rows:
        key = str(j.get("error_class") or "Unknown")
        error_classes[key] = error_classes.get(key, 0) + 1
    judge_errors = {
        "n_errors": len(error_rows),
        "n_leaves": len(judgments),
        "error_weight_lost": error_weight,
        "possible_weight": possible_weight,
        "error_fraction_of_possible": error_fraction,
        "error_classes": error_classes,
        "leaves": [
            {
                "leaf_index": j.get("leaf_index"),
                "leaf_id": j.get("leaf_id"),
                "effective_weight": j.get("effective_weight"),
                "error_class": j.get("error_class"),
                "error": j.get("error"),
                "rounds_observed": j.get("rounds_observed"),
                "tool_calls_observed": j.get("tool_calls_observed"),
            }
            for j in error_rows
        ],
    }
    rounds_hist: dict[str, int] = {}
    for j in judgments:
        if j.get("judge_error"):
            continue
        key = str(j.get("rounds_used"))
        rounds_hist[key] = rounds_hist.get(key, 0) + 1
    forced_zero_rows = [
        j
        for j in judgments
        if not j.get("judge_error")
        and int(j.get("score") or 0) == 0
        and any("forced score 0" in str(n) for n in (j.get("validation_notes") or []))
    ]
    forced_zero_after_cap = [j for j in forced_zero_rows if j.get("forced_final")]
    validation_forced_zero = {
        "n": len(forced_zero_rows),
        "weight": sum(float(j["effective_weight"]) for j in forced_zero_rows),
        "n_after_forced_final": len(forced_zero_after_cap),
        "weight_after_forced_final": sum(
            float(j["effective_weight"]) for j in forced_zero_after_cap
        ),
        "leaves": [
            {
                "leaf_index": j.get("leaf_index"),
                "leaf_id": j.get("leaf_id"),
                "effective_weight": j.get("effective_weight"),
                "forced_final": bool(j.get("forced_final")),
                "rounds_used": j.get("rounds_used"),
                "validation_notes": j.get("validation_notes"),
            }
            for j in forced_zero_rows
        ],
    }
    judge_diagnostics = {
        "n_forced_final": sum(1 for j in judgments if j.get("forced_final")),
        "validation_forced_zero": validation_forced_zero,
        "n_final_json_reasks": sum(
            1 for j in judgments if any("re-asked" in str(n) for n in (j.get("budget_notes") or []))
        ),
        "n_evidence_budget_squeezed": sum(
            1 for j in judgments if any("evidence budget" in str(n) for n in (j.get("budget_notes") or []))
        ),
        "rounds_used_histogram": rounds_hist,
        "settings": {
            "max_tool_rounds": args.max_tool_rounds,
            "final_parse_retries": args.final_parse_retries,
            "max_total_tool_chars": args.max_total_tool_chars,
            "max_tool_result_chars": args.max_tool_result_chars,
            "max_tokens": args.max_tokens,
            "http_timeout": args.http_timeout,
            "retries": args.retries,
            "retry_sleep": args.retry_sleep,
            "max_workers": args.max_workers,
        },
    }
    fail_loud = bool(error_rows) and args.fail_loud_on_judge_errors and error_fraction > args.fail_loud_threshold

    result = {
        "status": (
            "scored_partial"
            if partial
            else ("scored_with_judge_errors" if error_rows else "scored")
        ),
        "judge_ok": not error_rows,
        "evaluator_version": "meep-v2-tool-augmented-all-llm-v2",
        "task_root_name": task_root.name,
        "task_name": THIS_TASK.name,
        "evidence_root": str(evidence_root),
        "judge_model": args.model,
        "score": None if error_rows or partial else total,
        "rubric_score": None if error_rows or partial else total,
        "n_leaves": len(judgments),
        "n_judge_errors": len(error_rows),
        "judge_error_weight_lost": error_weight,
        "judge_error_fraction_of_possible": error_fraction,
        "judge_errors": judge_errors,
        "judge_diagnostics": judge_diagnostics,
        "reward_degraded": bool(error_rows),
        "partial": partial,
        "n_leaves_total": len(leaves),
        "n_leaves_scored": len(judgments),
        "resume": {
            "enabled": bool(args.resume),
            "only_leaves": args.only_leaves,
            "n_rescored": n_rescored,
            "n_reused": len(reused),
            "rescored_leaf_indices": sorted(redo),
            "reused_leaf_indices": sorted(reused),
            "notes": resume_notes,
        },
        "stage_scores": summarize_stages(rubric, judgments),
        "notes": manifest["notes"],
    }
    (args.out / "rubric_results.json").write_text(json.dumps(judgments, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "judge_errors.json").write_text(json.dumps(judge_errors, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if partial or error_rows:
        (args.out / "reward.txt").unlink(missing_ok=True)
        (args.out / "reward_partial.txt").unlink(missing_ok=True)
    else:
        from meep_score_publication import InvalidGrade, withhold_invalid_score

        try:
            withhold_invalid_score(args.out / "result.json", rubric_path, args.out / "rubric_results.json", args.out)
        except InvalidGrade:
            return 75
        (args.out / "reward.txt").write_text(f"{total:.6f}\n", encoding="utf-8")
    printable = {k: v for k, v in result.items() if k != "judge_errors"}
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    if error_rows:
        print(
            f"WARNING: {len(error_rows)} leaf/leaves failed inside the judge and were "
            f"left unscored; no overall reward is published. Affected weight: {error_weight:.4f} "
            f"({error_fraction * 100:.2f}% of possible). See judge_errors.json.",
            file=sys.stderr,
        )
        for j in error_rows:
            print(
                f"  judge_error leaf={j.get('leaf_index')} id={j.get('leaf_id')} "
                f"w={float(j.get('effective_weight') or 0):.4f} {j.get('error')}",
                file=sys.stderr,
            )
    if partial:
        print(
            f"WARNING: PARTIAL run - scored {len(judgments)} of {len(leaves)} leaves. "
            f"No numerical reward was written. Re-run with --resume to complete the score.",
            file=sys.stderr,
        )
    if forced_zero_after_cap:
        print(
            f"WARNING: {len(forced_zero_after_cap)} leaf/leaves were forced to 0 by the "
            f"required-evidence guard after the tool-round cap forced a final answer, "
            f"costing {sum(float(j['effective_weight']) for j in forced_zero_after_cap):.4f} "
            f"weight. Consider raising --max-tool-rounds. "
            f"See judge_diagnostics.validation_forced_zero in result.json.",
            file=sys.stderr,
        )
    if error_rows:
        return 75
    if fail_loud:
        print(
            f"JUDGE ERRORS EXCEED THRESHOLD ({error_fraction:.4f} > {args.fail_loud_threshold}): "
            "composite reward is degraded",
            file=sys.stderr,
        )
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
