"""Recompute weak reflected power; error-bound provenance needs independent review."""

import numpy as np

from review_numerics import quadrature_weights, real_axis


PROTOCOL = "brewster-power-evidence-bounds-2026-09-23"
SPEC = {
    "required_quantities": {
        "q": "1",
        "reflection_amplitude": "1 complex",
        "incident": "power",
        "transmitted": "power",
        "reflection_measurement": "power",
        "flux_error_bound": "1",
        "spectrum_error_bound": "1",
    },
    "required_context": {
        "input_kind": "gaussian or sinc; inspect the prescribed input source",
        "measurement_kind": "angular_basis or direct_beam",
        "reflection_kind": "backward_flux, outward_power, or net_forward_flux",
        "run_id": "inspected production device execution group",
        "reference_run_id": "independent incident-calibration execution group",
        "uncertainty_evidence": "flux and spectrum: path/quote for the independently justified integrated absolute error bound; inspect underlying calibrations and convergence, not only the reported number",
    },
    "optional_context": {
        "incident_flux_sign": "+1 default or -1, justified by monitor orientation",
        "transmission_flux_sign": "+1 default or -1, justified by monitor orientation",
    },
    "meaning": "Run separately for both production inputs. Bind native power and complex-response arrays, plus two nonnegative scalar absolute error bounds on the integrated normalized powers. No fixed null-plus-refinement formula is imposed. Bounds are not inferred or validated by this arithmetic: inspect independent calibration, refinement and systematic-error evidence. A claimed scalar, a small closure residual or a true numerically_qualified flag alone cannot establish a pass. Retained refinement powers and run settings also require review.",
}
CHECKS = {
    "native_closure", "native_power_tolerance", "resolved_reflected_signal",
    "uncertainty_budget", "power_agreement",
}


def _real_power(values, shape, name):
    values = np.asarray(values)
    if values.shape != shape or np.iscomplexobj(values) or not np.all(np.isfinite(values)):
        raise ValueError(name + " must be finite real power with the documented measurement shape")
    return values.astype(float)


def _reflection(measurement, incident, kind, incident_sign):
    if kind == "net_forward_flux":
        return (incident - measurement * incident_sign) / incident
    if kind == "backward_flux":
        return -measurement * incident_sign / incident
    if kind == "outward_power":
        return measurement / incident
    raise ValueError("Declare the reflected quantity; net forward flux is not reflected flux")


def _bound(value, name):
    values = np.asarray(value)
    if values.size != 1 or np.iscomplexobj(values) or not np.all(np.isfinite(values)):
        raise ValueError(name + " must be one finite real absolute error bound")
    result = float(values.reshape(()))
    if result < 0:
        raise ValueError(name + " cannot be negative")
    return result


