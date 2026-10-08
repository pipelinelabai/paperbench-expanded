"""Safe artifact readers and scoring-time provenance qualification."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime
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


def platform_validation(g):
    from task03_platform_validation import check
    return check(g)


def response_targets(leaf, variants):
    targets = set()
    for entry in leaf.get("evidence_inputs", []):
        path = entry.get("path", "")
        if not path.startswith("submission/"):
            continue
        relative = Path(path.removeprefix("submission/"))
        parts = relative.parts
        if len(parts) < 3 or parts[1] not in variants:
            continue
        if parts[0] == "results" and (relative.suffix == ".csv" or relative.name == "summary.json" or entry.get("kind") == "image"):
            targets.add(relative.as_posix())
        if parts[0] == "views" and relative.name.startswith("current_") and entry.get("kind") == "image":
            targets.add(relative.as_posix())
    return sorted(targets)


def manifest_sources(leaf, policy, g):
    variants = set(policy.get("variants", []))
    targets = response_targets(leaf, variants)
    audit_all = leaf["id"] in {"B2_4", "B2_5", "B2_6", "C_INV_3"}
    if not targets and not audit_all:
        return {}
    root = g.SUBMISSION.resolve()
    loaded, exports, derived = {}, {}, {}
    checked_raw, ancillary = set(), set()
    log_index_issues = {}

    def locate(base, name):
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            raise g.EvidenceError("manifest paths must be nonempty relative paths")
        path = base / name
        if not path.resolve().is_relative_to(root):
            raise g.EvidenceError("manifest path escapes submission")
        return path

    def owner(path):
        parts = path.resolve().relative_to(root).parts
        return parts[1] if len(parts) >= 3 and parts[0] in {"results", "views"} and parts[1] in variants else None

    def load_variant(variant):
        if variant in loaded:
            return
        raw = root / "results" / variant / "raw"
        payload = g.load_json(raw / "MANIFEST.json", root)
        if not isinstance(payload, dict) or payload.get("variant") != variant:
            raise g.EvidenceError(f"invalid raw manifest variant: {variant}")
        native, outputs = payload.get("exports"), payload.get("derived")
        if not isinstance(native, list) or not native or not isinstance(outputs, list):
            raise g.EvidenceError(f"invalid raw manifest lists: {variant}")
        loaded[variant] = raw
        for entry in native:
            if not isinstance(entry, dict):
                raise g.EvidenceError("manifest export must be an object")
            path = locate(raw, entry.get("file"))
            if ".." in Path(entry["file"]).parts or path.name == "MANIFEST.json":
                raise g.EvidenceError("raw export path must stay inside raw/")
            key = path.resolve()
            if key in exports:
                raise g.EvidenceError(f"duplicate manifest export: {entry['file']}")
            exports[key] = (variant, path, entry)
        for entry in outputs:
            if not isinstance(entry, dict):
                raise g.EvidenceError("manifest derived entry must be an object")
            path = locate(raw, entry.get("file"))
            key = path.resolve()
            if key.is_relative_to(raw.resolve()):
                raise g.EvidenceError("derived response cannot be stored inside raw/")
            inputs = entry.get("from")
            if not isinstance(inputs, list) or not inputs:
                raise g.EvidenceError(f"derived entry has no inputs: {entry['file']}")
            sources = [locate(raw, name) for name in inputs]
            by = entry.get("by")
            if not isinstance(by, str) or ":" not in by or not all(part.strip() for part in by.rsplit(":", 1)):
                raise g.EvidenceError(f"derived entry lacks its source/function locator: {entry['file']}")
            source_name = by.rsplit(":", 1)[0]
            source_path = locate(root, source_name)
            if not source_path.is_file() and len(Path(source_name).parts) == 1:
                source_path = locate(root / "src", source_name)
            g.regular(source_path, root)
            signature = ([source.resolve() for source in sources], by)
            if key in derived and derived[key][2] != signature:
                raise g.EvidenceError(f"conflicting derived provenance: {entry['file']}")
            derived[key] = (path, sources, signature)

    def check_export(key):
        variant, path, entry = exports[key]
        g.regular(path, root)
        if entry.get("sha256") != g.sha256(path) or type(entry.get("bytes")) is not int or entry["bytes"] != path.stat().st_size:
            raise g.EvidenceError(f"native export bytes/hash mismatch: {path.relative_to(root)}")
        for field in ("producer", "aedt_solution", "exported_utc"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise g.EvidenceError(f"native export missing {field}: {path.relative_to(root)}")
        try:
            stamp = datetime.fromisoformat(entry["exported_utc"].replace("Z", "+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
                raise ValueError("expected UTC")
        except ValueError as exc:
            raise g.EvidenceError("invalid native export UTC timestamp") from exc
        log = root / "results" / variant / "run.log"
        g.regular(log, root, max_bytes=g.MAX_TEXT)
        line_count = len(log.read_text(errors="replace").splitlines())
        span = entry.get("run_log_lines")
        if not isinstance(span, list) or len(span) != 2 or any(type(n) is not int for n in span) or not 1 <= span[0] <= span[1] <= line_count:
            detail = f"{path.relative_to(root)}: run_log_lines must be a valid inclusive [start,end] pair"
            if leaf["id"] == "B2_5":
                raise g.EvidenceError(detail)
            log_index_issues[key] = detail
        g.native_log_check(log, log.with_name("meta.json"))
        checked_raw.add(key)

    def is_static(path):
        rel = path.relative_to(root)
        if rel.parts[0] not in g.REPLAY_GENERATED_ROOTS and path.suffix.lower() not in g.NATIVE_INPUT_SUFFIXES:
            return True
        return (len(rel.parts) == 3 and rel.parts[0] == "results"
                and rel.name in {"meta.json", "structure.json", "coding_matrices.json"})

    def visit(path, trail):
        g.regular(path, root)
        key = path.resolve()
        if key in trail:
            raise g.EvidenceError("cycle in numerical response provenance")
        variant = owner(path)
        if variant:
            load_variant(variant)
        if key in exports:
            check_export(key)
            return {key}
        if is_static(key):
            ancillary.add(key)
            return set()
        if key not in derived:
            raise g.EvidenceError(f"response omitted from manifest provenance: {key.relative_to(root)}")
        sources = set()
        for item in derived[key][1]:
            sources.update(visit(item, trail | {key}))
        if not sources:
            raise g.EvidenceError(f"response has no native-data ancestor: {key.relative_to(root)}")
        return sources

    if audit_all:
        for variant in sorted(variants):
            load_variant(variant)
        for variant, raw in loaded.items():
            actual = {path.resolve() for path in g.safe_directory(raw, root) if path.name != "MANIFEST.json"}
            listed = {key for key, item in exports.items() if item[0] == variant}
            if actual != listed:
                raise g.EvidenceError(f"raw manifest inventory mismatch: {variant}")
        for key in exports:
            check_export(key)
        targets = sorted(set(targets) | {path.relative_to(root).as_posix() for path in derived})
    per_target = {}
    for target in targets:
        sources = visit(root / target, set())
        related = {owner(root / target)} | {owner(path) for path in sources}
        per_target[target] = {'targets': [target],
                              'raw': sorted(path.relative_to(root).as_posix() for path in sources),
                              'variants': sorted(variant for variant in related if variant),
                              'log_index_issues': [log_index_issues[path] for path in sorted(sources)
                                                   if path in log_index_issues]}
    for group in per_target.values():
        group['ancillary'] = sorted(path.relative_to(root).as_posix() for path in ancillary)
    return {"targets": targets,
            "per_target": per_target,
            "raw": sorted(path.relative_to(root).as_posix() for path in checked_raw),
            "ancillary": sorted(path.relative_to(root).as_posix() for path in ancillary),
            "variants": sorted(loaded),
            "log_index_issues": list(log_index_issues.values()),
            "note": "Hashes and declared ancestry checked; native format, dataflow and transformations require scientific source review."}


def precheck(leaf, policy, g):
    result = {}
    if leaf["id"] == "B2_6":
        result["platform_validation"] = platform_validation(g)
    if leaf["id"].startswith("C") or leaf["id"] in {"B2_4", "B2_5", "B2_6"}:
        result["provenance"] = manifest_sources(leaf, policy, g)
    return result


# Native exports are delivered complete up to this size so a required
# manifest-listed export is never silently truncated (a truncated required
# export provably forces a verifier_incomplete infrastructure error).
RAW_EXCERPT_FULL_BYTES = 256 * 1024


def raw_excerpt(path, g):
    g.regular(path, g.SUBMISSION)
    size = path.stat().st_size
    pieces = []
    with path.open("rb") as stream:
        if size <= RAW_EXCERPT_FULL_BYTES:
            data = stream.read()
            if b"\0" in data:
                return "BINARY INPUT NOT DECODED by the verifier; this is not a candidate omission."
            return "FULL NATIVE TEXT:\n" + data.decode("utf-8", errors="replace")
        for fraction in (0, .25, .5, .75, 1):
            start = max(0, min(int(size * fraction), size - 2400))
            stream.seek(start)
            data = stream.read(2400)
            if b"\0" in data:
                return "BINARY INPUT NOT DECODED by the verifier; this is not a candidate omission."
            text = data.decode("utf-8", errors="replace")
            if start:
                text = text.partition("\n")[2]
            pieces.append(f"byte offset {start}:\n{text}")
            if size <= 2400:
                break
    return "PARTIAL NATIVE TEXT: omitted samples cannot establish a complete integral or global extremum.\n" + "\n".join(pieces)


def judge_evidence(leaf, task_name, gate, g):
    if leaf.get('id') in {'B2_5', 'C_INV_3'}:
        inputs = [{**entry, 'kind': 'sampled_csv' if entry.get('kind') == 'csv'
                   else 'source_complete' if entry.get('kind') == 'source' else entry.get('kind')}
                  for entry in leaf.get('evidence_inputs', [])]
        leaf = {**leaf, 'evidence_inputs': inputs}
    contract = gate.get("contract", {})
    parts = ["ACTUAL SCORING PRECHECKS (not automatic scientific credit):\n" + json.dumps(contract, ensure_ascii=False)]
    for name in contract.get("provenance", {}).get("raw", []):
        path = g.SUBMISSION / name
        parts.append(f"NATIVE EXPORT EXCERPTS {name}; sha256={g.sha256(path)}:\n{raw_excerpt(path, g)}")
    reserve = min(160 * 1024, max(16 * 1024, sum(len(part) for part in parts) + 2 * len(parts)))
    try:
        primary = g.evidence_digest(leaf, task_name, limit=g.DIGEST_TOTAL_MAX - reserve)
    except g.EvidenceError as exc:
        if str(exc).startswith("complete CSV evidence exceeds judge digest limit"):
            raise g.JudgeInfrastructureError("verifier evidence packet cannot fit complete required CSVs") from exc
        raise
    supplement = g._fit_digest_parts(parts, limit=g.DIGEST_TOTAL_MAX - len(primary) - 2)
    return primary + "\n\n" + supplement


def source_evidence_status(raw):
    decoder = json.JSONDecoder()
    for index, character in enumerate(raw):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "score" in value:
            status = value.get("evidence_status")
            if status in {"sufficient", "candidate_missing", "verifier_incomplete"}:
                return status
    raise ValueError("source review omitted a valid evidence_status")


def review_numeric_sources(leaf, task_name, gate, context, cache, g):
    provenance = gate.get("contract", {}).get("provenance", {})
    if not provenance.get("targets"):
        return None
    if len(provenance['targets']) > 1 and provenance.get('per_target'):
        reviews = []
        for target in provenance['targets']:
            group = provenance['per_target'][target]
            partial = {**gate, 'contract': {**gate['contract'], 'provenance': group}}
            reviews.append(review_numeric_sources(leaf, task_name, partial, context, cache, g))
        return {'score': 1, 'targets': list(provenance['targets']), 'reviews': reviews,
                'reason': 'Every response file independently passed native-source qualification.'}
    key = tuple(provenance["targets"])
    if key not in cache:
        inputs = [{"path": "submission/src/", "kind": "source_complete"}]
        for name in provenance["targets"]:
            inputs.append({"path": "submission/" + name, "kind": "csv" if name.endswith(".csv") else "json"})
        for variant in provenance["variants"]:
            for name, kind in (("meta.json", "json"), ("raw/MANIFEST.json", "json"), ("run.log", "log")):
                inputs.append({"path": f"submission/results/{variant}/{name}", "kind": kind})
        included = {entry["path"] for entry in inputs}
        for name in provenance.get("ancillary", []):
            path = "submission/" + name
            if path not in included:
                suffix = Path(name).suffix.lower()
                kind = "json" if suffix == ".json" else "data" if suffix in {".npy", ".npz"} else "source" if suffix in {".py", ".sh"} else "text"
                inputs.append({"path": path, "kind": kind})
                included.add(path)
        scope = {'response_files': list(key),
                 'submitted_summary_files': [name for name in key if Path(name).name == 'summary.json']}
        criterion = 'EXACT RESPONSE REVIEW SCOPE: ' + json.dumps(scope, ensure_ascii=False) + '\n' + (
            "Qualify ONLY the native source of the listed response files, without comparing to paper target windows. "
            "Each response file in response_files must actually be computed from the identified native exports "
            "of the matching solved design, variation, excitation and quantity. Inspect export calls, manifest-linked log "
            "records, raw report expressions and the executed derivation dataflow. Audit the transformation algorithm, "
            "units, reference planes and required input components. For a full-sphere integral or global maximum, "
            "audit the complete algorithm and source identity; never claim to have numerically recomputed the full "
            "integral or maximum from file excerpts. Check directly mapped samples when the complete necessary inputs "
            "are available. The separate aggregate raw-data audit requires at least five actual response samples. "
            "Only a summary explicitly listed in submitted_summary_files is under review. A CSV-only review does not "
            "require any downstream summary, extrema or connected-band claims merely mentioned in its manifest or "
            "source. Complete target CSVs and independent numerical checks are separate from this provenance decision. "
            "Partial native excerpts cannot prove a numerical integral, but do not by themselves prevent an audit of "
            "the complete transformation algorithm, native source identity and directly mapped response samples. "
            "Legal complex-to-dB/phase, normalization, integration and frozen static inputs outside generated directories "
            "are allowed. Hash agreement or a declared from-list alone does not establish actual dataflow. "
            "Reject hardcoded/paper-fed responses, unrelated native exports, wrong quantities and unsupported provenance. "
            "A matching paper number cannot compensate for invalid provenance. Limit this decision to the files listed; "
            "an unrelated variant's failure is not a reason to reject them. Return an additional structured JSON field "
            "evidence_status: sufficient, candidate_missing, or verifier_incomplete. Use verifier_incomplete with "
            "score=0 when a necessary file is present in the inventory but omitted, truncated or undecoded by the "
            "verifier, or the verifier omitted needed source. This produces an infrastructure error, not a candidate "
            "failure. Use candidate_missing only for evidence actually absent from the submission. Sufficient means "
            "the packet supports a decision, including a proven wrong transformation. Never infer fabricated data "
            "from verifier truncation. A score of 1 requires all listed files to qualify."
        )
        packet = judge_evidence({"evidence_inputs": inputs}, task_name, gate, g)
        scope_id = hashlib.sha256(json.dumps(list(key)).encode()).hexdigest()[:12]
        cache[key] = g.llm_score(criterion, packet, context, [],
                               leaf_id=leaf["id"] + ":native_source:" + scope_id, source_review=True,
                               source_scope=provenance)
    score, reason, metadata = cache[key]
    status = metadata.get("evidence_status")
    if status not in {"sufficient", "candidate_missing", "verifier_incomplete"}:
        raise g.JudgeInfrastructureError("source review returned no valid evidence-status classification")
    if status == "verifier_incomplete":
        raise g.JudgeInfrastructureError("verifier source-evidence extraction is incomplete: " + reason)
    if score == 1 and status != "sufficient":
        raise g.JudgeInfrastructureError("source review passed despite reporting missing evidence")
    if score != 1:
        raise g.EvidenceError("native response provenance did not qualify: " + reason)
    return {"score": score, "reason": reason, "judge": metadata, "targets": list(key)}
