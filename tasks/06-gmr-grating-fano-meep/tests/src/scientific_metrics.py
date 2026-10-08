"""Native spectral characterization and conditional, identifiable Fano-pole fits."""

import numpy as np

from fano_review import derive_fano_pole
from scientific_core import canonical_samples, derive_metrics as derive_core_metrics, specs


METRIC_SPECS = specs("fano")
METRIC_SPECS["power"].update(
    required_quantities={"incident": "power", "transmitted": "power"},
    optional_quantities={"reflected_signed": "power", "reflected_total": "power", "reflected_reference": "power"},
    meaning="Bind incident/transmitted native flux and either reflected_signed after incident subtraction, or the actual reflected_total and reflected_reference from matched device/empty runs with the same monitor orientation. The metric subtracts total-reference; it never takes absolute values or fits a normalization scale. Original port-sign conventions and closure thresholds are unchanged. Different-run provenance and matched sampling must be inspected independently.",
)
METRIC_SPECS["fano_pole"].update(
    required_quantities={"frequency": "1/um"},
    optional_quantities={"reflection_amplitude": "1", "reference_field": "field", "total_field": "field", "reference_frequency": "1/um", "sample_width": "um", "sample_branch": "1"},
    optional_context={
        "spectrum_width_um": "Select one physical width by equality against bound sample_width when several runs share a table; never choose rows by measured fit quality.",
        "spectrum_branch": "Select one declared branch by equality against bound sample_branch when several spectra share a table.",
        "fit_frequency_bounds": "Inclusive [lower, upper] in 1/um, within the bound native spectrum; use the reported local fit window or document an independent window choice.",
        "center_guess": "Initial pole frequency in 1/um, not a fixed fitted result.",
        "gamma_guess": "Initial positive linewidth in 1/um, not a fixed fitted result.",
        "reflection_noise_rms": "Optional independently justified complex-amplitude RMS uncertainty; it can only increase the residual/roundoff error floor. Not a fitted normalization or a replacement for native convergence.",
        "monitor_position_um": "For native reference_field/total_field inputs only: the actual common monitor y position, established from source/metadata.",
        "interface_position_um": "For native fields only: the physical illuminated stack-interface y position, never a fitted phase correction.",
        "incident_propagation_sign": "For native fields only: +1 or -1 in exp(+i sign 2pi f y), from the source direction/verified empty-reference propagation under exp(-i omega t).",
    },
    meaning="Fit the fixed complex constant-background pole model to native-derived zero-order reflected amplitude. Bind a local spectrum directly, or bind the complete spectrum plus fit_frequency_bounds; selecting a window never interpolates, pads, or creates samples. The unchanged span>=4 Gamma and step/Gamma<=0.125 jointly require >=33 samples, not just 25; actual 4..12 Gamma, <=0.05 residual and changed-window checks still apply. Report identifiable, physical_pole_valid, reasons and conditioning/noise diagnostics; null physical Q/frequency/linewidth is not a resolved resonance. Context guesses cannot establish a pole. Establish reflected-side modal projection independently; a point field or transmitted-only flux check is not automatically a zero-order reflected amplitude.",
)

METRIC_SPECS["fano_scan"] = {
    "required_quantities": {"frequency": "1/um"},
    "optional_quantities": {name: units for name, units in METRIC_SPECS["fano_pole"]["optional_quantities"].items() if name != "sample_branch"},
    "required_context": ["spectrum_width_um"],
    "optional_context": {
        name: value for name, value in METRIC_SPECS["fano_pole"]["optional_context"].items()
        if name in ("spectrum_width_um", "monitor_position_um", "interface_position_um", "incident_propagation_sign")
    },
    "meaning": "Describe one complete native width scan, not a fitted window. Call for all four widths. Bind a normalized reflected amplitude or matched native zero-order fields; optional sample_width selects a width from a combined table. Reports original coverage, gaps and variation, never inferred pole count, absence, convergence or a score. Missing widths, gaps, native provenance, detection limits and independent controls require review. A flat spectrum is not a physical pole or proof of absence. Use fano_pole additionally for each claimed isolated pole; never invoke a fictitious fit just to score a supported null/overlap characterization.",
}


