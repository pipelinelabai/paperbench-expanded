"""Pure-array optical metrics. No paths, file loading, hidden fit corrections or scores."""

import numpy as np
from scipy.integrate import trapezoid


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


def jones_array(quantities, context, prefix, count):
    matrix_name = prefix + "_jones"
    if matrix_name in quantities:
        value = arrays(quantities, matrix_name)[0]
        layout = context.get("jones_layout", "frequency_output_input")
        if layout == "output_input_frequency":
            value = np.moveaxis(value, -1, 0)
        elif layout != "frequency_output_input":
            raise ValueError("Unknown declared Jones axis layout")
    else:
        names = [prefix + "_" + suffix for suffix in ("pp", "pm", "mp", "mm")]
        present = [name in quantities for name in names]
        if not any(present):
            return None
        if not all(present):
            raise ValueError("Need all four named Jones components")
        components = arrays(quantities, *names)
        if any(component.shape != (count,) for component in components):
            raise ValueError("Jones component columns must match wavelength")
        value = np.stack(components, axis=-1).reshape(count, 2, 2)
    if value.shape != (count, 2, 2):
        raise ValueError("Jones dimensions are invalid after declared axis mapping")
    return value


def channel_pair(quantities, name, count):
    if name in quantities:
        value = arrays(quantities, name)[0]
    elif name + "_plus" in quantities and name + "_minus" in quantities:
        components = arrays(quantities, name + "_plus", name + "_minus")
        value = np.stack(components, axis=-1)
    else:
        return None
    if value.shape != (count, 2):
        raise ValueError("Channel arrays must have one value per wavelength and fixed [+,-] ordering")
    return value


def canonical_samples(quantities, context):
    coordinate_name = {'compare': 'coordinate', 'stability': 'time', 'clc_channels': 'wavelength', 'clc_reference_compare': 'wavelength'}.get(context["operation"])
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
        if name in ("transmission_jones", "reflection_jones"):
            layout = context.get("jones_layout", "frequency_output_input").split("_")
            if sorted(layout) != ["frequency", "input", "output"]:
                raise ValueError("Jones axis declaration must identify frequency, output and input exactly once")
            value = np.transpose(value, tuple(layout.index(label) for label in ("frequency", "output", "input")))
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
                "meaning": "Independent raw-run comparison, never extrapolation. matched compares at baseline coordinates. spectral requires new raw refined coordinates and compares on the union, including coarse interpolation errors at new observations; report minimum, connected-edge and window-mean changes where applicable. No interpolation-only claim of new measurements."},
    "stability": {"required_quantities": {"time": "Meep time"},
                  "optional_quantities": {"field": "raw real or complex field", "field_envelope": "real nonnegative field magnitude", "noise_time": "independent time axis", "noise_field": "independent raw background", "noise_field_envelope": "independent nonnegative background magnitude"},
                  "one_of_field_inputs": [["field"], ["field_envelope"]],
                  "required_context": {"source_off_time": "actual source-end time", "arrival_time": "independently justified last direct-pulse arrival"},
                  "optional_context": {"arrival_basis": "source/monitor timing evidence", "run_id": "device execution identity", "noise_run_id": "distinct background execution identity", "noise_arrival_time": "independent background pulse arrival"},
                  "meaning": "Bind a full native raw field or nonnegative envelope, never both. Evaluate the fixed final half after independently justified arrival, with six equal-duration blocks and actual peak times. Resolved tail slope<=0 and final/first ratio<=1.1; independent background uncertainty can make a decision indeterminate, not pass. Audit complete traces, timing, observable and native provenance separately. Finite-window decay is not global stability."},
}


TASK_SPECS = {
    'clc': {
        "clc_reference_compare": {"required_quantities": {"wavelength": "um", "T": "1"}, "optional_quantities": {"R": "1"}, "required_context": {"pitches": "5 or 10 or 20 or 40 (all four required)", "channel_order": "['plus','minus']"}, "optional_context": {"handedness": "+1 default or -1 for the reversed helix"}, "meaning": "Evaluate the fixed independent continuous-Maxwell reference at every actual submitted wavelength; compare normalized channel powers. This mathematical reference is not native evidence and does not establish sampling convergence."},
        "clc_channels": {"required_quantities": {"wavelength": "um"},
            "one_of_transmission_inputs": [["transmission_jones"], ["transmission_pp", "transmission_pm", "transmission_mp", "transmission_mm"], ["incident", "transmitted"], ["incident_plus", "incident_minus", "transmitted_plus", "transmitted_minus"]],
            "units": {"*_jones and transmission_pp/pm/mp/mm and reflection_pp/pm/mp/mm": "1 complex", "linear_output or linear_output_plus/minus": "1 complex", "incident/transmitted/reflected_signed or *_plus/minus": "same power unit"},
            "optional_quantities": {
                **{name: "1 complex" for name in ("transmission_jones", "transmission_pp", "transmission_pm", "transmission_mp", "transmission_mm", "reflection_jones", "reflection_pp", "reflection_pm", "reflection_mp", "reflection_mm", "linear_output", "linear_output_plus", "linear_output_minus")},
                **{name: "power" for name in ("incident", "transmitted", "reflected_signed", "incident_plus", "incident_minus", "transmitted_plus", "transmitted_minus", "reflected_signed_plus", "reflected_signed_minus")}},
            "meaning": "Jones data may be a matrix or four independently bound complex component columns; pp/pm/mp/mm mean output then input. context jones_layout declares any underscore-separated permutation of frequency/output/input (default frequency_output_input). Native incident/transmitted powers alone suffice for power/edge statistics, not phase/superposition. Reflection data are required for closure. Missing observations return null, never a fabricated phase or automatic leaf pass."},
    }
}


