"""Independently check the public AF equation, arrays and referenced summaries."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from zipfile import BadZipFile, ZipFile


INITIAL = [[1] * 6] * 3 + [[0] * 6] * 3
OPTIMAL = [
    [1, 1, 1, 0, 0, 0], [1, 0, 0, 1, 1, 0], [0, 0, 1, 0, 0, 0],
    [1, 0, 1, 1, 0, 1], [1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 1, 1],
]


def required_patterns(leaf_id):
    return {"C3_1": ("uniform", "initial"),
            "C3_2": ("uniform", "optimal")}.get(leaf_id, ("uniform", "initial", "optimal"))


def checked_path(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("AF evidence paths must be submission-relative")
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("AF evidence path escapes submission")
    current = root
    for part in Path(name).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("AF evidence path contains a symlink")
    if not path.is_file():
        raise ValueError(f"missing AF evidence: {name}")
    return path


def read_json(root, name):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError(f"duplicate AF JSON key: {key}")
            value[key] = item
        return value
    path = checked_path(root, name)
    if path.stat().st_size > 8 * 1024**2:
        raise ValueError("oversized AF metadata")
    value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError(f"AF JSON must be an object: {name}")
    return value


def validate(root, leaf_id):
    import numpy as np

    root = Path(root)
    base = "results/af_patterns/"
    patterns = required_patterns(leaf_id)
    matrices = read_json(root, base + "coding_matrices.json")
    meta = read_json(root, base + "meta.json")
    summary = read_json(root, base + "af_summary.json")
    if matrices.get("row_axis") != "+x" or matrices.get("col_axis") != "+y":
        raise ValueError("AF matrix row/column axes must be +x/+y")
    if not isinstance(matrices.get("one_means"), str) or not matrices["one_means"].strip():
        raise ValueError("AF coding matrix requires its physical one_means mapping")
    if "numerical" not in str(meta.get("result_source", "")).lower():
        raise ValueError("AF result_source must identify the numerical model")
    for field in ("input_sha256", "source_sha256"):
        hashes = meta.get(field)
        if not isinstance(hashes, dict) or not hashes:
            raise ValueError(f"missing AF {field}")
        if field == "input_sha256" and base + "coding_matrices.json" not in hashes:
            raise ValueError("AF input_sha256 must cover coding_matrices.json")
        for name, digest in hashes.items():
            path = checked_path(root, name)
            if field == "source_sha256" and not path.relative_to(root).as_posix().startswith("src/"):
                raise ValueError("AF source_sha256 must reference a source under src/")
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"AF hash mismatch: {name}")

    matrix_arrays = {"uniform": np.zeros((6, 6), dtype=int)}
    complements = set()
    for name in patterns:
        if name == "uniform":
            continue
        array = np.asarray(matrices.get(name))
        if array.shape != (6, 6) or array.dtype.kind not in "iuf" or not np.isin(array, (0, 1)).all():
            raise ValueError(f"AF {name} must be a 6x6 binary matrix")
        reference = np.asarray(INITIAL if name == "initial" else OPTIMAL)
        if np.array_equal(array, reference):
            complements.add(False)
        elif np.array_equal(array, 1 - reference):
            complements.add(True)
        else:
            raise ValueError(f"AF {name} does not match the specified paper matrix")
        matrix_arrays[name] = array
    if len(complements) > 1:
        raise ValueError("AF matrices use inconsistent global bit relabeling")

    path = checked_path(root, base + "af_samples.npz")
    expected_names = {"theta_deg", "phi_deg", *("af_" + name for name in patterns)}
    try:
        with ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > 16 or len({entry.filename for entry in entries}) != len(entries):
                raise ValueError("invalid AF archive inventory")
            if sum(entry.file_size for entry in entries) > 16 * 1024**2:
                raise ValueError("oversized AF array archive")
            for name in expected_names:
                if name + ".npy" not in archive.namelist():
                    raise ValueError("AF archive is missing required arrays")
                with archive.open(name + ".npy") as stream:
                    version = np.lib.format.read_magic(stream)
                    if version == (1, 0):
                        shape, _, dtype = np.lib.format.read_array_header_1_0(stream)
                    elif version in {(2, 0), (3, 0)}:
                        shape, _, dtype = np.lib.format.read_array_header_2_0(stream)
                    else:
                        raise ValueError("unsupported NPY storage version")
                required_shape = (91,) if name == "theta_deg" else (360,) if name == "phi_deg" else (91, 360)
                if shape != required_shape or dtype.kind not in "iuf":
                    raise ValueError(f"invalid AF array shape/dtype: {name}")
        with np.load(path, allow_pickle=False) as archive:
            if not expected_names.issubset(archive.files):
                raise ValueError("AF archive is missing required arrays")
            arrays = {name: archive[name] for name in expected_names}
    except (BadZipFile, OSError, EOFError) as exc:
        raise ValueError(f"unreadable AF arrays: {exc}") from exc
    for name, values in arrays.items():
        if values.dtype.kind not in "iuf" or not np.isfinite(values).all():
            raise ValueError(f"AF {name} must contain finite real values")
    for name, count in (("theta_deg", 91), ("phi_deg", 360)):
        if arrays[name].shape != (count,) or not np.allclose(arrays[name], np.arange(count), rtol=0, atol=1e-8):
            raise ValueError(f"AF {name} does not use the specified grid")

    theta = np.deg2rad(np.arange(91))[:, None]
    phi = np.deg2rad(np.arange(360))[None, :]
    k_d = 2 * math.pi * 5.8e9 / 299792458 * 0.04
    x = k_d * np.sin(theta) * np.cos(phi)
    y = k_d * np.sin(theta) * np.sin(phi)
    recomputed = {"evaluation_frequency_GHz": 5.8, "grid_step_deg": 1.0}
    for name in patterns:
        values = arrays["af_" + name]
        if values.shape != (91, 360) or (values < 0).any():
            raise ValueError(f"AF {name} must be nonnegative with shape (91,360)")
        matrix = matrix_arrays[name]
        field = sum(np.exp(1j * (m * x + n * y)) * (-1) ** int(matrix[m, n])
                    for m in range(6) for n in range(6))
        expected = np.abs(field)
        tolerance = 1e-6 + 1e-3 * np.maximum(values, expected)
        if (np.abs(values - expected) > tolerance).any():
            raise ValueError(f"AF {name} samples disagree with the public equation")
        recomputed["af_max_" + name] = float(values.max())
        recomputed["af_at_broadside_" + name] = float(values[0, 0])
    for field, expected in recomputed.items():
        actual = summary.get(field)
        tolerance = 1e-8 if field in {"evaluation_frequency_GHz", "grid_step_deg"} else 0.0011
        if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isfinite(actual):
            raise ValueError(f"AF summary field is not finite: {field}")
        if abs(actual - expected) > tolerance + 1e-12:
            raise ValueError(f"AF summary differs from its arrays: {field}")
    return {**summary, **recomputed}
