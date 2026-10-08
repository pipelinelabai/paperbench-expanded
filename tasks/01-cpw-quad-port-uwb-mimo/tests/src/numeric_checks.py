"""Recompute reported metrics and apply deterministic rubric checks."""

from __future__ import annotations

import argparse
import ast
import csv as _csv
import json
import math
import sys
from pathlib import Path

import evidence_contract


# ---------------------------------------------------------------- Data loading


class Missing(Exception):
    """Missing evidence; the message is included directly in the reason."""


_json_cache: dict[Path, object] = {}
_csv_cache: dict[Path, list[dict]] = {}


def load_json(root: Path, rel: str):
    p = root / rel
    if p in _json_cache:
        return _json_cache[p]
    if not p.exists():
        raise Missing(f"Missing file {rel}")
    try:
        obj = evidence_contract.read_json(p)
    except (OSError, ValueError) as exc:
        raise Missing(f"{rel} invalid JSON: {exc}") from exc
    _json_cache[p] = obj
    return obj


def load_csv(root: Path, rel: str) -> list[dict]:
    p = root / rel
    if p in _csv_cache:
        return _csv_cache[p]
    if not p.exists():
        raise Missing(f"Missing file {rel}")
    try:
        _, rows = evidence_contract.read_csv(p)
    except (OSError, ValueError, _csv.Error) as exc:
        raise Missing(f"{rel} invalid CSV: {exc}") from exc
    if not rows:
        raise Missing(f"{rel} has no data rows")
    _csv_cache[p] = rows
    return rows


def _path_parts(path):
    if isinstance(path, list):
        return [str(p) for p in path]
    return str(path).split(".")


def _path_str(path) -> str:
    return "/".join(_path_parts(path)) if isinstance(path, list) else str(path)


def dig(obj, path, rel: str):
    """Look up a dotted path or key list; numeric segments support dict keys and list indices."""
    cur = obj
    ps = _path_str(path)
    for part in _path_parts(path):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
                continue
            except (ValueError, IndexError) as exc:
                raise Missing(f"{rel}:{ps} index {part} is out of range") from exc
        if not isinstance(cur, dict) or part not in cur:
            raise Missing(f"{rel} missing field {ps} (at {part})")
        cur = cur[part]
    return cur


def as_num(x, where: str) -> float:
    if x is None or (isinstance(x, str) and x.strip().lower() in ("", "null", "nan", "none")):
        raise Missing(f"{where} is null/empty")
    if isinstance(x, bool):
        raise Missing(f"{where} is a boolean, not a number")
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise Missing(f"{where} is not numeric: {x!r}") from exc
    if not math.isfinite(v):
        raise Missing(f"{where} is not finite: {v}")
    return v


# ---------------------------------------------------------------- Column expressions (colexpr)

_COLEXPR_FUNCS = {
    "abs": abs, "log10": math.log10, "log": math.log, "exp": math.exp,
    "sqrt": math.sqrt, "max": max, "min": min,
}
_COLEXPR_OK_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd,
)
_colexpr_cache: dict[str, tuple[object, list[str]]] = {}