def characterize_scan(quantities, context):
    if any(name in context for name in ("fit_frequency_bounds", "spectrum_branch")) or "sample_branch" in quantities:
        raise ValueError("A width scan cannot be restricted to a fitted window or selected branch")
    width = np.asarray(context.get("spectrum_width_um"))
    if width.ndim or np.iscomplexobj(width) or width.dtype.kind not in "fiu" or not np.isfinite(width):
        raise ValueError("A scan requires its finite physical spectrum_width_um")
    widths = np.array([.030, .050, .070, .150])
    matched_width = np.isclose(widths, float(width), rtol=0, atol=16 * np.finfo(float).eps)
    if np.count_nonzero(matched_width) != 1:
        raise ValueError("Scan width must be one of the four fixed air-slot widths")
    frequency = np.asarray(quantities["frequency"])
    reflection, origin = reflected_amplitude(quantities, context)
    if frequency.ndim != 1 or np.iscomplexobj(frequency) or reflection.shape != frequency.shape:
        raise ValueError("Scan requires matching real frequencies and complex amplitudes")
    if "sample_width" in quantities:
        labels = np.asarray(quantities["sample_width"])
        if labels.shape != frequency.shape or np.iscomplexobj(labels) or not np.all(np.isfinite(labels)):
            raise ValueError("Width labels must be finite real values aligned with the native samples")
        selected = np.isclose(labels, float(width), rtol=0, atol=16 * np.finfo(float).eps)
        frequency, reflection = frequency[selected], reflection[selected]
    if (len(frequency) < 2 or not np.all(np.isfinite(frequency)) or not np.all(np.isfinite(reflection))
            or np.any(frequency <= 0) or len(np.unique(frequency)) != len(frequency)):
        raise ValueError("Scan needs at least two finite, unique positive native frequency samples")
    wavelength = np.sort(1 / frequency)
    variation = float(np.sqrt(np.mean(abs(reflection - np.mean(reflection))**2)))
    roundoff = float(64 * np.finfo(float).eps * np.max(abs(reflection)))
    return {
        "width_um": float(widths[matched_width][0]),
        "sample_count": len(frequency),
        "wavelength_extent_um": [float(wavelength[0]), float(wavelength[-1])],
        "covers_public_band": bool(wavelength[0] <= 1.25 + 1e-12 and wavelength[-1] >= 1.75 - 1e-12),
        "maximum_wavelength_gap_um": float(np.max(np.diff(wavelength))),
        "maximum_frequency_gap": float(np.max(np.diff(np.sort(frequency)))),
        "spectral_variation_rms": variation,
        "roundoff_amplitude_floor": roundoff,
        "roundoff_flat": bool(variation <= roundoff),
        "reflection_amplitude_origin": origin,
        "resolved_pole_count": None,
        "absence_established": False,
        "sampling_convergence_established": False,
        "assessment": "Native provenance, search sensitivity, all features and independent controls require review; coverage alone is not resolution.",
    }


def reflected_amplitude(quantities, context):
    native_names = {"reference_field", "total_field", "reference_frequency"}
    if "reflection_amplitude" in quantities:
        if native_names.intersection(quantities):
            raise ValueError("Choose normalized amplitude or the matched native fields, not both")
        return np.asarray(quantities["reflection_amplitude"]), "bound_amplitude"
    if not native_names.issubset(quantities):
        raise ValueError("Bind normalized reflected amplitude or all matched native reference/total field inputs")
    frequency = np.asarray(quantities["frequency"])
    reference_frequency = np.asarray(quantities["reference_frequency"])
    reference = np.asarray(quantities["reference_field"])
    total = np.asarray(quantities["total_field"])
    values = (frequency, reference_frequency, reference, total)
    if any(value.shape != frequency.shape or not np.all(np.isfinite(value)) for value in values):
        raise ValueError("Native device/reference arrays must be finite and identically sampled")
    if np.iscomplexobj(frequency) or np.iscomplexobj(reference_frequency) or not np.allclose(frequency, reference_frequency, rtol=1e-12, atol=0):
        raise ValueError("The native reference must use the device frequency samples")
    if np.any(abs(reference) == 0):
        raise ValueError("Native incident reference fields must be nonzero")
    monitor = float(context["monitor_position_um"])
    interface = float(context["interface_position_um"])
    sign = context["incident_propagation_sign"]
    if not np.isfinite(monitor) or not np.isfinite(interface) or sign not in (-1, 1):
        raise ValueError("Require actual finite reference planes and propagation sign +/-1")
    amplitude = (total - reference) / reference
    amplitude = amplitude * np.exp(4j * np.pi * sign * frequency * (monitor - interface))
    return amplitude, "matched_native_fields"


