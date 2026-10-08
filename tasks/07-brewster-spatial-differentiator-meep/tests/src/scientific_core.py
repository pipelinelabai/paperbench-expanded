"""Pure-array optical metrics. No paths, file loading, hidden fit corrections or scores."""

import numpy as np


def arrays(quantities, *names):
    result = [np.asarray(quantities[name]) for name in names]
    if any(value.size == 0 or not np.all(np.isfinite(value)) for value in result):
        raise ValueError("Empty or nonfinite scientific data")
    return result


def axis(values, minimum=3):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < minimum or np.any(np.diff(values) <= 0):
        raise ValueError("Coordinate must be unique, strictly increasing, and sufficiently sampled")
    return values


def same_shape(*values):
    if len({value.shape for value in values}) != 1:
        raise ValueError("Inconsistent sample shapes")


def positive(values):
    if np.any(values <= 0):
        raise ValueError("Reference power must be positive")


def oriented_power(values, context, name, default):
    sign = context.get(name + "_flux_sign", default)
    if sign not in (-1, 1):
        raise ValueError("A port orientation conversion is only +1 or -1, never a fitted scale")
    if np.iscomplexobj(values) and np.any(values.imag != 0):
        raise ValueError("Time-averaged through-power must be real, not reactive complex power")
    return np.real(values) * sign


def canonical_samples(quantities, context):
    coordinate_name = {'compare': 'coordinate', 'stability': 'time', 'brewster_operator': 'q'}.get(context["operation"])
    if coordinate_name is None:
        return quantities, context
    coordinate = np.atleast_1d(np.asarray(quantities[coordinate_name]))
    if coordinate.ndim != 1 or np.iscomplexobj(coordinate) or not np.all(np.isfinite(coordinate)):
        raise ValueError("Physical sample coordinates must be finite real numbers")
    ordering = np.argsort(coordinate, kind="stable")
    if len(coordinate) > 1 and np.any(np.diff(coordinate[ordering]) <= 0):
        raise ValueError("Duplicate sample coordinates are not valid independent observations")
    result = {}
    context = dict(context)
    for name, value in quantities.items():
        value = np.asarray(value)
        own_refined_axis = context["operation"] == "compare" and "refined_coordinate" in quantities and name in ("refined", "refined_coordinate")
        own_noise_axis = context["operation"] == "stability" and name in ("noise_time", "noise_field", "noise_field_envelope")
        if value.ndim and value.shape[0] == len(coordinate) and not own_refined_axis and not own_noise_axis:
            value = value[ordering]
        result[name] = value
    if context["operation"] == "stability" and "noise_time" in result:
        noise_time = result["noise_time"]
        if noise_time.ndim != 1 or np.iscomplexobj(noise_time) or not np.all(np.isfinite(noise_time)):
            raise ValueError("Independent noise times must be finite real coordinates")
        noise_order = np.argsort(noise_time, kind="stable")
        if np.any(np.diff(noise_time[noise_order]) <= 0):
            raise ValueError("Independent noise times cannot contain duplicates")
        for name in ("noise_time", "noise_field", "noise_field_envelope"):
            if name in result:
                if result[name].ndim != 1 or len(result[name]) != len(noise_time):
                    raise ValueError("Independent noise fields must match their own time axis")
                result[name] = result[name][noise_order]
    if "jones_layout" in context:
        context["jones_layout"] = "frequency_output_input"
    result[coordinate_name] = coordinate[ordering]
    return result, context


def connected_interval(coordinate, values, threshold, center):
    from review_numerics import connected_interval as reviewed_interval
    return reviewed_interval(coordinate, values, threshold, center)