def _compile_colexpr(src: str):
    if src in _colexpr_cache:
        return _colexpr_cache[src]
    try:
        tree = ast.parse(src, mode="eval")
    except SyntaxError as exc:
        raise Missing(f"colexpr syntax error {src!r}: {exc}") from exc
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, _COLEXPR_OK_NODES):
            raise Missing(f"colexpr contains a disallowed node {type(node).__name__}: {src!r}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise Missing(f"colexpr permits only numeric constants: {src!r}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _COLEXPR_FUNCS:
                raise Missing(f"colexpr permits calls only to {sorted(_COLEXPR_FUNCS)}: {src!r}")
            if node.keywords:
                raise Missing(f"colexpr does not permit keyword arguments: {src!r}")
        if isinstance(node, ast.Name) and node.id not in _COLEXPR_FUNCS:
            names.append(node.id)
    code = compile(tree, "<colexpr>", "eval")
    _colexpr_cache[src] = (code, names)
    return code, names


def _row_value(row: dict, col: str | None, colexpr: str | None, rel: str) -> float:
    if colexpr is None:
        return as_num(row.get(col), f"{rel}:{col}")
    code, names = _compile_colexpr(colexpr)
    env = {"__builtins__": {}}
    env.update(_COLEXPR_FUNCS)
    for n in names:
        if n not in row:
            raise Missing(f"{rel} missing column {n} (colexpr {colexpr!r})")
        env[n] = as_num(row.get(n), f"{rel}:{n}")
    try:
        v = eval(code, env)  # noqa: S307
    except (ArithmeticError, ValueError) as exc:
        raise Missing(f"colexpr {colexpr!r} evaluation failed: {exc}") from exc
    return as_num(v, f"{rel}:colexpr({colexpr})")


# ---------------------------------------------------------------- Expression evaluation

_AGGS = ("min", "max", "mean", "argmin", "argmax", "count", "ptp", "maxabs",
         "first", "last", "n_unique", "n_nonincreasing", "n_offgrid", "max_decimals")
_GRID_TOL = 1e-6


def _match(row: dict, where: dict, rel: str) -> bool:
    for k, want in where.items():
        if k not in row:
            raise Missing(f"{rel} missing column {k}")
        if isinstance(want, str):
            if str(row[k]).strip() != want:
                return False
        else:
            try:
                if abs(float(row[k]) - float(want)) > _GRID_TOL + 1e-9 * abs(float(want)):
                    return False
            except (TypeError, ValueError):
                return False
    return True


def _in_range(row: dict, rng: dict, rel: str) -> bool:
    for k, (lo, hi) in rng.items():
        if k not in row:
            raise Missing(f"{rel} missing column {k}")
        try:
            v = float(row[k])
        except (TypeError, ValueError):
            return False
        if lo is not None and v < lo - _GRID_TOL:
            return False
        if hi is not None and v > hi + _GRID_TOL:
            return False
    return True


def _decimals(s) -> int:
    t = str(s).strip().lower()
    if "e" in t:
        return 99
    return len(t.split(".", 1)[1]) if "." in t else 0


def _table_value(expr: dict, rows: list[dict], rel: str, root: Path, env: dict, sub) -> float:
    col = sub(expr["col"]) if "col" in expr else None
    colexpr = sub(expr["colexpr"]) if "colexpr" in expr else None
    if (col is None) == (colexpr is None):
        raise Missing("csv/jsontable expressions require exactly one of col and colexpr")
    static_where, nearest_where = {}, {}
    for k, v in (expr.get("where") or {}).items():
        if isinstance(v, dict) and "nearest" in v:
            nearest_where[k] = ev(v["nearest"], root, env)
        else:
            static_where[k] = sub(v) if isinstance(v, str) else v
    rng = expr.get("range") or {}
    sel = [r for r in rows if _match(r, static_where, rel) and _in_range(r, rng, rel)]
    for k, target in nearest_where.items():
        if not sel:
            break
        if k not in sel[0]:
            raise Missing(f"{rel} missing column {k}")

        def dist(r, _k=k, _t=target):
            try:
                return abs(float(r[_k]) - _t)
            except (TypeError, ValueError):
                return math.inf
        best = min(sel, key=dist)
        if dist(best) == math.inf:
            raise Missing(f"{rel} column {k} has no numeric rows for nearest matching to {target:.6g}")
        sel = [best]
    agg = expr.get("agg")
    where_desc = dict(static_where)
    where_desc.update({k: f"nearest({v:.6g})" for k, v in nearest_where.items()})
    if agg == "count":
        return float(len(sel))
    if not sel:
        raise Missing(f"{rel} has no matching rows where={where_desc} range={rng}")
    if agg is None:
        if len(sel) != 1:
            raise Missing(f"{rel} where={where_desc} matched {len(sel)} rows; require a unique row or specify agg")
        return _row_value(sel[0], col, colexpr, rel)
    if agg not in _AGGS:
        raise Missing(f"Unknown agg {agg}")
    if agg == "first":
        return _row_value(sel[0], col, colexpr, rel)
    if agg == "last":
        return _row_value(sel[-1], col, colexpr, rel)
    if agg == "max_decimals":
        if col is None:
            raise Missing("max_decimals requires col")
        return float(max(_decimals(r.get(col)) for r in sel))
    vals = [_row_value(r, col, colexpr, rel) for r in sel]
    if agg == "min":
        return min(vals)
    if agg == "max":
        return max(vals)
    if agg == "mean":
        return sum(vals) / len(vals)
    if agg == "ptp":
        return max(vals) - min(vals)
    if agg == "maxabs":
        return max(abs(v) for v in vals)
    if agg == "n_unique":
        return float(len({round(v, 9) for v in vals}))
    if agg == "n_nonincreasing":
        return float(sum(1 for a, b in zip(vals, vals[1:]) if b <= a + _GRID_TOL))
    if agg == "n_offgrid":
        step = expr.get("step")
        if not step:
            raise Missing("n_offgrid requires step")
        return float(sum(1 for v in vals if abs(v / step - round(v / step)) > 1e-6))
    key = sub(expr.get("arg_col") or "")
    if not key:
        raise Missing("argmin/argmax requires arg_col")
    pick = min if agg == "argmin" else max
    idx = pick(range(len(sel)), key=lambda i: vals[i])
    return as_num(sel[idx].get(key), f"{rel}:{key}")


def ev(expr, root: Path, env: dict) -> float:
    """Evaluate expr as a scalar; env substitutes {V} placeholders."""
    if isinstance(expr, (int, float)) and not isinstance(expr, bool):
        return float(expr)
    if not isinstance(expr, dict):
        raise Missing(f"Invalid expression {expr!r}")

    def sub(s):
        return s.format(**env) if env and isinstance(s, str) else s

    if "const" in expr:
        return float(expr["const"])
    if "abs" in expr:
        return abs(ev(expr["abs"], root, env))
    if "neg" in expr:
        return -ev(expr["neg"], root, env)
    if "sub" in expr:
        a, b = expr["sub"]
        return ev(a, root, env) - ev(b, root, env)
    if "add" in expr:
        return sum(ev(e, root, env) for e in expr["add"])
    if "mul" in expr:
        out = 1.0
        for e in expr["mul"]:
            out *= ev(e, root, env)
        return out
    if "max" in expr:
        return max(ev(e, root, env) for e in expr["max"])
    if "min" in expr:
        return min(ev(e, root, env) for e in expr["min"])
    if "div" in expr:
        a, b = expr["div"]
        den = ev(b, root, env)
        if den == 0:
            raise Missing("Division by zero")
        return ev(a, root, env) / den
    if "json" in expr:
        rel = sub(expr["json"])
        path = expr["path"]
        path = [sub(p) for p in path] if isinstance(path, list) else sub(path)
        return as_num(dig(load_json(root, rel), path, rel), f"{rel}:{_path_str(path)}")
    if "csv" in expr:
        rel = sub(expr["csv"])
        return _table_value(expr, load_csv(root, rel), rel, root, env, sub)
    if "jsontable" in expr:
        rel = sub(expr["jsontable"])
        obj = load_json(root, rel)
        path = expr.get("path")
        if path is not None:
            path = [sub(p) for p in path] if isinstance(path, list) else sub(path)
            obj = dig(obj, path, rel)
        if not isinstance(obj, list):
            raise Missing(f"{rel}:{_path_str(path)} is not an array")
        rows = []
        for i, r in enumerate(obj):
            if not isinstance(r, dict):
                raise Missing(f"{rel}:{_path_str(path)}[{i}] is not an object")
            rows.append(r)
        return _table_value(expr, rows, f"{rel}:{_path_str(path)}", root, env, sub)
    raise Missing(f"Invalid expression {expr!r}")


# ---------------------------------------------------------------- Criterion evaluation

_CMPS = ("in", "le", "ge", "lt", "gt", "eq", "finite")


def clause(cl: dict, root: Path, env: dict) -> tuple[bool, str]:
    if "forall" in cl:
        spec = cl["forall"]
        name = spec.get("as", "V")
        oks, notes = [], []
        for item in spec["over"]:
            sub_env = dict(env or {})
            sub_env[name] = item
            for c in spec["all"]:
                try:
                    ok, why = clause(c, root, sub_env)
                except Missing as exc:
                    ok, why = False, f"Missing evidence: {exc}"
                oks.append(ok)
                if not ok:
                    notes.append(f"[{item}] {why}")
        return all(oks), ("; ".join(notes[:4]) if notes else f"forall: all {len(spec['over'])} items passed")
    if "any" in cl:
        notes = []
        for c in cl["any"]:
            try:
                ok, why = clause(c, root, env)
            except Missing as exc:
                ok, why = False, f"Missing evidence: {exc}"
            if ok:
                return True, f"any satisfied: {why}"
            notes.append(why)
        return False, "any: no alternatives passed: " + " | ".join(notes[:4])

    v = ev(cl["value"], root, env)
    label = cl.get("label") or _label(cl["value"], env)
    if isinstance(label, str) and env:
        try:
            label = label.format(**env)
        except (KeyError, IndexError, ValueError):
            pass
    if "in" in cl:
        lo, hi = cl["in"]
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        return ok, f"{label}={v:.6g} {'∈' if ok else '∉'} [{lo}, {hi}]"
    if "le" in cl:
        return v <= cl["le"], f"{label}={v:.6g} vs ≤{cl['le']}"
    if "ge" in cl:
        return v >= cl["ge"], f"{label}={v:.6g} vs ≥{cl['ge']}"
    if "lt" in cl:
        return v < cl["lt"], f"{label}={v:.6g} vs <{cl['lt']}"
    if "gt" in cl:
        return v > cl["gt"], f"{label}={v:.6g} vs >{cl['gt']}"
    if "eq" in cl:
        tol = cl.get("tol", 0.0)
        return abs(v - cl["eq"]) <= tol, f"{label}={v:.6g} vs {cl['eq']}±{tol}"
    if cl.get("finite"):
        return True, f"{label}={v:.6g} exists"
    raise Missing(f"clause is missing a comparison operator; requires one of {_CMPS}")


def _label(expr, env) -> str:
    def fmt(s):
        try:
            return s.format(**(env or {}))
        except (KeyError, IndexError, ValueError):
            return s
    if isinstance(expr, dict):
        if "json" in expr:
            return fmt(f"{expr['json']}:{_path_str(expr['path'])}")
        for key in ("csv", "jsontable"):
            if key in expr:
                what = expr.get("col") or f"colexpr({expr.get('colexpr')})"
                tail = f":{_path_str(expr['path'])}" if key == "jsontable" and expr.get("path") else ""
                return fmt(f"{expr[key]}{tail}:{expr.get('agg') or ''}{what}")
        for op in ("sub", "add", "div", "mul", "abs", "neg", "max", "min"):
            if op in expr:
                return op
    return "value"


def score_leaf(leaf: dict, root: Path) -> dict:
    chk = leaf["check"]
    mode = chk.get("mode", "full")
    notes, ok_all = [], True
    for cl in chk["all"]:
        try:
            ok, why = clause(cl, root, {})
        except Missing as exc:
            ok, why = False, f"Missing evidence: {exc}"
        ok_all &= ok
        notes.append(("OK " if ok else "NG ") + why)
    reason = "; ".join(notes)
    if len(reason) > 700:
        bad = [n for n in notes if n.startswith("NG ")]
        reason = "; ".join(bad[:5] if bad else notes[:5]) + f" … ({len(notes)} subcriteria total)"
    tier = chk.get("tier", 1)
    if mode == "fail_only":
        if ok_all:
            manual = chk.get("manual") or "subitems in description not covered by the script"
            return {"id": leaf["id"], "score": None,
                    "reason": f"[auto tier{tier} fail_only] all mechanical subchecks passed: {reason} ‖ "
                              f"pending judge assessment: {manual}"}
        return {"id": leaf["id"], "score": 0,
                "reason": f"[auto tier{tier} fail_only] {reason}"}
    return {"id": leaf["id"], "score": 1 if ok_all else 0,
            "reason": f"[auto tier{tier}] {reason}"}


# ---------------------------------------------------------------- Main entrypoint


def leaves_with_check(node, out=None):
    out = [] if out is None else out
    if "sub_tasks" in node:
        for c in node["sub_tasks"]:
            leaves_with_check(c, out)
    elif "check" in node:
        out.append(node)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rubric")
    ap.add_argument("submission", help="submission/ directory containing results/")
    ap.add_argument("--tier", type=int, default=None, help="evaluate only this tier (0/1/2)")
    ap.add_argument("--json", dest="out", default=None, help="write results as a leaf_results fragment")
    a = ap.parse_args()

    rubric = json.loads(Path(a.rubric).read_text(encoding="utf-8"))
    root = Path(a.submission)
    if not root.is_dir():
        print(f"submission directory does not exist: {root}", file=sys.stderr)
        return 1

    leaves = leaves_with_check(rubric)
    if a.tier is not None:
        leaves = [l for l in leaves if l["check"].get("tier", 1) == a.tier]
    results = [score_leaf(l, root) for l in leaves]

    by_tier: dict[int, list] = {}
    for l, r in zip(leaves, results):
        by_tier.setdefault(l["check"].get("tier", 1), []).append(r["score"])

    for r in results:
        s = "-" if r["score"] is None else str(r["score"])
        print(f"{s}  {r['id']:10s} {r['reason']}")
    print("-" * 60)
    for t in sorted(by_tier):
        s = by_tier[t]
        passed = sum(1 for x in s if x == 1)
        pending = sum(1 for x in s if x is None)
        failed = sum(1 for x in s if x == 0)
        print(f"tier{t}: {passed} pass / {failed} fail / {pending} pending judge (all fail_only mechanical subchecks passed)"
              f" of {len(s)}")

    if a.out:
        Path(a.out).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"written {a.out}")
    return 0


