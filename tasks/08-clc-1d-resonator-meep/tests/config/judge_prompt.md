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

# Private scientific grading guide

The frozen public contract is authoritative. Inspect actual solver source and run provenance; analytic references, candidate-supplied labels, precomputed paper targets and derived arrays alone are not native FDTD. Follow the leaf's scientific metric_operation with explicit bindings after inspecting candidate array names/units. Arbitrary filenames, JSON/CSV/NPZ/HDF5, split real/imaginary fields and documented unit conversions are equivalent. No presentation points, mandatory manifest, duplicated threshold penalties or desired score distribution.

Each leaf is independently binary. Do not fail one leaf because a different deliverable is absent unless physically necessary for this observation. Do not allow successful pure-array arithmetic to stand in for provenance. `bilayer` is an explicitly mathematical auxiliary, not raw FDTD; other numeric leaves require raw-run traceability. `compare` must bind actual matched observables from two independently executed runs, not a candidate-written difference. Context is for physical conventions, not fabricated result arrays. A negative-control label alone is insufficient.

Optional metric inputs allow independent partial evidence: PT left-side observations do not require right-incidence arrays; CLC transmission/edge statistics do not require the independent linear-input output. A null reciprocity/closure/superposition result is NOT a pass for the leaf requiring that missing observation, but must not veto unrelated observed quantities. Inspect precisely the observations required by the current leaf.

CLC Jones matrices may be stored whole or as four separate complex component columns, including CSV real/imaginary pairs. Bind component quantities rather than demand a particular tensor file layout. Pure channel-power and spectral-edge leaves may also use calibrated native incident/transmitted flux columns without inventing missing phase; that does not pass Jones/superposition leaves. Scalar or two-branch convergence comparisons are valid: the comparison metric does not impose a three-sample presentation requirement.

For stability, bind complete native real/complex time traces as field together with time and the documented source_off_time. The reviewed metric performs magnitude extraction and post-source selection itself. field_envelope is only for an explicitly real nonnegative envelope. Do not treat a missing precomputed absolute-value/cropped array as missing FDTD evidence; do not relabel a signed raw field as an envelope. Growth thresholds and six-block statistics are unchanged.

For native flux, the metric's optional incident_flux_sign, transmission_flux_sign and reflection_flux_sign convert explicitly documented monitor conventions. Fixed-coordinate signed flux and outward-positive reflected power are equivalent when the source's monitor normals/weights establish the conversion. The default signs are +1,+1,-1. Never choose a sign based on the measured value or closure, never take abs() to repair a wrong result, and never accept a fitted normalization scale as a port orientation.

The reference bundle separates mathematical/continuous-Maxwell checks from genuine Meep probes. The Fano w70 coarse probe is NOT a high-Q, closure or convergence gold standard. Do not assert that an untested minimum Q is impossible or that a faithful answer should earn a prescribed score. No acceptance claim extends beyond measured evidence.

For complex-pole fits, raw power arrays alone do not supply phase. Zero-variation or unresolved fits do not pass. For active PT media never require passive energy conservation. Brewster operator gain is not reflected-power efficiency. CLC channels stay fixed globally; independent Ex input validates coherent superposition rather than a half-power assumption.

## Native evidence versus physical consistency

Leaf002 evaluates genuine acquisition and faithful representation: inspect actual Ex/Ey/Hx/Hy, fluxes, both circular and independently executed linear-input runs, their references, documented component/basis/phasor conventions, and the traceable raw-to-normalized conversion. Directly reconcile saved normalized quantities with the retained raw fields and documented physical reference planes, allowing the documented output precision rather than requiring a particular format or machine-precision serialization.

A failure of leaf002 requires its own concrete evidence defect, such as absent or fabricated native inputs, a wrong component/conjugation convention, an undocumented phase correction, or a raw-to-normalized discrepancy not explained by the declared representation. Do not infer such a defect solely from failure of linear superposition, energy closure, independent-theory agreement or numerical convergence. If the required native observations and faithful conversion are established, leaf002 passes even when those separate physical checks fail.

The <=0.02 independent-linear/Jones comparison belongs to leaf003, not leaf002. Keep its failure when supported, and separately retain the stated closure, spectral-cross-check and convergence deductions under leaves004,005,009. This separation removes duplicate penalties; it does not waive any physical threshold or prescribe a score for a particular candidate.

## Four-thickness scope

Require D/p=5,10,20,40 with all fixed circular and independently executed linear inputs. The 5p,10p,40p grid/time comparisons and justified 20p discretization are mandatory; every thickness needs new-point sampling convergence. No minimum-transmission suppression threshold is scored. Minimum transmission and its location are descriptive diagnostics, not extra gates or deductions under another criterion. No absent thick-slab result is exempted or passed. Correctly reported narrow-peak or convergence failures remain unmet results under their applicable criteria.

For the full four-thickness spectral cross-check, invoke clc_reference_compare separately on Jones-derived and independently normalized native channel powers at their actual coordinates; both use the public 0.03 limit. A small native/Jones difference is calibration evidence, not a substitute for the direct-native/reference comparison.
