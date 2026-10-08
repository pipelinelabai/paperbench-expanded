# Judge Addendum — 03-dual-passband-angular-stable-fss (private to the judge)

## Native execution evidence placement

For B2_1, count native evidence categories across run.log and the corresponding
original native convergence, mesh-statistics and profile exports, not only inside
run.log. Inspect receipt-bound contents and verify hashes, sizes and the actual
project/design, setup, variation and shared-solve relationship. Native headers may
establish setup identity. Missing transcription of these records or hashes into
run.log is not a failure and must not be reassigned as a deduction elsewhere.
Missing MANIFEST log indices remain B2_5's separate inventory obligation.
File presence and byte agreement alone do not earn authenticity credit. Wrapper
assertions and fabricated keyword lists do not substitute for genuine native
execution. Unreadable native formats are verifier limitations, not scientific zeros.
B1_5 convergence and B1_5b current-run reporting remain separately evaluated.

## Leaf-local replay policy

Judge only the current leaf's requirements. A failed or timed-out other variant,
a missing unrelated artifact, or nonzero top-level replay exit must not by itself
fail this leaf. Cross-variant criteria still require all of their cited evidence.
The verifier binds artifact/source hashes globally, and qualifies native proof
and provenance locally. Do not invent missing metadata or accept fabricated
native outputs. Harmless CSV column order/BOM/whitespace/extra columns and JSON
BOM/key order are not scientific failures. Required field semantics and units
are unchanged. Distinguish candidate missing evidence from truncated/unavailable
verifier context; the latter is a verifier error, not a candidate zero.


This private grading document accompanies tests/rubric.json and refs/.

## Scoring scope

Use exactly 10/10/80 points for stages A/B/C. Stage C allocates 12 points to
normal incidence, 28 to TE angular response, 28 to TM angular response, 8 to
field distributions and 4 to physical invariants and response consistency.
The TE86 and TM83 first/second measured peak losses each carry 10 points.
Their frequency, bandwidth, plateau and other angular checks remain separate.
There is no completeness bonus, repeated aggregate loss penalty or score cap.
All original numerical thresholds and measurement definitions remain unchanged.

Source qualification for numerical leaves must have the same receipt-bound
native-artifact access as the modeling and evidence leaves. Inspect native mode
labels, lattice basis, report expressions and normalization together. Do not
reject an existing correct native mapping merely because the candidate also
described a weak trend heuristic or did not duplicate native settings in prose.
Source qualification itself grants no numerical performance credit.

B2_5 owns missing or invalid MANIFEST log indices. Other items must inspect the
available records and decide actual provenance, transformation coverage or field
semantics; they must not reuse that index defect as their failure reason. Hashes
must match actual native files, but native log lines need not contain hashes.
B1_5b independently checks the current run report's convergence-log references.
B2_6 is an independent platform numerical check of complete native responses and summaries. Candidate self-check scripts, their coverage and their exit status are not scored.
Missing raw ancestors, incorrect excitation, altered bytes, wrong transformations
and fabricated evidence remain disqualifying for affected responses. An existing
artifact omitted or undecoded by the verifier requires an infrastructure-error
classification and renewed inspection, never an inferred candidate failure.

## 1. Variants and geometry facts for group A

All dimensions are in mm. Public facts from Table 1, Fig. 6, and Sec. 2.1: a square unit cell with P=11.0; a duroid-type substrate with εr=2.2, tanδ=0.0009, and thickness SubH=1.0; copper on the upper, incident-side surface only, with paper-specified thickness 0.017–0.035. The solver may select a value in that range or an equivalent conductive sheet, documented in README/meta. The aperture pattern, from the center outward, is: central circular aperture r=1.5 (R4) → metal annulus 1.5–3.0 → inner annular slot 3.0–3.5 (R3+W3) → metal ring 3.5–4.5 (W2) → outer annular slot 4.5–5.0 (R2/R1/W1) → metal border 5.0–5.5 (g/2=0.5). Four X-shaped slots are centered on the diagonals at radius R5=6.0, with coordinates (±4.243, ±4.243), arm length L1=2.0, width W4=0.4, and orientation ±45°. They appear as X shapes in an edge-aligned view (Fig. 2c/6), but as + shapes in Fig. 1 because the entire 3D view is rotated 45°. The inner endpoint of each radial arm touches the outer edge of the outer slot (R5−L1/2=R1).

All 8 variants share the same geometry and differ only in scan angle/polarization:

| variant | Polarization | θ | Paper source |
|---|---|---|---|
| te_00 / tm_00 | TE / TM | 0° | Fig. 8 (HFSS dashed curves), Fig. 9, Table 2 row 1, and normal-incidence bandwidths in the text |
| te_30 / tm_30 | TE / TM | 30° | Table 2 row 2 only; the paper has no 30° curves |
| te_60 / tm_60 | TE / TM | 60° | Green curves in Fig. 10 / Fig. 11 and Table 2 row 3 |
| te_86 | TE | 86° | Blue curve in Fig. 10, Fig. 5(a) inset, and Table 2 row 4 |
| tm_83 | TM | 83° | Blue curve in Fig. 11, Fig. 5(b) inset, Table 2 row 4, and 83° bandwidths in the text |

Task conventions from addendum Clarification 1, used for B1_2/B1_4: the incidence plane is x–z (φ=0°, along a principal lattice axis); θ is measured from the +z normal; TE has E perpendicular to the incidence plane (along y), and TM has E within that plane. The four meta.json fields must agree. Equivalent descriptions such as "phi=0" or "E-field along y for TE" are acceptable.

CSV contract: 3.00–16.50 GHz in 0.01 GHz steps, 1351 rows, with columns `frequency_GHz,S11_dB,S21_dB`.


## Scoring policy