def rows(root, variant, filename):
    _, result = evidence_contract.read_csv(root / "results" / variant / filename)
    if not result:
        raise ValueError(f"empty {variant}/{filename}")
    for row in result:
        for name, value in row.items():
            if name != "plane":
                try:
                    row[name] = float(value)
                except ValueError:
                    continue
                if not math.isfinite(row[name]):
                    raise ValueError(f"non-finite {variant}/{filename}:{name}")
    return result


def extremum(data, column, maximize=False):
    ordered = sorted(data, key=lambda row: row["frequency_GHz"])
    return (max if maximize else min)(ordered, key=lambda row: row[column])


def component(data, index, column, threshold, above=True):
    qualifies = lambda row: row[column] >= threshold if above else row[column] <= threshold
    if not qualifies(data[index]):
        return None
    lo = hi = index
    while lo and qualifies(data[lo - 1]):
        lo -= 1
    while hi + 1 < len(data) and qualifies(data[hi + 1]):
        hi += 1
    return [data[lo]["frequency_GHz"], data[hi]["frequency_GHz"]]


def local_minima(data):
    """Match find_peaks(-S11, prominence=2), without a new grader dependency."""
    signal = [-row["S11_dB"] for row in data]
    peaks = []
    index = 1
    while index < len(signal) - 1:
        end = index
        while end + 1 < len(signal) and signal[end + 1] == signal[index]:
            end += 1
        if signal[index - 1] < signal[index] and end + 1 < len(signal) and signal[end + 1] < signal[index]:
            center = (index + end) // 2
            left = right = center
            left_min = right_min = signal[center]
            while left >= 0 and signal[left] <= signal[center]:
                left_min = min(left_min, signal[left])
                left -= 1
            while right < len(signal) and signal[right] <= signal[center]:
                right_min = min(right_min, signal[right])
                right += 1
            prominence = signal[center] - max(left_min, right_min)
            if prominence >= 2:
                peaks.append((center, prominence))
        index = end + 1
    selected = sorted(peaks, key=lambda pair: (-pair[1], data[pair[0]]["frequency_GHz"]))[:8]
    return [{"f_GHz": data[i]["frequency_GHz"], "S11_dB": data[i]["S11_dB"]}
            for i, _ in sorted(selected)]


