# Broadband differential phase in two periodic SWG waveguides: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

- [Objective and Paper Scope](#objective-and-paper-scope)
- [Fixed Geometry, Materials, and Mode](#fixed-geometry-materials-and-mode)
- [Complex Phase and Power Definitions](#complex-phase-and-power-definitions)
- [Spectral Metrics](#spectral-metrics)
- [Experiments and Numerical Accuracy](#experiments-and-numerical-accuracy)
- [Basis of the Measurement Standard](#basis-of-the-measurement-standard)
- [Submission and Reproduction](#submission-and-reproduction)
- [Computing resources and independent reproduction](#computing-resources-and-independent-reproduction)

## Objective and Paper Scope

Use genuine three-dimensional Meep FDTD simulations to compute complex transmission,
differential phase, and transmitted power for two subwavelength-grating (SWG)
waveguides. Cross-check them with an independent three-dimensional MPB or
Floquet–Bloch eigenmode calculation. Retain raw numerical evidence and perform
spatial, temporal, and spectral-sampling convergence studies and negative controls.

Reference: Gonzalez-Andrade et al., *Photonics Research* **8(3), 359–367 (2020)**,
DOI `10.1364/PRJ.373223`.

The fixed model has **two SWG arms, 110 periods, a 22.0 μm propagation length,
and no transitions**. It is a purely periodic experiment inspired by the paper,
not the paper's complete 84-period device with transitions.

The complete device's simulated ±1.7° phase error over 400 nm, measured phase
slope of 16°/μm, and loss below 0.2 dB are background comparisons, not hard
performance requirements for this different model. Do not confuse the measured
145 nm bandwidth with the simulated 400 nm bandwidth.

Use 90° as the design reference for reporting phase errors. Do not force agreement
by changing geometry, optimizing widths or the number of periods, or adding an
approximately 20° transition-phase correction. Splitters, cascaded devices, edge
couplers, and Mach–Zehnder interferometers are outside scope.

## Fixed Geometry, Materials, and Mode

Lengths are in μm. Propagation is along +x; y is the lateral width direction and
z the thickness direction.

| Parameter | Fixed value or definition |
| --- | --- |
| Dimensions | Genuine three-dimensional simulation |
| Silicon thickness | 0.220 μm, centered at z=0 |
| Narrow SWG arm width | 1.600 μm |
| Wide SWG arm width | 1.800 μm |
| Arm-width difference | 0.200 μm |
| Period Λ | 0.200 μm |
| Duty cycle | 0.5 |
| Periods between reference planes | 110 |
| Reference-plane separation L | 22.0 μm |
| Silicon refractive index | 3.476, constant and lossless |
| Silica refractive index | 1.444, constant and lossless |
| Relative permeability | 1 |
| Wavelength range | 1.350–1.750 μm |
| Design wavelength | 1.550 μm |
| Target mode | Fundamental guided quasi-TE mode, predominantly Ey |

The center of unit cell j is `x=j*Λ`. Its silicon region satisfies:

```text
|x-j*Λ| < 0.050 μm
|y| < width/2
|z| < 0.110 μm
```

Everything else, including the upper and lower cladding, is silica. Extend the
same periodic waveguide into input and output buffers; do not insert strip
waveguides or tapers. Simulate the arms separately if desired. Every `cell_size`
must have three components.

Place each arm's input and output reference planes at equivalent unit-cell
positions, exactly 110 periods apart. Report their coordinates, source/PML
buffers, and transverse boundary distances. This separation is longitudinal
within each arm, not the lateral separation between arms.

Track the fundamental quasi-TE mode by overlap or continuity rather than blindly
keeping a band index near a crossing. Distinguish phase index from group index
and identify the arm and mode. There is no universal `neff=2.40` target. Similar
group delays do not imply vanishing group velocity. Optional dispersive-material
studies must be labeled separately and cannot replace the constant-index model.

## Complex Phase and Power Definitions

### Per-Arm Transmission and Differential Phase

Use time dependence `exp(-iωt)` and +x propagation:

```text
t_arm = a_out_plus / a_in_plus
Δφ_FDTD = unwrap(arg(t_wide / t_narrow)) × 180/π
```

The coefficients are the forward complex modal amplitudes at the input and
output reference planes. Use a consistent modal phase gauge within each arm.
The source amplitudes may differ, but normalize each arm by its own input.

Sort by increasing wavelength before unwrapping. An equivalent sign convention
is acceptable with an explicit mapping. Resolve any integer multiple of 360°
using physical evidence such as independently tracked Bloch propagation, not
proximity to 90°. Do not fit away errors or add a 20° constant correction. Phase
is undefined near zero transmission; report this rather than inventing a branch.
Retain raw complex coefficients with wavelength, mode, and reference-plane
associations. Intensities cannot substitute for complex-phase evidence.

A periodic SWG requires a longitudinally periodic Bloch basis, or an equivalent
validated complex-field projection, at equivalent unit-cell planes. A uniform
strip/cross-section eigenmode is not automatically that basis. Document the actual
eigenmode cell, wavevector, normalization, forward/backward separation and phase
gauge; calling an eigenmode API alone does not establish applicability. Conversely,
a missing reference calculation does not prove a properly implemented Bloch
projection physically wrong.

Distinguish a mathematically nonzero coefficient from a phase resolved above
numerical noise. Report source-relative coefficient scales and an independently
supported noise/error estimate where a coefficient or transfer is near zero;
a common small source amplitude alone is not evidence of unresolved phase. An
absolute coefficient error bound whose disk contains zero cannot establish phase.
Optional raw per-coefficient noise-bound arrays can quantify this; documented
native decay/convergence evidence is also admissible. Missing noise bounds are
unknown, not assumed zero. Do not assign phase or interpolate a phase branch
through unresolved samples to claim full-band evidence.

### Per-Arm Power and Loss

The narrow arm is a physical phase reference, not a power-normalization run.
Normalize each arm using its own incident power:

```text
T_arm = P_transmitted_arm / P_incident_arm
IL_arm = -10*log10(T_arm)  [dB]
```

Use documented modal-power weights or native fluxes. A normalization run must
match the illumination, source amplitude, and modal normalization; an unrelated
strip waveguide is not a substitute. Report losses of the periodic interval,
not of the complete device with transitions. Measure reflection or radiation
independently if reported; do not define reflection as `1-T`. Port transmission
alone does not establish complete energy closure.

### Independent Bloch Prediction

Independently solve the same three-dimensional periodic model with MPB or a
Floquet–Bloch eigenmode solver:

```text
Δφ_Bloch = 360 × L × (neff_wide - neff_narrow) / λ  [degrees]
L = 22.0 μm
```

Retain native eigenvalues, wavevectors, mode associations, units, and solver
logs. If native wavelength grids differ, interpolate each arm onto common
physical wavelengths; equal array lengths do not establish frequency matching.
Do not label Bloch results as FDTD. Derived effective-index arrays alone do not
prove solver execution. Broadband subtraction and metric extraction are
postprocessing of the two arms; a third duplicate FDTD solve is unnecessary.

## Spectral Metrics

- Cover `[1.350, 1.750] μm` with initially no adjacent wavelength gap above
  0.020 μm, then refine sampling. Compare both arms at the same wavelengths.
- Evaluate design-point phase at 1.550 μm by piecewise-linear interpolation,
  without extrapolation. Do not substitute the wavelength nearest 90° phase.
- Report the maximum of `|Δφ-90°|` across the complete wavelength range.
- Interpolate onto a uniform 401-sample full-band grid, fit phase versus
  wavelength, and report signed and absolute slopes in °/μm. A large negative
  slope is not flat.
- Also report the maximum absolute piecewise slope and the phase standard
  deviation on that 401-sample grid as diagnostics, without extra thresholds.
- Report the connected interval containing 1.550 μm with `|Δφ-90°|≤1.7°`.
- Separately report the corresponding interval for `|Δφ-90°|≤5°`.

Include endpoints and interpolate threshold crossings linearly. Do not
extrapolate or add disconnected intervals. If no qualifying interval contains
the design wavelength, report 0 nm bandwidth. Do not alter data to obtain a
nonzero bandwidth. The phase error need not cross zero at 1.550 μm.

Report the original native wavelength extent, coverage and largest gap before
inserting interpolated endpoints or plotting samples. A covered span with a large
internal gap is not dense sampling; interpolation cannot meet the existing
0.020 μm initial-spacing requirement. For the full-band FDTD/Bloch cross-check,
form a common wavelength set including the FDTD samples and both Bloch axes,
interpolate each arm's phase index there without extrapolation, then evaluate
360 L (neff_wide-neff_narrow)/lambda at those same wavelengths. Do not instead
interpolate a sparsely derived Bloch phase curve and conflate the two procedures.

## Experiments and Numerical Accuracy

These are experimental accuracy requirements, not precomputed simulation
answers. Report discrepancies and numerical uncertainty honestly if they are
not met; never modify observations to manufacture agreement.

### Nominal Model and Raw Results

Build the fixed three-dimensional SWG arms, verify geometry, materials, and the
110-period reference-plane separation, and track the fundamental quasi-TE mode.
Preserve actual Meep execution logs and the connections between inputs, raw
outputs, modes/monitors, and postprocessing. Reconstruct complex transmission
from frequency-matched input/output coefficients with consistent phase gauges
and per-arm normalization. Explain the phase sign and integer branch physically,
distinguish FDTD from Bloch, and report every metric defined in Section 4.

### Independent Modal Cross-Check

Run independent three-dimensional MPB/Bloch calculations and preserve native
eigenmode and mode-tracking evidence. Use identical materials, length, reference
planes, and periodic geometry. The maximum Bloch–FDTD phase difference over the
common spectral range must be at most **2°**. Do not shift curves to match.
Independent modal predictions do not replace FDTD evidence.

### Per-Arm Power Accounting

Recompute transmission and loss from raw per-arm incident and transmitted
power, documenting reference planes and any scaling. Transmission must lie
within **`[-0.01, 1.01]`**. Do not mix periodic-region and complete-device losses.

Longitudinal termination also needs numerical validation: periodic material in
an absorbing region need not satisfy the assumptions of a conventional PML.
Document the chosen PML/absorber, buffer distances and measured sensitivity to
termination thickness/strength or buffer placement, including differential phase
and each arm's T. Treat that sensitivity as numerical uncertainty, not as an
unannounced additional performance threshold. A finite-time check alone does not
prove the absence of boundary reflections or modal-projection error.

### Numerical Convergence

- Spatial: perform an independent native run with at least **1.4 times** the
  resolution. Maximum phase change must be at most **1°**, and per-arm
  transmission change at most **0.01**. Also report a transverse-domain check.
- Temporal: independently at least double the post-source duration, or use a
  demonstrably stricter decay stopping condition. Phase change must be at most
  **0.2°**, and transmission change at most **0.005**.
- Spectral sampling: halve the wavelength spacing using new native samples.
  Phase change on the common interpolation grid must be at most **0.2°**;
  report bandwidth-endpoint sensitivity. Interpolating old data is not a new
  experiment.

### Scientific Controls and Error Detection

Run a genuine equal-width two-arm FDTD control. Its absolute differential phase
must be at most **0.2°** under a consistent gauge. Also inject a phase or
normalization error and demonstrate numerical rejection, independent of filenames.

The error-injection check tests analysis sensitivity and may be performed on a
copy of measured arrays or with an analytical unit-test fixture. It does not
require another native solve with intentionally wrong physics and never replaces
the genuine equal-width FDTD control. No particular solver implementation,
absolute grid, absolute run time, port interpolation switch or refinement
schedule is prescribed beyond the independent checks and ratios above.

Local source normalization and phase/gauge validity can be assessed on the
measured wavelengths independently of full-band performance. Local evidence does
not establish the full-band slope, bandwidth, sampling or convergence conditions,
and missing full-band coverage is not by itself proof of incorrect local algebra.

No particular filenames, directory hierarchy, image count, receipts, or manifest
are required. Raw evidence must be identifiable and independently recomputable.
Correlated paper metrics derived from one phase curve are reporting quantities,
not additional independent performance thresholds.

## Basis of the Measurement Standard

The paper motivates differential propagation in two SWG arms and comparison of
Bloch and finite-difference simulations. The explicit 110-period, transition-free
geometry is the task's fixed model, not the paper's 84-period complete device.
Per-arm normalization, periodic port applicability, a resolved complex phase,
physical branch selection and independent boundary/convergence controls are
measurement-validity requirements. The 2° cross-check, phase/power convergence
tolerances, refinement ratios, native spacing and 401-point reporting grid are
disclosed numerical policies, not paper performance targets. All remain as
specified. The 90° reference and 1.7°/5° bandwidth definitions describe the measured
response; neither a nonzero bandwidth nor a phase near 90° is required.

All specified formats, source restrictions, controls and computing limits remain requirements of the complete calculation.

## Submission and Reproduction

Submit an executable, no-argument `reproduce.sh` under `/home/submission`. It must
locate its own directory and regenerate raw results offline as unprivileged
`pbsolver`. Store editable code and parameters in `src/`; generated `config/`,
`geometry/`, `results/`, `views/`, and `receipts/` are removed before replay.

Provide model/mode conventions, solver and postprocessing sources, native logs,
raw complex fields/modal coefficients or relevant fluxes, eigenmode data,
derived metrics, convergence studies, and negative-control evidence. Identify
each array's physical quantity, units, and originating run.

NPZ, JSON, CSV, HDF5, and documented real/imaginary split representations are
equivalent. No particular layout or additional manifest is mandatory.
Documented raw numerical evidence may replace images. Report solver/reader
errors explicitly rather than converting them into physical zero results.

Plan for **8 CPUs, 32 GiB RAM, offline execution, and an unprivileged user**.
Record actual runtime and resource usage. The existing task time limit remains
unchanged; packaging a development reference does not extend it.

## Computing resources and independent reproduction

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 25,200 seconds (7 hours) |
| Complete native calculation from source | 18,000 seconds (5 hours) |
| Entire reproduction and independent review | 21,600 seconds (6 hours) |
| CPU allocation | 8 CPUs |
| RAM | 32 GiB |

The native-run limit covers the complete no-argument calculation, including all
required reference runs, controls, convergence studies and generated reports.
Setup, source-integrity checks and independent review use the remaining overall
interval; that reserve is not additional simulation time. No network access is
available during independent reproduction. Preserve partial native output and
identify unfinished work rather than reducing fidelity or omitting controls.
