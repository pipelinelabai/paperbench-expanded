"""Array-only SWG phase and power metrology; provenance is checked separately."""

import numpy as np


def quantity(units, meaning):
    return {"units": units, "meaning": meaning}


PHASE_QUANTITIES = {
    "wavelength_um": quantity("um", "Common vacuum wavelength samples for both arms"),
    "wide_input": quantity("mode amplitude", "Complex forward input coefficient, wide arm"),
    "wide_output": quantity("mode amplitude", "Complex forward output coefficient, wide arm"),
    "narrow_input": quantity("mode amplitude", "Complex forward input coefficient, narrow arm"),
    "narrow_output": quantity("mode amplitude", "Complex forward output coefficient, narrow arm"),
}
POWER_QUANTITIES = {
    "wavelength_um": quantity("um", "Common vacuum wavelengths"),
    **{f"{arm}_{location}_power": quantity("consistent flux", f"{arm} {location} power in one consistent source normalization")
       for arm in ("wide", "narrow") for location in ("incident", "transmitted")},
}
BLOCH_QUANTITIES = {
    "wide_wavelength_um": quantity("um", "Native wavelengths of the tracked wide-arm Bloch branch"),
    "narrow_wavelength_um": quantity("um", "Native wavelengths of the tracked narrow-arm Bloch branch"),
    "wide_neff": quantity("1", "Wide-arm phase index derived from native Bloch eigenvalues"),
    "narrow_neff": quantity("1", "Narrow-arm phase index derived from native Bloch eigenvalues"),
}
METRIC_SPECS = {
    "swg_local_transfer": {
        "required_quantities": PHASE_QUANTITIES,
        "required_context": [],
        "meaning": "Local input-normalized complex phase and noise diagnostics; does not establish full-band coverage, slope, bandwidth, or convergence",
    },
    "swg_phase": {
        "required_quantities": PHASE_QUANTITIES,
        "required_context": [],
        "meaning": "Input-normalized complex two-arm FDTD phase; never a submitted phase table. The 90-degree error and 1.7/5-degree bandwidths are reporting quantities, not mandatory performance targets; a supported zero bandwidth is valid. Native coverage and measurement validity remain required.",
    },
    "swg_power": {
        "required_quantities": POWER_QUANTITIES,
        "required_context": [],
        "meaning": "Per-arm transmitted power divided by its OWN incident normalization",
    },
    "swg_bloch": {
        "required_quantities": BLOCH_QUANTITIES,
        "required_context": ["length_um"],
        "meaning": "Recompute beta difference; requires native eigensolver provenance, is NOT raw FDTD evidence",
    },
    "swg_raw_compare": {
        "required_quantities": {f"{prefix}_{name}": description for prefix in ("first", "second")
                                for name, description in PHASE_QUANTITIES.items()},
        "required_context": [],
        "meaning": "Phase-only comparison for spectral sampling; does not measure power convergence",
    },
    "swg_phase_power_compare": {
        "required_quantities": {f"{prefix}_{name}": description for prefix in ("first", "second")
                                for name, description in {**PHASE_QUANTITIES, **POWER_QUANTITIES}.items()},
        "required_context": [],
        "meaning": "Recompute two FDTD phases and both arms' own-input-normalized transmissions; compare phase and T on the union of physical wavelength samples. Spatial/temporal refinement metadata and provenance still require inspection.",
    },
    "swg_crosscheck": {
        "required_quantities": {**PHASE_QUANTITIES, **BLOCH_QUANTITIES},
        "required_context": ["length_um"],
        "meaning": "Recompute FDTD phase from complex transfers and Bloch phase from independently tracked native indices; compare piecewise-linear spectra on their combined wavelength grid. Same-model geometry, materials, length, phase gauge and solver provenance require separate inspection.",
    },
}


PHASE_NOISE_QUANTITIES = {name + "_noise_bound": quantity("mode amplitude", "Native absolute complex-amplitude error bound for " + name)
                          for name in PHASE_QUANTITIES if name != "wavelength_um"}
