"""Explicit quadrature, center-connected intervals, and independent sampling checks."""

import numpy as np


def real_axis(values, minimum=2):
    values = np.asarray(values)
    if values.ndim != 1 or np.iscomplexobj(values) or len(values) < minimum or not np.all(np.isfinite(values)) or np.any(np.diff(values) <= 0):
        raise ValueError("Coordinates must be finite, real, strictly increasing independent samples")
    return values.astype(float)


def interpolation(coordinate, source_coordinate, values):
    coordinate, source_coordinate = np.asarray(coordinate), np.asarray(source_coordinate)
    values = np.asarray(values)
    if coordinate[0] < source_coordinate[0] - 1e-12 or coordinate[-1] > source_coordinate[-1] + 1e-12:
        raise ValueError("Interpolation cannot extrapolate beyond raw observations")
    columns = values.reshape(len(source_coordinate), -1)
    return np.column_stack([np.interp(coordinate, source_coordinate, column) for column in columns.T]).reshape((len(coordinate), *values.shape[1:]))


def quadrature_weights(coordinate, lower=None, upper=None):
    coordinate = real_axis(coordinate)
    lower = coordinate[0] if lower is None else float(lower)
    upper = coordinate[-1] if upper is None else float(upper)
    if not np.isfinite([lower, upper]).all() or lower >= upper or lower < coordinate[0] - 1e-12 or upper > coordinate[-1] + 1e-12:
        raise ValueError("Quadrature requires a nonempty covered integration interval")
    weights = np.zeros(len(coordinate))
    for index, width in enumerate(np.diff(coordinate)):
        left, right = max(coordinate[index], lower), min(coordinate[index + 1], upper)
        if right <= left:
            continue
        start, end = (left - coordinate[index]) / width, (right - coordinate[index]) / width
        right_weight = width * (end * end - start * start) / 2
        weights[index] += right - left - right_weight
        weights[index + 1] += right_weight
    return weights


def connected_interval(coordinate, values, threshold, center):
    coordinate = real_axis(coordinate)
    values = np.asarray(values)
    if values.shape != coordinate.shape or np.iscomplexobj(values) or not np.all(np.isfinite(values)) or not np.isfinite([threshold, center]).all():
        raise ValueError("Interval observations, threshold and center must be finite real values")
    if not coordinate[0] <= center <= coordinate[-1]:
        raise ValueError("The requested center is outside the observed domain")
    inserted = not np.any(coordinate == center)
    center_value = float(np.interp(center, coordinate, values))
    if inserted:
        position = int(np.searchsorted(coordinate, center))
        coordinate = np.insert(coordinate, position, center)
        values = np.insert(values, position, center_value)
    anchor = int(np.searchsorted(coordinate, center))
    result = {"center": float(center), "center_value": center_value, "center_interpolated": inserted,
              "contains_center": bool(center_value <= threshold)}
    if center_value > threshold:
        return {**result, "lower": None, "upper": None, "width": 0.0, "censored": False}
    inside = values <= threshold
    first = last = anchor
    while first > 0 and inside[first - 1]:
        first -= 1
    while last + 1 < len(inside) and inside[last + 1]:
        last += 1

    def crossing(outside, within):
        return float(coordinate[outside] + (coordinate[within] - coordinate[outside]) * (threshold - values[outside]) / (values[within] - values[outside]))

    lower = float(coordinate[first]) if first == 0 else crossing(first - 1, first)
    upper = float(coordinate[last]) if last == len(inside) - 1 else crossing(last + 1, last)
    return {**result, "lower": lower, "upper": upper, "width": upper - lower,
            "censored": first == 0 or last == len(inside) - 1}


def window_mean(coordinate, values, windows):
    total = 0.0
    width = 0.0
    for lower, upper in windows:
        total += float(np.dot(quadrature_weights(coordinate, lower, upper), values))
        width += upper - lower
    if width <= 0:
        raise ValueError("Integration windows must have positive total width")
    return total / width


