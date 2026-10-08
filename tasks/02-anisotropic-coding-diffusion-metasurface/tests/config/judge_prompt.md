# Judge Addendum: Anisotropic Coding Diffusion Metasurface

This is private evaluation material used with `rubric.json` and `refs/`.

## Geometry and variants

All lengths are in mm. The square period is a=10; the centered rectangular patch
is px=9.5 along x and py=7.4 along y. The F4B substrate has h=3, relative
permittivity 2.65 and loss tangent 0.001, with a complete metal ground. The paper
reports 0.036-mm copper layers. Copper solids, appropriate sheet treatments and
an explicitly explained PEC approximation are accepted, while retaining substrate
loss. A lattice contains 4 x 4 equally oriented elements with d=40. The array is
6 x 6 lattices, or 24 x 24 elements, on a 240 x 240 x 3 board.

Bit 1 denotes px along x; bit 0 rotates it 90 degrees about z. Global relabeling
is allowed only with the corresponding decoding change and unchanged physical
layout. Rows run along +x and columns along +y. The Fig. 3(c)/Fig. 4 optimal matrix
is balanced 18/18:

```
1 1 1 0 0 0
1 0 0 1 1 0
0 0 1 0 0 0
1 0 1 1 0 1
1 0 1 0 1 0
0 1 0 1 1 1
```

The initial matrix has three all-one rows followed by three all-zero rows.
The PEC reference is a bare 240 x 240 metal plate without dielectric, as specified
by public Clarification 2. The physical-optics comparison sigma=4*pi*A^2/lambda^2
gives about 8.7 dBsm at 4 GHz, consistent with the Fig. 5 reference interpretation;
it does not replace the required native reference solve.

| Variant | Required model/response | Paper location |
|---|---|---|
| unit_normal | Periodic element, x/y reflection magnitudes and phases | Fig. 1 |
| unit_tm15 / unit_tm30 / unit_tm45 | TM incidence in the xoz plane; both element orientations | Fig. 7(a) |
| af_patterns | Eq. (2) numerical AF for three matrices; no HFSS required | Fig. 3 |
| array_ms | Finite 24 x 24 array, normal x/y total RCS, reduction, 5.86 GHz current and far-field figures | Figs. 5, 10(a), 6(a)/(e) |
| array_pec | Same-size bare metal reference | Figs. 5, 6(b)/(f) |

Response CSV grids contain 81 rows from 4.00 to 8.00 GHz at 0.05 GHz steps.

## Evidence and scoring

Use only the current rubric leaves, the public addendum and this note. Multiply
weights along the rubric tree. There is no group-wide cascade to zero. Judge only
the current leaf: another variant's failure, an unrelated missing artifact, or a
nonzero top-level exit is not by itself a failure of this leaf. A cross-variant
criterion still requires every physical solution that it actually specifies.

The verifier binds source and artifact hashes globally and qualifies native proof
locally. Do not invent metadata or accept fabricated native exports. Equivalent
CSV column order, BOM, whitespace, extra columns, JSON key order or numeric spelling
is not a scientific failure; required field meanings and units remain unchanged.
Distinguish missing candidate evidence from incomplete verifier context. Context,
transport and infrastructure failures must not be reported as candidate zeros.

- `code_numeric` uses the declared deterministic check. `llm_binary` evaluates the
  public proposition. For `fail_only`, evaluate the mechanical check and then the
  manual remainder. Do not claim to have executed an unused helper.
- Before scoring native numerical results, check their actual input files,
  manifests, hashes, transformations, native expressions, physical solutions and
  source dataflow. Reuse a source review for the same file set within this review.
  A partial file excerpt cannot establish a complete sphere integral or global
  maximum. Review at least five response samples with sufficient native inputs;
  frequencies and angles do not count as response samples. Record the input,
  transformation, recomputed value and error at the public direct/derived tolerances.
- A missing or invalid source chain affects only leaves relying on it. A number
  inside a target window cannot replace native proof. Use `candidate_missing` and
  `verifier_incomplete` distinctly. The latter is an infrastructure error.
