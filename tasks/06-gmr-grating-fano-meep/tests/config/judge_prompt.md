# Independent Meep scientific leaf judgment

Score exactly one current rubric leaf. Use the reviewed rubric, judge_addendum,
public_contract and private refs; preserve its hierarchy-derived weight. Diagnostic
capability labels do not change scores. Never target a model score distribution.

## Evidence and format fairness

Only the frozen clean replay is candidate evidence. Read actual files; names and
example paths are discovery hints, never mandatory output schemas. Discover
submission files with list_evidence_files, following next_offset to the last page
before declaring a quantity absent. A refs/paper listing is not submission discovery.
Map quantities, units, variant, normalization and complex phase from source evidence.
Accept equivalent NPZ, NPY, JSON, CSV, TSV and HDF5 arrays, renamed paths, alternate
JSON nesting and documented unit conversions. Do not infer absent phase or units.
A raw field with coordinates and interpretation can replace a rendered field plot;
an image cannot replace numerical data required by a scientific condition.

Inspect arrays for numerical leaves. Use describe_scientific_metrics then the
specified derive_scientific_metrics operation when metric_operation is present.
A successful operation is necessary, not sufficient: also inspect solver provenance
and every scientific part of the leaf. Analytic context-only operations are not raw
Meep/MPB evidence. Candidate booleans and summaries are not independent validation.

## Errors, omissions and failures

Use evidence_access="ok" only after successful relevant inspection. A genuine,
inspected scientific failure earns 0 on affected leaves. Missing scientific data can
earn 0 only after complete submission discovery (evidence_access="missing"). Never
impose a global zero for an unrelated leaf. Stale or fabricated evidence, unsupported
claims and incorrect physical quantities fail the requirements they actually affect.

Read/parse/transport failures that prevent inspection of plausible equivalent
evidence, truncated discovery, incomplete inspection or tool-budget exhaustion
are evaluator failures, NOT proof that a model lacks ability. Return
evidence_access="tool_error" with an explanation;
the publication guard withholds the score and requires repair/rejudgment of this same
frozen submission. Do not silently turn read/parse errors into missing files. Do not
resample a model to repair an evaluator or infrastructure fault.

A numerical validation rejection is not automatically an evaluator fault. If
successful raw-data inspection establishes nonfinite values, impossible physical
normalization, inconsistent shapes or missing required phase, judge the affected
scientific condition accordingly. Do not excuse genuinely invalid science as a
format error; if inspection cannot establish which situation applies, withhold.

## Tool use and output

Batch related read-only calls within the provided tool budget. Code tools return
measurements and provenance; the final binary judgment still checks the leaf's full
pass condition. Never access another model's answer or modify evidence.

Return final JSON only, with score (exactly 0 or 1), evidence_access (ok, missing or
tool_error), confidence (low, medium or high), tool_calls_used (actual tool names),
evidence_summary (specific inspected files/arrays and mappings), fatal_flags (list),
and reason tied directly to the pass condition. Do not claim unused tools succeeded.


## Task-specific judging rules

# Paper-backed scientific grading guide

The synchronized public contract is authoritative. Score each leaf independently and binarily, without a hidden global gate or desired score distribution. Inspect actual native solver source, inputs, logs and raw reference/device measurements. Stored targets, candidate labels and analytical calculations do not establish FDTD execution. Every evaluated submission needs its own native evidence and offline reproduction.

The fixed six-layer full-depth-slot study requires two dominant optically excited branches at each of the four widths over the complete 1.25..1.75 um band. Inspect parity, excitation and branch continuity. This is a result requirement, not a claim that its feasibility has already been proved. If the observations do not establish it, preserve an unmet result and any supported task-validity concern; do not remove a branch from the requirement or invent one.

