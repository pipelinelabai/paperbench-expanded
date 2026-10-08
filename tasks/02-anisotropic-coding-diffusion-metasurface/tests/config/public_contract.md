# Polarization-dependent reflection and diffuse scattering from a coding metasurface: scientific protocol

Read the paper for the geometry, materials, physical results and figure context. This addendum specifies the reproduction scope, missing conventions, output schemas and reproduction requirements. Its explicit task conventions take precedence for this model and must not be presented as facts recovered from the paper. Figure numbers refer to paper captions, not converted image filenames.

This document brings together the research scope, comparison conditions, measurement definitions, required data, reproduction procedure and computing limits.

- [Scientific measurements](#scientific-measurements)
- [Paper interpretation](#phase-frequency-and-polarization)
- [Phase and reflection basis](#phase-and-reflection-basis-convention)
- [Data products](#required-data-products) and [output schemas](#output-schemas)
- [Reproduction procedure](#workspace-and-provided-materials)
- [Budget accounting](#budget-accounting) and [computing resources](#computing-resources-and-independent-reproduction)
- [Licensed HFSS environment](#licensed-hfss-environment)

## Scientific measurements

Reproduce and compare the paper's **HFSS simulation** results (not the measurements) plus the paper's own array-factor model:

| # | Target paper figures | Object | Metrics | Variant name(s) |
|---|---|---|---|---|
| T1 | Fig. 1b, Fig. 1c | Anisotropic unit cell of Fig. 1a, infinite periodic, normal incidence | Reflection amplitude for x- and y-polarization; reflection phases and their difference | `unit_normal` |
| T2 | Fig. 7a (all three legend curves) | Same unit cell under oblique TM incidence in the paper's stated incidence plane, at the three legend angles | Reflection-phase difference between the "0" and "1" element orientations vs frequency | `unit_tm15`, `unit_tm30`, `unit_tm45` |
| T3 | Fig. 3a/b/c (three matrices and their patterns) | Array-factor model of Eq. (1)(2) — **numerical target, no HFSS solve required for this variant** | AF_max and broadside AF for the uniform, initial and optimal coding matrices; 3D/hemispheric AF pattern plots | `af_patterns` |
| T4 | Fig. 5 (red/blue curves), Fig. 10a (simulated curves only), Fig. 6a and Fig. 6e | Finite 240 mm coding metasurface built from the optimal coding matrix (Fig. 3c / Fig. 4) | Monostatic backscatter RCS vs frequency under normal incidence for x- and y-polarization; RCS reduction vs the PEC reference; surface-current map and 3D far-field scattering pattern at the paper's stated Fig. 6 frequency (x-polarization) | `array_ms` |
| T5 | Fig. 5 (black curve), Fig. 6b and Fig. 6f | Same-size metallic reference surface | Monostatic backscatter RCS vs frequency; surface-current map and 3D far-field pattern at the same frequency | `array_pec` |

The RCS-reduction curves (T4) must be derived from your own two solved RCS spectra (`array_ms` minus `array_pec`), not from any analytical plate formula.

## Scope

- Included: everything in the table above, simulation only.
- Excluded: all measured results (Fig. 9, Fig. 10a measured traces, Fig. 10b); the Simulated-Annealing optimization run itself (Fig. 2a/2b) — the optimal coding matrix is fully given in the paper and re-running SA is not part of the requested work; the near-electric-field cut planes Fig. 6c/6d; the oblique-incidence full-array results Fig. 7b and the scattering-spectra maps Fig. 8.

## Clarifications

1. TM polarization for the oblique-incidence targets: the paper states the incidence plane and angles but does not spell out its TE/TM convention. Use TM = magnetic field perpendicular to the plane of incidence (E in the plane of incidence). Record this in `meta.json` (`polarization_definition`).
2. The "same-size metallic surface" reference: model it as a bare metallic plate of the same 240 mm × 240 mm footprint (no dielectric layer). Its metal thickness is not given by the paper; use a reasonable engineering treatment and state it in README/meta.json.
3. Array-factor evaluation contract: the paper does not fully specify the angular sampling domain or evaluation frequency behind the AF_max values of Fig. 2b, so the converged value printed there is NOT a reviewed target and the SA run is not required. `af_patterns` is reviewed solely on the fixed evaluation contract given in Output Schemas, applied to the three matrices of Fig. 3.
4. Reflection reference plane: z=h fixes comparisons between your own runs. The paper does not specify its plane, so its absolute phase/zero-crossing values are not fixed absolute-phase targets. Check the raw-to-phase conversion and reference-plane implementation. A common reference shift cancels in the oriented phase difference but not in either absolute phase; it cannot justify an incorrect phase-difference peak.
5. No exploration parameters are declared. Keep the paper-given geometry/materials and the public task conventions. Disclose implementation assumptions; missing reference-plane metadata is not permission to tune nominal dimensions or fit phase offsets to paper curves.

## Phase, frequency and polarization

Results paragraph 1 and Fig. 1(a–c) define the rectangular element, x/y
incidence and broad near-180-degree contrast. Fig. 1(c)'s directed phase
difference rises above 180 degrees (roughly 200 degrees near 5.5–6 GHz).
It must not be replaced by the minimal unsigned angular distance, which is
bounded by 180 degrees. Keep the declared signed laboratory bases, common
reference plane, temporal convention and oriented phase-difference rule.
Report the measured maximum and its own frequency, not an imposed maximum
at the 5.86-GHz field-snapshot frequency. The paper itself attributes finite
array dip/element phase-crossing frequency differences to boundary conditions.

The Angular performances paragraph explicitly uses TM incidence at 15/30/45
degrees in the xoz plane (Fig. 7a). Those angles/plane are paper-supported;
the existing E/k/basis records make the implementation auditable. The paper
does not specify an absolute reflection reference plane, so absolute phase
and zero-crossing locations remain characterization, not absolute targets.
Do not force a legend swap or choose a basis sign to fit a curve; Fig. 1a's
physical patch orientation and a documented native basis control labels.

## Finite-array receive definition

Keep the 240-mm square array, 6x6 coding lattices, 4x4 patches per lattice,
nominal geometry, bit-to-orientation decoding and bare same-size reference.
The x-oriented lattice is called 1 in the Results text; a global bit rename
is valid only if decoding preserves the physical layout.

Fig. 5 and the simulated traces of Fig. 10(a) report RCS/reduction for x/y
incident polarizations but do not identify a complete receive-component
definition. Incident polarization is not a specification of received total
versus co-polar power. The task explicitly asks for total scattered RCS,
including both orthogonal transverse components, and a bare-plate reference.
Do not change that model to chase the paper traces. Retain the quantitative RCS, dip, reduction, coverage and morphology comparisons below. The receive-definition uncertainty must be reported and independently resolved before claiming paper agreement; it does not turn a mismatch into a successful reproduction.

The paper's simulated -10 dB intervals (x: 5.2–6.86 GHz; y: 5.44–6.9 GHz) remain distinct from the measured intervals. Report every actual strict qualifying component, outer envelope and coverage. Empty or truncated intervals must be reported truthfully and cannot establish a required band or coverage. The fixed-core -9 dB and 80% criteria below are retained task comparison requirements, not uncertainty bounds quoted from the article.

AF remains a separate fixed mathematical calculation of Eq. (2), on the
disclosed 5.8-GHz/1-degree grid, not HFSS evidence or a reproduction of the
incompletely specified optimization history. Do not impose Fig. 2b's ~7.8
value on this different evaluation domain. All original deliverables remain.

## Measurement validity and comparison scope

Use the paper's reported observations as comparators only at their stated
conditions. Keep all requested variants, grids, raw exports, summaries, field
images, source/provenance records and disclosed operating budgets. Independent
native evidence is required for every claimed HFSS observation; a citation or
synthetic curve is not a computed result. Do not adjust primary dimensions to
fit a comparator. Report absent passbands, truncated intervals and negative
results using the prescribed null/status conventions, with their actual
evidence and interpretation. A negative observation is not a missing file and
does not establish reproduction of a positive paper result.

Use the measurement definitions and output schemas in this document. Quantify disagreement with the paper across the requested
curves and experiments, including uncertainty from discretization and geometry.
For quantities defined differently from the paper, provide the actual measured
quantity, its definition and the condition difference, rather than asserting
equivalence. See Licensed HFSS environment below for the owner-specific runtime and
operating-resource prerequisites.

## Phase and Reflection-Basis Convention

All reported complex reflection coefficients and phases use `E_physical(r,t) = Re(E(r)*exp(+i*omega*t))`. Record `meta.phasor_convention: "exp(+i*omega*t)"`. If an internal/native representation uses the opposite time convention, conjugate its phasors and consistently convert the reference-plane operation before producing the reported outputs. Recording a different convention without conversion does not make the same directed-phase target comparable. This is a fixed output convention, not a fitted phase correction.

The published HFSS phasor definition is the same positive-sign convention: Ansys HFSS 2025 R1 Help, [Peak Versus RMS Phasors](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v251/en/Subsystems/HFSS/Content/HFSS/PeakVersusRMSPhasors.htm), Eq. (1). That page also specifies plane-wave source amplitudes in the peak sense; the field-map excitation above is therefore 1 V/m peak. Preserve all native exports unchanged and record any representation conversion in the derived dataflow.

At normal incidence, use propagation direction `k_inc=(0,0,-1)` and reflected direction `k_ref=(0,0,1)`. For x polarization, project incident and reflected electric fields onto the same laboratory +x unit vector; for y polarization use the same +y vector for both. Define each co-polar reflection coefficient as reflected amplitude divided by incident amplitude in these signed bases. Do not independently reverse the reflected basis or inherit arbitrary Floquet eigenvector phases. At a PEC reference plane this convention gives electric-field reflection -1, not +1.

For positive TM incidence angle theta in the x-z plane, use `k_inc=(sin(theta),0,-cos(theta))`, `k_ref=(sin(theta),0,cos(theta))`, `e_inc=(cos(theta),0,sin(theta))` and `e_ref=(cos(theta),0,-sin(theta))`; the tangential x components have the same sign. The corresponding TE basis is +y for both propagation directions. Both element orientations use this same physical incidence and basis. Map any rotated-incidence implementation back to these vectors before taking `phase_element0 - phase_element1`. Record the native mode-to-field projection and basis vectors in `meta.reflection_basis`. Temporal convention, signed polarization basis and the common z=h reference plane must all agree before comparing the directed phase difference. These conventions do not change the paper-target windows.

## Numerical and Bandwidth Details

For `af_patterns`, use c=299792458 m/s, k=2*pi*f/c, d equal to the paper lattice spacing, bit phase 0 or pi, and the 6x6 matrices in Eq. (2). With row index m along +x and column n along +y, compute the complex sum of exp(i*(k*d*sin(theta)*(m*cos(phi)+n*sin(phi))+pi*bit[m,n])) and take its magnitude. Starting the indices at 0 versus 1 changes only a common phase. The uniform matrix is all zero (all one is equivalent). Preserve `af_samples.npz` containing one-dimensional theta_deg (91 samples) and phi_deg (360 samples), and af_uniform, af_initial, af_optimal as non-normalized magnitude arrays each shaped (91,360). --check recomputes these and af_summary from the matrices on the exact 5.8 GHz/1-degree hemisphere grid; it must not import a modeling module that imports ansys. Record input matrix and numerical-source SHA-256 hashes in `af_patterns/meta.json`. Numerical images are checked against these arrays and their plotting source, not an AEDT export. Do not force the paper's approximately 7.8 optimization trace value onto this different, explicitly specified evaluation domain.

In AF meta.json, `input_sha256` is an object mapping submission-relative input paths to their SHA-256 strings and must include `results/af_patterns/coding_matrices.json`; `source_sha256` similarly maps the numerical source files under `src/` to their hashes. Retain sufficient data to verify these hashes, the paper matrices (including a consistent global bit relabeling), the exact array grid and Eq. (2), and to recompute each reported scalar from its corresponding array. A summary alone cannot establish the AF result. Arrays use the derived-quantity tolerances in the common contract; array-derived scalar serialization tolerance is 0.0011. Numerical target comparisons use the actual array-derived values.

### Total-RCS convention

For the finite metasurface, PEC reference, reduction spectra and Fig. 6 far-field images, use total RCS: `sigma_total = lim(r->infinity) 4*pi*r^2*(|E_theta_scattered|^2 + |E_phi_scattered|^2)/|E_incident|^2`, in square meters, and `rcs_dBsm = 10*log10(sigma_total / 1 m^2)`. Use HFSS `RCSTotal` with its stated units, or the exactly equivalent sum of two orthogonal transverse scattered-field powers with the same incident normalization. Do not sum dB values or substitute a single received component. The total is independent of the chosen orthonormal transverse basis, including at the monostatic pole. Keep the total/scattered-field distinction explicit; incident-plus-scattered total electric field is not an RCS input.

Record `meta.rcs_quantity` with `kind: "total"`, the native report expression(s), output unit, incident amplitude and polarization, observation direction and scattered-field component mapping. Preserve the native total-RCS export or the two complex transverse scattered-field exports used for the sum. Other received components may be exported as diagnostics with distinct names; they cannot replace these required columns or Fig. 6 plots. Finite coding does not establish zero cross-polarized scattering. Total RCS is an explicit task convention for the paper's unspecified receive-component choice; characterize the total-RCS response with independent native evidence and document the receive-definition difference. The paper's unspecified receive-channel traces are comparators, not guaranteed total-RCS performance windows.

Coding labels may be renamed only with a corresponding change of `one_means`/orientation decoding so that the physical layout is unchanged. Complementing bits while keeping the same physical bit-to-orientation map rotates the patches and is not a mere relabeling; that changes the x/y RCS assignment. Geometry, AF and metadata must use one consistent decoded matrix.

For each polarization p in {x,y}, compute from `rcs_reduction.csv`:

- `band10dB_envelope_p_GHz`: first and last qualifying grid frequencies with reduction<=-10 dB, or null if none. This is an outer envelope, not a continuous bandwidth.
- `band10dB_intervals_p_GHz`: all maximal consecutive qualifying grid components [lo,hi], in frequency order; [] if none. A single isolated row is [f,f] with zero width.
- `band10dB_longest_p_GHz`: longest component, with ties resolved by lower lo; null if none.
- `band10dB_coverage_p`: number of qualifying rows divided by total rows inside the envelope, including its endpoints; 0 if no envelope.
- `band10dB_worst_reduction_p_dB`: maximum reduction in the envelope, null if none.

Report outer-edge placement separately from suppression inside the band. The paper does not establish fixed-core <=-9 dB/every-row or >=80% -10 dB coverage conditions for the specified total-RCS definition. Preserve actual intervals, coverage and null results; no endpoint interpolation is used. Compare the paper's simulated interval observations without treating them as hard targets for total RCS.

Unit-cell raw exports must include power-normalized complex co- and cross-polarized fundamental reflection coefficients for each used incident polarization/orientation, with the phase convention recorded. One full-matrix Floquet solution at normal incidence may supply both x/y incident polarizations. For oblique TM, both element orientations require real solutions at the same physical incidence; an equivalent rotated-incidence solution is allowed with the rotation and basis mapping documented. For the finite array, x/y results require the corresponding incident-wave excitations or a complete solved source basis with documented linear superposition; reusing a mesh does not turn one single-polarization response into both. The reflected co+cross power subset must be <=1.005; do not infer absorption merely from the co-polarized term. A substrate backed by metal has no required transmission output. Absolute phase, covariance under a common reference shift and physical phase difference are separate checks.

## Completion policy

Completion requires a successful no-argument clean replay producing the full
addendum-required HFSS projects, native solve evidence, numerical artifacts,
views, logs, and provenance. Before finishing, run `reproduce.sh` from a clean
generated-output state and verify that all required files exist. A smoke test or
unsolved project is not a completed submission.

## Comparison and numerical integrity

Compare the unit-cell complex reflection amplitudes and directed phase differences across frequency, polarization and incidence angle. Keep the numerical array-factor experiment distinct from the native finite-array and PEC scattering experiments. Report co- and cross-polarized evidence, spectral coverage and angular redistribution, not just a fitted phase difference or peak reduction.

Use the paper's simulated curves only under the stated matching conditions; do not tune geometry or replace computed data with digitized curves. Keep nominal dimensions exact in the construction. A geometry readback tolerance of 0.05 mm accommodates numerical extraction, not a change to the design. Quantify mesh and sweep sensitivity, preserve unrounded native exports, and keep summaries consistent with their underlying arrays. Check finite responses, passivity and the applicable reciprocity relations. The output grids, units, reference planes, polarization conventions and control experiments in this document remain required.

## Method and evidence requirements

Read the supplied paper and use
Ansys HFSS through ansys.aedt.core / PyAEDT to build, solve, and export genuine
native models. Use numerical calculations instead only where the addendum
explicitly defines a numerical experiment.

1. Read addendum.md, the complete paper, and relevant figures. Figure numbers
   refer to captions, not extracted filenames. Consult the PDF for ambiguities.
   Read blacklist.md and the computing limits in this document.
2. Extract geometry, materials, and comparison targets from the paper. Follow
   the addendum's public coordinate, port, phase, statistical, and evidence
   conventions. Nominal dimensions must drive the actual geometry. Document
   unspecified engineering choices; do not tune dimensions to match curves.
3. Preserve native projects, solver logs, mesh/adaptive histories, and unmodified
   exports. Solve every distinct physical variation. Identify any legitimate
   multiport, polarization, or Optimetrics reuse as defined in the addendum.
4. Implement src/run_all.py --variant <name>, no-argument reproduce.sh, and
   offline src/derive.py --results <path> [--check]. The offline module may use
   only the standard library, NumPy, and SciPy, without importing AEDT.
5. Keep README.md static. Write current execution status, solved-variation
   mappings, convergence, and failures to results/run_summary.json. Do not
   rewrite source files during replay or replace failures with fabricated values.
6. Do not derive final electromagnetic responses from digitized figures,
   analytic curves, other solvers, cached historical results, or fabricated
   logs. Paper targets are comparison inputs, never simulation outputs.
7. Submit PAPER_AUDIT.md with checked paper locations, evidence, conclusions,
   modeling decisions, and sources of already-disclosed clarifications. A
   numerical mismatch alone does not establish an error in the paper.
8. Keep deliverables under /home/submission. Run the complete entrypoint and
   offline checks before handoff, preserving source immutability and isolation.

The addendum's specific scientific definitions take precedence over this summary.

Read `/home/paper/blacklist.md` before consulting external resources and follow its resource-use restrictions throughout this task.

## Data formats and preparation checks

The required artifact paths, field names, physical units and grids in this addendum are the
public submission contract. CSV column order, UTF-8 BOM, CRLF/LF, surrounding
header/cell whitespace and additional nonempty columns do not change the scientific
meaning. JSON whitespace/key order and UTF-8 BOM are also accepted. Column names
remain case-sensitive; duplicate names after trimming, duplicate JSON keys,
nonfinite required numbers, ambiguous units/polarization, missing required data,
and conflicting CSV/summary values are not silently repaired. Do not parse a
native HFSS CSV with `split(',')`: quoted S-parameter names contain commas; use
Python's `csv` reader. No curve interpolation or fabricated provenance is used
to repair a submission.

Before the final handoff, run this read-only, no-solver public preflight:

```bash
python3 /home/paper/tools/check_submission.py --submission /home/submission
```

`--variant <name>` limits other variants' result/view checks, while retaining
shared submission requirements. The checker reports exact missing paths,
required CSV columns and grids; it does not call a model, execute your code,
launch HFSS, modify artifacts, or certify scientific correctness. Its machine-
readable checklist is `/home/paper/tools/submission_contract.json`; it contains only public schema requirements. The checklist covers the Required
data products tree and CSV schemas; the remaining scientific and provenance
requirements in this addendum still apply.

Retain completed, intact evidence if a later variant fails, and report
the incomplete run explicitly. Every reported HFSS-dependent result needs
native execution evidence. Changed source, stale or unbound outputs, failed
isolation, and unstable artifacts invalidate trusted reproducibility.
Report tool or infrastructure failures separately from scientific results.

## Required data products

```text
submission/README.md
submission/PAPER_AUDIT.md
submission/results/run_summary.json
submission/results/<HFSS-variant>/structure.json
submission/src/                                   # all build/run/postprocess sources
submission/src/derive.py                  # offline response derivation; coverage classes below
submission/src/run_all.py                 # contract entry: python3 src/run_all.py --variant <name>  (full HFSS chain of one variant)
submission/hfss/                                  # <project>.aedt, <design>.structure.json, logs/
submission/views/unit_cell/top.png
submission/views/unit_cell/perspective.png
submission/views/array_ms/top.png
submission/views/array_pec/perspective.png
submission/results/unit_normal/meta.json
submission/results/unit_normal/run.log
submission/results/unit_normal/reflection.csv
submission/results/unit_normal/summary.json
submission/results/unit_tm15/meta.json
submission/results/unit_tm15/run.log
submission/results/unit_tm15/phase_diff.csv
submission/results/unit_tm15/summary.json
submission/results/unit_tm30/meta.json
submission/results/unit_tm30/run.log
submission/results/unit_tm30/phase_diff.csv
submission/results/unit_tm30/summary.json
submission/results/unit_tm45/meta.json
submission/results/unit_tm45/run.log
submission/results/unit_tm45/phase_diff.csv
submission/results/unit_tm45/summary.json
submission/results/af_patterns/meta.json
submission/results/af_patterns/coding_matrices.json
submission/results/af_patterns/af_summary.json
submission/results/af_patterns/af_samples.npz
submission/results/af_patterns/af_pattern_uniform.png
submission/results/af_patterns/af_pattern_initial.png
submission/results/af_patterns/af_pattern_optimal.png
submission/results/array_ms/meta.json
submission/results/array_ms/run.log
submission/results/array_ms/rcs_normal.csv
submission/results/array_ms/rcs_reduction.csv
submission/results/array_ms/summary.json
submission/results/array_ms/current_fig6.png
submission/results/array_ms/farfield3d_fig6.png
submission/results/array_pec/meta.json
submission/results/array_pec/run.log
submission/results/array_pec/rcs_normal.csv
submission/results/array_pec/summary.json
submission/results/array_pec/current_fig6.png
submission/results/array_pec/farfield3d_fig6.png
submission/results/array_ms/raw/                # byte-for-byte AEDT exports
submission/results/array_ms/raw/MANIFEST.json
submission/results/array_pec/raw/                # byte-for-byte AEDT exports
submission/results/array_pec/raw/MANIFEST.json
submission/results/unit_normal/raw/                # byte-for-byte AEDT exports
submission/results/unit_normal/raw/MANIFEST.json
submission/results/unit_tm15/raw/                # byte-for-byte AEDT exports
submission/results/unit_tm15/raw/MANIFEST.json
submission/results/unit_tm30/raw/                # byte-for-byte AEDT exports
submission/results/unit_tm30/raw/MANIFEST.json
submission/results/unit_tm45/raw/                # byte-for-byte AEDT exports
submission/results/unit_tm45/raw/MANIFEST.json
```

`af_patterns` is a numerical variant: it has no `run.log` and its `meta.json` must state `result_source: "numerical array-factor model (Eq. 2)"` plus the script path. All other variants are HFSS variants with full run evidence.

## Output Schemas

Frequency sampling requirements (all frequency-domain CSVs): rows at **exact multiples of 0.05 GHz from 4.00 to 8.00** (81 rows). Provide the specified grid directly rather than relying on interpolation.

Check summary consistency independently of agreement with the paper. Recompute every CSV-derived summary using the definitions below. Agreement tolerances are 0.011 dB/degree/dBsm, 0.0051 GHz and 0.0011 for dimensionless summaries; these are serialization tolerances, not extra paper-target tolerances. Use at least six decimal places for response values and at least three for derived scalars. Frequencies that are grid selections must be grid members; explicitly permitted crossing interpolation is the only exception. For equal extrema choose the lowest frequency, then the first declared column; for a flat local extremum choose the middle grid row, rounding toward the lower index. Report missing or inconsistent summaries explicitly. Distinguish quantities that depend on an affected summary from independent observations supported by intact CSV data. JSON must use null with an allowed status, never NaN or Infinity.

Phase conventions (unit-cell variants): de-embed reflection coefficients to the nominal substrate/patch interface z=h, with z=0 at the ground interface. This is a task reference plane, not a recovered paper reference plane. Record port distance, de-embedding sign, time convention, Floquet mode/polarization and incoming/outgoing field basis. Report individual phases in (-180,180] degrees. Compute the oriented difference from the phase of R_y*conjugate(R_x) (or R_0*conjugate(R_1)) and map modulo 360 into [0,360); boundary wraps are allowed and must not be mistaken for discontinuous physics. Do not use an absolute/unsigned phase difference. Absolute phases and their zero crossings are diagnostic relative to the paper; no empirically fitted common phase offset is allowed. Same-reference phase differences and reflection magnitudes remain reproduction targets.

- `reflection.csv` (`unit_normal`): `frequency_GHz,mag_x,phase_x_deg,mag_y,phase_y_deg,phase_diff_deg` — x/y refer to the incident-E polarization along the paper's x/y axes of Fig. 1a with the patch long side px along x; `phase_diff_deg = phase_y_deg − phase_x_deg` (modulo 360, in [0, 360)).
- `phase_diff.csv` (`unit_tm*`): `frequency_GHz,phase_element1_deg,phase_element0_deg,phase_diff_deg` — element "1"/"0" are the two lattice orientations defined in the paper (Fig. 4); `phase_diff_deg = phase_element0_deg − phase_element1_deg` (modulo 360, in [0, 360)); both phases from the same de-embed plane and the same incidence.
- `summary.json` (`unit_normal`): `min_mag_x`, `min_mag_y` over 4-8 GHz; `f_zero_phase_x_GHz`, `f_zero_phase_y_GHz` as diagnostic zero-phase crossings. Unwrap adjacent complex phases before locating a crossing of an integer multiple of 360 degrees, interpolate linearly, and select the lowest crossing frequency; never count a +180/-180 wrap as a zero crossing. A missing crossing is null with `phase_zero_status_x/y="no_crossing"`; otherwise status is `valid`. Also report `phase_diff_peak_deg`, `f_phase_diff_peak_GHz`, and `phase_diff_band_150deg_GHz`: the maximal contiguous grid component with phase_diff>=150 containing the peak, null if the peak is below150. Do not bridge any failed row. Report `phase_diff_intervals_150deg_GHz` (all qualifying components, [] if none) and `phase_diff_band_status` (`valid`, a truncated_* status, or `no_qualifying_interval`).
- `summary.json` (`unit_tm*`): `incidence_theta_deg`, `phase_diff_peak_deg`, `f_phase_diff_peak_GHz`.
- `coding_matrices.json` (`af_patterns`): `{"optimal": [[...6x6 of 0/1...]], "initial": [[...]], "row_axis": "+x", "col_axis": "+y", "one_means": "<your extracted definition>"}` — the same optimal matrix must drive your `array_ms` model build.
- `af_summary.json` (`af_patterns`): `af_max_uniform`, `af_max_initial`, `af_max_optimal`, `af_at_broadside_uniform`, `af_at_broadside_initial`, `af_at_broadside_optimal`, `evaluation_frequency_GHz`, `grid_step_deg`. Evaluation contract (fixed, see Clarification 3): Eq. (2) with the paper's lattice spacing and M = N = 6, element factor EF ≡ 1, evaluated at 5.8 GHz on a 1° × 1° grid over θ ∈ [0°, 90°], φ ∈ [0°, 360°); AF values reported as linear magnitude |AF| (not dB, not normalized).
- `af_pattern_*.png`: hemispheric |AF| pattern of each matrix on the contract grid (3D lobe plot or θ–φ map; linear scale; state the scale in the plot).
- `rcs_normal.csv` (`array_ms`): `frequency_GHz,rcs_x_dBsm,rcs_y_dBsm`: total monostatic RCS in dBsm for x/y incident E polarization, observing along -k of the normally incident plane wave. The x/y suffix selects the incident polarization, not the received field component. Use the total-RCS convention below for both columns.
- `rcs_normal.csv` (`array_pec`): `frequency_GHz,rcs_dBsm`, using the same total monostatic RCS convention. The normally illuminated square reference is equivalent under x/y exchange; state the incident polarization used in meta.json.
- `rcs_reduction.csv` (`array_ms`): `frequency_GHz,reduction_x_dB,reduction_y_dB` where `reduction = rcs_ms_dBsm − rcs_pec_dBsm` row-by-row from your own two CSVs (negative values = reduction).
- `summary.json` (`array_ms`): `rcs_x_min_dBsm`, `f_rcs_x_min_GHz`, `rcs_y_min_dBsm`, `f_rcs_y_min_GHz`, `reduction_x_min_dB`, `f_reduction_x_min_GHz`, `reduction_y_min_dB`, `f_reduction_y_min_GHz`, `band10dB_envelope_x_GHz`, `band10dB_envelope_y_GHz` (use the explicitly named envelope and interval fields below).
- `summary.json` (`array_pec`): `rcs_dBsm_at_4GHz`, `rcs_dBsm_at_8GHz`.
- `current_fig6.png` / `farfield3d_fig6.png`: exported at the frequency the paper states for Fig. 6, under x-polarized normal incidence, with color scales matching the corresponding paper colorbars (Fig. 6a/b for surface current, Fig. 6e/f for far-field RCS in dBsm); far-field pattern as a 3D bistatic total-RCS lobe plot in dBsm using the same total-RCS definition below.
- `meta.json` (every variant): `aedt_version`, `pyaedt_version`, `solver_type`, `design_type`, `model_units`, `coordinate_system`, `frequency_sweep`, `key_frequency_points`, `boundary_summary`, `excitation_summary`, `setup_names`, `mesh_summary`, `report_export_summary`, `result_source`, `run_timestamp_utc`; unit-cell and array variants additionally: `angle_convention`, `incident_plane`, `polarization_definition`, `floquet_phase_or_scan_settings` (for the array variants describe the plane-wave definition there). For `af_patterns` the HFSS-specific fields may be `null` but `result_source` and the script path are mandatory.
- `structure.json`: `model_units`, `parameters`, `materials`, `named_objects`, `boundaries`, `excitations`, `setups`, `ports`; `named_objects` must allow textual recovery of every required geometric fact (unit-cell dimensions; per-lattice patch orientation of the full array — a compressed per-lattice orientation matrix is acceptable; PEC reference plate).

Plane-wave excitation amplitude for the field-map exports: 1 V/m peak (so the current color scales are comparable with the paper's).

## Calculation records and independent reproducibility

The following requirements define simulation evidence, source preservation, offline derivation, and independent reproduction.

### HFSS execution and native evidence

The HFSS variants for this study are: **`unit_normal`, `unit_tm15`, `unit_tm30`, `unit_tm45`, `array_ms`, `array_pec`**. Every one requires a genuine PyAEDT-controlled HFSS solution, its native project under `hfss/`, `results/<variant>/run.log`, `meta.json`, `structure.json`, and an AEDT export directory `raw/` with `MANIFEST.json`. Numerical variants explicitly listed in the target table are governed by their own numerical contract; they do not require an AEDT project, run.log or raw directory.

`python3 src/run_all.py --variant <name>` must build, solve, export and derive the requested variant (including declared dependencies). `reproduce.sh` remains the no-argument complete entry. Do not replace required HFSS responses with another solver, analytic response curves, digitized paper data, cached runs, fabricated logs or an unsolved project.

Each HFSS run.log must include every name in its meta.json `setup_names` and at least three native evidence categories: (a) adaptive pass/convergence rows; (b) native solve/sweep start and completion; (c) mesh/convergence statistics; (d) export records; (e) AEDT Message Manager/profile messages; (f) project result/profile paths. PyAEDT wrapper INFO/WARNING lines alone do not satisfy category (e). Keep the original messages and export convergence/mesh tables. Wrapper messages can supplement native evidence but cannot replace it.

For driven port models the adaptive target is Max Mag. Delta S <= 0.02. A finite incident-wave scattering model may use HFSS's native relative Delta Energy <= 0.02 instead; record its definition, unit and target. Record the last measured value, pass count, positive tetrahedra count and native converged/not-converged status for each physical solution. A generic successful process exit is not proof of adaptive convergence. Report an unresolved convergence target honestly; documenting a failure does not establish convergence.

One Optimetrics/session log may contain several solved variations and may be copied unchanged into their variant directories. Link each exported result to its actual design, setup, variation, excitation and `solve_id`. When sharing a log, identify the Optimetrics/shared session in meta.result_source and include a literal `variation` object in each meta.json with its actual geometry parameters, angle and polarization/excitation selection; detailed log records may be referenced elsewhere. A shared log hash, equal pass counts or similar curves alone do not prove copying. Conversely, a declaration of sharing does not make different geometries or scan angles the same physical solution. Each required geometry/angle/orientation must really be solved; same-solution polarization extraction is allowed only where the study explicitly permits it.

### Static documentation and current-run records

Keep README static: method, commands, variant/dependency map, artifact index, modeling choices, known limitations, and a pointer to `results/run_summary.json`. Do not rewrite it during replay. Historical measurements may be included if labeled with their run/date; they need not equal a new run's adaptive history.

Generate `results/run_summary.json` with this schema:

- `schema_version`: integer 1.
- `variants`: object keyed by all required variant names. Each value contains `status` (`solved`, `partial`, `failed`, or `numerical`), `solve_ids` (array of keys into `solves`; empty only for numerical/failed variants), and `reason` (string or null).
- `solves`: object keyed by unique physical `solve_id`. Each value contains `project`, `design`, `setup`, `variation` (object, including geometry/angle/orientation values), `excitations` (array), `convergence` (object with `criterion`, `target`, `last_value`, `passes`, `converged`), `tetrahedra`, and `log_refs` (array of objects with submission-relative `path` and 1-based inclusive `lines`). Failed attempts may have null measured values and must state the cause. Shared physical solves are recorded once and referenced by every beneficiary; a variant requiring two orientations references both solves.

Record solver and PyAEDT versions, UTC run time, sweep and key field frequencies in meta.json. `mesh_summary` includes a numeric `tetrahedra` count and, if needed, per-solve records. `result_source` identifies the solve(s), variation(s), excitation(s), raw exports and any postprocessing; it may be a string plus structured fields or one structured object. `report_export_summary` may reference the raw MANIFEST instead of repeating it. Mode/polarization mappings may live once in `fundamental_trace_map` and be referenced by other fields. A structured reference has the form `{"$ref": "results/<variant>/meta.json#/fundamental_trace_map"}`; paths are relative to the submission root, JSON pointers use RFC 6901, and references must resolve without cycles inside the submission. Descriptive/provenance entries may refer to the single authoritative record; duplicate prose is not required. For HFSS variants, typed fields keep their declared types: setup_names is a literal nonempty array of strings, mesh_summary is an object with its numeric count, and result_source explicitly names HFSS/AEDT plus the solve identity before referring to detailed records. A reference is not a substitute for these machine-read fields. The explicitly numerical AF variant retains its stated HFSS-field null exception.

Place an explicit readable `results/<variant>/structure.json` for every HFSS variant, in addition to any native engineering snapshot under hfss/. It has the structural fields listed above and records the actual modeled objects and variation. A compact shared parameter table is allowed, but each file must describe enough of that variant to reconstruct it independently. Give each paper dimension a symbol, value/unit, geometric role, paper location and source-code use; equivalent algebra or shared constants are acceptable if the intended geometry is actually constructed. Merely listing a parameter without using it is not enough. Dimension labels and their physical meaning take precedence over sketch pixel proportions.

### Raw exports and offline derivation

Preserve AEDT-written files byte-for-byte in raw/. Relocating/renaming a file is allowed if its bytes are unchanged and MANIFEST records the original export name. Reformatting, changing columns/units, filtering or interpolation creates a derived file outside raw/.

Each `raw/MANIFEST.json` contains `variant`, `exports` and `derived`. Each export records `file` (relative to raw/), `sha256`, `bytes`, `producer`, `aedt_solution`, `run_log_lines` (inclusive 1-based `[start,end]`), and `exported_utc`; record design/variation/excitation in it or link to meta.json. Each derived entry records `file` (also relative to raw/, normally `../response.csv`), `from` (inputs relative to raw/, including `../` within the submission), and `by` (`derive.py:function`). Cross-variant dependencies such as an RCS reference are explicit. Static metadata, source files and nominal inputs may be additional dependencies, but every HFSS response must also have a native response-data ancestor. The manifest records provenance, not permission to substitute one solution for another.

`python3 src/derive.py --results /home/submission/results [--check]` uses only the standard library, NumPy and SciPy, without importing HFSS/AEDT or accessing the network. `--check` recomputes and compares required numerical responses/summaries; it exits 0 only if all covered items agree, otherwise 1 with a per-item diff. For linear quantities use `abs(a-b) <= atol + rtol*max(abs(a),abs(b))`, with `(atol, rtol)=(1e-9,1e-6)` for direct exports and `(1e-6,1e-3)` for derived quantities. For dB/degree outputs use absolute tolerances 1e-5 (direct) or 1e-3 (derived); phase differences use circular distance. Grid coordinates use absolute tolerance 1e-8 GHz. These checks do not add slack to paper-target windows. For each CSV-derived summary field, report a value consistent with independent recomputation from the CSV. Compare the recomputed value with the paper target; an inconsistent summary must be corrected in the analysis, not silently rewritten during independent reproduction. Grid-selected summary frequencies must match their actual grid rows within 1e-8 GHz; the general summary tolerance does not permit off-grid frequencies.

The coverage classes are:

- HFSS response arrays, metrics and summaries: recompute from native data. Complex-to-magnitude/dB/phase conversion, declared normalization, integration and interpolation are legitimate transformations; check their mathematics, not identical strings. Probe at least five response samples across variants/frequencies; frequency/angle coordinates alone do not count.
- Native images: preserve an original in raw/ and verify the byte hash; direct copying is allowed. For a re-rendered plot, check its data, plotting source and labels. Offline --check need not render PNGs or import a graphics package. Geometry views under views/ are verified with the native model/source and are not numerical derive outputs. Keep result PNGs at their listed Required data products paths, including current maps under views/ where specified; record their provenance/hashes in the manifest or numerical metadata.
- meta.json, structure.json, MANIFEST, README, PAPER_AUDIT, input matrices and nominal design frequencies: check their stated source, structure and agreement with the model; they are not response data that must be derived from raw. Current convergence records are checked against native logs, not paper curves.
- Explicit numerical models: recompute from their permitted static inputs and formula, record input/source hashes, and never label the result as HFSS data.

### Native provenance and paper audit

For every reported HFSS result, retain its native-export ancestry, byte hashes,
solved-variation and quantity mapping, and the source code that transforms the
exports into the reported arrays. Document integration, extrema, and other
data-reduction algorithms so that they can be independently checked. Numerical
AF results must follow the specified equation and use the declared array grid.
Keep the offline derivation checks reproducible from the actual raw exports;
an exit code alone does not establish scientific correctness. Distinguish missing
scientific evidence from tool, extraction, or infrastructure failures.

Submit `PAPER_AUDIT.md` with at least three checked paper locations spanning
geometry/materials, result claims, and equations/conventions. For each location,
quote the relevant text or identify the figure feature, explain the check and
its evidence, classify it as consistent, ambiguous, or apparently contradictory,
and document your modeling decision and affected outputs. There is no required
number of contradictions. Identify disclosed task clarifications as such and
avoid unsupported claims. Do not confuse resonance frequency with band edge,
whole-view rotation with internal geometry rotation, or missing plotting
metadata with proof of physical inconsistency.

### Budget accounting

Development is limited to 20 full HFSS solves. The two finite-array scattering models dominate the expected work; retain convergence retries within this development budget. Reserve and execute one additional complete end-to-end reproduction run through reproduce.sh; that run and independently maintained replay are not charged to the development count. The 72-hour development allowance and the separate complete-calculation and review limits are listed under Computing resources and independent reproduction; actual environment timeouts remain those of the supplied runner. Count a new adaptive physical solution for a distinct geometry/scan/orientation or a recomputed attempt as a solve, including failed attempts that entered Analyze. Exporting another report, exciting another solved port in postprocessing, or deriving another metric is not a new adaptive solve. For a session budget, record both the session count and its physical variations. Log actual runtime and resource use; the stated limits are not an empirical runtime guarantee.

## Workspace and provided materials

Your workspace is `/home`. The following files are preloaded in the container:

- `/home/paper/paper.md` - paper text in Markdown, including figure references
- `/home/paper/paper.pdf` - original-layout PDF fallback
- `/home/paper/paper_image/` - extracted paper figures
- `/home/paper/addendum.md` - study-specific reproduction protocol and data formats; read this first
- `/home/paper/tools/` - read-only submission-format checker and its schema
- `/home/paper/blacklist.md` - external-resource restrictions
- `/home/starter_submission/` - editable starter pipeline

At container startup, the starter pipeline is copied into `/home/submission/`
without overwriting existing files. All final deliverables must remain under
`/home/submission/`.

This study uses source-only clean reproduction. During verification,
old generated artifacts are removed and the reproduction process runs:

```bash
bash /home/submission/reproduce.sh
```

under an unprivileged account without external service credentials. Only artifacts generated
by that replay establish the reported results.

## Required deliverables

The initial submission contains:

- `/home/submission/reproduce.sh`
- `/home/submission/README.md`
- `/home/submission/src/run_all.py`
- `/home/submission/src/derive.py`

Modify or replace the starter as needed. The final submission must include an
executable, no-argument `reproduce.sh`, all source and editable configuration
needed for replay, and every artifact required by `addendum.md`.

`results/`, `hfss/`, `views/`, `calibration.md`, and `calibration_log.csv` are
generated outputs. They are removed before clean replay and must be regenerated
by `reproduce.sh`. Keep indispensable editable inputs under `src/` or another
non-generated top-level path.

Typical outputs include:

- `submission/src/` modeling, solve-control, export, and postprocessing code
- `submission/hfss/` native `.aedt` projects and project result artifacts
- `submission/results/<variant>/` CSV, JSON, NPZ, metadata, and native run logs
- `submission/views/<variant>/` geometry, field, current, or radiation images
- `submission/README.md` with variants, commands, artifact index, and limitations

The exact variants, filenames, schemas, units, grids, and required views are
specified by `/home/paper/addendum.md`.

## Simulation requirements

Use Ansys AEDT/HFSS through
`ansys.aedt.core` and run genuine three-dimensional driven HFSS solves: periodic/Floquet unit-cell models and finite-array scattering models. Use non-graphical mode where
possible and record the project, setup names, mesh/adaptive convergence, solver
messages, and exported report provenance.

All electromagnetic response evidence must come from the replayed HFSS model.
The explicitly listed `af_patterns` variant is a numerical Eq. (2) calculation
and follows the addendum's numerical-evidence exception:

- construct explicit geometry, materials, boundaries, ports, setups, sweeps,
  mesh controls, and units;
- execute the required solved variants and export native solver evidence;
- derive CSV/JSON/NPZ metrics and figures from exported HFSS results;
- preserve native logs containing every declared setup name and recognizable
  solve, convergence, and mesh evidence.

Do not substitute CST, COMSOL, FEKO, Meep, openEMS, Tidy3D, analytic curves,
hand-digitized paper values, cached historical results, fabricated logs, or a
project that was never solved.

## Portable source package

The clean-replay container is a fresh copy of the same image you are already working in, and it
provides the task's interpreter, required scientific software, and supplied materials
under `/home/paper`. Do not reinstall or vendor any of it into your submission.

- `/home/submission` must not contain a symbolic link at any depth, and must not contain any other
  non-regular filesystem object (FIFO, socket, device node). The reproduction process builds a *source-only*
  replay snapshot from your submission and rejects it with `exit 126` if it finds one:
  `reproduce.sh` never runs, dependent artifacts lack a valid clean-replay provenance chain, and
  this happens even when all required outputs are already present. Sanitizing a later copy does
  not erase or excuse the violation.
- Do not copy or package a runtime environment into the submission: no conda/mamba environment,
  virtualenv, `site-packages`, toolchain tarball, `/opt` or `/usr` tree, or interpreter copy.
  Call the preinstalled tools from `reproduce.sh` instead.
- Keep the submission source-only: code, configs, static inputs, and the required
  `reproduce.sh` / `README.md`. Generated output directories are deleted before replay and must
  be regenerated by `reproduce.sh`.
- `reproduce.sh` must not modify the submission's own source or documentation files. The reproduction process
  hashes the frozen source tree before and after replay and stops reproduction with `exit 125` if any
  file under it changed. Write only into the declared generated output directories, or into `/tmp`.
- Before you finish, run both checks and require empty output:

  ```bash
  find /home/submission -type l -print
  find /home/submission -mindepth 1 ! -type f ! -type d -print
  ```

  If either command prints entries, remove them (replace a bundled environment with a call to the
  preinstalled tools) and re-run the checks before submitting.

## Filesystem checks

Before submission, run `python3 /usr/local/bin/pbx-submission-check check`. This checks filesystem safety only; it does not replace a clean replay. Keep `README.md` and editable inputs unchanged during replay. Write runtime reports under `results/`, not back into `README.md`; keep templates under `src/`. Write Python/plotting caches under `/tmp`. Review or infrastructure failures are reported separately from analysis failures and scientific conclusions.

The addendum distinguishes static README documentation from current
`results/run_summary.json`, requires explicit per-variant structural snapshots
under results/, and defines reference/metric conventions. Read those definitions
before modeling. The reproduction and submission packaging procedures above
remain the reproduction entry point.

## Quantitative comparison requirements

The following result requirements apply in addition to the native-execution, model, normalization and convergence requirements. They retain the study's comparison ranges; they are not a claim that every ambiguous paper/model correspondence has already been resolved. Report discrepancies honestly. An unresolved correspondence requires independent scientific review, not relaxed thresholds, altered geometry or an automatic agreement claim.

- **PEC reference RCS anchors and monotonic rise**: The native total-RCS metallic reference must be in [7.3,10.3] dBsm at 4.00 GHz, [13.4,16.5] at 8.00 GHz, and [10.7,13.7] at 5.85 GHz. Across 4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0 GHz, each decrease must be no greater than 0.3 dB. Reported endpoint summaries must agree with the native-derived CSV within 0.011 dB.
- **Metasurface x-polarization primary dip**: Require the x-polarized metasurface total-RCS minimum in [-8.1,-2.1] dBsm at a frequency in [5.58,6.08] GHz. The nearest native-derived CSV sample must agree with the reported minimum within 0.3 dB.
- **x-polarization double-dip morphology**: Require x-polarized RCS at 6.20 GHz in [0.0,6.0] dBsm, and the smaller RCS at 6.45/6.50 GHz in [-2.7,3.3] dBsm. The 6.20-GHz value must exceed that second-dip value by at least 1.0 dB.
- **Metasurface y-polarization dip and x-y asymmetry**: Require the y-polarized total-RCS minimum in [-4.9,1.2] dBsm at a frequency in [5.69,6.19] GHz. The x minimum must be at least 1.3 dB below the y minimum, using the fixed physical polarization labels.
- **Outer envelope of -10 dB samples**: From actual RCS-reduction samples <=-10 dB, require the first/last x frequencies in [5.00,5.40]/[6.66,7.06] GHz and the first/last y frequencies in [5.24,5.64]/[6.70,7.10] GHz. These are outer-envelope endpoints, not proof of a connected bandwidth. An empty qualifying set does not satisfy the endpoint requirements.
- **Near-10 dB suppression inside the band**: On the complete 0.05-GHz grid require every x sample in [5.40,6.65] GHz and every y sample in [5.65,6.70] GHz to have reduction <=-9 dB; at least 80% of each window must have reduction <=-10 dB. Two isolated qualifying endpoints are insufficient. Separately report strict connected <=-10-dB intervals.
- **Peak RCS-reduction depths (Fig. 10a simulated)**: Require the x reduction minimum in [-20.3,-14.3] dB at a frequency in [5.60,6.10] GHz, and the y minimum in [-17.2,-11.2] dB. The nearest native-derived x sample must agree with the reported minimum within 0.3 dB. Both scattered-power spectra must use the same total-RCS normalization.
- **Surface-current maps visual (Fig. 6a/b)**: Require native surface-current maps at the specified Figure 6 conditions. The metasurface must show nonuniform strong/weak 40-mm coding-lattice blocks; the metallic reference must show the reported low-amplitude, non-blocked pattern. Retain the paper comparison color range and underlying native values. Missing maps or contradictory morphology do not establish reproduction; do not rescale independently to fabricate agreement.
- **3D far-field scattering patterns visual (Fig. 6e/f)**: Require native three-dimensional scattered-power patterns at the specified Figure 6 conditions. The metallic reference must have a dominant normal pencil beam; the metasurface must redistribute scattering into multiple comparable lobes without that dominant beam and with a lower peak. Use the specified common dBsm scale and native total-RCS definition. Missing patterns or contradictory morphology do not establish reproduction.


## Computing resources and independent reproduction

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 259,200 seconds (72 hours) |
| Complete native calculation from source | 259,200 seconds (72 hours) |
| Entire reproduction and independent review | 262,800 seconds (73 hours) |
| CPU allocation | 32 CPUs |
| RAM | 128 GiB |

The native-run limit covers the complete no-argument calculation, including all
required reference runs, controls, convergence studies and generated reports.
Setup, source-integrity checks and independent review use the remaining overall
interval; that reserve is not additional simulation time. No network access is
available during independent reproduction. Preserve partial native output and
identify unfinished work rather than reducing fidelity or omitting controls.



## Licensed HFSS environment

This task is a source/research kit, not a grant of ANSYS use or redistribution
rights. No commercial solver license, license-server access or image clearance
is conveyed. Obtain the solver and an authorized license through the owner or
vendor under applicable terms before execution.

The supplied `environment/docker-compose.yaml` requires an authorized,
operator-provided `HFSS_BASE_IMAGE` reference and `ANSYSLMD_LICENSE_FILE` for the
operator's own reachable license server. No original hostname, MAC address or
license identity is supplied. An authorized operator must confirm the permitted
runtime and network settings for their own license and record the actual
runtime identity privately, without putting credentials in outputs. These
deployment settings do not change the scientific model or acceptance rules.

The Dockerfile expects the ANSYS v251 installation and its Python runtime,
including the specified PyAEDT package. A pinned base image or an image
identifier alone does not prove a portable clean build, correct license
access, or permission to redistribute an image. Some dependency layers are
not exactly pinned. Candidate/public images require an independently cleared
clean source-boundary build; pre-existing runtime images may contain
private source or evidence. Do not distribute them based on an ID lock.

Before an authorized run, confirm installation/interpreter/library versions,
license availability and permitted resource/network configuration; bind the
actual source and image hashes. Use the Budget accounting and Computing resources and independent reproduction
sections of this document. Their empirical sufficiency and cross-machine portability
have not been measured for this source kit. Confirm these operating
conditions before execution; this note does not authorize extra compute or
server access.
Retain native evidence for candidate-generated results and distinguish
infrastructure failure from a negative scientific observation.
