# Matching, isolation and radiation in a four-port CPW UWB antenna: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

- [Scientific measurements](#scientific-measurements)
- [Scope](#scope)
- [Reconstruction scope](#reconstruction-scope)
- [Clarifications](#clarifications)
- [Completion policy](#completion-policy)
- [Comparison and numerical integrity](#comparison-and-numerical-integrity)
- [Geometry symbols are local to the cited equation or figure](#geometry-symbols-are-local-to-the-cited-equation-or-figure)
- [Documented layout reconstruction](#documented-layout-reconstruction)
- [Retained scientific scope](#retained-scientific-scope)
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

Reproduce and compare the paper's **HFSS simulation** results (not the measurements) for the following targets. Figure numbers are paper figure numbers (match them via the captions, not via `figure-NNN` file names).

| # | Target paper figures/tables | Design / variant selection | Metrics | Variant name |
|---|---|---|---|---|
| T1 | Fig. 8 (simulated curves only), Fig. 11, Fig. 12, Fig. 13, Fig. 10 (simulated curves, at the three frequencies stated in its caption), Fig. 9 (surface currents at the four frequencies stated in its caption) | Final 4-element MIMO antenna per Fig. 3 and Table 1 | S11/S12/S13/S14, radiation efficiency, ECC (per paper Eq. (6)) + DG (Eq. (7)), peak gain + multiplexing efficiency (Eq. (8)), radiation patterns, surface current maps | `mimo_final` |
| T2 | Fig. 1(b) | Initial single element of Fig. 1(a) (no stub), on the W/2 × L/2 board | S11 | `single_initial` |
| T3 | Fig. 2(b) | Single element with matching stub per Fig. 2(a), same board | S11 | `single_stub` |
| T4 | Fig. 4, the two non-nominal legend curves | Same 4-element MIMO antenna with H2 changed to the legend values 10.7 mm / 11.7 mm (all other parameters per Table 1) | S11 | `h2_10p7`, `h2_11p7` (the H2 = 11.2 mm member IS `mimo_final`; do not duplicate it) |
| T5 | Fig. 6, the "without stub" curve | Same 4-element MIMO antenna with the feedline stubs removed on all four elements (all other parameters per Table 1) | S11 | `mimo_nostub` (the "with stub" member IS `mimo_final`) |

Total: 6 variants, each a distinct geometry requiring its own real HFSS solution. For the four-port variants, one full-matrix solve per variant yields all required S-parameter columns and (for `mimo_final`) all port far fields; that is a single solution, not cross-variant sharing.

## Scope

- Included: everything in the table above, simulation only.
- Excluded: all measured curves (dashed traces in Figs. 8 and 10), the Fig. 5 (Lp) parametric study, Fig. 7 photographs, Table 2 rows other than "This work", and the CPW closed-form calculation of Eqs. (1)–(4) / monopole estimate of Eq. (5) (you may use them as sanity checks; they are not deliverables).

## Reconstruction scope

The primary model is a documented Fig. 3/Table 1 layout reconstruction, not uniquely known author CAD. Follow the dimension/endpoints record in `/home/paper/addendum.md`. Source-supported g/W4 feature interpretations are admissible when reported values, topology and one common construction across all six variants are preserved. Report empirical g=1.56 mm separately from the defined actual CAD distance; neither response fitting nor an undisclosed exact-endpoint requirement is part of this scope. Primary matching, isolation and radiation observations remain required and compared under the public numerical rules.

## Clarifications

1. Coordinate/plane convention: place the board in global x-y with normal +z. Its global in-plane orientation is free. Define a local orthonormal basis with local x along the port-1 feed from board edge toward radiator, local z along the board normal, and local y = z cross x. Record the three basis vectors in global coordinates as `meta.pattern_basis` plus `port_edge_mapping`. For angle a, xy samples x*cos(a)+y*sin(a), xz samples x*cos(a)+z*sin(a), and yz samples y*cos(a)+z*sin(a). A global rotation therefore does not change the labeled local cuts. Fig. 10 does not establish its axes relative to Fig. 3; its fixed xy-ripple and yz-null thresholds are not reviewed. Reproduce and compare genuine HFSS patterns, reporting the unresolved paper-axis mapping rather than choosing a rotation to force agreement.
2. ECC/DG: use isotropic uniform illumination, XPR=1, and complex embedded far fields F_i=(E_theta_i,E_phi_i), exciting port i alone with all other ports matched. Define rho_c_ij = integral(F_i dot conjugate(F_j) dOmega) / sqrt(integral(|F_i|^2 dOmega)*integral(|F_j|^2 dOmega)), dOmega=sin(theta)*dtheta*dphi; ECCij=|rho_c_ij|^2. Use full-sphere quadrature without double-counting the phi seam, a common angular basis, and exported complex fields, not S-parameter ECC. Define DG_dB = 10*sqrt(1-max(ECC12,ECC13,ECC14)^2), following paper Eq. (7); despite the legacy column name this formula is not an additional logarithm. Document the angular grid and integration. Zero field norm is an error, not ECC=0.
3. Multiplexing efficiency convention: define eta_total_i = P_radiated_i/P_incident_i from native power reports with the same single-port excitation and matched unused ports. For each j in {2,3,4}, eta_mux_1j = sqrt(eta_total_1*eta_total_j*(1-ECC1j)); report `mux_eff_dB = min_j(10*log10(eta_mux_1j))`. ECC is already |rho_c|^2 in Eq. (8); do not square ECC again in this formula. Keep `efficiency.csv` as native radiation efficiency P_radiated_1/P_accepted_1, not total efficiency. Preserve all three power definitions; do not assume a single-port mismatch formula for accepted power in a coupled multiport system. This fixes a task convention where the paper does not specify the pair or efficiency definition; the published mux curve is a coarse comparison, not a unique implementation independent reference. The retained multiplexing-efficiency comparison ranges are stated below. Their validity for the declared efficiency convention must be checked, not assumed from the paper; a mismatch does not establish the requested performance.
4. Metal thickness is not given in the paper. Model the metallization as zero-thickness sheets or as standard-thickness copper foil; state your choice and its treatment (PEC vs finite conductivity) in README/meta.json. The substrate material data are in the paper.
5. Port numbering is only visible in the prototype photo (Fig. 7). Any numbering that is consecutive around the perimeter is acceptable provided the `sparams.csv` column semantics of the Output Schemas section (S13 = diagonal pair) are respected.
6. The SMA connectors visible in Fig. 7 are measurement hardware and are not part of the simulated model.
7. `single_initial` and `single_stub` use the reduced board explicitly dimensioned in the captions/annotations of Figs. 1–2; all element dimensions follow Table 1 (Table 1's caption says "shown in Figure 1"; its symbols are the ones annotated in Fig. 3).

8. CPW ports and native matrix: use exactly one logical, power-normalized CPW port per feed, referenced to 50 ohm, with a consistent port plane and polarity. The port represents the center conductor and both return-ground sides of the CPW cross-section; a wave or equivalent single logical lumped/terminal port is acceptable. Four-port models must export an AEDT-native full complex .s4p matrix; single-element models export .s1p. Two independent gap ports per feed followed by selecting four entries of .s8p is not the contracted four-port network. Undeclared multiport-to-logical transformations are not accepted. Include all raw complex Sij, reference impedances and excitation normalization, not only magnitude S11/S12/S13/S14 columns.
9. Network/metric consistency: for all four-port variants, check each complex reciprocal pair abs(Sij-Sji) <= 0.02 at the same reference planes and each incident-port power sum sum_j|Sji|^2 <= 1.005. For the C4-related reflections compare dB magnitudes only when both are above -20 dB, tolerance 0.5 dB; otherwise use linear-magnitude difference <= 0.02. ECC must lie in [0,1] within 1e-6 numerical tolerance. Check DG and mux against the formulas above to 0.001 dB. Larger violations must be reported, not clipped away.

## Completion policy

Completion requires a successful no-argument clean replay producing the full
addendum-required HFSS projects, native solve evidence, numerical artifacts,
views, logs, and provenance. Before finishing, run `reproduce.sh` from a clean
generated-output state and verify that all required files exist. A smoke test or
unsolved project is not a completed submission.

## Comparison and numerical integrity

Compare the full S-parameter curves, impedance-band edges, resonance frequencies and depths, isolation across the band, radiation efficiency, ECC/DG and gain. For the H2 and stub controls, report frequency shifts and changes in matching, not just a single headline value. Preserve all six geometries and the field-based radiation and correlation measurements.

Use the paper's simulated curves only under the stated matching conditions; do not tune geometry or replace computed data with digitized curves. Keep nominal dimensions exact in the construction. A geometry readback tolerance of 0.05 mm accommodates numerical extraction, not a change to the design. Quantify mesh and sweep sensitivity, preserve unrounded native exports, and keep summaries consistent with their underlying arrays. Check finite responses, passivity and the applicable reciprocity relations. The output grids, units, reference planes, polarization conventions and control experiments in this protocol and `addendum.md` remain required.

## Geometry symbols are local to the cited equation or figure

- In Sec. 2.1, the CPW formula's W is the center-conductor width and G is
  the conductor-to-ground slot: the following paragraph gives 1.5 mm and
  0.5 mm. In Table 1 / Fig. 3, W and L are instead the 38-mm board sides,
  Wf=1.5 mm and W1=0.5 mm. Do not substitute the board width into Eq. (2).
- Table 1 gives g=1.56 mm, and the paragraph after Eq. (5) calls it the
  ground-to-radiator distance. This is not the 0.5-mm CPW slot G/W1.
  Preserve the Table 1 value and identify the endpoints of any CAD distance
  claimed to represent g. A separately computed 1.4-mm distance from an
  assumed pair of concentric/offset arcs is not a replacement paper value.
- Table 1 gives W4=0.4 mm, W3=0.1 mm, W2=1 mm and L4=5.8 mm. Figure 3
  supplies their dimension arrows; Figs. 1(a)/2(a) distinguish the initial
  and stubbed 19-mm boards. Record the annotated features rather than treating
  similarly named dimensions as interchangeable. The dimension annotations do not establish unique W4/g endpoints.
  Declare a source-supported reconstruction as described below; do not
  present inferred endpoints as the author's exact CAD.
- Eq. (5)'s following paragraph assigns A1/A2 and l1/l2 to ground/radiator,
  whereas Sec. 3.2 refers to increasing radiator length as increasing l1.
  Preserve and report that notation ambiguity. The empirical resonance
  estimate is not an independent geometric constraint permitting a retune.

## Documented layout reconstruction

Reconstruct the layout from Fig. 3 and Table 1; do not claim access to the
authors' exact CAD. The supplied drawing does not uniquely establish every
g/W4 endpoint. Distinguish reported dimension values from inferred feature
associations, endpoints and topology choices. Use one documented, consistent
construction for the six requested variants, preserving the paper's layout,
named nominal dimensions, material definitions and the specified control changes.

In README and the existing structure/source records, provide a dimension map:
paper symbol/value, figure or text location, associated constructed feature,
whether that association is reported or inferred, and its explicit coordinates
or construction rule. Preserve the nominal Table 1 values. For W4=0.4 mm,
state and illustrate the chosen feature/endpoints and why they are supported
by the crowded annotation, without asserting that the drawing supplies a
unique endpoint choice. An alternative source-supported interpretation is
admissible if it preserves the reported value and the stated topology.

Record the reported empirical g=1.56 mm separately from a measured distance
in the reconstructed CAD. Define the latter's endpoints, direction or
minimum-distance operation and its actual value. If a construction yields
1.4 mm for a particular arc separation, report it as that constructed distance,
not as a replacement paper value, and do not change radii or positions merely
to force that distance to 1.56 mm. Explain the Eq. (5) notation ambiguity
without treating its empirical estimate as an extra exact-CAD constraint.

Keep the 38-mm four-port board, 19-mm single-element boards, single-sided
CPW-fed circular-based radiators, ground cutouts, stub/top-protrusion/notch
features and C4-related four-edge placement. Where the placement uses an
inferred equation such as L1+W1+Wf/2, record it as a construction inference,
not an additional independently reported coordinate. The four-port cases
must use one common template; the H2 controls change only H2, the no-stub
case removes only the stubs, and the single initial/stub pair differs only
by the stub on its reduced board.

Choose and document the reconstruction from the paper before comparing
performance; freeze it across controls. Do not search unspecified endpoint
choices or alter reported dimensions to fit spectra. Keep primary matching,
isolation, radiation and field measurements and their public paper comparisons.
A documented interpretation is not evidence of successful performance.
Numerical deviations remain visible; dimension uncertainty does not grant
automatic agreement or permit fabricated/fitted responses. Retain independent
native geometry and electrical evidence for the actual reconstruction.

## Retained scientific scope

All six designs and detailed matching, isolation, radiation, current and
control measurements remain. Paper observations in Figs. 1–6 and 8–13 are
comparators at the paper's simulated conditions; measurements/SMA hardware
are not added to the simulated primary model. The Fig. 10 paper-axis mapping
remains explicitly unresolved as already stated in the protocol.

The task's multiplexing quantity fixes total efficiency, the worst of three
port pairs and a specified illumination model. Eq. (8)/Fig. 13 do not establish
that entire convention. Treat the reported -3 dB floor as a comparison under the paper definition,
not a guaranteed bound for this different metric. Derive all prescribed
powers/ECC/multiplexing values honestly and
compare to Fig. 13 while stating the definition difference. Formula, units,
raw-field provenance and internal consistency remain required.

Document the unresolved g/W4 endpoints using the dimensioned source;
do not silently choose a geometric interpretation to force agreement.

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
submission/src/                       # all build/run/postprocess sources
submission/src/derive.py                  # offline response derivation; coverage classes below
submission/src/run_all.py                 # contract entry: python3 src/run_all.py --variant <name>  (full HFSS chain of one variant)
submission/hfss/                      # <project>.aedt, structure.json, logs/
submission/views/mimo_final/top.png
submission/views/single_initial/top.png
submission/views/single_stub/top.png
submission/views/mimo_final/current_f1.png
submission/views/mimo_final/current_f2.png
submission/views/mimo_final/current_f3.png
submission/views/mimo_final/current_f4.png
submission/results/<variant>/meta.json
submission/results/<variant>/run.log
submission/results/<variant>/sparams.csv
submission/results/<variant>/summary.json
```

where `<variant>` ∈ { mimo_final, single_initial, single_stub, h2_10p7, h2_11p7, mimo_nostub } (all 6 required).

Additionally — the four `mimo_final`-only CSVs, plus the raw AEDT export directory of every HFSS variant:

```text
submission/results/mimo_final/efficiency.csv
submission/results/mimo_final/gain.csv
submission/results/mimo_final/mimo_metrics.csv
submission/results/mimo_final/patterns.csv
submission/results/h2_10p7/raw/                # byte-for-byte AEDT exports
submission/results/h2_10p7/raw/MANIFEST.json
submission/results/h2_11p7/raw/                # byte-for-byte AEDT exports
submission/results/h2_11p7/raw/MANIFEST.json
submission/results/mimo_final/raw/                # byte-for-byte AEDT exports
submission/results/mimo_final/raw/MANIFEST.json
submission/results/mimo_nostub/raw/                # byte-for-byte AEDT exports
submission/results/mimo_nostub/raw/MANIFEST.json
submission/results/single_initial/raw/                # byte-for-byte AEDT exports
submission/results/single_initial/raw/MANIFEST.json
submission/results/single_stub/raw/                # byte-for-byte AEDT exports
submission/results/single_stub/raw/MANIFEST.json
```

`current_f1..f4.png` are the port-1-excited surface-current-magnitude maps of the full board at the four frequencies stated in the caption of Fig. 9, in ascending frequency order (f1 = lowest). Use one continuous color scale per image, rendered on the metal layer, with the excited port and frequency stated in the image title or an adjacent caption in README.

## Output Schemas

Frequency sampling requirements:

- `sparams.csv` — step **0.02 GHz exactly**, frequencies preferably written with two decimals (equivalent numerical spellings are accepted); coverage 3.00–20.00 GHz for the four-port variants (`mimo_final`, `h2_10p7`, `h2_11p7`, `mimo_nostub`) and 2.00–20.00 GHz for the single-element variants (`single_initial`, `single_stub`). Provide an exact row at every specified frequency rather than relying on interpolation.
- `efficiency.csv`, `gain.csv`, `mimo_metrics.csv` — step **0.25 GHz exactly**, 3.00–20.00 GHz.

Check summary consistency independently of agreement with the paper. Recompute every CSV-derived summary using the definitions below. Agreement tolerances are 0.011 dB/degree/dBsm, 0.0051 GHz and 0.0011 for dimensionless summaries; these are serialization tolerances, not extra paper-target tolerances. Use at least six decimal places for response values and at least three for derived scalars. Frequencies that are grid selections must be grid members; explicitly permitted crossing interpolation is the only exception. For equal extrema choose the lowest frequency, then the first declared column; for a flat local extremum choose the middle grid row, rounding toward the lower index. Report missing or inconsistent summaries explicitly. Distinguish quantities that depend on an affected summary from independent observations supported by intact CSV data. JSON must use null with an allowed status, never NaN or Infinity.

Columns:

- `sparams.csv` (four-port variants): `frequency_GHz,S11_dB,S12_dB,S13_dB,S14_dB`. Port semantics: number the four ports consecutively around the board perimeter (one port per board edge), so that port 2 and port 4 are the two elements adjacent to port 1 and port 3 is the diagonally opposite element. S11 is the reflection at port 1; record your port-to-edge mapping in meta.json and README.
- `sparams.csv` (single-element variants): `frequency_GHz,S11_dB`.
- `efficiency.csv`: `frequency_GHz,radiation_efficiency` (linear 0–1, port 1 excited).
- `gain.csv`: `frequency_GHz,peak_gain_dBi`: maximum of HFSS `GainTotal` over the full sphere with port 1 excited and all other ports matched. Gain uses accepted-power normalization, `4*pi*U/P_accepted`, and dBi is `10*log10(gain_linear)`. Do not substitute `RealizedGainTotal` in this column. An optional separately named realized-gain file may be supplied as a diagnostic; record the native quantity and angular grid in meta.json.
- `mimo_metrics.csv`: `frequency_GHz,ECC12,ECC13,ECC14,DG_dB,mux_eff_dB`, computed by the fixed definitions in Clarifications 2-3. Preserve the complex embedded far fields and native per-port incident, accepted and radiated powers needed for these calculations in raw/.
- `patterns.csv`: `plane,frequency_GHz,angle_deg,gain_norm_dB`, with plane in {xy, xz, yz}, the three Fig. 10 caption frequencies, and angles 0..355 degrees in steps of 5. These are the local antenna planes defined in Clarification 1, not an asserted mapping to the paper's unexplained axes. For each cut use port-1 `GainTotal`, normalize by its own linear maximum and convert with 10*log10. Export 9 cuts (648 rows). Also generate `results/mimo_final/pattern_comparison.md` identifying the local basis, raw expressions, normalization and comparison limitations; no paper-derived artificial nulls or filled-in pattern data.
- `summary.json` (per variant; all values derived from your exported CSVs, retain enough data to verify consistency):
  - all variants: `s11_band_GHz` is the maximal contiguous grid component with S11_dB <= -9.5 that contains the global minimum (lowest frequency wins a tie). Use included grid rows as edges, never bridge a failed row; null if no row qualifies. `s11_band_status` is `valid`, `truncated_low`, `truncated_high`, `truncated_both`, or `no_qualifying_interval`. `s11_local_minima` is an array of {`f_GHz`,`S11_dB`}: use scipy.signal.find_peaks on -S11 with prominence >= 2 dB, including its documented plateau-center rule; if more than 8 remain choose the 8 greatest prominences, break ties by lower frequency, then sort by frequency. Sweep endpoints are not local peaks.
  - `mimo_final` additionally: `worst_coupling_dB` (maximum of all S12/S13/S14 values over the sweep), `s13_max_dB`, `eff_min`, `eff_max`, `ecc_max` + `f_ecc_max_GHz` (over the three ECC columns), `dg_min_dB`, `peak_gain_max_dBi` + `f_peak_gain_max_GHz`, `peak_gain_min_dBi`, `mux_eff_min_dB`, and `patterns`: for each of the nine (frequency, plane) cuts an object {`ripple_dB` = max − min of the normalized cut, `min_norm_dB`, `angle_of_min_deg`}, keyed `"<frequency>_<plane>"` (e.g. `"<f>_xy"` with `<f>` the caption frequency in GHz, printed exactly as the caption prints it — same decimals; the two-decimal spelling is also supported).
- `meta.json` (per variant): `aedt_version`, `pyaedt_version`, `solver_type`, `design_type`, `model_units`, `coordinate_system`, `frequency_sweep`, `key_frequency_points`, `boundary_summary`, `excitation_summary`, `port_edge_mapping`, `setup_names`, `mesh_summary`, `report_export_summary`, `result_source`, `run_timestamp_utc`.
- `structure.json`: `model_units`, `parameters`, `materials`, `named_objects`, `boundaries`, `excitations`, `setups`, `ports`; `named_objects` must allow textual recovery of every required geometric fact (element outline, ground cut-out, CPW feed, stub, board) for all 6 variants (parameter-table compression across variants is fine).

## Calculation records and independent reproducibility

The following requirements define simulation evidence, source preservation, offline derivation, and independent reproduction.

### HFSS execution and native evidence

The HFSS variants for this study are: **`mimo_final`, `single_initial`, `single_stub`, `h2_10p7`, `h2_11p7`, `mimo_nostub`**. Every one requires a genuine PyAEDT-controlled HFSS solution, its native project under `hfss/`, `results/<variant>/run.log`, `meta.json`, `structure.json`, and an AEDT export directory `raw/` with `MANIFEST.json`. Numerical variants explicitly listed in the target table are governed by their own numerical contract; they do not require an AEDT project, run.log or raw directory.

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

Record solver and PyAEDT versions, UTC run time, sweep and key field frequencies in meta.json. `mesh_summary` includes a numeric `tetrahedra` count and, if needed, per-solve records. `result_source` identifies the solve(s), variation(s), excitation(s), raw exports and any postprocessing; it may be a string plus structured fields or one structured object. `report_export_summary` may reference the raw MANIFEST instead of repeating it. Mode/polarization mappings may live once in `fundamental_trace_map` and be referenced by other fields. A structured reference has the form `{"$ref": "results/<variant>/meta.json#/fundamental_trace_map"}`; paths are relative to the submission root, JSON pointers use RFC 6901, and references must resolve without cycles inside the submission. Descriptive/provenance entries may refer to the single authoritative record; duplicate prose is not required. For HFSS variants, typed fields keep their declared types: setup_names is a literal nonempty array of strings, mesh_summary is an object with its numeric count, and result_source explicitly names HFSS/AEDT plus the solve identity before referring to detailed records. A reference is not a substitute for these machine-read fields.

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

Development is limited to 14 full HFSS solves. The six required geometries and convergence retries share this development budget; one full four-port solution supplies its complete S matrix and the requested port far fields. Reserve and execute one additional complete end-to-end reproduction run through reproduce.sh; that run and independently maintained replay are not charged to the development count. The 24-hour development allowance and the separate complete-calculation and review limits are listed under Computing resources and independent reproduction; actual environment timeouts remain those of the supplied runner. Count a new adaptive physical solution for a distinct geometry/scan/orientation or a recomputed attempt as a solve, including failed attempts that entered Analyze. Exporting another report, exciting another solved port in postprocessing, or deriving another metric is not a new adaptive solve. For a session budget, record both the session count and its physical variations. Log actual runtime and resource use; the stated limits are not an empirical runtime guarantee.

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

- **Multiplexing efficiency floor (paper: > -3 dB)**: Compute worst-pair multiplexing efficiency over (1,2), (1,3), (1,4) using the specified native total efficiencies and field-based ECC. Require mux_eff_min_dB in [-3.3,-0.8] and mux_eff_dB at 20 GHz in [-4.2,-0.8]. Do not change efficiency definitions to meet these ranges.


## Computing resources and independent reproduction

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 86,400 seconds (24 hours) |
| Complete native calculation from source | 86,400 seconds (24 hours) |
| Entire reproduction and independent review | 90,000 seconds (25 hours) |
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
