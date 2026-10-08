# Private SWG scientific guide

The config/public_contract.md is authoritative. Use only binary leaves; no format points,
global score cap or assumed score band. Each passing numerical leaf must call its
metric_operation on original arrays and inspect source/log provenance. Successful
arithmetic alone is not proof of an FDTD or MPB run. All band metrics use
[1.35,1.75] um and design 1.55 um. A shortened band cannot satisfy the full-band leaf.
phase_sign and integer branch_turns must be justified physically, never optimized
against 90. NPZ/JSON/HDF5/CSV, row order and documented units are equivalent.

swg_phase, swg_raw_compare, swg_phase_power_compare and swg_crosscheck accept original
COMPLEX transfer coefficients, not candidate phase tables. Match the two arm
wavelength axes from source before binding.
swg_power accepts own-arm consistent powers; it is valid to undo/redo a documented
common source normalization, but never divide normalized output by an unnormalized
incident power. Check the algebra using saved P_out_raw/source_power_normalization
or equivalent raw evidence. There is no universal upper/lower absolute incident flux.
swg_bloch recomputes phase from phase indices; inspect native eigenvalue/k arrays,
solver logs and tracking code before awarding provenance. Do not misclassify this
operation as FDTD evidence. No context-only operation exists here.

For the same-model cross-check leaf, swg_crosscheck must succeed on BOTH original
FDTD complex transfers and native-branch Bloch indices. It uses length_um from the
physical port separation, with 22 um required by the nominal model. Its first result
is reconstructed FDTD; second is the independently reconstructed Bloch prediction.
Compare max_phase_difference_deg with the unchanged 2-degree limit. Interpolate
each native Bloch index onto the union including FDTD wavelengths BEFORE computing
360 L delta-neff/lambda; interpolate the measured FDTD phase on that common grid. The FDTD sign and integer branch need the
same physical justification as in swg_phase. Verify geometry, materials, reference
planes, mode tracking and solver logs independently; a tool result is not provenance.

For spatial and temporal convergence, require swg_phase_power_compare. Every run
needs first_/second_ prefixed wavelength_um, wide_input, wide_output, narrow_input,
narrow_output, wide_incident_power, wide_transmitted_power, narrow_incident_power
and narrow_transmitted_power. Within a run, these arrays must describe the same
physical wavelength axis; the two runs may have different sample grids or ordering.
The operation reconstructs both phases and divides each transmitted power by its
OWN arm/run incident power before comparing on the union of wavelength samples.
Inspect max_phase_difference_deg AND max_T_difference for BOTH wide and narrow:
spatial limits are 1 degree and 0.01; temporal limits are 0.2 degree and 0.005.
design_T_difference alone is insufficient; an off-design discrepancy must not pass.
A truthful above-limit result is a scientific failure for that leaf, not a tool
error. Do not award a pass merely because an operation returned successfully.
Missing native powers cannot be replaced with phase-only swg_raw_compare, equal
source assumptions, hard-coded T=1, or submitted convergence booleans.

Inspect actual resolution/refinement and duration/decay settings separately:
at least 1.4x spatial resolution, and at least 2x post-source time or demonstrably
tighter decay. There are no mandatory absolute grid or time values. A pair of
identical arrays or a synthetic perturbation is not an independent convergence run.
The phase-only swg_raw_compare remains appropriate for spectral sampling, whose
0.2 degree requirement does not add an unannounced power-convergence threshold.

Example binding structure (choose ACTUAL paths and quantities):
{"path":"submission/results/arm/raw.npz","array":"coeff_in",
 "source_unit":"mode amplitude","target_unit":"mode amplitude",
 "unit_evidence":{"path":"submission/src/solver.py","quote":"exact source passage identifying the complex modal coefficient"}}
unit_evidence is an OBJECT with path and verbatim quote, not a string. The source
quote must genuinely establish the array and convention. Common f/lam arrays must
be checked for both arms. Do not bind intensity to complex amplitudes. Root model
parameters, material functions and sample/port associations must all agree.

Do not award multiple performance penalties for one phase offset: a truthful large
error/zero bandwidth can satisfy the measurement leaf. Strong performance belongs
to independent model consistency and convergence checks, not headline ladders.
Require original numerical evidence and measured resource use from each submission.


## Review metrology and scope

`swg_local_transfer` uses the same original complex coefficients and returns local
phase, gauge, source-relative magnitude and noise diagnostics without requiring
full-band coverage. It is the operation for the local normalization and phase/gauge
leaves only. It cannot satisfy broadband measurements or full-band convergence.
`swg_phase`, `swg_power`, `swg_bloch` and the full-band comparisons retain their
separate full-band obligations. Never infer all local algebra is wrong merely
because the full-band calculation is incomplete.

`native_sampling` reports original extent, sample count, span coverage, maximum
native gap, `is_full_public_band` and `satisfies_public_max_gap`. Interpolated output
points do not enter the native gap calculation. For the full-band measurement leaf
require the public [1.35,1.75] um band and the existing <=0.020 um initial spacing;
a customized context band or three-point pilot is not full-band evidence. Bloch
results report each arm's own native sampling separately; interpolation remains
an explicit numerical operation, not additional native samples.

Optional `wide_input_noise_bound`, `wide_output_noise_bound`,
`narrow_input_noise_bound`, `narrow_output_noise_bound` are nonnegative absolute
complex-amplitude error bounds on the same native axis and in the same amplitude
units. Supply all four or none; two-run comparisons use `first_`/`second_` prefixes.
Their provenance must establish an actual noise/error estimate, not fitted bounds.
A coefficient whose magnitude is <= its bound cannot establish phase and is
rejected. Otherwise the metric returns a conservative summed arcsine angular bound.
Without arrays `phase_noise.status` explicitly says noise resolution is not
established; it is not automatically a scientific failure or a zero-noise pass.
Inspect equivalent native decay/convergence evidence, especially near nulls.
Common source rescaling, including small absolute amplitudes, must not change this
assessment. No arbitrary absolute-amplitude cutoff or new physical tolerance is used.

The source/provenance audit must establish a periodic Bloch basis or a validated
equivalent projection, consistent gauge and normalization, and numerical boundary
sensitivity. Conventional uniform-section mode decomposition and a PML name alone
are not proofs for a longitudinally periodic guide. Neither are absent benchmarks
proofs of physical error. Retain missing-native/needs-review findings explicitly.
All existing phase and BOTH-arm T tolerances remain unchanged. A phase-only
operation still cannot satisfy spatial or temporal power convergence.

## Paper-backed review boundary

The 90-degree reference and 1.7/5-degree bandwidths are descriptive measurements,
not success targets. Preserve all original phase, normalization, Bloch, boundary,
spatial, temporal, sampling and equal-width validity requirements. The numerical
error-injection check may use copied measurements or an analytical unit-test
fixture; no intentionally erroneous native solve is required. No port-interpolation
switch or absolute solver schedule is prescribed. A paper-backed task review
supplies neither a candidate solution nor proof of native accuracy or runtime.
