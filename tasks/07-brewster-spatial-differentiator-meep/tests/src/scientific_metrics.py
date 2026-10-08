"""Brewster array metrics with equivalent representations of the fixed static source."""

import numpy as np

from brewster_power import SPEC as POWER_SPEC, derive_power
from scientific_core import canonical_samples, derive_metrics as derive_core_metrics, specs


METRIC_SPECS = specs("brewster")
METRIC_SPECS["brewster_power"] = POWER_SPEC
METRIC_SPECS["brewster_operator"].update(
    required_quantities={"q": "1", "reflection_amplitude": "1 complex"},
    optional_quantities={"input_spectrum": "field"},
    optional_context={"fixed_public_input": "gaussian or sinc, only after verifying the actual synthesis source implements the fixed public spectrum"},
    meaning="Native-derived q and complex reflection_amplitude with a bound input_spectrum or a verified fixed_public_input. Gaussian and Sinc definitions remain public source inputs, never reconstructed FDTD responses. Use |A|^2 times interval quadrature for the continuous slope fit. Sinc integration stops exactly at its retained +/-0.09 cutoff samples; cropped and zero-padded representations are equivalent. Provenance, >=33 genuine angular samples and convergence are independently checked, not inferred from pure-array arithmetic."
)


def derive_metrics(quantities, context):
    if context.get("operation") == "brewster_power":
        return derive_power(quantities, context)
    if context.get("operation") != "brewster_operator":
        return derive_core_metrics(quantities, context)
    quantities = dict(quantities)
    quantities, context = canonical_samples(quantities, context)
    kind = context.get("fixed_public_input")
    if "input_spectrum" in quantities:
        if kind is not None:
            raise ValueError("Choose an explicit input spectrum or its fixed static definition, not both")
        origin = "bound_input_spectrum"
    else:
        coordinate = np.asarray(quantities["q"])
        if kind == "gaussian":
            quantities["input_spectrum"] = np.where(abs(coordinate) <= .1 + 1e-12, np.exp(-.5 * (coordinate / .025)**2), 0)
        elif kind == "sinc":
            quantities["input_spectrum"] = np.where(abs(coordinate) <= .09 + 1e-12, 1.0, 0.0)
        else:
            raise ValueError("Missing input spectrum: bind an array or identify the verified fixed public source")
        origin = "fixed_public_" + kind
    result = derive_core_metrics(quantities, context)
    result["input_spectrum_origin"] = origin
    result["quadrature"] = "sinc_cutoff_trapezoid" if result["input_kind"] == "sinc" else "retained_axis_trapezoid"
    result["integration_samples"] = int(np.count_nonzero(result["quadrature_weights"])) if result["quadrature_weights"] is not None else None
    return result
