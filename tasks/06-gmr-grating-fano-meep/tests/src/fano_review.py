"""Fixed single-pole fitting with explicit identifiability and applicability checks.

No solver, stored reference, scientific_core import, or fitted background slope is
used here. Frequencies must already be canonicalized by the caller. Statistical
errors are local linearized diagnostics, not independent FDTD convergence proof.
"""

import math

import numpy as np
from scipy.optimize import least_squares


MIN_SAMPLES = 33
RESIDUAL_LIMIT = 0.05
NORMAL_95 = 1.959963984540054
NUMERICAL_RCOND = math.sqrt(np.finfo(float).eps)
PHYSICAL_KEYS = ("frequency", "gamma", "Q", "wavelength_um", "pole_linewidth_um_approx", "q_complex")


def _finite_real(value, name):
    array = np.asarray(value)
    if array.ndim or np.iscomplexobj(array) or not np.isfinite(array):
        raise ValueError(f"{name} must be a finite real scalar")
    return float(array)


def _prediction(parameters, coordinate):
    background = complex(parameters[0], parameters[1])
    residue = complex(parameters[2], parameters[3])
    denominator = coordinate - parameters[4] + .5j * np.exp(parameters[5])
    return background + residue / denominator


def _jacobian(parameters, coordinate):
    residue = complex(parameters[2], parameters[3])
    gamma = np.exp(parameters[5])
    denominator = coordinate - parameters[4] + .5j * gamma
    columns = np.column_stack((np.ones(len(coordinate)), np.full(len(coordinate), 1j),
                               1 / denominator, 1j / denominator, residue / denominator**2,
                               -.5j * gamma * residue / denominator**2))
    return np.concatenate((columns.real, columns.imag), axis=0)


def _condition_and_covariance(jacobian, noise_per_real_component):
    norms = np.linalg.norm(jacobian, axis=0)
    if np.any(norms == 0) or not np.all(np.isfinite(norms)):
        return {"rank": int(np.count_nonzero(norms)), "column_scaled_condition_number": None}, None
    normalized = jacobian / norms
    unused_left, singular, right = np.linalg.svd(normalized, full_matrices=False)
    rank = int(np.count_nonzero(singular > singular[0] * NUMERICAL_RCOND))
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else None
    diagnostic = {"rank": rank, "column_scaled_condition_number": condition,
                  "column_scaled_singular_values": singular.tolist(),
                  "rank_relative_tolerance": NUMERICAL_RCOND,
                  "parameterization": "Re/Im background, Re/Im residue per window span, center per span, log linewidth"}
    if rank != 6:
        return diagnostic, None
    inverse = (right.T / singular**2) @ right
    covariance = inverse / np.outer(norms, norms) * noise_per_real_component**2
    return diagnostic, covariance