COMMON_SPECS = {
    "power": {"required_quantities": {"incident": "power", "transmitted": "power", "reflected_signed": "power"},
              "optional_context": {"incident_flux_sign": "+1 default or -1", "transmission_flux_sign": "+1 default or -1", "reflection_flux_sign": "-1 default or +1"},
              "meaning": "Native power ratios with declared monitor orientations. Default reflected_signed is negative backward flux after incident subtraction. Outward-positive reflected power uses reflection_flux_sign=+1 only when source/metadata prove that convention; never select signs to repair a result."},
    "compare": {"required_quantities": {"coordinate": "declared matched coordinate unit", "baseline": "declared observable unit", "refined": "same observable unit"},
                "optional_quantities": {"refined_coordinate": "same unit as coordinate"},
                "optional_context": {"comparison_kind": "matched for spatial/time checks; spectral for sampling refinement", "feature_center": "center for connected-component changes", "feature_threshold": "threshold for connected-component changes", "integration_windows": "Covered [lower,upper] windows for integral changes"},
                "meaning": "Independent raw-run comparison, never extrapolation. matched compares at baseline coordinates and requires refined coverage of those coordinates. spectral accepts a complete refined grid OR a separate file of new independently measured coordinates within the baseline interval: for incremental observations the tool retains baseline samples and merges the new raw observations, without inventing endpoint measurements. Incremental overlaps must agree with retained baseline values. It reports raw versus merged sample counts, merged maximum gap and coarse interpolation errors at new observations, plus minimum, connected-edge and window-mean changes where applicable. Confirm native provenance separately; interpolation-only values are not new measurements. This union is only for spectral sampling, never a substitute for spatial/time whole-input convergence."},
    "stability": {"required_quantities": {"time": "Meep time"},
                  "optional_quantities": {"field": "raw real or complex field", "field_envelope": "real nonnegative field magnitude", "noise_time": "independent time axis", "noise_field": "independent raw background", "noise_field_envelope": "independent nonnegative background magnitude"},
                  "one_of_field_inputs": [["field"], ["field_envelope"]],
                  "required_context": {"source_off_time": "actual source-end time", "arrival_time": "independently justified last direct-pulse arrival"},
                  "optional_context": {"arrival_basis": "source/monitor timing evidence", "run_id": "device execution identity", "noise_run_id": "distinct background execution identity", "noise_arrival_time": "independent background pulse arrival"},
                  "meaning": "Bind a full native raw field or nonnegative envelope, never both. Evaluate the fixed final half after independently justified arrival, with six equal-duration blocks and actual peak times. Resolved tail slope<=0 and final/first ratio<=1.1; independent background uncertainty can make a decision indeterminate, not pass. Audit complete traces, timing, observable and native provenance separately. Finite-window decay is not global stability."},
}


TASK_SPECS = {
    'brewster': {
        "brewster_operator": {"required_quantities": {"q": "1", "input_spectrum": "field", "reflection_amplitude": "1"}, "optional_context": {"input_kind": "gaussian or sinc; the fixed formula can also be identified from its samples up to one global amplitude"}, "meaning": "Power-normalized angular basis and interface deembedding. All integrals use nodal trapezoid weights on the exact input support, with no Sinc area beyond +/-0.09. Fit continuous |A|^2-weighted least squares using quadrature on [-0.05,0.05], not sample-count weights. Returned weights also define real-space synthesis."},
    }
}


def specs(task):
    return {name: dict(value, sampling_policy="Coordinates and all corresponding samples are jointly sorted; file row order is not scored. Duplicate/nonfinite coordinates are rejected, missing samples are never imputed.")
            for name, value in dict(COMMON_SPECS, **TASK_SPECS[task]).items()}


def derive_metrics(quantities, context):
    quantities, context = canonical_samples(quantities, context)
    operation = context["operation"]
    if operation == "power":
        incident, transmitted, reflected = arrays(quantities, "incident", "transmitted", "reflected_signed")
        same_shape(incident, transmitted, reflected)
        incident = oriented_power(incident, context, "incident", 1)
        transmitted = oriented_power(transmitted, context, "transmission", 1)
        reflected = oriented_power(reflected, context, "reflection", -1)
        positive(incident)
        transmission, reflection = transmitted / incident, reflected / incident
        return {"T": transmission, "R": reflection, "closure_max": float(np.max(abs(transmission + reflection - 1))),
                "minimum_power_ratio": float(min(np.min(transmission), np.min(reflection)))}
    if operation == "compare":
        from review_numerics import compare_samples
        return compare_samples(quantities, context)
    if operation == "stability":
        from field_stability import stability_metrics
        return stability_metrics(quantities, context)
    if operation == "brewster_operator":
        from review_numerics import brewster_operator
        return brewster_operator(quantities, context)
    raise ValueError("Unknown operation: " + str(operation))