for operation in ("swg_local_transfer", "swg_phase", "swg_crosscheck"):
    METRIC_SPECS[operation]["optional_quantities"] = dict(PHASE_NOISE_QUANTITIES)
for operation in ("swg_raw_compare", "swg_phase_power_compare"):
    METRIC_SPECS[operation]["optional_quantities"] = {
        prefix + "_" + name: description for prefix in ("first", "second")
        for name, description in PHASE_NOISE_QUANTITIES.items()}


for operation in ("swg_local_transfer", "swg_phase"):
    METRIC_SPECS[operation]["optional_quantities"].update({
        arm + "_field_wavelength_um": quantity("um", "Own native wavelength axis for " + arm + " input/output coefficients; bind this when independent field arrays have different lengths. Every common wavelength must match exactly one native sample; no interpolation is performed.")
        for arm in ("wide", "narrow")})


def vector(value, name, complex_allowed=False, minimum_samples=3):
    values = np.asarray(value)
    if values.ndim != 1 or len(values) < minimum_samples or not np.all(np.isfinite(values)):
        raise ValueError(f"{name}: need at least {minimum_samples} finite one-dimensional samples")
    if not complex_allowed and np.iscomplexobj(values):
        raise ValueError(f"{name}: real samples required")
    return values


def ordered(quantities, names, minimum_samples=3):
    wavelength = vector(quantities["wavelength_um"], "wavelength_um", minimum_samples=minimum_samples)
    if np.any(wavelength <= 0) or len(np.unique(wavelength)) != len(wavelength):
        raise ValueError("Wavelengths must be positive and distinct")
    order = np.argsort(wavelength)
    result = {"wavelength_um": wavelength[order]}
    for name in names:
        values = vector(quantities[name], name, complex_allowed=True, minimum_samples=minimum_samples)
        if values.shape != wavelength.shape:
            raise ValueError("All quantities must match their wavelength axis")
        result[name] = values[order]
    return result


def native_sampling(wavelength, context):
    band = np.asarray(context.get("band_um", [1.35, 1.75]), dtype=float)
    if band.shape != (2,) or not np.all(np.isfinite(band)) or band[0] >= band[1]:
        raise ValueError("band_um must be two ordered finite endpoints")
    wavelength = np.asarray(wavelength)
    intersects = (wavelength[:-1] < band[1]) & (wavelength[1:] > band[0])
    gaps = np.diff(wavelength)[intersects]
    maximum = float(np.max(gaps)) if gaps.size else None
    covered = bool(wavelength[0] <= band[0] + 1e-12 and wavelength[-1] >= band[1] - 1e-12)
    overlap = max(0.0, min(wavelength[-1], band[1]) - max(wavelength[0], band[0]))
    return dict(requested_band_um=band.tolist(), native_extent_um=[float(wavelength[0]), float(wavelength[-1])],
                native_sample_count=len(wavelength), covers_requested_band=covered,
                span_coverage_fraction=float(overlap / (band[1] - band[0])), max_gap_um=maximum,
                is_full_public_band=bool(np.allclose(band, [1.35, 1.75], rtol=0, atol=1e-12)),
                public_max_gap_um=0.020,
                satisfies_public_max_gap=bool(covered and maximum is not None and maximum <= 0.020 + 1e-12))


def band_samples(wavelength, values, context):
    band = np.asarray(context.get("band_um", [1.35, 1.75]), dtype=float)
    if band.shape != (2,) or not np.all(np.isfinite(band)) or band[0] >= band[1]:
        raise ValueError("band_um must be two ordered finite endpoints")
    if wavelength[0] > band[0] + 1e-12 or wavelength[-1] < band[1] - 1e-12:
        raise ValueError("Measured wavelengths must cover the band; extrapolation is forbidden")
    samples = np.unique(np.r_[band, wavelength[(wavelength > band[0]) & (wavelength < band[1])]])
    return samples, np.interp(samples, wavelength, values)


