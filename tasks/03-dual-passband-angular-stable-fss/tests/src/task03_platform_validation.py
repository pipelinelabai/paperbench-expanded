import csv
import io
import math
import posixpath
import re


VERSION = "fss-platform-validation-v1"
COLUMNS = ("frequency_GHz", "S11_dB", "S21_dB")
VARIANTS = ("te_00", "te_30", "te_60", "te_86", "tm_00", "tm_30", "tm_60", "tm_83")


class UnsupportedEvidence(Exception):
    pass


def csv_rows(text):
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), skipinitialspace=True, strict=True)
    fields = [field.strip() for field in reader.fieldnames or []]
    if not fields or any(not field for field in fields) or len(fields) != len(set(fields)):
        raise ValueError("Blank or duplicate CSV headers")
    reader.fieldnames = fields
    records = list(reader)
    if not records or any(None in row or any(value is None or not value.strip() for value in row.values()) for row in records):
        raise ValueError("Empty, ragged or blank CSV data")
    return fields, records


def finite(value):
    if isinstance(value, bool):
        raise ValueError("A boolean is not a response number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Nonfinite response number")
    return result


def response_rows(text):
    fields, records = csv_rows(text)
    if not set(COLUMNS).issubset(fields):
        raise ValueError("Missing required response columns")
    result = [tuple(finite(row[column]) for column in COLUMNS) for row in records]
    if len(result) != 1351:
        raise ValueError("The response must contain all 1351 contract-grid rows")
    if any(abs(row[0] - (3 + index / 100)) > 1e-8 for index, row in enumerate(result)):
        raise ValueError("Response frequencies are duplicated, unordered or off the contract grid")
    return result


def normalize_expression(value):
    return re.sub(r"\s+", "", value)


def native_rows(text, expressions):
    fields, records = csv_rows(text)
    frequencies = []
    for field in fields:
        match = re.fullmatch(r"Freq(?:uency)?\s*\[(Hz|kHz|MHz|GHz|THz)\]", field, re.I)
        if match:
            frequencies.append((field, {"hz": 1e-9, "khz": 1e-6, "mhz": 1e-3, "ghz": 1, "thz": 1000}[match[1].lower()]))
    if len(frequencies) != 1:
        raise UnsupportedEvidence("Native frequency units need an additional verifier reader")
    selected = []
    for expression in expressions:
        expected = normalize_expression(expression)
        if not expected.startswith("dB("):
            raise UnsupportedEvidence("Declared response conversion needs a transformation-specific verifier")
        matches = [field for field in fields if normalize_expression(field) in {expected, expected + "[]", expected + "[dB]"}]
        if len(matches) != 1:
            raise UnsupportedEvidence("Native response expression needs a different-format or transformation-specific verifier")
        selected.append(matches[0])
    frequency, scale = frequencies[0]
    return [(finite(row[frequency]) * scale, *(finite(row[field]) for field in selected)) for row in records]


def relative_path(store, base, value):
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise ValueError("Manifest dependencies must be nonempty relative paths")
    result = posixpath.normpath(base + "/" + value)
    store.canonical(result)
    return result


def native_response(store, variant):
    base = f"results/{variant}/raw"
    target = f"results/{variant}/sparams.csv"
    manifest = store.json(base + "/MANIFEST.json")
    if not isinstance(manifest, dict) or manifest.get("variant") != variant:
        raise ValueError(f"Invalid manifest variant: {variant}")
    entries = [entry for entry in manifest.get("derived", []) if relative_path(store, base, entry["file"]) == target]
    if len(entries) != 1 or not isinstance(entries[0].get("from"), list) or not entries[0]["from"]:
        raise ValueError("A unique, nonempty native response ancestry is required")
    exports = {}
    for entry in manifest.get("exports", []):
        path = relative_path(store, base, entry["file"])
        if path in exports:
            raise ValueError("Duplicate native export")
        exports[path] = entry
    metadata = store.json(f"results/{variant}/meta.json")
    mapping = store.resolve_reference(metadata.get("fundamental_trace_map"))
    if not isinstance(mapping, dict) or not all(isinstance(mapping.get(key), str) for key in ("S11_expression", "S21_expression")):
        raise UnsupportedEvidence("Native trace identity requires an additional verifier mapping")
    expressions = [mapping["S11_expression"], mapping["S21_expression"]]
    records, paths = [], []
    for dependency in entries[0]["from"]:
        path = relative_path(store, base, dependency)
        if path not in exports or not path.lower().endswith(".csv"):
            raise UnsupportedEvidence("Response ancestry requires a different native-format or transformation reader")
        text = store.text(path)
        entry = exports[path]
        if store.verified[path]["sha256"] != entry.get("sha256") or type(entry.get("bytes")) is not int or store.verified[path]["bytes"] != entry["bytes"]:
            raise ValueError(f"Native export hash or byte count mismatch: {path}")
        records.extend(native_rows(text, expressions))
        paths.append(path)
    records.sort(key=lambda row: row[0])
    if len(records) != 1351:
        raise UnsupportedEvidence("Native sampling requires a transformation-specific verifier; no interpolation is inferred")
    if any(abs(row[0] - (3 + index / 100)) > 1e-8 for index, row in enumerate(records)):
        raise UnsupportedEvidence("Native sampling does not directly map onto the contract grid")
    return records, paths