def specs(task):
    return {name: dict(value, sampling_policy="Coordinates and all corresponding samples are jointly sorted; file row order is not scored. Duplicate/nonfinite coordinates are rejected, missing samples are never imputed.")
            for name, value in dict(COMMON_SPECS, **TASK_SPECS[task]).items()}


def derive_metrics(quantities, context):
    quantities, context = canonical_samples(quantities, context)
    operation = context["operation"]
    if operation == "clc_reference_compare":
        from reference_models import clc_jones
        wavelength = axis(arrays(quantities, "wavelength")[0], 1)
        pitches, handedness = context.get("pitches"), context.get("handedness", 1)
        if pitches not in (5, 10, 20, 40) or handedness not in (-1, 1) or context.get("channel_order") != ["plus", "minus"]:
            raise ValueError("Reference model requires a declared fixed thickness, helix and global channel order")
        power_t = channel_pair(quantities, "T", len(wavelength))
        power_r = channel_pair(quantities, "R", len(wavelength))
        if power_t is None:
            raise ValueError("Bind both normalized native transmission channels")
        transmission, reflection = clc_jones(wavelength, pitches, handedness=handedness)
        return {"transmission_power_absolute_max": float(np.max(abs(power_t - np.sum(abs(transmission)**2, axis=1)))),
                "reflection_power_absolute_max": float(np.max(abs(power_r - np.sum(abs(reflection)**2, axis=1)))) if power_r is not None else None,
                "reference_evaluated_at_all_submitted_wavelengths": True, "sample_count": len(wavelength),
                "reference_is_native_evidence": False, "reference_is_sampling_convergence_proof": False}
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
    if operation == "clc_channels":
        wavelength = arrays(quantities, "wavelength")[0]
        axis(wavelength, 1)
        count = len(wavelength)
        transmission = jones_array(quantities, context, "transmission", count)
        reflection = jones_array(quantities, context, "reflection", count)
        linear = channel_pair(quantities, "linear_output", count)
        incident = channel_pair(quantities, "incident", count)
        transmitted = channel_pair(quantities, "transmitted", count)
        reflected_signed = channel_pair(quantities, "reflected_signed", count)
        native_transmission = native_reflection = None
        if incident is not None:
            incident = oriented_power(incident, context, "incident", 1)
            positive(incident)
            if transmitted is not None:
                native_transmission = oriented_power(transmitted, context, "transmission", 1) / incident
                if np.any(native_transmission < -1e-12):
                    raise ValueError("Negative native transmitted power is not channel suppression")
            if reflected_signed is not None:
                native_reflection = oriented_power(reflected_signed, context, "reflection", -1) / incident
                if np.any(native_reflection < -1e-12):
                    raise ValueError("Reflected native power has the wrong propagation sign")
        if transmission is None and native_transmission is None:
            raise ValueError("Transmission needs Jones amplitudes or calibrated incident/transmitted native powers")
        if context.get("channel_order") != ["plus", "minus"]:
            raise ValueError("Fixed channel order [+,-] is required; rowwise minimum is not a channel")
        maximum_gap = float(np.max(np.diff(wavelength))) if count > 1 else None
        complete_coverage = bool(count > 1 and wavelength[0] <= 1.15000001 and wavelength[-1] >= 2.49999999 and maximum_gap <= .00500001)
        if context.get("require_full_coverage", False) and not complete_coverage:
            raise ValueError("Incomplete CLC spectral coverage for a full-band statistic")
        power_t = np.sum(abs(transmission)**2, axis=1) if transmission is not None else native_transmission
        power_r = np.sum(abs(reflection)**2, axis=1) if reflection is not None else native_reflection
        predicted = np.sum(transmission, axis=2) / np.sqrt(2) if transmission is not None else None
        numerator = denominator = 0.0
        for lower, upper in ([(1.15, 1.40), (1.90, 2.50)] if complete_coverage else []):
            grid = np.r_[lower, wavelength[(wavelength > lower) & (wavelength < upper)], upper]
            numerator += trapezoid(np.interp(grid, wavelength, power_t[:, 1]), grid)
            denominator += upper - lower
        return {"T_plus": power_t[:, 0] if count <= 512 else None, "T_minus": power_t[:, 1] if count <= 512 else None, "linear_component_power": abs(linear)**2 if linear is not None and count <= 512 else None,
                "linear_superposition_max_error": float(np.max(abs(linear - predicted))) if linear is not None and predicted is not None else None,
                "closure_max": float(np.max(abs(power_t + power_r - 1))) if power_r is not None else None,
                "jones_available": transmission is not None,
                "native_transmission_consistency_max": float(np.max(abs(power_t - native_transmission))) if transmission is not None and native_transmission is not None else None,
                "native_reflection_consistency_max": float(np.max(abs(power_r - native_reflection))) if reflection is not None and native_reflection is not None else None,
                "spectral_coverage_complete": complete_coverage, "observed_wavelength_range_um": [float(wavelength[0]), float(wavelength[-1])],
                "maximum_wavelength_gap_um": maximum_gap, "sampling_convergence_established": False,
                "full_power_arrays_returned": count <= 512, "all_bound_samples_used_for_metrics": True,
                "minimum_T_minus": float(np.min(power_t[:, 1])), "minimum_wavelength_um": float(wavelength[np.argmin(power_t[:, 1])]),
                "outside_mean_T_minus": float(numerator / denominator) if complete_coverage else None,
                "spectral_edges_um": connected_interval(wavelength, power_t[:, 1], .5, 1.65) if complete_coverage else None,
                "theoretical_edges_um": [1.5, 1.8]}
    raise ValueError("Unknown operation: " + str(operation))