def flat_interval(wavelength, error, tolerance, design):
    intervals = []
    for index in range(len(wavelength) - 1):
        left, right = wavelength[index:index + 2]
        first, second = error[index:index + 2]
        if abs(first - second) <= 1e-12:
            if abs(first) <= tolerance + 1e-12:
                intervals.append((float(left), float(right)))
            continue
        crossings = sorted(((-tolerance - first) / (second - first),
                            (tolerance - first) / (second - first)))
        lower, upper = max(0.0, crossings[0]), min(1.0, crossings[1])
        if lower <= upper:
            intervals.append((float(left + lower * (right - left)), float(left + upper * (right - left))))
    merged = []
    for left, right in intervals:
        if merged and left <= merged[-1][1] + 1e-12:
            merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
        else:
            merged.append((left, right))
    selected = next((interval for interval in merged if interval[0] - 1e-12 <= design <= interval[1] + 1e-12), None)
    return {"interval_um": list(selected) if selected else None,
            "bandwidth_nm": 1000 * (selected[1] - selected[0]) if selected else 0.0}


def phase_summary(wavelength, phase, context):
    wavelength, phase = band_samples(wavelength, phase, context)
    design = float(context.get("design_wavelength_um", 1.55))
    target = float(context.get("target_phase_deg", 90.0))
    if not np.isfinite(design + target) or not wavelength[0] <= design <= wavelength[-1]:
        raise ValueError("Design wavelength must lie in the measured band")
    error = phase - target
    uniform = np.linspace(wavelength[0], wavelength[-1], 401)
    uniform_phase = np.interp(uniform, wavelength, phase)
    slope = float(np.polyfit(uniform - design, uniform_phase, 1)[0])
    return {
        "wavelength_um": wavelength.tolist(), "phase_deg": phase.tolist(),
        "phase_at_design_deg": float(np.interp(design, wavelength, phase)),
        "phase_error_max_deg": float(np.max(np.abs(error))),
        "phase_error_std_deg": float(np.std(uniform_phase - target)),
        "slope_signed_deg_per_um": slope, "slope_abs_deg_per_um": abs(slope),
        "max_piecewise_slope_abs_deg_per_um": float(np.max(np.abs(np.diff(phase) / np.diff(wavelength)))),
        "flat_1p7_deg": flat_interval(wavelength, error, 1.7, design),
        "flat_5_deg": flat_interval(wavelength, error, 5.0, design),
        "design_wavelength_um": design,
    }


def align_field_samples(quantities):
    aligned = dict(quantities)
    common = vector(quantities["wavelength_um"], "wavelength_um", minimum_samples=1)
    for arm in ("wide", "narrow"):
        axis_key = arm + "_field_wavelength_um"
        if axis_key not in quantities:
            continue
        native = vector(quantities[axis_key], axis_key, minimum_samples=1)
        if len(np.unique(native)) != len(native):
            raise ValueError("Native field wavelengths must be unique")
        selections = [np.flatnonzero(np.abs(native - wavelength) <= 1e-10) for wavelength in common]
        if any(len(selection) != 1 for selection in selections):
            raise ValueError("Every requested common wavelength needs exactly one actual native sample")
        indices = np.asarray([int(selection[0]) for selection in selections])
        for location in ("input", "output"):
            name = arm + "_" + location
            values = vector(quantities[name], name, complex_allowed=True, minimum_samples=1)
            if values.shape != native.shape:
                raise ValueError("Native field values must match their own wavelength axis")
            aligned[name] = values[indices]
            bound = name + "_noise_bound"
            if bound in quantities:
                noise = np.asarray(quantities[bound])
                if noise.shape != native.shape:
                    raise ValueError("Native error bounds must match their own wavelength axis")
                aligned[bound] = noise[indices]
    return aligned