def compare_samples(quantities, context):
    coordinate = real_axis(np.atleast_1d(quantities["coordinate"]), 1)
    baseline = np.atleast_1d(quantities["baseline"])
    refined = np.atleast_1d(quantities["refined"])
    if baseline.shape[0] != len(coordinate) or not np.all(np.isfinite(baseline)) or not np.all(np.isfinite(refined)):
        raise ValueError("Finite observables must match their coordinate axes")
    refined_coordinate = np.atleast_1d(quantities.get("refined_coordinate", coordinate))
    ordering = np.argsort(refined_coordinate)
    refined_coordinate = real_axis(refined_coordinate[ordering], 1)
    if refined.shape[0] != len(refined_coordinate) or refined.shape[1:] != baseline.shape[1:]:
        raise ValueError("Refined observable dimensions disagree")
    refined = refined[ordering]
    kind = context.get("comparison_kind", "matched")
    if kind not in ("matched", "spectral"):
        raise ValueError("comparison_kind must be matched or spectral")
    positions = np.searchsorted(coordinate, refined_coordinate)
    left = coordinate[np.clip(positions - 1, 0, len(coordinate) - 1)]
    right = coordinate[np.clip(positions, 0, len(coordinate) - 1)]
    novel = np.minimum(abs(refined_coordinate - left), abs(refined_coordinate - right)) > 1e-12
    if kind == "spectral":
        if len(coordinate) < 2 or len(refined_coordinate) < 2 or not np.allclose(refined_coordinate[[0, -1]], coordinate[[0, -1]], rtol=0, atol=1e-12):
            raise ValueError("Spectral refinement must cover the same complete observed interval")
        if not np.any(novel):
            raise ValueError("Spectral sampling convergence needs new independent raw sample coordinates")
        comparison_coordinate = np.unique(np.r_[coordinate, refined_coordinate])
    else:
        comparison_coordinate = coordinate
    compared_baseline = interpolation(comparison_coordinate, coordinate, baseline)
    compared_refined = interpolation(comparison_coordinate, refined_coordinate, refined)
    difference = abs(compared_refined - compared_baseline)
    weights = quadrature_weights(comparison_coordinate) if len(comparison_coordinate) > 1 else np.ones(1)
    error_power = np.sum(abs(compared_refined - compared_baseline).reshape(len(weights), -1)**2, axis=1)
    reference_power = np.sum(abs(compared_baseline).reshape(len(weights), -1)**2, axis=1)
    norm = float(np.dot(weights, reference_power))
    result = {"absolute_max": float(np.max(difference)), "rms": float(np.sqrt(np.dot(weights, error_power) / np.sum(weights))),
              "relative_l2": float(np.sqrt(np.dot(weights, error_power) / norm)) if norm > 0 else None,
              "interpolation_used": "refined_coordinate" in quantities, "comparison_kind": kind,
              "baseline_sample_count": len(coordinate), "refined_sample_count": len(refined_coordinate),
              "new_refined_sample_count": int(np.count_nonzero(novel)),
              "sampling_convergence_evaluated": kind == "spectral", "new_points_absolute_max": None,
              "baseline_maximum_gap": float(np.max(np.diff(coordinate))) if len(coordinate) > 1 else None,
              "refined_maximum_gap": float(np.max(np.diff(refined_coordinate))) if len(refined_coordinate) > 1 else None}
    if kind == "spectral":
        result["new_points_absolute_max"] = float(np.max(abs(refined[novel] - interpolation(refined_coordinate[novel], coordinate, baseline))))
        if baseline.ndim == 1 and not np.iscomplexobj(baseline) and not np.iscomplexobj(refined):
            features = {"minimum_absolute_change": float(abs(np.min(refined) - np.min(baseline)))}
            if "feature_center" in context or "feature_threshold" in context:
                old = connected_interval(coordinate, baseline, context["feature_threshold"], context["feature_center"])
                new = connected_interval(refined_coordinate, refined, context["feature_threshold"], context["feature_center"])
                features["center_interval"] = {"baseline": old, "refined": new,
                    "component_presence_changed": old["contains_center"] != new["contains_center"],
                    **{name + "_absolute_change": abs(new[name] - old[name]) if old[name] is not None and new[name] is not None else None for name in ("lower", "upper")}}
            if "integration_windows" in context:
                old = window_mean(coordinate, baseline, context["integration_windows"])
                new = window_mean(refined_coordinate, refined, context["integration_windows"])
                features["window_mean_absolute_change"] = abs(new - old)
            result["feature_changes"] = features
    return result
