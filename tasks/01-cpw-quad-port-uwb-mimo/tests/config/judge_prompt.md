# Judge Addendum: CPW Quad-Port UWB MIMO

This is private evaluation material used with `rubric.json` and `refs/`.

## Geometry and variants

Evaluate the public documented-reconstruction scope, not a uniquely known author
CAD. Table 1 values and Fig. 3 topology remain the evidence: FR4, single-sided
metal, CPW feed, circular radiator/ground cutout, notches, protrusion and stub.
Classify feature endpoints and coordinate equations as reported or inferred.
W4 association, g endpoints, L4 association and a derived 3.25-mm feed offset are
not hidden author-exact constraints. Retain reported values, inspect the supported
reconstruction and native readbacks, and require consistency across six variants.
Distinguish the reported empirical g=1.56 from the defined constructed distance.
Do not change other nominal dimensions to force that distance or a spectrum.

| Variant | Structure | Difference from nominal |
|---|---|---|
| mimo_final | 38 x 38 mm, four ports, four elements related by 90-degree rotations about the board center | Table 1, H2=11.2 mm, stubs present |
| single_initial | 19 x 19 mm single element, Fig. 1(a) | No stub |
| single_stub | 19 x 19 mm single element, Fig. 2(a) | Stub present |
| h2_10p7 / h2_11p7 | Full four-port array | Only H2 changes to 10.7 / 11.7 mm in all four elements |
| mimo_nostub | Full four-port array | Only the four stubs are removed |

S-parameter grids have 0.02 GHz steps: 3-20 GHz for four-port variants and
2-20 GHz for single elements. Efficiency, gain and MIMO metrics use 0.25 GHz steps
over 3-20 GHz. Figs. 4 and 6 sweep the four-port array; see the cross-figure
comparison in `refs/extraction_log.md`.

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

- The text's 3.7 GHz value is the first resonance, not the lower band edge.
  The stated DG > 9.97 is consistent with ECC=0.0745 and Eq. (7), giving
  approximately 9.972209. This formula check is not a new digitized DG reference.
- Fig. 10 does not establish the mapping between its axes and the antenna.
  C7_1 checks genuine patterns, the public local basis, per-cut normalization and
  the comparison report. Do not impose unsubstantiated fixed xy-ripple or yz-null
  cutoffs, or call them rotation invariants.
- Follow B1_4's native four-port contract. Selecting four entries from independent
  slot ports in an eight-port model does not meet it. Complex reciprocity tolerance
  is 0.02; use the public power sums, GainTotal, radiation/total efficiency,
  embedded-field ECC, DG and multiplexing-efficiency definitions.
- C6_1 separates three gain levels, low-to-mid-band rise and high-frequency
  ordering with weights 60/20/20. Retain the rubric windows and 1.5 dB rise threshold.
- C8_1 requires native current images at 3.5, 9, 14 and 19 GHz, with actual
  excitation/frequency evidence. Principal morphology comparisons concern
  Fig. 9(a)/(d); no extra hotspot threshold applies to the two middle frequencies.
- Single-sided topology, nominal dimensions, H2 controls and stub differences
  remain required. Offline contract tests do not certify physical reproduction
  or settle metal, excitation and far-field integration uncertainties.
- C6_3 is characterization-only. Reference performance windows are comparison
  context, not acceptance conditions; apply its current measurement requirements.
- A2/A3/A5 accept an evidenced reconstruction with reported/inferred geometry
  distinguished, not an assumed unique g/W4 endpoint assignment. A6 topology,
  A8 one-template controls and primary matching, isolation and radiation criteria
  remain unchanged. This scope does not grant automatic performance credit.