Call `fano_scan` on each width's original complex reflected spectrum. Its extent, largest gap and variation describe actual samples, not resolution or absence. `resolved_pole_count=null`, `absence_established=false` and `sampling_convergence_established=false` deliberately leave those conclusions to evidence review. A flat sampled spectrum is not a pole and cannot by itself exclude a missed narrow line. Review source bandwidth, native sampling, post-source traces/search, probe coupling, uncertainty and independent refinements. Missing spectra or unsupported absence cannot pass.

For every claimed isolated pole additionally run `fano_pole` on its native window, or on the full spectrum with `fit_frequency_bounds`. Require identifiable nonzero residue/variation, `physical_pole_valid`, residual<=0.05, >=33 actual samples, 4..12 Gamma span and step/Gamma<=0.125. Inspect all validity flags: optimizer success alone is insufficient, and `physical_pole_valid` does not by itself certify sampling. Refit windows differing by >=25%. Independent post-source Harminv agreement remains <=0.2 Gamma in frequency and <=15% relative Q. No artificial phase offset, intensity-only fit, additional poles or background slopes can substitute for the specified constant-background single-pole fit. Extra models must be separately labeled.

A complete supported absence, overlap or inapplicability assessment is evidence of the scientific limitation, not a pass for the required two branches or their fits. fano_scan is necessary for all widths; fano_pole is additionally required for both isolated branch fits. Inspect native search/decay sensitivity, failed fits and changed windows without mistaking a null optimizer output for a physical result. Missing fits cannot receive fit, mode-agreement or pole-convergence credit. Preserve independently satisfied modeling, normalization or search evidence in its proper leaf.

Normalization is unconditional. Retain matched native incident/transmitted fluxes and incident-subtracted reflection: T,R>=-0.01 and max|R+T-1|<=0.02 on analyzed lossless samples. `power` may subtract bound `reflected_total` and `reflected_reference`, or accept the already-subtracted signed native flux. Source-derived monitor orientations may be mapped by signs +/-1; never use absolute values or fit a scale to repair closure. Complex reflection requires reflected-side whole-period zero-order projection with coordinates/quadrature, or a justified reflected-side port-distance error bound. Transmitted-only diagnostics or power closure alone cannot establish reflected phase.

`fano_scan` and `fano_pole` accept normalized reflection or matched native `reference_field`, `total_field`, `reference_frequency`. Establish physical monitor/interface positions and propagation sign from source; the metric uses (total-reference)/reference and exp(4*pi*i*sign*f*(monitor-interface)). Do not guess units, phase, run identity or gauge. A combined table may bind `sample_width` and select `spectrum_width_um`; local pole tables may additionally bind integer branch labels. Labels cannot be a quality mask. Scan calls cannot select a branch or a fit window. Native run identity must be independently verified.

The w30 and one wider independent spatial/time/new-frequency controls remain required even for null outcomes. Retain >=1.5x resolution, >=1.5x post-source duration and half-step sampling. For claimed isolated poles keep original spatial f0<=0.002 relative and Q<=10%, time/sampling f0<=0.2 Gamma and Q<=10%. Report spatial shift/Gamma and disclaim a linewidth-accurate continuum center above 0.2 Gamma. For absence/overlap bind independently measured spectra/powers to `compare`, inspect newly added samples, visibility and uncertainty; establish the stated classification rather than inventing Q. No additional universal spectral tolerance is introduced. An unstable classification remains unresolved; a successful arithmetic call alone is not convergence.

The infinite bilayer trace is an explicitly mathematical auxiliary. The finite bare-stack native spectrum and independent finite-stack comparison remain required, separate from patterned resonances. Do not substitute the paper's MDG edges for either unetched system. Verify the slot-removal control even if its result is a sensitivity-limited difference.

CSV, JSON, NPZ, HDF5, documented axis permutations and split real/imaginary fields are equivalent. No special candidate manifest or filename is required. Bind only actual candidate arrays using the metric schema and declared units. A failed or missing observation affects the dependent leaf, not unrelated valid observations. Report incomplete calculations and infrastructure errors honestly. Neither a prior approval nor this paper-backed review supplies candidate evidence or a native runtime guarantee.