def summary_from_rows(records, variant):
    result = {"f0_p1_GHz": 8.45, "f0_p2_GHz": 12.76}
    statuses = {}
    bands = {}
    for band, lower, upper in ((1, 3.0, 9.5), (2, 11.5, 13.6)):
        indices = [index for index, row in enumerate(records) if lower <= row[0] <= upper]
        peak = max(indices, key=lambda index: records[index][2])
        result[f"f_peak_p{band}_GHz"] = records[peak][0]
        result[f"S21_peak_p{band}_dB"] = records[peak][2]
        center = result[f"f0_p{band}_GHz"]
        result[f"S21_at_f0_p{band}_dB"] = next(row[2] for row in records if abs(row[0] - center) <= 1e-8)
        if records[peak][2] < -3:
            bands[band] = None
            result[f"band{band}_3dB_GHz"] = None
            result[f"f_S11_min_p{band}_GHz"] = None
            result[f"S11_min_p{band}_dB"] = None
            statuses[f"band{band}"] = statuses[f"S11_min_p{band}"] = "no_passband"
            continue
        left = right = peak
        while left > 0 and records[left - 1][2] >= -3:
            left -= 1
        while right + 1 < len(records) and records[right + 1][2] >= -3:
            right += 1
        bands[band] = (left, right)
        result[f"band{band}_3dB_GHz"] = [records[left][0], records[right][0]]
        statuses[f"band{band}"] = "truncated_both" if left == 0 and right == len(records) - 1 else "truncated_low" if left == 0 else "truncated_high" if right == len(records) - 1 else "valid"
        minimum = min(records[left:right + 1], key=lambda row: row[1])
        result[f"f_S11_min_p{band}_GHz"], result[f"S11_min_p{band}_dB"] = minimum[:2]
        statuses[f"S11_min_p{band}"] = "valid"
    zero = min((row for row in records if 9.5 <= row[0] <= 11.5), key=lambda row: row[2])
    result["f_tz_GHz"], result["S21_tz_dB"] = zero[0], zero[2]
    result["f_tz2_GHz"] = result["S21_tz2_dB"] = None
    statuses["tz2"] = "not_applicable"
    if variant == "te_86":
        if bands[2] is None:
            statuses["tz2"] = "no_passband"
        elif bands[2][1] == len(records) - 1:
            statuses["tz2"] = "no_search_interval"
        else:
            zero = min(records[bands[2][1] + 1:], key=lambda row: row[2])
            result["f_tz2_GHz"], result["S21_tz2_dB"] = zero[0], zero[2]
            statuses["tz2"] = "valid"
    result["metric_status"] = statuses
    return result


def compare_summary(actual, expected, field="summary"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or not expected.keys() <= actual.keys():
            raise ValueError(f"Missing required summary fields: {field}")
        for name, value in expected.items():
            compare_summary(actual[name], value, name)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError(f"Invalid summary array: {field}")
        for observed, recomputed in zip(actual, expected):
            compare_summary(observed, recomputed, field)
    elif expected is None or isinstance(expected, str):
        if actual != expected:
            raise ValueError(f"Inconsistent summary status or null: {field}")
    else:
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            raise ValueError(f"Summary number has incorrect type: {field}")
        tolerance = 1e-8 if field.endswith("_GHz") else 1e-3
        if abs(finite(actual) - expected) > tolerance:
            raise ValueError(f"Inconsistent summary {field}: reported={actual}, recomputed={expected}, tolerance={tolerance}")


def validate(store):
    reports = []
    for variant in VARIANTS:
        actual = response_rows(store.text(f"results/{variant}/sparams.csv"))
        native, paths = native_response(store, variant)
        maximum = 0.0
        for index, (observed, expected) in enumerate(zip(actual, native)):
            for column, tolerance in enumerate((1e-8, 1e-5, 1e-5)):
                error = abs(observed[column] - expected[column])
                if error > tolerance:
                    raise ValueError(f"{variant}/{COLUMNS[column]} row {index + 1}: error={error}, tolerance={tolerance}")
                if column:
                    maximum = max(maximum, error)
        summary = store.json(f"results/{variant}/summary.json")
        compare_summary(summary, summary_from_rows(actual, variant))
        reports.append({"variant": variant, "response_samples": 2702, "native_inputs": paths,
                        "maximum_direct_error_dB": maximum, "summary_fields": 19})
    return {"version": VERSION, "status": "completed", "score": 1, "variants": reports,
            "candidate_checker_required": False, "candidate_code_executed": False,
            "verified_artifact_hashes": store.verified.copy(),
            "scope": "Numerical native/output/summary consistency; physical source identity remains separately audited."}


def check(grader):
    from artifact_review import ArtifactStore, InspectionError

    try:
        return validate(ArtifactStore(grader))
    except UnsupportedEvidence as exc:
        raise grader.JudgeInfrastructureError(f"Platform numerical reader incomplete: {exc}") from exc
    except InspectionError as exc:
        if exc.status in {"verifier_incomplete", "invalid_tool_request"}:
            raise grader.JudgeInfrastructureError(f"Platform evidence binding incomplete: {exc}") from exc
        raise grader.EvidenceError(f"Platform numerical verification failed: {exc}") from exc
    except (ValueError, TypeError, KeyError, IndexError, csv.Error, StopIteration) as exc:
        raise grader.EvidenceError(f"Platform numerical verification failed: {exc}") from exc
