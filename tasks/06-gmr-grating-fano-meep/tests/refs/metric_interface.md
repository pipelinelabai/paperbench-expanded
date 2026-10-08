# Paper-backed characterization metric interface

The executable schema is `METRIC_SPECS` in `tests/src/scientific_metrics.py`, exposed
by `describe_scientific_metrics`. These array-only operations never prove native
execution or award a score. Retain the original arrays and independently verify
their source, units, physical ports and run identity.

`fano_scan` requires frequency in 1/um and context `spectrum_width_um`, one of
0.030, 0.050, 0.070, 0.150 um. Bind dimensionless complex `reflection_amplitude`,
or matched `reference_field`, `total_field`, `reference_frequency` with the actual
monitor/interface positions and propagation sign. The fields must establish the
reflected-side zero-order port, not an arbitrary point sample. An optional
`sample_width` column selects one physical width from a combined table; otherwise
the arrays must already describe that width. No branch/window selector is allowed.
Call separately for all four widths. No new candidate manifest is required.

Outputs are original sample count, wavelength extent, coverage of [1.25,1.75] um,
maximum native wavelength/frequency gaps, complex spectral variation and the same
64-epsilon roundoff diagnostic used for fitting. At least two samples are needed
to describe an extent; this is not a sufficient-resolution criterion. Coverage
uses only a 1e-12 um floating-point endpoint allowance, not physical extrapolation.
There is no universal new coarse-search spacing threshold. Search resolution must
be justified by native sampling, source/duration/probe evidence and refinements.
`resolved_pole_count` is null and `absence_established` and
`sampling_convergence_established` are false: these conclusions require separate
evidence, not an inferred pass. Missing/nonfinite/duplicate or unmatched data fail.

`fano_pole` remains required additionally for every claimed isolated pole.
Its original identifiability, residual, sampling, positive-linewidth and window
requirements are unchanged, as are independent mode/grid/time/sampling checks.
It can bind a native local window directly or select actual samples with
`fit_frequency_bounds`. A null physical Q is never a valid pole; a successful
optimizer and `physical_pole_valid` alone do not establish resolved sampling.
No fictitious fit call is required for a supported sensitivity-limited absence.

The characterization leaves require `fano_scan` so the generic required-operation
gate does not demand a nonexistent pole. They additionally require native evidence
for all features, supported absence/overlap/applicability and all relevant checks.
Conditional `fano_pole` execution is enforced by the scientific rubric/judge, not
silently inferred from a scan. `power`, `bilayer` and `compare` are retained;
`compare` binds independently generated observables even when Q is undefined.
Null results, missing controls and declarations of inapplicability do not earn
automatic credit or renormalize the rubric weights.