def derive_power(quantities, context):
    if context.get("input_kind") not in ("gaussian", "sinc"):
        raise ValueError("Declare the prescribed Gaussian or Sinc input")
    if context.get("measurement_kind") not in ("angular_basis", "direct_beam"):
        raise ValueError("Declare angular-basis or direct-beam native powers")
    for name in ("incident_flux_sign", "transmission_flux_sign"):
        if isinstance(context.get(name, 1), bool) or context.get(name, 1) not in (-1, 1):
            raise ValueError("A documented monitor conversion is only +1 or -1")
    if set(quantities) != set(SPEC["required_quantities"]):
        raise ValueError("Bind production powers, complex response and independently supported error bounds")
    for name in ("run_id", "reference_run_id"):
        if not isinstance(context.get(name), str) or not context[name].strip():
            raise ValueError("Identify the inspected device and incident-reference executions")
    if context["run_id"] == context["reference_run_id"]:
        raise ValueError("The incident reference must be independent of the device execution")
    evidence = context.get("uncertainty_evidence")
    if not isinstance(evidence, dict):
        raise ValueError("Identify the supporting evidence for both power error bounds")
    for name in ("flux", "spectrum"):
        support = evidence.get(name)
        if not isinstance(support, dict) or any(
            not isinstance(support.get(field), str) or not support[field].strip()
            for field in ("path", "quote")
        ):
            raise ValueError("Both error bounds need inspectable path/quote evidence, not bare scalars")
    coordinate = np.asarray(quantities["q"])
    if coordinate.ndim != 1 or np.iscomplexobj(coordinate):
        raise ValueError("q must be a real vector")
    ordering = np.argsort(coordinate, kind="stable")
    coordinate = real_axis(coordinate[ordering])
    if coordinate[0] < -.1 - 1e-12 or coordinate[-1] > .1 + 1e-12:
        raise ValueError("Power observations must use the prescribed angular support")
    boundary = .1 if context["input_kind"] == "gaussian" else .09
    for endpoint in (-boundary, boundary):
        matches = np.flatnonzero(abs(coordinate - endpoint) <= 1e-12)
        if len(matches) != 1:
            raise ValueError("Retain both input-support endpoints without ambiguous duplicates")
        coordinate[matches[0]] = endpoint
    coordinate = real_axis(coordinate)
    reflection = np.asarray(quantities["reflection_amplitude"])
    if reflection.shape != coordinate.shape or not np.all(np.isfinite(reflection)):
        raise ValueError("Complex reflection amplitudes must match the angular observations")
    reflection = reflection[ordering]
    amplitude = np.exp(-.5 * (coordinate / .025) ** 2) if boundary == .1 else np.ones(len(coordinate))
    weights = quadrature_weights(coordinate, -boundary, boundary) * abs(amplitude) ** 2
    weights /= np.sum(weights)
    spectral_eta = float(np.dot(weights, abs(reflection) ** 2))
    shape = coordinate.shape if context["measurement_kind"] == "angular_basis" else ()
    powers = {}
    for name in ("incident", "transmitted", "reflection_measurement"):
        values = np.asarray(quantities[name])
        if shape == () and values.shape == (1,):
            values = values.reshape(())
        powers[name] = _real_power(values, shape, name)
        if shape:
            powers[name] = powers[name][ordering]
    incident_sign = context.get("incident_flux_sign", 1)
    incident = powers["incident"] * incident_sign
    if np.any(incident <= 0):
        raise ValueError("Independent incident powers must be positive after orientation conversion")
    reflected = _reflection(powers["reflection_measurement"], incident, context["reflection_kind"], incident_sign)
    transmitted = powers["transmitted"] * context.get("transmission_flux_sign", 1) / incident
    if not np.isfinite(spectral_eta) or any(not np.all(np.isfinite(values)) for values in (reflected, transmitted)):
        raise ValueError("Normalized powers must remain finite")
    flux_eta = float(np.dot(weights, reflected)) if shape else float(reflected)
    flux_bound = _bound(quantities["flux_error_bound"], "flux_error_bound")
    spectrum_bound = _bound(quantities["spectrum_error_bound"], "spectrum_error_bound")
    combined_bound = flux_bound + spectrum_bound
    if not np.isfinite(combined_bound):
        raise ValueError("Combined error bounds must remain finite")
    closure = float(np.max(abs(reflected + transmitted - 1)))
    minimum_ratio = float(min(np.min(reflected), np.min(transmitted)))
    disagreement = abs(flux_eta - spectral_eta)
    roundoff = 32 * np.finfo(float).eps * max(abs(flux_eta), spectral_eta)
    checks = {
        "native_closure": closure <= .02,
        "native_power_tolerance": minimum_ratio >= -.01,
        "resolved_reflected_signal": flux_eta > flux_bound and spectral_eta > 0,
        "uncertainty_budget": spectral_eta > 0 and combined_bound <= .10 * spectral_eta,
        "power_agreement": bool(disagreement <= combined_bound + roundoff),
    }
    return {
        "protocol": PROTOCOL,
        "input_kind": context["input_kind"],
        "flux_eta": flux_eta,
        "spectral_eta": spectral_eta,
        "absolute_disagreement": disagreement,
        "flux_error_bound": flux_bound,
        "spectrum_error_bound": spectrum_bound,
        "combined_error_bound": combined_bound,
        "maximum_allowed_error_bound": .10 * spectral_eta,
        "maximum_closure_error": closure,
        "minimum_power_ratio": minimum_ratio,
        "integration_interval": [-boundary, boundary],
        "checks": checks,
        "numerically_qualified": all(checks.values()),
        "error_bound_provenance": "requires independent scientific review; not established by this operation",
    }


def validate_power_review(trace):
    observed = {}
    for entry in trace:
        result = entry.get("result")
        if entry.get("tool") != "derive_scientific_metrics" or not isinstance(result, dict):
            continue
        if result.get("operation") != "brewster_power" or result.get("status") != "recomputed_from_candidate_arrays":
            continue
        metrics = result.get("metrics", {})
        kind = metrics.get("input_kind")
        if metrics.get("protocol") != PROTOCOL or kind not in ("gaussian", "sinc") or not result.get("bindings"):
            raise ValueError("Power qualification requires current, bound native evidence")
        observed[kind] = result
    if set(observed) != {"gaussian", "sinc"}:
        raise ValueError("A power pass requires separate native/spectral and uncertainty checks for both inputs")
    for result in observed.values():
        metrics = result["metrics"]
        checks = metrics.get("checks", {})
        if set(checks) != CHECKS or not all(value is True for value in checks.values()) or metrics.get("numerically_qualified") is not True:
            raise ValueError("The power pass contradicts recomputed observations; review this same submission, not the model")
    if any(result.get("context", {}).get("measurement_kind") == "direct_beam" for result in observed.values()):
        identities = [result.get("context", {}).get("run_id") for result in observed.values()]
        if any(not identity for identity in identities) or len(set(identities)) != len(identities):
            raise ValueError("Direct-beam Gaussian and Sinc powers require their own native solves")
