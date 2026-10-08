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

The public model and scientific thresholds are authoritative. Each leaf is independently binary; there are no layout points, desired score distributions or automatic global vetoes. Bind actual candidate arrays with documented units, axes, signs and run provenance. JSON/CSV/NPZ/HDF5, complex arrays and identified real/imaginary pairs are equivalent. Pure-array arithmetic never establishes that Meep ran. Static public source definitions may be reconstructed, but measured FDTD responses may not be replaced by theory.

The runner distinguishes original source/static inputs from newly generated outputs. A new report, plot, log or other regular output is not source mutation. Source deletion/modification and symlink substitution remain failures. Do not invent a zero score for a withheld infrastructure result. No candidate-authored manifest or particular report filename is mandatory.

For compare, bind observables from two independently executed runs or an explicitly independent same-model reference, not a candidate-written difference. Coordinate interpolation is the public piecewise-linear rule with no extrapolation. Missing evidence affects only the observations that physically require it. Report missing provenance, a numerical threshold exceedance and unestablished convergence as distinct reasons.

## Brewster observations and quadrature

The direct-beam and genuine plane-wave-basis/synthesis routes are both valid. For a basis route verify >=33 independently acquired native angular samples and their source wavevectors. For a direct beam verify its prescribed angular content and calibrated input/output fields, rather than demanding 33 separate plane-wave jobs. Either route retains the required angular evaluation samples and convergence evidence. Interpolating a few runs or writing theoretical Fresnel samples does not create genuine acquired samples.

The Gaussian and Sinc spectra are fixed static source definitions. fixed_public_input is allowed only after checking the actual source implements that definition. Do not demand a redundant saved A(q), but always bind native-derived complex r. For Sinc integrate on [-0.09,0.09] with retained cutoff samples; cropped and zero-padded spectra must give identical metrics. No invented quadrature weights, fitted normalization or pointwise phase corrections are permitted. Acquisition sample counts are checked from the actual experiment, not the cropped table length.

Leaf006 uses the public evidence-based power protocol. Require separate successful brewster_power operations for the two production inputs, binding their native powers, complex response and independently supported integrated error bounds. Inspect the source and calibration evidence behind the bounds, not just the declared path/quote or scalar. The operation performs arithmetic only: its numerically_qualified flag does not establish provenance or a valid uncertainty model. Review source/reference normalization, null or equivalent calibration residuals, refinements, quadrature, monitor/boundary effects and correlations. An invariant bias can survive every refinement; never impose or accept total uncertainty solely as a sum of refinement changes and a null residual.

Apply eta_spectrum>0, eta_flux>u_flux, u_flux+u_spectrum<=0.10*eta_spectrum and absolute flux/spectrum disagreement<=u_flux+u_spectrum, with the public arithmetic slack only. The 10% budget is a disclosed study precision criterion, not a paper result. Inspect closure<=.02 and native R/T>=-.01 in retained refinement runs as well as production. Net forward flux requires incident-minus-net extraction; never bind it as signed backward reflection. Do not replace native power with |r|^2, clip negatives, fit normalization or accept uncertainty enlarged to cover the discrepancy. Separate duplicate null jobs at every refinement are not required if a genuinely independent calibration demonstrably covers those configurations. Direct-beam inputs need their own native powers.

A pass with a missing input check, invalid error-bound evidence or failed inequality is an evaluator inconsistency; correct the same-submission review rather than publishing a contradictory pass. Missing scientific evidence after complete inspection is distinct from unreadable evidence or failed tool binding. A negative integrated signal may satisfy broad per-angle tolerances but does not establish a resolved weak-reflection measurement. A power-only limitation does not automatically fail independently supported operator measurements. No minimum reflection efficiency applies.

## Paper coverage and input conventions

Leaf003 includes the Gaussian-width analysis in the public protocol. Require the prescribed input's Fourier-derived envelope, both stated intensity widths before and after truncation, and the separate analytical 32-lambda0 interpretation. The article does not explicitly identify an FWHM or 1/e^2 convention: a documented ambiguity is scientifically acceptable, an unsupported equivalence is not. The declared full 1/e^2 intensity width is a comparison case, not an asserted author definition. Never allow it to replace the prescribed Meep Gaussian or adjust the operator thresholds.

Leaf011 is an independent analytical Fig.5 result. Check the public norm, ideal-derivative denominator, one-sided bandwidth, index coverage, physical incidence interval, threshold and quadrature convergence. Inspect the candidate's calculation and figure comparison; no hidden pointwise target or extra FDTD index sweep applies. Numerical convergence criteria do not imply the raster figure is accurate to 1e-4. Accept a justified discrepancy in convention or image reading only when the defined calculation and its comparison are actually completed, not as a substitute for the curve.

Leaf weights total 100, but that score is task completion, not a measured percentage of the entire article reproduced.

## Qualified performance and independent observations

The public Gaussian/Sinc accuracy statement explicitly applies after convergence. For leaves004/005, distinguish a numerical error above its limit from an error below its limit whose required input-specific convergence or genuine angular sampling is not established. State which condition failed and cite that input's actual arrays/comparison; do not describe a passing error as exceeding the threshold. A passing baseline Sinc error alone does not waive this public prerequisite. Leaf009 separately evaluates the required numerical-convergence experiment and comparisons.

This prerequisite is not a global veto: do not propagate a Gaussian-only failure to Sinc, or a performance/convergence failure to independently demonstrated native evidence, power accounting, transfer fitting or spectral moments. Those leaves retain their own stated observations and limits. Never penalize a filename, redundant static input array or report layout, and never adjust a threshold to obtain a preferred score.