def derive_fano_pole(quantities, context):
    """Return supported pole keys plus reasons, validity flags and noise diagnostics.

    ``reflection_noise_rms`` in context is an optional independent complex RMS
    amplitude-error estimate. It can only raise, never lower, the residual-based
    error floor. The 95% local uncertainty diagnostics assume independent errors;
    deterministic FDTD/model bias still needs the public independent refinements.
    """
    frequency = np.asarray(quantities["frequency"])
    reflection = np.asarray(quantities["reflection_amplitude"], dtype=complex)
    if (frequency.ndim != 1 or np.iscomplexobj(frequency) or len(frequency) < MIN_SAMPLES
            or reflection.shape != frequency.shape or not np.all(np.isfinite(frequency))
            or not np.all(np.isfinite(reflection)) or np.any(frequency <= 0)
            or np.any(np.diff(frequency) <= 0)):
        raise ValueError("Fano fitting requires at least 33 finite matching samples at strictly increasing positive frequencies")
    frequency = frequency.astype(float)
    origin, span = float(np.mean(frequency)), float(np.ptp(frequency))
    coordinate = (frequency - origin) / span
    amplitude_scale = float(np.max(abs(reflection)))
    variation = float(np.linalg.norm(reflection - np.mean(reflection)))
    variation_rms = variation / math.sqrt(len(frequency))
    roundoff = 64 * np.finfo(float).eps * amplitude_scale
    supplied_noise = _finite_real(context.get("reflection_noise_rms", 0), "reflection_noise_rms")
    if supplied_noise < 0:
        raise ValueError("reflection_noise_rms cannot be negative")
    result = {key: None for key in PHYSICAL_KEYS}
    result.update(fit_success=False, identifiable=False, physical_pole_valid=False,
                  reasons=[], applicability_reasons=[], sample_count=len(frequency),
                  spectral_variation=variation, background=complex(np.mean(reflection)), residue=0j,
                  relative_residual=None, max_step_over_gamma=None, window_width_over_gamma=None,
                  fit_frequency_bounds=[float(frequency[0]), float(frequency[-1])])
    diagnostics = {"spectral_variation_rms": variation_rms, "amplitude_scale": amplitude_scale,
                   "roundoff_amplitude_floor": roundoff, "supplied_noise_rms": supplied_noise,
                   "uncertainty_scope": "local linearization; residual/model error is not independent native convergence",
                   "normal_confidence_multiplier": NORMAL_95}
    result["diagnostics"] = diagnostics
    if amplitude_scale == 0 or variation_rms <= roundoff:
        result["reasons"] = ["flat_spectrum_no_resolvable_variation"]
        result["validity_flags"] = {"identifiable": False, "single_pole_applicable": False,
                                    "sampling_resolved": False, "physical_pole_valid": False}
        return result

    values = reflection / amplitude_scale
    background = (values[0] + values[-1]) / 2
    peak = int(np.argmax(abs(values - background)))
    center = (_finite_real(context.get("center_guess", frequency[peak]), "center_guess") - origin) / span
    width = _finite_real(context.get("gamma_guess", span / 8), "gamma_guess") / span
    lower_center, upper_center = float(coordinate[0]), float(coordinate[-1])
    if not lower_center <= center <= upper_center or not np.exp(-20) <= width <= np.exp(2):
        raise ValueError("Pole guesses must lie inside the sampled window and positive numerical linewidth bounds")

    def residual(parameters):
        difference = _prediction(parameters, coordinate) - values
        return np.r_[difference.real, difference.imag]

    fits = []
    for factor in (1., .5, 2.):
        initial_width = np.clip(width * factor, np.exp(-20), np.exp(2))
        residue = (values[peak] - background) * .5j * initial_width
        initial = [background.real, background.imag, residue.real, residue.imag, center, np.log(initial_width)]
        fits.append(least_squares(residual, initial,
                                 bounds=([-np.inf] * 4 + [lower_center, -20],
                                         [np.inf] * 4 + [upper_center, 2]),
                                 jac=lambda parameters: _jacobian(parameters, coordinate),
                                 ftol=1e-12, xtol=1e-12, gtol=1e-12, max_nfev=5000))
    fit = min(fits, key=lambda candidate: float(np.sum(candidate.fun**2)))
    gamma = float(np.exp(fit.x[5]) * span)
    center_frequency = float(origin + fit.x[4] * span)
    base = complex(fit.x[0], fit.x[1]) * amplitude_scale
    residue = complex(fit.x[2], fit.x[3]) * span * amplitude_scale
    prediction = _prediction(fit.x, coordinate) * amplitude_scale
    difference = prediction - reflection
    residual_norm = float(np.linalg.norm(difference))
    residual_noise = residual_norm / math.sqrt(len(frequency) - 3)
    noise = max(roundoff, supplied_noise, residual_noise)
    relative_residual = residual_norm / variation
    jacobian = _jacobian(fit.x, coordinate)
    condition, covariance = _condition_and_covariance(jacobian, noise / amplitude_scale / math.sqrt(2))
    diagnostics.update(condition, residual_noise_rms=residual_noise, effective_noise_rms=noise,
                       noise_source="max(roundoff, supplied independent RMS, residual RMS with six-parameter degrees of freedom)",
                       peak_resonant_amplitude=2 * abs(residue) / gamma,
                       modeled_variation_rms=float(np.std(prediction)),
                       spectral_variation_over_noise=variation_rms / noise,
                       optimizer_evaluations=int(fit.nfev))
    reasons = result["reasons"]
    if not fit.success:
        reasons.append("optimizer_did_not_converge")
    if variation_rms <= NORMAL_95 * noise:
        reasons.append("spectral_variation_not_resolved_above_noise")
    if np.any(fit.active_mask[4:] != 0):
        reasons.append("pole_at_search_boundary")
    if covariance is None:
        reasons.append("pole_parameters_numerically_rank_deficient")
    else:
        residue_sigma = math.sqrt(max(0., float(np.linalg.eigvalsh(covariance[2:4, 2:4])[-1])))
        residue_snr = abs(complex(fit.x[2], fit.x[3])) / max(residue_sigma, np.finfo(float).tiny)
        log_gamma_sigma = math.sqrt(max(0., float(covariance[5, 5])))
        center_sigma = math.sqrt(max(0., float(covariance[4, 4]))) * span
        q_gradient = np.array([0., 0., 0., 0., span / center_frequency, -1.])
        q_sigma = math.sqrt(max(0., float(q_gradient @ covariance @ q_gradient)))
        diagnostics.update(residue_signal_to_standard_error=float(residue_snr),
                           frequency_standard_error=center_sigma, linewidth_relative_standard_error=log_gamma_sigma,
                           Q_relative_standard_error=q_sigma)
        if residue_snr <= NORMAL_95:
            reasons.append("pole_residue_not_resolved_above_noise")
        if NORMAL_95 * log_gamma_sigma >= 1:
            reasons.append("linewidth_uncertainty_not_resolved")
    identifiable = not reasons
    applicable = relative_residual <= RESIDUAL_LIMIT
    if not applicable:
        result["applicability_reasons"].append("constant_background_single_pole_residual_exceeds_0.05")
    step_ratio = float(np.max(np.diff(frequency)) / gamma)
    span_ratio = span / gamma
    sampling = 4 - 1e-10 <= span_ratio <= 12 + 1e-10 and step_ratio <= .125 + 1e-10
    physical_valid = identifiable and applicable
    q_value = 1j + 2 * residue / (gamma * base) if abs(base) > roundoff else None
    estimate = dict(frequency=center_frequency, gamma=gamma, Q=center_frequency / gamma,
                    wavelength_um=1 / center_frequency, pole_linewidth_um_approx=gamma / center_frequency**2,
                    q_complex=q_value)
    result.update(fit_success=bool(fit.success), identifiable=identifiable, physical_pole_valid=physical_valid,
                  background=base, residue=residue, relative_residual=relative_residual,
                  max_step_over_gamma=step_ratio, window_width_over_gamma=span_ratio,
                  optimizer_estimate=estimate,
                  validity_flags={"identifiable": identifiable, "single_pole_applicable": applicable,
                                  "sampling_resolved": sampling, "physical_pole_valid": physical_valid})
    if physical_valid:
        result.update(estimate)
    return result