Use only the current rubric leaves, public addendum, and this document. Multiply leaf weights along the tree; there is no group-wide invalidation. The gate_policy in `config/evidence_policy.json` is leaf_local, retaining per-item native-evidence qualification checks. Do not interpret isolation, solver, or judge infrastructure failures as deficiencies in the model's scientific ability.

- `code_numeric` is evaluated by numeric_checks, with full/zero credit determined by the check. Evaluate `llm_binary` against the public proposition; for a fail_only check, assess the mechanical subchecks before the manual content. Do not claim to have executed helper scripts that were not called.
- For HFSS numerical items, first check the MANIFEST, hashes, and derivation chain for their actual input files, then inspect native expressions, physical solutions, source data flow, and algorithms. The current review record may be reused for the same file set. Do not claim independent recomputation of a full-sphere integral or global maximum from file excerpts. The overall native-data audit still requires at least five response samples with sufficient inputs. Provenance evidence_status distinguishes candidate_missing from verifier_incomplete; the latter is a grading infrastructure error, not grounds for penalizing the model because the verifier truncated evidence. Invalid provenance affects only dependent leaves and cannot be compensated by a value falling inside a numerical window.  B2_6 uses trusted code on replay-bound data without invoking candidate validation code. Invalid numerical data fail; unsupported verifier readers leave the score null. Do not demand a candidate self-check script or grade its implementation.
- Convergence requires native adaptive metrics and a successful native status; native Delta Energy is acceptable for finite plane-wave scattering. Process completion alone is not adaptive convergence. B1_5b reads the static README and current results/run_summary.json. A shared physical solution may cover multiple variants through a mapping. Historical reports need not match new runs value for value.
- Native images may be copied and hash-checked; meta/structure/README/nominal inputs are not raw responses.  Offline dependency errors remain submission errors.
- Verify legitimate transformations such as complex-to-dB, magnitude/phase conversion, and integration. Native data and results need not contain identical strings. Sample at least five electromagnetic response quantities; frequency/angle coordinates are not substitutes. Sample files, inputs, transformations, recomputed values, and errors must be verifiable.
- Read the explicitly listed results/<variant>/structure.json files and verify object construction and parameter roles. A filename listing of hfss/ does not constitute reading project contents. Equivalent algebra, shared constants, and resolvable structured references are acceptable; the same fact need not be repeated across multiple fields.
- Optimetrics parent logs may be identical, but each variation's geometry, scan angle, modes, solution, and export mapping must be genuine and traceable. Equal log hashes do not by themselves prove copying; different hashes do not prove independent solves. allowed_shared_solve_groups permits shared session logs, not reuse of responses across different physical variants.
- The PAPERAUDIT checklist contains verification examples, not a hidden discovery quota. Assess A9 against the three public review domains; at least two substantive checks with complete evidence and resolution suffice. Disregard each incorrect finding individually. Finding no contradiction is not itself penalized. New findings must rely on the paper's text/figures and need not match private wording.
- Do not interpolate refs to invent new hard acceptance criteria. Sparse graph readings are not control solutions and cannot replace a control reproduction in the same environment. Excluded readings and noncomparable quantities must not become implicit deduction criteria.
- Distinguish insufficient evidence, physical-result deviations, and format/derivation inconsistencies item by item. One upstream discrepancy may affect multiple metrics; do not describe every resulting deduction as an independent ability deficit. Grade only against the rubric, without moving thresholds.

## FSS assessment conventions

- TE86 values at 8.05/8.80 GHz are not −3 dB crossings in the PDF and must not be used as band1 edge, width, or shape references. The approximate 0.2 GHz width, with a conservative pixel range of 0.14–0.28, is diagnostic only, not a narrow acceptance window. C2_3 checks angular narrowing and positive bandwidth; TE60 width is assessed separately.
- The fixed peak windows band1 [3,9.5] and band2 [11.5,13.6] are public main-passband identification conventions. The latter precedes the earliest air-side grating onset near 13.64 GHz and covers the main peak in Fig. 5; passband edges may extend beyond the peak window. C3_2 has no private any fallback. Summaries and checks use the same algorithm.
- Distinguish no_passband, truncation, undefined dependencies, not_applicable, and solve_failed. tz2=null outside TE86 is prescribed N/A and needs no per-item README explanation. Resolve tied extrema at the lowest frequency; search for the second transmission zero after the band2 upper edge.
- Keep R5=6.0, W4=0.4, and the nominal contact relationship unchanged; do not change dimensions to solve meshing problems. Rotating the entire view is not rotating a feature relative to the lattice and does not establish an X/+ orientation contradiction.
- TM0 band edges and first measured peak loss are independent items; use the weights in the rubric. The first-peak insertion-loss threshold is −0.89 dB, and 8.45 GHz remains a separate diagnostic. Mode mapping may use one structured source. The specular power sum is required only to be <=1.005, not equal to 1.

## Paper-backed alignment

Trust reported paper observations only at stated conditions. Evaluate the required evidence without assumptions about additional runs or unmeasured runtime. Keep candidate-native evidence and leaf-local provenance requirements. Read the public addendum's comparison conditions and Licensed HFSS environment section.

The angular result items, including the children of C2_2, C3_2 and C3_3, require the numerical performance stated in the public addendum and rubric. They are not characterization-only credit. Extra windows in extraction notes/reference material are diagnostic, not additional acceptance conditions. Independently inspect the required measurements and honest comparison. Do not grant credit merely for saying that a result disagrees. Do not require calibration runs beyond the public requirements.

Normal-incidence loss checks C1_1/C1_3_loss/C3_6 use measured per-band peak values. Table 2 is not proof that each oblique center is exactly 8.45/12.76 GHz, and phi=0 is a task convention, not a paper fact.
