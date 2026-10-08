# Two-passband transmission and angular response of a frequency-selective surface: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

The complete article is available locally as `/home/paper/paper.md` and `/home/paper/paper.pdf`, with figures in `/home/paper/paper_image/`. Use these files to inspect the paper; no article download is needed.

- [Scientific measurements](#scientific-measurements)
- [Scope](#scope)
- [Clarifications](#clarifications)
- [Summary Status and Physical Conventions](#summary-status-and-physical-conventions)
- [Completion policy](#completion-policy)
- [Comparison and numerical integrity](#comparison-and-numerical-integrity)
- [Table 2 is a center-frequency loss table](#table-2-is-a-center-frequency-loss-table)
- [Azimuth and model-condition boundary](#azimuth-and-model-condition-boundary)
- [Measurement validity and comparison scope](#measurement-validity-and-comparison-scope)
- [Method and evidence requirements](#method-and-evidence-requirements)
- [Data formats and preparation checks](#data-formats-and-preparation-checks)
- [Required data products](#required-data-products)
- [Output Schemas](#output-schemas)
- [Calculation records and independent reproducibility](#calculation-records-and-independent-reproducibility)
- [Workspace and provided materials](#workspace-and-provided-materials)
- [Required deliverables](#required-deliverables)
- [Simulation requirements](#simulation-requirements)
- [Portable source package](#portable-source-package)
- [Filesystem checks](#filesystem-checks)
- [Computing resources and independent reproduction](#computing-resources-and-independent-reproduction)
- [Licensed HFSS environment](#licensed-hfss-environment)

Read the paper for the geometry, materials, physical results and figure context. This addendum specifies the reproduction scope, missing conventions, output schemas and reproduction requirements. Its explicit task conventions take precedence for this model and must not be presented as facts recovered from the paper. Figure numbers refer to paper captions, not converted image filenames.

## Scientific measurements

Reproduce and compare the paper's **HFSS full-wave simulation** results (not the ECM curves, not the measurements) for the following targets. Figure numbers are paper figure numbers (match them via the captions, not via `figure-NNN` file names).

| # | Target paper figures/tables | Selection | Metrics | Variant name(s) |
|---|---|---|---|---|
| T1 | Fig. 8 [HFSS curves only] and Fig. 9 [all four curves] | Normal incidence, final unit of Fig. 2(c)/Fig. 6/Table 1 | S11(f), S21(f), 3–16.5 GHz; TE/TM coincidence at 0° | `te_00`, `tm_00` |
| T2 | Fig. 10 [all curves] + Table 2 TE column (all four angle rows) + Sec. 3.2 text bandwidth statements for TE at 0° | TE polarization at the paper's labeled angles | S21(f) and S11(f) per angle; insertion loss at both passband centers; −3 dB band edges; transmission zeros | `te_00`, `te_30`, `te_60`, `te_86` |
| T3 | Fig. 11 [all curves] + Table 2 TM column (all four angle rows) + Sec. 3.2 text bandwidth statements for TM at 0° and 83° | TM polarization at the paper's labeled angles | same as T2 | `tm_00`, `tm_30`, `tm_60`, `tm_83` |
| T4 | Fig. 12(a)(b) surface current and Fig. 13(a)(b) electric field | Normal incidence, at the paper's two passband center frequencies | field-distribution plots (hotspot locations) | field images under `te_00` (see Required data products) |

Total: 8 variants = {TE, TM} × the angle sets labeled in Figs. 10/11 and Table 2 (θ = 0°/30°/60° plus the paper's stated polarization-specific maximum angles encoded in the variant names). Note that θ = 30° appears in Table 2 only (no curve figure); it is still a required simulation.

## Scope

- Included: everything in the table above, HFSS simulation only.
- Excluded: the ECM curves of Figs. 7/8 and the ECM element values (no circuit-model reproduction is required or accepted as a result source); the design-evolution Stages 1 and 2 (Figs. 2(a)(b), 3, 4 — their exact dimensions are not individually given by the paper); all measured results (Figs. 14–16, the prototype array, Table 3); Fig. 5 is the same final-unit S21 data as Figs. 10/11 and needs no separate deliverable.

## Clarifications

1. **Plane of incidence and TE/TM convention (task convention; the paper defines θ from the surface normal but does not state the azimuth, and its TM wave-impedance formula in Sec. 3.2 is written non-standardly):** let the two lattice vectors of the square cell be x and y and the surface normal be z. For all oblique variants, the plane of incidence is the x–z plane (azimuth φ = 0°, along a lattice axis). TE = E-field perpendicular to the plane of incidence (E along y); TM = E-field in the plane of incidence. θ is measured from the +z normal. Record these in the four angle/polarization fields of `meta.json`. Nonzero-angle performance is characterized under this fixed plane; it is not asserted to reproduce an unreported paper azimuth.
2. Copper cladding thickness is given by the paper only as a range; choose a value within the paper's stated range (or an equivalent finite-conductivity sheet representation) and state your choice and its rationale in README/meta.json.
3. Exploration parameters: **none**. All unit-cell dimensions and material constants required for the reproduction are given by the paper; they must be used as given.
4. A single parametric/Optimetrics session sweeping the scan angle is acceptable, and one Floquet solve at a given θ may legitimately supply both the TE and the TM variant of that θ; every such shared/derived result must be declared in `meta.json` `result_source` under the HFSS execution and native evidence contract below. Copying results between different θ values is fabrication.
5. Fig. 12/13 field plots are at normal incidence; export your plots from the 0° solve (declare in `result_source` of `te_00`).

## Summary Status and Physical Conventions

`summary.json` additionally contains `metric_status` with keys `band1`, `band2`, `S11_min_p1`, `S11_min_p2`, `tz2`:

- Bands: `valid`, `truncated_low`, `truncated_high`, `truncated_both`, `no_passband`, or `solve_failed`. A truncated band is an observed grid interval and a lower bound on complete bandwidth, not a measured crossing outside the sweep.
- S11 minima: `valid` if the corresponding band exists (including truncated bands); otherwise paired frequency/value fields are null with `no_passband` or `solve_failed`. Take the lowest-frequency minimum within that same connected band.
- tz2: `valid`, `not_applicable`, `no_passband`, `no_search_interval`, or `solve_failed`, as defined above. A prescribed not_applicable null does not indicate solver failure.

Peak locations and the fixed-window inter-band zero remain defined for any complete finite S-parameter curve, even if no -3dB band exists. `f0_p1_GHz` and `f0_p2_GHz` are static paper inputs and remain defined if a solve fails. Failures must be identified in results/run_summary.json; do not fill response arrays with guessed values. A correctly reported no_passband documents the absence of a measured passband; it does not establish reproduction of the paper's passband.

The fixed peak windows use the paper's separated design bands and the Fig.5 second-band inset; 13.60 GHz lies before the earliest first-order air-side grating onset for this P=11 mm task at the largest scan angle (approximately c/[P*(1+sin86deg)] = 13.64 GHz). This prevents a ~15GHz secondary lobe from being selected as the main second band. The search convention does not prove grating modes are absent at higher frequencies. Export enough Floquet modes for a converged physical solution and record their order/polarization; the reported CSV is still the co-polarized specular coefficient. For power-normalized coefficients the necessary bound is |S11|^2+|S21|^2<=1.005. Missing cross/higher-order power and material loss can make this subset smaller than1; do not force equality or infer absorption from the subset.

For oblique incidence identify the physical propagation vector, top incident side, TE/TM E-vector and the code's Floquet scan/phase convention. Theta denotes the incidence angle relative to the surface normal (0 is normal incidence), and the transverse propagation lies on the x lattice axis. Incidence is in the x-z plane: TE E along y, TM E in x-z with E dot k=0. A sign convention or reversed transverse direction is acceptable only with the corresponding basis/periodic-phase mapping recorded; an internally inconsistent scan/phase setting is not.

Use the Table1/Fig.6 nominal aperture dimensions, including R5=6.0 mm and W4=0.4 mm, and evaluate coordinates such as R5/sqrt(2) at sufficient precision. The inward cross-arm endpoint touches the outer circular slot at R5-L1/2=R1. Do not silently create a finite gap/overlap by changing a radius or arm width to make the mesher succeed. Preserve the specified geometry in exact/parametric form and report the kernel tolerance, meshing treatment and any unresolved contact failure. A global perspective rotation of Fig.1 does not imply a different cross-arm orientation relative to the lattice; use the dimensioned top view.

The exact TE86 first-band width is diagnostic: retain true solved curves and report the measured width and angular narrowing, without using a new uncalibrated numerical width window. All detailed observations remain in scope, including TE86 fixed-frequency transmission and both measured peaks. Characterize nonzero-angle performance under the retained nominal geometry and explicit phi=0 convention, distinguishing it from the paper's unspecified azimuth.

## Completion policy

Completion requires a successful no-argument clean replay producing the full
addendum-required HFSS projects, native solve evidence, numerical artifacts,
views, logs, and provenance. Before finishing, run `reproduce.sh` from a clean
generated-output state and verify that all required files exist. A smoke test or
unsolved project is not a completed submission.

## Comparison and numerical integrity

Compare both transmission passbands across all eight TE/TM angle cases. Report connected band edges, peak frequencies, peak insertion losses and the changes from normal incidence, alongside the full transmission and reflection spectra. Distinguish a missing or truncated passband from an uncomputed spectrum.

Use the paper's simulated curves only under the stated matching conditions; do not tune geometry or replace computed data with digitized curves. Keep nominal dimensions exact in the construction. A geometry readback tolerance of 0.05 mm accommodates numerical extraction, not a change to the design. Quantify mesh and sweep sensitivity, preserve unrounded native exports, and keep summaries consistent with their underlying arrays. Check finite responses, passivity and the applicable reciprocity relations. The output grids, units, reference planes, polarization conventions and control experiments in this protocol and `addendum.md` remain required.

## Table 2 is a center-frequency loss table

Sec. 3.2 / Table 2 labels its two loss columns as insertion loss of the
center frequency in each passband. Retain its TE/TM observations at angles
0, 30, 60 and 86/83 degrees: first-band losses 0.36/0.24, 0.12/0.23,
0.71/0.08, 0.76/0.52 dB; second-band losses 0.98/0.98, 0.84/0.59,
0.30/0.10, 0.70/0.99 dB. Positive insertion loss is minus S21 in dB.

The abstract and normal-incidence discussion give design centers 8.45 and
12.76 GHz. Retain those nominal values and their directly sampled S21 values
as diagnostics. They are not automatically the measured centers of every
angular response. Use the existing per-band peak frequency/S21 fields for
center-loss comparisons and report frequency offsets separately. Do not
rename a fixed-frequency sample as a peak, fit an amplitude correction or
interpolate a favorable maximum. Existing connected-band/null/truncation
definitions and complete spectra remain required.

## Azimuth and model-condition boundary

The paper defines theta relative to the surface normal; Figs. 10/11 label
TE/TM and theta. The supplied diagram/text does not establish an azimuth
relative to the dimensioned lattice sufficient to equate it to phi=0.
Keep the task's x-z/phi=0 plane, signed propagation/polarization mapping,
Table 1 dimensions, nominal aperture contacts and declared metal treatment.
Do not rotate the lattice or alter geometry to obtain a desired spectrum.

Retain the angular insertion-loss, passband-width, transmission-zero and trend comparisons below. The unresolved paper azimuth must be disclosed and independently checked; it is not permission to waive a performance condition. Correct the location of Table 2 comparisons to each measured passband center while keeping fixed-frequency samples as separate diagnostics. A missing passband or nonmatching angular response must remain an unmet result, not a successful reproduction.

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
4. Implement src/run_all.py --variant <name> and no-argument reproduce.sh,
   including all postprocessing needed to produce the required outputs.
   No separate self-check script or --check interface is required. The trusted
   verifier independently checks replayed native exports, responses and summaries.
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

All specified formats, source restrictions, controls and computing limits remain requirements of the complete calculation.

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
submission/src/                          # all build/run/postprocess sources
submission/src/derive.py                  # offline response derivation; coverage classes below
submission/src/run_all.py                 # contract entry: python3 src/run_all.py --variant <name>  (full HFSS chain of one variant)
submission/hfss/                         # <project>.aedt, <design>.structure.json, logs/
submission/views/unit_cell/top.png       # top view of the patterned metal face, cell edges axis-aligned
submission/views/unit_cell/oblique_3d.png
submission/results/<variant>/meta.json
submission/results/<variant>/run.log
submission/results/<variant>/sparams.csv
submission/results/<variant>/summary.json
submission/results/te_00/fields/jsurf_8p45GHz.png
submission/results/te_00/fields/jsurf_12p76GHz.png
submission/results/te_00/fields/efield_8p45GHz.png
submission/results/te_00/fields/efield_12p76GHz.png
submission/results/te_00/raw/                # byte-for-byte AEDT exports
submission/results/te_00/raw/MANIFEST.json
submission/results/te_30/raw/                # byte-for-byte AEDT exports
submission/results/te_30/raw/MANIFEST.json
submission/results/te_60/raw/                # byte-for-byte AEDT exports
submission/results/te_60/raw/MANIFEST.json
submission/results/te_86/raw/                # byte-for-byte AEDT exports
submission/results/te_86/raw/MANIFEST.json
submission/results/tm_00/raw/                # byte-for-byte AEDT exports
submission/results/tm_00/raw/MANIFEST.json
submission/results/tm_30/raw/                # byte-for-byte AEDT exports
submission/results/tm_30/raw/MANIFEST.json
submission/results/tm_60/raw/                # byte-for-byte AEDT exports
submission/results/tm_60/raw/MANIFEST.json
submission/results/tm_83/raw/                # byte-for-byte AEDT exports
submission/results/tm_83/raw/MANIFEST.json
```

where `<variant>` ∈ { te_00, te_30, te_60, te_86, tm_00, tm_30, tm_60, tm_83 } (all 8 required).

## Output Schemas

Frequency sampling requirements (applies to every `sparams.csv`): rows at **exactly 0.01 GHz steps from 3.00 to 16.50 GHz inclusive (1351 rows)**, `frequency_GHz` preferably written with two decimals (equivalent numerical spellings are accepted). The two nominal design centers fall on this grid; report their directly sampled values as fixed-frequency diagnostics. Table 2 center-loss comparisons use the separately measured per-band peak values, not an assumption that every angular center is fixed at 8.45/12.76 GHz.

Check summary consistency independently of agreement with the paper. Recompute every CSV-derived summary using the definitions below. Agreement tolerances are 0.011 dB/degree/dBsm, 0.0051 GHz and 0.0011 for dimensionless summaries; these are serialization tolerances, not extra paper-target tolerances. Use at least six decimal places for response values and at least three for derived scalars. Frequencies that are grid selections must be grid members; explicitly permitted crossing interpolation is the only exception. For equal extrema choose the lowest frequency, then the first declared column; for a flat local extremum choose the middle grid row, rounding toward the lower index. Report missing or inconsistent summaries explicitly. Distinguish quantities that depend on an affected summary from independent observations supported by intact CSV data. JSON must use null with an allowed status, never NaN or Infinity.

- `sparams.csv`: `frequency_GHz,S11_dB,S21_dB` — magnitude in dB of the specular (fundamental Floquet mode) reflection and transmission coefficients for this variant's polarization and scan angle, from this study's HFSS solves.
- `summary.json` (per variant; every value must be derived from that variant's own `sparams.csv` by the following non-circular chain; retain enough data to verify consistency):
  - `f0_p1_GHz`, `f0_p2_GHz`: the paper's two design passband center frequencies (extract from the paper).
  - `S21_at_f0_p1_dB`, `S21_at_f0_p2_dB`: CSV values at those rows.
  - `f_tz_GHz`, `S21_tz_dB`: frequency and value of the minimum S21 within the fixed inter-band search window [9.50, 11.50] GHz.
  - `f_peak_p1_GHz`, `S21_peak_p1_dB`: maximum S21 inside the fixed peak-search window [3.00,9.50] GHz; `f_peak_p2_GHz`, `S21_peak_p2_dB`: maximum inside [11.50,13.60] GHz. Equal maxima choose the lowest frequency. These windows identify the first two design passbands without allowing the high-frequency secondary lobe to replace band2; they are task conventions, not claimed exact paper band edges. The complete band can extend outside its peak-search window.
  - `band1_3dB_GHz`, `band2_3dB_GHz`: maximal consecutive grid component with S21>=-3 dB containing its selected peak. Walk left and right across the full sweep until the first failed row; do not stop at the peak-search window and do not join disconnected components. Included rows define [lo,hi]. If a component reaches 3.00/16.50, record that grid endpoint and a truncated status. A peak below -3 dB gives null and `no_passband`; a single qualifying row has [f,f] and width0.
  - `f_S11_min_p1_GHz`, `S11_min_p1_dB`, `f_S11_min_p2_GHz`, `S11_min_p2_dB`: location and value of the minimum S11 inside `band1_3dB_GHz` / `band2_3dB_GHz`.
  - `f_tz2_GHz`, `S21_tz2_dB`: for te_86 only, the minimum on grid rows strictly above the band2 upper edge through16.50 GHz. Null with `no_passband` if band2 is null, or `no_search_interval` if no row remains. For all other variants both are null with `not_applicable`, which requires no repeated README explanation. Use the lowest frequency for equal minima.
- `meta.json` (per variant): `aedt_version`, `pyaedt_version`, `solver_type`, `design_type`, `model_units`, `coordinate_system`, `frequency_sweep`, `key_frequency_points`, `boundary_summary`, `excitation_summary`, `setup_names`, `mesh_summary`, `report_export_summary`, `result_source`, `run_timestamp_utc`, plus `angle_convention`, `incident_plane`, `polarization_definition`, `floquet_phase_or_scan_settings` (this variant's scan setting). `result_source` must declare any shared/derived solve relationship under the HFSS execution and native evidence contract below.
- `structure.json`: `model_units`, `parameters`, `materials`, `named_objects`, `boundaries`, `excitations`, `setups`, `ports`; `named_objects` must allow textual recovery of every required geometric fact of the unit cell.
- Field images (`te_00/fields/`): surface-current-magnitude and E-field-magnitude plots on the patterned metal face of the unit cell at the two passband center frequencies, exported from this study's HFSS solution (colormap/scale free; the file names encode the frequencies).

## Calculation records and independent reproducibility

The following requirements define simulation evidence, source preservation, offline derivation, and independent reproduction.

### HFSS execution and native evidence

The HFSS variants for this study are: **`te_00`, `te_30`, `te_60`, `te_86`, `tm_00`, `tm_30`, `tm_60`, `tm_83`**. Every one requires a genuine PyAEDT-controlled HFSS solution, its native project under `hfss/`, `results/<variant>/run.log`, `meta.json`, `structure.json`, and an AEDT export directory `raw/` with `MANIFEST.json`. Numerical variants explicitly listed in the target table are governed by their own numerical contract; they do not require an AEDT project, run.log or raw directory.

`python3 src/run_all.py --variant <name>` must build, solve, export and derive the requested variant (including declared dependencies). `reproduce.sh` remains the no-argument complete entry. Do not replace required HFSS responses with another solver, analytic response curves, digitized paper data, cached runs, fabricated logs or an unsolved project.

For each HFSS physical solution, preserve run.log together with original native convergence, mesh-statistics and profile exports (for example `.conv`, `.ms` and `.prof`, or equivalent native exports). These records collectively must identify every setup in `meta.json.setup_names` and provide at least three distinct native evidence categories: (a) adaptive pass/convergence rows; (b) native solve/sweep start and completion; (c) mesh/convergence statistics; (d) native export records; (e) AEDT Message Manager/native solver-profile records; (f) linked project result/profile paths. Setup identity may be recorded in the original native headers. Native records and hashes need not be transcribed into run.log; absence of such duplication is not a missing native record. PyAEDT wrapper INFO/WARNING lines alone are not native evidence. The verifier checks replay-bound bytes, MANIFEST hashes and sizes, source code and saved native artifacts to establish the actual design, setup, variation and shared-solve relationship. A matching hash or filename alone does not prove genuine execution. All native-execution and convergence requirements remain in force; this changes evidence placement, not scientific requirements.

For driven port models the adaptive target is Max Mag. Delta S <= 0.02. A finite incident-wave scattering model may use HFSS's native relative Delta Energy <= 0.02 instead; record its definition, unit and target. Record the last measured value, pass count, positive tetrahedra count and native converged/not-converged status for each physical solution. A generic successful process exit is not proof of adaptive convergence. Report an unresolved convergence target honestly; documenting a failure does not establish convergence.

One Optimetrics/session log may contain several solved variations and may be copied unchanged into their variant directories. Link each exported result to its actual design, setup, variation, excitation and `solve_id`. When sharing a log, identify the Optimetrics/shared session in meta.result_source and include a literal `variation` object in each meta.json with its actual geometry parameters, angle and polarization/excitation selection; detailed log records may be referenced elsewhere. A shared log hash, equal pass counts or similar curves alone do not prove copying. Conversely, a declaration of sharing does not make different geometries or scan angles the same physical solution. Each required geometry/angle/orientation must really be solved; same-solution polarization extraction is allowed only where the study explicitly permits it.

### Static documentation and current-run records

Keep README static: method, commands, variant/dependency map, artifact index, modeling choices, known limitations, and a pointer to `results/run_summary.json`. Do not rewrite it during replay. Historical measurements may be included if labeled with their run/date; they need not equal a new run's adaptive history.

Generate `results/run_summary.json` with this schema:

- `schema_version`: integer 1.
- `variants`: object keyed by all required variant names. Each value contains `status` (`solved`, `partial`, `failed`, or `numerical`), `solve_ids` (array of keys into `solves`; empty only for numerical/failed variants), and `reason` (string or null).
- `solves`: object keyed by unique physical `solve_id`. Each value contains `project`, `design`, `setup`, `variation` (object, including geometry/angle/orientation values), `excitations` (array), `convergence` (object with `criterion`, `target`, `last_value`, `passes`, `converged`), `tetrahedra`, and `log_refs` (array of objects with submission-relative `path` and 1-based inclusive `lines`). Failed attempts may have null measured values and must state the cause. Shared physical solves are recorded once and referenced by every beneficiary; a variant requiring two orientations references both solves.

Record solver and PyAEDT versions, UTC run time, sweep and key field frequencies in meta.json. `mesh_summary` includes a numeric `tetrahedra` count and, if needed, per-solve records. `result_source` identifies the solve(s), variation(s), excitation(s), raw exports and any postprocessing; it may be a string plus structured fields or one structured object. `report_export_summary` may reference the raw MANIFEST instead of repeating it. Mode/polarization mappings may live once in `fundamental_trace_map` and be referenced by other fields. A structured reference has the form `{"$ref": "results/<variant>/meta.json#/fundamental_trace_map"}`; paths are relative to the submission root, JSON pointers use RFC 6901, and references must resolve without cycles inside the submission. Descriptive/provenance entries may refer to the single authoritative record; duplicate prose is not required. For HFSS variants, typed fields keep their declared types: setup_names is a literal nonempty array of strings, mesh_summary is an object with its numeric count, and result_source explicitly names HFSS/AEDT plus the solve identity before referring to detailed records. A reference is not a substitute for these machine-read fields.

Place an explicit readable `results/<variant>/structure.json` for every HFSS variant, in addition to any native engineering snapshot under hfss/. It has the structural fields listed above and records the actual modeled objects and variation. A compact shared parameter table is allowed, but each file must describe enough of that variant to reconstruct it independently. Give each paper dimension a symbol, value/unit, geometric role, paper location and source-code use; equivalent algebra or shared constants are acceptable if the intended geometry is actually constructed. Merely listing a parameter without using it is not enough. Dimension labels and their physical meaning take precedence over sketch pixel proportions.

### Raw exports and independent numerical verification

Preserve AEDT-written files byte-for-byte in raw/. Relocating/renaming a file is allowed if its bytes are unchanged and MANIFEST records the original export name. Reformatting, changing columns/units, filtering or interpolation creates a derived file outside raw/.

Each `raw/MANIFEST.json` contains `variant`, `exports` and `derived`. Each export records `file` (relative to raw/), `sha256`, `bytes`, `producer`, `aedt_solution`, `run_log_lines` (inclusive 1-based `[start,end]`), and `exported_utc`; record design/variation/excitation in it or link to meta.json. Each derived entry records `file` (also relative to raw/, normally `../response.csv`), `from` (inputs relative to raw/, including `../` within the submission), and `by` (the actual submitted source path and function, such as `src/postprocess.py:function`; a `derive.py:function` locator is also accepted). Cross-variant dependencies such as an RCS reference are explicit. Static metadata, source files and nominal inputs may be additional dependencies, but every HFSS response must also have a native response-data ancestor. The manifest records provenance, not permission to substitute one solution for another.

The trusted verifier independently recomputes numerical responses from replay-bound native exports and summaries from complete response arrays, without executing candidate validation code. A candidate self-check script is optional. Replay does not run it, and its presence, absence, or verdict does not change the delivered data. Verification failures concern the delivered data, not the implementation of an optional checker. Unsupported native formats or verifier reader limitations are infrastructure errors, not candidate scientific failures. For linear quantities use `abs(a-b) <= atol + rtol*max(abs(a),abs(b))`, with `(atol, rtol)=(1e-9,1e-6)` for direct exports and `(1e-6,1e-3)` for derived quantities. For dB/degree outputs use absolute tolerances 1e-5 (direct) or 1e-3 (derived); phase differences use circular distance. Grid coordinates use absolute tolerance 1e-8 GHz. These checks do not add slack to paper-target windows. For each CSV-derived summary field, report a value consistent with independent recomputation from the CSV. Compare the recomputed value with the paper target; an inconsistent summary must be corrected in the analysis, not silently rewritten during independent reproduction. Grid-selected summary frequencies must match their actual grid rows within 1e-8 GHz; the general summary tolerance does not permit off-grid frequencies.

The coverage classes are:

- HFSS response arrays, metrics and summaries: recompute from native data. Complex-to-magnitude/dB/phase conversion, declared normalization, integration and interpolation are legitimate transformations; check their mathematics, not identical strings. Probe at least five response samples across variants/frequencies; frequency/angle coordinates alone do not count.
- Native images: preserve an original in raw/ and verify the byte hash; direct copying is allowed. For a re-rendered plot, check its data, plotting source and labels. The verifier does not require a candidate image-validation script. Geometry views under views/ are verified with the native model/source and are not numerical derive outputs. Keep result PNGs at their listed Required data products paths, including current maps under views/ where specified; record their provenance/hashes in the manifest or numerical metadata.
- meta.json, structure.json, MANIFEST, README, PAPER_AUDIT, input matrices and nominal design frequencies: check their stated source, structure and agreement with the model; they are not response data that must be derived from raw. Current convergence records are checked against native logs, not paper curves.
- Explicit numerical models: recompute from their permitted static inputs and formula, record input/source hashes, and never label the result as HFSS data.

### Native provenance and paper audit

For every reported HFSS result, retain its native-export ancestry, byte hashes,
solved-variation and quantity mapping, and the source code that transforms the
exports into the reported arrays. Document integration, extrema, and other
data-reduction algorithms so that they can be independently checked.
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

Development is limited to four HFSS solve sessions. An angle-sweeping parametric/Optimetrics session counts as one session; the five distinct angles still require their actual physical solutions. A solved angle may supply both polarizations when declared as specified above. Reserve and execute one additional complete end-to-end reproduction run through reproduce.sh; that run and independently maintained replay are not charged to the development count. The 48-hour development allowance and the separate complete-calculation and review limits are listed under Computing resources and independent reproduction; actual environment timeouts remain those of the supplied runner. Count a new adaptive physical solution for a distinct geometry/scan/orientation or a recomputed attempt as a solve, including failed attempts that entered Analyze. Exporting another report, exciting another solved port in postprocessing, or deriving another metric is not a new adaptive solve. For a session budget, record both the session count and its physical variations. Log actual runtime and resource use; the stated limits are not an empirical runtime guarantee.

## Workspace and provided materials

Your workspace is `/home`. The following files are preloaded in the container:

- `/home/paper/paper.md` - paper text in Markdown, including figure references
- `/home/paper/paper.pdf` - original-layout PDF fallback
- `/home/paper/paper_image/` - extracted paper figures
- `/home/paper/addendum.md` - study-specific reproduction protocol and data formats; read this first
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
`ansys.aedt.core` and run genuine HFSS solves. Use non-graphical mode where
possible and record the project, setup names, mesh/adaptive convergence, solver
messages, and exported report provenance.

All reported numerical and visual evidence must come from the replayed HFSS model:

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

- **te_30 / te_60 center-frequency insertion loss (Table 2)**: At the actually measured centers of the two connected passbands, require TE30 S21 >=-0.77/-1.49 dB and TE60 S21 >=-1.36/-0.95 dB, respectively. Derive centers and peak powers from the full native spectra. Keep S21 at 8.45/12.76 GHz as separate diagnostics rather than substituting them for measured centers.
- **te_86 extreme-angle passbands (relaxed)**: Require the TE86 first measured passband peak S21 >=-2.0 dB, second peak frequency in [12.50,13.05] GHz with S21 >=-1.5 dB, and connected second-band -3-dB width <=0.9 GHz. The nearest raw spectral sample must agree with the reported second peak within 0.25 dB. Both measured passbands must exist.
- **TE first-band angular narrowing**: Require positive connected first-band widths ordered w(TE00)>w(TE30)>w(TE60)>w(TE86)>0. Do not restore the previously erroneous 0.75-GHz reading as an exact TE86 width target.
- **TE60 first-band width**: Require the connected TE60 first-band -3-dB width in [1.05,1.65] GHz, independently of the exact TE86 width.
- **TE band-2 bandwidth narrowing with angle**: Require connected second-band widths w2(TE00)>w2(TE30)>w2(TE60)>w2(TE86), with w2(TE60) in [0.80,1.55] GHz.
- **TE transmission-zero angular stability**: Require the TE30, TE60 and TE86 first transmission-zero frequencies in [10.08,10.64] GHz, with S21 <=-32, <=-32 and <=-26 dB, respectively. Verify the minima against the native spectra.
- **te_86 second transmission zero (~15.15 GHz)**: Require the TE86 second transmission-zero frequency in [14.75,15.55] GHz with S21 <=-25 dB; the corresponding native-derived CSV sample must also satisfy <=-25 dB.
- **tm_30 / tm_60 center-frequency insertion loss (Table 2)**: At the actually measured centers of the two connected passbands, require TM30 S21 >=-0.88/-1.24 dB and TM60 S21 >=-0.73/-0.75 dB, respectively. Retain the 8.45/12.76-GHz samples as distinct diagnostics, not as falsely identified measured centers.
- **tm_83 -3 dB band edges (Sec. 3.2 exact: 3.01-9.96 / 11.11-13.50 GHz)**: Require TM83 first-band lower/upper -3-dB edges in [3.00,3.55]/[9.68,10.24] GHz and second-band edges in [10.83,11.39]/[13.22,13.78] GHz. Select the second peak within [11.50,13.60] GHz, but allow its connected edges outside that peak-search window. Derive CSV and summary edges using the same public algorithm; lawful censoring at 3.00 GHz is permitted for the first lower edge.
- **tm_83 extreme-angle insertion loss (relaxed)**: Require TM83 S21 at the measured first/second passband centers >=-1.17/-1.64 dB and the separately sampled 12.30-GHz plateau S21 >=-2.1 dB. Distinguish measured centers from fixed 8.45/12.76-GHz diagnostic samples.
- **TM band-1 bandwidth widening with angle**: Require first-band widths w1(TM00)<w1(TM30)<w1(TM60)<w1(TM83), with w1(TM60) in [2.75,3.68] GHz. Do not invent a monotonic second-band TM requirement.
- **TM transmission-zero angular stability**: Require TM30, TM60 and TM83 first transmission-zero frequencies in [10.03,10.58] GHz, with S21 <=-31, <=-31 and <=-22 dB, respectively.


## Evidence assessment

All numerical thresholds, measurement definitions, source requirements and geometry constraints
above remain in force. A failed peak-loss condition does not invalidate a different
correct peak, bandwidth, transmission zero or angular trend.

Native source qualification is required before a response is a scientific measurement.
The verifier may inspect the saved project, mode settings, lattice basis,
source code, logs and raw exports together; the same fact need not be repeated in
multiple files. A trend-based polarization label alone is insufficient. A
missing or invalid MANIFEST log index is assessed in the native-export inventory
item, not repeatedly as a numerical, image or offline-checker failure. Actual
export identity must still be established from the existing native evidence;
neither a file hash nor an export declaration alone proves it. Native log lines
need not repeat SHA-256 digests. Incorrect convergence-log references remain a
separate run-report issue. Missing or undecoded verifier context is an evaluation
error, not proof that the submission omitted evidence.

## Computing resources and independent reproduction

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 172,800 seconds (48 hours) |
| Complete native calculation from source | 172,800 seconds (48 hours) |
| Entire reproduction and independent review | 176,400 seconds (49 hours) |
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
