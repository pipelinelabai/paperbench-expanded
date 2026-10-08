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
    raw_refined_coordinate, raw_refined = refined_coordinate, refined
    layout = "matched"
    reused_baseline_count = 0
    if kind == "spectral":
        if len(coordinate) < 2 or refined_coordinate[0] < coordinate[0] - 1e-12 or refined_coordinate[-1] > coordinate[-1] + 1e-12:
            raise ValueError("Spectral refinement must stay within the baseline observed interval")
        if not np.any(novel):
            raise ValueError("Spectral sampling convergence needs new independent raw sample coordinates")
        layout = "complete_grid" if np.allclose(refined_coordinate[[0, -1]], coordinate[[0, -1]], rtol=0, atol=1e-12) else "incremental_observations"
        if layout == "incremental_observations":
            nearest = np.where(abs(refined_coordinate - left) < abs(refined_coordinate - right), positions - 1, positions)
            nearest = np.clip(nearest, 0, len(coordinate) - 1)
            if len(np.unique(nearest[~novel])) != int(np.count_nonzero(~novel)):
                raise ValueError("Duplicate retained baseline coordinates are not independent observations")
            if not np.allclose(refined[~novel], baseline[nearest[~novel]], rtol=0, atol=1e-12):
                raise ValueError("Incremental spectral observations conflict with retained baseline samples")
            merged_coordinate = np.r_[coordinate, refined_coordinate[novel]]
            merged_refined = np.concatenate([baseline, refined[novel]], axis=0)
            ordering = np.argsort(merged_coordinate)
            refined_coordinate, refined = merged_coordinate[ordering], merged_refined[ordering]
            reused_baseline_count = len(coordinate) - int(np.count_nonzero(~novel))
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
              "baseline_sample_count": len(coordinate), "refined_sample_count": len(raw_refined_coordinate),
              "refined_grid_sample_count": len(refined_coordinate), "comparison_sample_count": len(comparison_coordinate),
              "refined_observation_layout": layout, "reused_baseline_sample_count": reused_baseline_count,
              "new_refined_sample_count": int(np.count_nonzero(novel)),
              "sampling_convergence_evaluated": kind == "spectral", "new_points_absolute_max": None,
              "baseline_maximum_gap": float(np.max(np.diff(coordinate))) if len(coordinate) > 1 else None,
              "refined_maximum_gap": float(np.max(np.diff(refined_coordinate))) if len(refined_coordinate) > 1 else None}
    if kind == "spectral":
        result["new_points_absolute_max"] = float(np.max(abs(raw_refined[novel] - interpolation(raw_refined_coordinate[novel], coordinate, baseline))))
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


def brewster_operator(quantities, context):
    coordinate = real_axis(quantities["q"])
    incident, reflection = np.asarray(quantities["input_spectrum"]), np.asarray(quantities["reflection_amplitude"])
    if incident.shape != coordinate.shape or reflection.shape != coordinate.shape or not np.all(np.isfinite(incident)) or not np.all(np.isfinite(reflection)):
        raise ValueError("Finite input and reflection samples must match q")
    if coordinate[0] < -.1 - 1e-12 or coordinate[-1] > .1 + 1e-12:
        raise ValueError("Outside defined angular support")
    if not np.any(np.isclose(coordinate, 0, atol=1e-12, rtol=0)):
        raise ValueError("The input center must be a native sample")
    amplitude = incident[np.argmin(abs(coordinate))]
    if abs(amplitude) == 0:
        raise ValueError("A nonzero input center amplitude is required")
    sinc = np.where(abs(coordinate) <= .09 + 1e-12, 1, 0)
    gaussian = np.exp(-.5 * (coordinate / .025)**2)
    detected = "sinc" if np.allclose(incident / amplitude, sinc, rtol=1e-9, atol=1e-12) else "gaussian" if np.allclose(incident / amplitude, gaussian, rtol=1e-9, atol=1e-12) else None
    kind = context.get("input_kind", detected)
    if kind not in ("sinc", "gaussian") or detected != kind:
        raise ValueError("Declare one of the two fixed input formulas; do not alter the spectrum to repair quadrature")
    boundary = .09 if kind == "sinc" else .1
    if any(not np.any(np.isclose(coordinate, point, atol=1e-12, rtol=0)) for point in (-boundary, boundary)):
        raise ValueError("The input integration endpoints must be native samples")
    weights = quadrature_weights(coordinate, -boundary, boundary)
    coefficient = 2.1 / 2 - 1 / (2 * 2.1**3)
    target, output = -coefficient * coordinate * incident, reflection * incident
    norm, denominator, power = [float(np.sum(weights * abs(values)**2)) for values in (target, output, incident)]
    if min(norm, denominator, power) <= 0:
        raise ValueError("Nonzero input, ideal and observed powers are needed for normalized errors")
    gain = np.sum(weights * np.conj(target) * output) / norm
    fit_coordinate = np.unique(np.r_[-.05, coordinate[(coordinate > -.05 + 1e-12) & (coordinate < .05 - 1e-12)], .05])
    fit_incident = interpolation(fit_coordinate, coordinate, incident)
    fit_reflection = interpolation(fit_coordinate, coordinate, reflection)
    fit_weights = quadrature_weights(fit_coordinate) * abs(fit_incident)**2
    fit_weights[abs(fit_incident) < .01 * np.max(abs(incident))] = 0
    design = np.column_stack([fit_coordinate, np.ones(len(fit_coordinate))])
    fitted, _, rank, _ = np.linalg.lstsq(design * np.sqrt(fit_weights[:, None]), fit_reflection * np.sqrt(fit_weights), rcond=None)
    if rank != 2:
        raise ValueError("The supported angular observations do not identify a slope and intercept")
    slope, intercept = fitted
    residual = np.sqrt(np.sum(fit_weights * abs(design @ fitted - fit_reflection)**2) / np.sum(fit_weights * abs(fit_reflection)**2))
    return {"fixed_gain_error": float(np.sqrt(np.sum(weights * abs(output - target)**2) / norm)),
            "best_complex_gain": gain, "shape_error": float(np.sqrt(np.sum(weights * abs(output - gain * target)**2) / denominator)),
            "reflected_power_fraction": denominator / power, "slope": slope, "intercept": intercept,
            "weighted_transfer_residual": float(residual),
            "rms_q_input": float(np.sqrt(np.sum(weights * coordinate**2 * abs(incident)**2) / power)),
            "rms_q_output": float(np.sqrt(np.sum(weights * coordinate**2 * abs(output)**2) / denominator)),
            "quadrature_weights": weights if len(weights) <= 512 else None, "quadrature_weight_sum": float(np.sum(weights)), "integration_interval": [-boundary, boundary],
            "input_integral": power, "input_kind": kind, "sample_count": len(coordinate),
            "observed_q_interval": [float(coordinate[0]), float(coordinate[-1])],
            "basis_coverage_requires_separate_evidence": True,
            "fit_coordinate": fit_coordinate if len(fit_coordinate) <= 512 else None,
            "fit_quadrature_times_input_power": fit_weights if len(fit_weights) <= 512 else None,
            "array_return_policy": "All observations are used; full quadrature arrays are returned only for at most512 samples. Recompute the stated nodal rule for larger arrays.",
            "quadrature_rule": "Piecewise-linear nodal trapezoid on the exact input support; no area outside a Sinc cutoff.",
            "fit_rule": "Continuous weighted least squares discretized with |A|^2 dq weights on [-0.05,0.05]; boundary amplitudes are interpolated, not new native observations."}
