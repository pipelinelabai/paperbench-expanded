import numpy as np

from scientific_core import canonical_samples, channel_pair, oriented_power, positive


FLUX_NAMES = ("incident", "transmitted", "reflected_signed")


def configure_reference_inputs(specification):
    specification["required_quantities"] = {"wavelength": "um"}
    specification["optional_quantities"] = {
        **{name + suffix: "1" for name in ("T", "R") for suffix in ("", "_plus", "_minus")},
        **{name + suffix: "consistent native flux" for name in FLUX_NAMES for suffix in ("", "_plus", "_minus")},
    }
    specification["input_alternatives"] = "Bind normalized T/R in fixed [+,-] order, or incident/transmitted/reflected_signed raw flux pairs. Raw fluxes use the same per-channel normalization and documented monitor signs as clc_channels, at every bound native wavelength. Do not mix both representations. Missing reflection remains unavailable, never inferred from conservation."
    specification["optional_context"] = dict(specification.get("optional_context", {}),
        incident_flux_sign="+1 default or -1, justified from source/metadata",
        transmission_flux_sign="+1 default or -1, justified from source/metadata",
        reflection_flux_sign="-1 default or +1, justified from source/metadata; no fitted scales")


def reference_quantities(quantities, context):
    raw_names = {name + suffix for name in FLUX_NAMES for suffix in ("", "_plus", "_minus")}
    if not raw_names.intersection(quantities):
        return quantities
    normalized_names = {name + suffix for name in ("T", "R") for suffix in ("", "_plus", "_minus")}
    if normalized_names.intersection(quantities):
        raise ValueError("Bind raw flux or normalized powers explicitly, not competing representations")
    canonical, context = canonical_samples(quantities, context)
    wavelength = canonical["wavelength"]
    incident = channel_pair(canonical, "incident", len(wavelength))
    transmitted = channel_pair(canonical, "transmitted", len(wavelength))
    reflected = channel_pair(canonical, "reflected_signed", len(wavelength))
    if incident is None or transmitted is None:
        raise ValueError("Direct native/reference comparison requires both incident and transmitted channel pairs")
    incident = oriented_power(incident, context, "incident", 1)
    positive(incident)
    transmission = oriented_power(transmitted, context, "transmission", 1) / incident
    if np.any(transmission < -1e-12):
        raise ValueError("Negative native transmitted power is not channel suppression")
    result = {"wavelength": wavelength, "T": transmission}
    if reflected is not None:
        reflection = oriented_power(reflected, context, "reflection", -1) / incident
        if np.any(reflection < -1e-12):
            raise ValueError("Reflected native power has the wrong propagation sign")
        result["R"] = reflection
    return result