def cpw_value(root, variant, field):
    if field in {"s11_band_GHz", "s11_local_minima", "worst_coupling_dB", "s13_max_dB"}:
        data = rows(root, variant, "sparams.csv")
        if field == "s11_band_GHz":
            return component(data, data.index(extremum(data, "S11_dB")), "S11_dB", -9.5, False)
        if field == "s11_local_minima":
            return local_minima(data)
        if field == "worst_coupling_dB":
            return max(row[column] for row in data for column in ("S12_dB", "S13_dB", "S14_dB"))
        return max(row["S13_dB"] for row in data)
    if field in {"eff_min", "eff_max"}:
        data = rows(root, variant, "efficiency.csv")
        return extremum(data, "radiation_efficiency", field == "eff_max")["radiation_efficiency"]
    if "gain" in field:
        data = rows(root, variant, "gain.csv")
        point = extremum(data, "peak_gain_dBi", field != "peak_gain_min_dBi")
        return point["frequency_GHz"] if field.startswith("f_") else point["peak_gain_dBi"]
    if field in {"ecc_max", "f_ecc_max_GHz", "dg_min_dB", "mux_eff_min_dB"}:
        data = rows(root, variant, "mimo_metrics.csv")
        if field in {"ecc_max", "f_ecc_max_GHz"}:
            point = max(data, key=lambda row: max(row[c] for c in ("ECC12", "ECC13", "ECC14")))
            return point["frequency_GHz"] if field.startswith("f_") else max(point[c] for c in ("ECC12", "ECC13", "ECC14"))
        return min(row["DG_dB" if field == "dg_min_dB" else "mux_eff_dB"] for row in data)
    raise ValueError(f"unsupported CPW summary field: {field}")