def transfer_from_fields(quantities, context):
    quantities = align_field_samples(quantities)
    names = [name for name in PHASE_QUANTITIES if name != "wavelength_um"]
    bounds = [name for name in PHASE_NOISE_QUANTITIES if name in quantities]
    if bounds and len(bounds) != len(PHASE_NOISE_QUANTITIES):
        raise ValueError("Phase noise bounds must cover all four modal coefficients")
    data = ordered(quantities, names + bounds, minimum_samples=1)
    sign = context.get("phase_sign", 1)
    turns = context.get("branch_turns", 0)
    if sign not in (-1, 1) or isinstance(turns, bool) or not np.isfinite(turns) or turns != int(turns):
        raise ValueError("Use a documented sign and an integer branch, never a fitted phase offset")
    relative_minimum = {}
    uncertainty = np.zeros(len(data["wavelength_um"]))
    for name in names:
        if np.any(np.abs(data[name]) == 0):
            raise ValueError("Phase is undefined at a zero modal coefficient")
        magnitude = np.abs(data[name])
        relative_minimum[name] = float(np.min(magnitude / np.max(magnitude)))
        if bounds:
            bound = data[name + "_noise_bound"]
            if np.iscomplexobj(bound) or np.any(bound < 0):
                raise ValueError("Native amplitude noise bounds must be real and nonnegative")
            if np.any(magnitude <= bound):
                raise ValueError("Phase is unresolved at or below the native amplitude noise bound")
            uncertainty += np.arcsin(bound / magnitude)
    angle = (np.angle(data["wide_output"]) - np.angle(data["wide_input"])
             - np.angle(data["narrow_output"]) + np.angle(data["narrow_input"]))
    phase = sign * np.rad2deg(np.unwrap(np.angle(np.exp(1j * angle)))) + 360 * int(turns)
    noise = dict(status="resolved_against_bound_arrays_provenance_required" if bounds else "not_established_no_noise_bound_arrays",
                 minimum_relative_coefficient_magnitude=relative_minimum,
                 phase_uncertainty_bound_deg=np.rad2deg(uncertainty).tolist() if bounds else None,
                 amplitude_rescaling_invariant=True)
    return dict(wavelength_um=data["wavelength_um"].tolist(), phase_deg=phase.tolist(), phase_sign=sign,
                branch_turns=int(turns), source_kind="complex_two_arm_transfer", phase_noise=noise,
                native_sampling=native_sampling(data["wavelength_um"], context))


def phase_from_fields(quantities, context):
    transfer = transfer_from_fields(quantities, context)
    result = phase_summary(np.asarray(transfer["wavelength_um"]), np.asarray(transfer["phase_deg"]), context)
    result.update({name: value for name, value in transfer.items() if name not in ("wavelength_um", "phase_deg")})
    return result


def bloch_from_indices(quantities, context, common_wavelength=()):
    arms, sampling = {}, {}
    for arm in ("wide", "narrow"):
        arms[arm] = ordered({"wavelength_um": quantities[f"{arm}_wavelength_um"],
                             "neff": quantities[f"{arm}_neff"]}, ["neff"])
        if np.iscomplexobj(arms[arm]["neff"]):
            raise ValueError("Tracked lossless Bloch phase indices must be real")
        band_samples(arms[arm]["wavelength_um"], arms[arm]["neff"], context)
        sampling[arm] = native_sampling(arms[arm]["wavelength_um"], context)
    length = float(context["length_um"])
    if not np.isfinite(length) or length <= 0:
        raise ValueError("A measured positive propagation length is required")
    band = context.get("band_um", [1.35, 1.75])
    wavelength = np.unique(np.r_[band, context.get("design_wavelength_um", 1.55), common_wavelength,
                                  arms["wide"]["wavelength_um"], arms["narrow"]["wavelength_um"]])
    wavelength = wavelength[(wavelength >= band[0]) & (wavelength <= band[1])]
    wide = np.interp(wavelength, arms["wide"]["wavelength_um"], arms["wide"]["neff"])
    narrow = np.interp(wavelength, arms["narrow"]["wavelength_um"], arms["narrow"]["neff"])
    result = phase_summary(wavelength, 360 * length * (wide - narrow) / wavelength, context)
    result.update(source_kind="bloch_prediction_not_fdtd", length_um=length, native_sampling=sampling)
    return result


def compare_phases(first, second):
    samples = np.unique(np.r_[first["wavelength_um"], second["wavelength_um"]])
    difference = (np.interp(samples, second["wavelength_um"], second["phase_deg"])
                  - np.interp(samples, first["wavelength_um"], first["phase_deg"]))
    return {"max_phase_difference_deg": float(np.max(np.abs(difference))),
            "design_phase_difference_deg": abs(second["phase_at_design_deg"] - first["phase_at_design_deg"]),
            "first": first, "second": second}