def derive_metrics(quantities, context):
    if context.get("operation") == "fano_scan":
        return characterize_scan(quantities, context)
    if context.get("operation") == "power":
        native_names = {"reflected_total", "reflected_reference"}
        if "reflected_signed" in quantities:
            if native_names.intersection(quantities):
                raise ValueError("Choose reflected signed flux or the native subtraction inputs, not both")
            return derive_core_metrics(quantities, context)
        if not native_names.issubset(quantities):
            raise ValueError("Bind reflected_signed or both reflected_total and reflected_reference")
        total, reference = (np.asarray(quantities[name]) for name in ("reflected_total", "reflected_reference"))
        if total.shape != reference.shape or not np.all(np.isfinite(total)) or not np.all(np.isfinite(reference)):
            raise ValueError("Incident subtraction requires finite, identically sampled native flux arrays")
        if any(np.iscomplexobj(value) and np.any(value.imag != 0) for value in (total, reference)):
            raise ValueError("Native time-averaged flux must be real before subtraction")
        return derive_core_metrics(dict(quantities, reflected_signed=total - reference), context)
    if context.get("operation") != "fano_pole":
        return derive_core_metrics(quantities, context)
    frequency = np.asarray(quantities["frequency"])
    reflection, origin = reflected_amplitude(quantities, context)
    if frequency.ndim != 1 or np.iscomplexobj(frequency) or reflection.shape != frequency.shape:
        raise ValueError("Bind matching one-dimensional real frequency and complex-amplitude arrays")
    input_sample_count = len(frequency)
    selected_spectrum = np.ones(frequency.shape, dtype=bool)
    for quantity_name, selector_name in (("sample_width", "spectrum_width_um"), ("sample_branch", "spectrum_branch")):
        if (quantity_name in quantities) != (selector_name in context):
            raise ValueError("Spectrum grouping needs both bound labels and an explicit scalar selector")
        if quantity_name not in quantities:
            continue
        labels = np.asarray(quantities[quantity_name])
        selector = np.asarray(context[selector_name])
        if labels.shape != frequency.shape or np.iscomplexobj(labels) or not np.all(np.isfinite(labels)):
            raise ValueError("Spectrum labels must be finite real arrays aligned with the bound spectrum")
        if selector.ndim != 0 or np.iscomplexobj(selector) or not np.isfinite(selector):
            raise ValueError("A spectrum selector must be one finite real scalar")
        if selector_name == "spectrum_branch" and (float(selector) % 1 or np.any(labels % 1)):
            raise ValueError("Branch labels must be integers, not interpolated results")
        tolerance = 16 * np.finfo(float).eps * max(1, abs(float(selector)))
        selected_spectrum &= np.isclose(labels, float(selector), rtol=0, atol=tolerance)
    frequency, reflection = frequency[selected_spectrum], reflection[selected_spectrum]
    if not frequency.size or not np.all(np.isfinite(frequency)) or not np.all(np.isfinite(reflection)):
        raise ValueError("The complete selected spectrum must be finite and nonempty")
    if np.any(frequency <= 0) or len(np.unique(frequency)) != len(frequency):
        raise ValueError("Native frequencies must be positive and unique within the selected spectrum")
    if "fit_frequency_bounds" in context:
        bounds = np.asarray(context["fit_frequency_bounds"])
        if bounds.shape != (2,) or np.iscomplexobj(bounds) or not np.all(np.isfinite(bounds)):
            raise ValueError("fit_frequency_bounds must contain two finite real frequencies in 1/um")
        lower, upper = map(float, bounds)
        if not 0 < lower < upper or lower < frequency.min() or upper > frequency.max():
            raise ValueError("The ordered fit window must lie inside the native frequency coverage")
        selected = (frequency >= lower) & (frequency <= upper)
        frequency, reflection = frequency[selected], reflection[selected]
    if len(frequency) < 33:
        raise ValueError("The selected local fit window needs at least 33 native samples")
    local_quantities = dict(quantities, frequency=frequency, reflection_amplitude=reflection)
    local_quantities, local_context = canonical_samples(local_quantities, context)
    result = derive_fano_pole(local_quantities, local_context)
    result.update(
        input_sample_count=input_sample_count,
        sample_count=len(frequency),
        fit_frequency_bounds=[float(frequency.min()), float(frequency.max())],
        reflection_amplitude_origin=origin,
    )
    return result