def referenced_fields(check):
    output = set()
    def visit(node, env=None):
        env = env or {}
        if isinstance(node, list):
            for value in node:
                visit(value, env)
        elif isinstance(node, dict):
            if "forall" in node:
                spec = node["forall"]
                for value in spec["over"]:
                    visit(spec["all"], {**env, spec.get("as", "V"): value})
            else:
                for kind in ("json", "jsontable"):
                    if kind in node:
                        path = node[kind].format(**env)
                        parts = Path(path).parts
                        if len(parts) == 3 and parts[0] == "results" and parts[2] == "summary.json":
                            field = node["path"][0] if isinstance(node["path"], list) else node["path"].split(".")[0]
                            output.add((parts[1], field.format(**env)))
                for value in node.values():
                    visit(value, env)
    visit(check)
    return sorted(output)


def source_files(variant, field):
    if field in {"s11_band_GHz", "s11_local_minima", "worst_coupling_dB", "s13_max_dB"}:
        return ["sparams.csv"]
    if field.startswith("eff_"):
        return ["efficiency.csv"]
    if "gain" in field:
        return ["gain.csv"]
    return ["mimo_metrics.csv"]


def equivalent(actual, expected, field):
    if expected is None:
        return actual is None
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(equivalent(a,b,field) for a,b in zip(actual,expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(key in actual and equivalent(actual[key], value, key) for key,value in expected.items())
    if isinstance(actual, bool) or not isinstance(actual, (int,float)) or not math.isfinite(actual):
        return False
    # All frequency fields referenced by numerical leaves are grid selections.
    tolerance = 1e-8 if field.endswith("_GHz") else .011 if "dB" in field or "deg" in field else .0011
    return abs(actual-expected) <= tolerance + 1e-12


def validated_summary_view(leaf, root):
    import json

    errors = []
    views = {}
    for variant, field in referenced_fields(leaf["check"]):
        try:
            path = root / "results" / variant / "summary.json"
            payload = evidence_contract.read_json(path)
            if not isinstance(payload, dict):
                raise ValueError("summary must be a JSON object")
            expected = cpw_value(root, variant, field)
            if field not in payload or not equivalent(payload[field], expected, field):
                errors.append(f"{variant}/summary.json:{field}: reported={payload.get(field)!r}, recomputed={expected!r}")
            else:
                views.setdefault(path, payload)[field] = expected
        except (OSError, ValueError, KeyError, IndexError, StopIteration, TypeError) as exc:
            errors.append(f"{variant}/summary.json:{field}: cannot verify from CSV: {exc}")
    return errors, views


def validate_references(leaf, root):
    return validated_summary_view(leaf, root)[0]


def _leaves(node: dict) -> list[dict]:
    children = node.get("sub_tasks")
    if isinstance(children, list):
        result: list[dict] = []
        for child in children:
            result.extend(_leaves(child))
        return result
    return [node]


def score(leaf_id: str, submission: Path) -> tuple[int, str]:
    rubric = json.loads((Path(__file__).resolve().parents[1] / "rubric.json").read_text(encoding="utf-8"))
    matching = [leaf for leaf in _leaves(rubric) if str(leaf.get("id")) == str(leaf_id)]
    if len(matching) != 1 or matching[0].get("check", {}).get("mode") != "full":
        raise ValueError(f"no deterministic rubric check for {leaf_id}")
    errors, summaries = validated_summary_view(matching[0], Path(submission))
    if errors:
        return 0, "CSV/summary contract: " + "; ".join(errors[:4])
    # Evaluate response-derived scalars at their actual values, without editing outputs.
    missing = object()
    previous = {path: _json_cache.get(path, missing) for path in summaries}
    _json_cache.update(summaries)
    try:
        result = score_leaf(matching[0], Path(submission))
    finally:
        for path, value in previous.items():
            if value is missing:
                _json_cache.pop(path, None)
            else:
                _json_cache[path] = value
    value = result.get("score")
    if type(value) is not int or value not in (0, 1):
        raise ValueError(f"non-terminal deterministic result for {leaf_id}: {value!r}")
    return value, str(result.get("reason", ""))


if __name__ == "__main__":
    sys.exit(main())