def derive_metrics(quantities: dict[str, np.ndarray], context: dict) -> dict:
    operation = context.get("operation")
    if operation not in METRIC_SPECS:
        raise ValueError("Unknown SWG operation")
    specification = METRIC_SPECS[operation]
    if set(specification["required_quantities"]) - quantities.keys():
        raise ValueError("Required raw quantities are missing")
    if set(specification["required_context"]) - context.keys():
        raise ValueError("Required physical context is missing")
    if operation == "swg_local_transfer":
        return dict(transfer_from_fields(quantities, context), scope="local_transfer_not_full_band_metrology")
    if operation == "swg_phase":
        return phase_from_fields(quantities, context)
    if operation == "swg_raw_compare":
        runs = []
        for prefix in ("first", "second"):
            arrays = {name: quantities[f"{prefix}_{name}"] for name in (*PHASE_QUANTITIES, *PHASE_NOISE_QUANTITIES)
                      if f"{prefix}_{name}" in quantities}
            runs.append(phase_from_fields(arrays, {**context, "branch_turns": context.get(f"{prefix}_branch_turns", 0)}))
        return compare_phases(*runs)
    if operation == "swg_phase_power_compare":
        result = derive_metrics(quantities, {**context, "operation": "swg_raw_compare"})
        powers = []
        for prefix in ("first", "second"):
            arrays = {name: quantities[f"{prefix}_{name}"] for name in POWER_QUANTITIES}
            powers.append(derive_metrics(arrays, {**context, "operation": "swg_power"}))
        samples = np.unique(np.r_[powers[0]["wavelength_um"], powers[1]["wavelength_um"]])
        maximum, design = {}, {}
        for arm in ("wide", "narrow"):
            difference = (np.interp(samples, powers[1]["wavelength_um"], powers[1][arm]["T"])
                          - np.interp(samples, powers[0]["wavelength_um"], powers[0][arm]["T"]))
            maximum[arm] = float(np.max(np.abs(difference)))
            design[arm] = abs(powers[1][arm]["T_at_design"] - powers[0][arm]["T_at_design"])
        result.update(max_T_difference=maximum, design_T_difference=design,
                      max_T_difference_any_arm=max(maximum.values()),
                      first_power=powers[0], second_power=powers[1],
                      source_kind="two_run_phase_and_power_comparison")
        return result
    if operation == "swg_crosscheck":
        fdtd = phase_from_fields(quantities, context)
        bloch = bloch_from_indices(quantities, context, fdtd["wavelength_um"])
        result = compare_phases(fdtd, bloch)
        result["source_kind"] = "fdtd_bloch_phase_comparison"
        return result
    if operation == "swg_bloch":
        return bloch_from_indices(quantities, context)
    names = [name for name in specification["required_quantities"] if name != "wavelength_um"]
    data = ordered(quantities, names)
    result = {"source_kind": "per_arm_power_normalization", "native_sampling": native_sampling(data["wavelength_um"], context)}
    for arm in ("wide", "narrow"):
        incident, transmitted = data[f"{arm}_incident_power"], data[f"{arm}_transmitted_power"]
        if np.iscomplexobj(incident) or np.iscomplexobj(transmitted) or np.any(incident <= 0):
            raise ValueError("Native powers must be real, incident power strictly positive")
        wavelength, transmission = band_samples(data["wavelength_um"], transmitted / incident, context)
        design = float(context.get("design_wavelength_um", 1.55))
        if not wavelength[0] <= design <= wavelength[-1]:
            raise ValueError("Design wavelength outside the band")
        central = float(np.interp(design, wavelength, transmission))
        result[arm] = {"T": transmission.tolist(), "T_at_design": central,
                       "IL_at_design_dB": float(-10 * np.log10(central)) if central > 0 else None,
                       "passive": bool(np.all((transmission >= -0.01) & (transmission <= 1.01)))}
    result["wavelength_um"] = wavelength.tolist()
    return result