- B2_6 requires the trusted offline execution receipt and actual source coverage.
  An execution failure does not pass; absent infrastructure leaves the score
  unresolved. Exit zero alone is not proof that the checker covers every response.
- Native adaptive convergence and its reported status are required. Portless
  incident-wave problems may use native relative Delta Energy. Process completion
  is not adaptive convergence. B1_5b reads the static README and current
  `results/run_summary.json`; do not require replay to rewrite the README.
  Distinct variants may reference one genuinely shared physical solution where
  allowed, without repeating its statistics. Historical statistics need not equal
  the new run's values.
- Native images may be copied and hash-checked. Metadata, structures, README and
  nominal inputs are not native response arrays. Legitimate complex-to-magnitude,
  phase, dB, unit, normalization and integration transformations are allowed;
  native and derived values need not contain identical text strings.
- Read the relevant `results/<variant>/structure.json` and inspect actual geometry
  and parameter roles. A list of project filenames is not a project inspection.
  Equivalent algebra, shared constants and resolvable structured references are
  allowed; do not require redundant copies of the same fact in several fields.
- Optimetrics variations may share a session log, but geometry, scan, modes,
  solution and export mappings must remain distinguishable. Equal log hashes do
  not prove copying; different hashes do not prove independent solves. Declaring
  a shared session does not allow different required physical responses to be reused.
- PAPER_AUDIT examples are not a hidden discovery quota. A9 covers the three public
  audit domains and at least two substantive, evidenced checks with resolution
  and impact. Verified consistency may pass. An unsupported finding receives no
  credit for that finding, without erasing other valid checks. No private wording
  match or mandatory contradiction is required.
- Sparse paper readings are not control solutions. Do not interpolate new hard
  thresholds from references or reinstate withdrawn, non-comparable quantities.
  Distinguish physical disagreement, missing evidence and derivation/format errors.
  One upstream error may affect several metrics; these are not necessarily
  independent ability failures. Do not move thresholds to fit a candidate.
- Trust paper observations only under their stated conditions. A
  characterization criterion requires genuine measurements and an honest
  comparison; merely stating disagreement does not earn credit. Read the public
  comparison-scope and licensed-environment requirements.

## Physical interpretation

- z=h is the task reference plane, not a known author phase reference. Verify
  native x/y phase origins and the circular difference identity without absolute
  paper-phase or zero-crossing cutoffs. C1 weights are amplitude 20%, provenance
  10%, identity 10% and physical phase difference 60%; retain the peak-height,
  peak-frequency and connected-band criteria separately.
- Outputs use exp(+i*omega*t). At normal incidence, reflected and incident
  co-polarized electric fields use the same laboratory direction. Follow the
  public incident/reflected TM vectors at oblique incidence. Convert opposite
  internal conventions before export; conjugation that changes 205 to 155 degrees
  or an arbitrary reflected-basis sign is not the same declared convention.
- Score oblique peak heights and frequencies independently at the rubric windows.
  A shared reference-plane shift cannot explain a differential-phase discrepancy.
- AF does not require AEDT raw files or run.log. Independently check Eq. (2), the
  declared matrices, full fixed-grid arrays, derived summaries and input/source
  hashes. Self-reported values such as 12 or 26.7 are insufficient. Physical patch
  reversal with unchanged decoding is not equivalent to bit relabeling.
- Finite-array, PEC, reduction and Fig. 6 far-field quantities use total RCS.
  x/y identify incident polarization, not selected received components. Require
  native RCSTotal or both orthogonal scattered-field components; never assume a
  missing cross component is zero. This is a task convention, not a demonstrated
  identification of the paper's receiver component.
- Characterization-only leaves are C4_1, C4_2, C4_3, C4_4, C4_5_envelope,
  C4_5_coverage, C4_6, C4_7 and C4_8. Apply their current rubric descriptions and
  measurement requirements. Reference performance windows, including the former
  outer-envelope/core suppression cutoffs, are not acceptance conditions.
- Report strict intervals as connected grid components, not disconnected outer
  envelopes. A phase wrap may cross a branch boundary, but a +180/-180 jump is
  not a zero crossing. Honest characterization still requires actual calculations,
  correct quantities, native provenance and comparison under stated conditions.
