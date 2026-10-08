# Common evidence and replay contract

The task-specific contract defines the scientific question. The bundled article is the source of scientific claims; explicitly labelled benchmark adaptations are not attributed to the authors. Report a substantiated discrepancy rather than fitting an answer to the article. An unresolved result must identify the actual missing evidence, not replace an available computation with generic uncertainty language.

## Execution and evidence

Work in `/home/submission`. Submit editable source and static inputs, plus a no-argument `bash reproduce.sh`. A preparation-stage full clean replay is not required. The verifier must regenerate all production calculations and analyses offline within the separately frozen native budget. Preparation probes cannot substitute for production evidence.

Keep immutable code and data in `src/` and `inputs/`. Generated content belongs in `outputs/`; the verifier clears this directory before replay. Do not change source or static inputs during replay. Preserve partial outputs and failures without inventing missing numerical results. A fresh calculation of an identical state may be reused within the current replay if the model, coordinates and native record are exactly identified; changing a record's label is not a new calculation or an independent control.

Provide `outputs/evidence_manifest.json`, mapping logical observations to regular relative file paths, units, case IDs, array columns, native run IDs and checksums. Equivalent JSON, CSV, NPZ or HDF5 representations are acceptable. Splitting an axis across files is acceptable if sample identities are explicit, duplicates are checked, and the union has the required coverage. Native order, plot layout and optional explanatory fields do not determine scientific correctness. A particular RNG spelling or redundant reporting of the same observation is not an additional measurement.

Native logs, input decks, raw coordinates/fields/eigenvalues, analysis source and machine-readable final measurements must be available to the isolated read-only grader. An inaccessible evidence file is a replay/reader problem to diagnose, not proof that the scientific observation is zero. A candidate-written receipt alone is not trusted engine provenance. Private evaluation resources and reference result arrays are not candidate inputs.

Include a concise generated report and the task's requested figures. Figures illustrate retained data; a picture is neither a substitute for raw values nor an additional full scientific result. Interpretation must cite the regenerated observations. An LLM judge may assess whether reasoning follows the evidence, but must not replace deterministic arithmetic, state matching or native-provenance checks.

## Numerical precision

The object being reproduced is fixed; numerical implementation is not. State numerical uncertainties and retain controls that justify them. Controls measure sensitivity and do not automatically constitute rigorous mathematical error bounds. Comparison with a paper using a different computational model is distinct from same-model agreement.

Numeric reference envelopes require independent numerical validation and may not be selected from a tested model's output. Do not introduce a hidden method, a new target, or a retrospective change to obtain agreement.

Missing native evidence invalidates dependent numerical claims, not unrelated successfully computed cases. Zero, negative and inconclusive scientific findings are not automatically wrong.

The complete finite study requires valid raw evidence, recomputation and justified interpretation. Running a pipeline, matching a broad literature window, or writing all requested headings is insufficient by itself.

# Fixed study and observable definitions — 09

## 1. Inputs and model

Only the supplied syn-CPP TSre and TSsi structures are in scope. `inputs/initial_states.json` fixes atom order, masses, coordinates in angstrom and velocities in bohr/atomic-time. Its associated checksums and public provenance define the problem. No random sampling, coordinate displacement, transition-state search or reinitialization is required of the solver.

Use gas-phase RKS B3LYP-D3(BJ)/6-31G(d), charge +1, spin 0, GPU4PySCF with the released image/dependencies, DFT grid level 1, SCF energy convergence 1e-8 hartree, maximum 150 iterations and no solvation. Use the native analytic nuclear gradient including the stated dispersion treatment. `model_manifest.json` pins the calibration image and direct, non-density-fitted RKS implementation (no auxiliary basis), package versions and grid defaults. Changing the Hamiltonian or integral approximation is not an optimization option. Cross-platform state equivalence and numerical error envelopes are not established by the supplied model manifest.

At the initial frame use an ordinary fresh RKS guess. Later frames may start fresh or carry the preceding converged RKS density; record the actual method and verify the same RKS state. Do not change to UKS, a force field, a learned potential, cached force arrays or an interpolated force surface. Different SCF roots must be investigated before asserting same-state agreement, not hidden by a wide trajectory tolerance. GPU execution is allowed and required by the planned native resource profile.

## 2. A finite, predeclared experiment

| Family | IDs / initial state | dt | End time | Count |
|---|---|---:|---:|---:|
| Primary | tsre-01..04, tssi-01..04 | 1 fs | 40 fs | 8 |
| Momentum reversal | tsre-01-reversed, tssi-01-reversed | 1 fs | 20 fs | 2 |
| Numerical controls | primary tsre-01, tssi-01 and their two reversals, each suffixed `-halfstep` | 0.5 fs | 20 fs | 4 |

The control cases are selected by ID before observing an outcome. They are not new ensemble members. Include frame zero and every subsequent full-step velocity-Verlet frame, with post-update velocities. This gives 534 logical frame records before any explicitly identified within-replay reuse of identical initial electronic states. Every distinct propagated geometry requires a freshly computed native energy/gradient. Receipt reuse at identical initial states is not independent execution evidence.

The primary initial velocities are the previous public thermal-plus-1-kcal/mol-mode-kick construction at 298.15 K, now supplied as data. Reversed cases use `v_reversed = -v_thermal + v_kick`, with identical coordinates, total initial kinetic energy and positive reactive kick. This changes only the transverse thermal component, not the forward reaction-mode direction. It is a benchmark counterfactual, not the paper's QCT ensemble preparation.

Use NVE velocity-Verlet with the supplied unit constants and masses. Retain native SCF identity/status, total electronic energy, gradient, coordinates, full-step velocity and actual time for each frame. Preserve failed continuous prefixes without early-success labels. A 20 fs control does not establish the numerical convergence or terminal chemistry of a 40 fs primary trajectory.

## 3. Fixed observables, not open-ended storytelling

All indices below are zero-based in the supplied atom order. At 0, 10, 20 and 40 fs where available, compute distances `d_B=distance(44,48)`, `d_C=distance(38,48)`, `d_D=distance(41,48)` and the two-component contrast `q=(d_C-d_B, d_D-d_B)` in angstrom.

For every primary trajectory report `q(0)`, `q(time)-q(0)` and both proton distances. For each TS condition report the arithmetic mean of the four changes; report TSre minus TSsi differences at each common time. Decompose the absolute condition contrast exactly into initial-geometry contrast plus subsequent-motion contrast. This decomposition does not claim that a distance difference measures orbital overlap.

For each selected pair, report `q_reversed(time)-q_primary(time)` at 10 and 20 fs, together with the four half-step controls at the same times. The geometry is identical within a pair, so the difference is an effect of the specified velocity intervention in this deterministic model. It does not isolate one chemical orbital, prove a population-wide mechanism, or establish terminal product selectivity. Retain the full distance vector so motion toward D cannot be hidden by a B-versus-C-only comparison.

Report time-step changes separately for both members of each pair and for their difference. Quantify whether each component is numerically resolved using the publicly specified numerical error envelope plus the observed control sensitivity. State when only sensitivity, not a rigorous bound, is available. Do not choose a favorable endpoint, sign convention or effect-size threshold after seeing the results. An unresolved sign can be correct; missing numerical comparisons are not full-credit uncertainty analysis.

## 4. Primary 40 fs classification and accounting

Always retain the two proton distances and all three product distances. At frame 40 apply these ordered tests: if `distance(24,25)<1.2 A`, label `reactant`; otherwise if `distance(25,50)>=1.2 A`, label `incomplete`; otherwise sort B/C/D by `(distance,label)`, label `ambiguous` if the second-smallest minus smallest distance is `<0.01 A`, and otherwise label `toward_B`, `toward_C` or `toward_D` from the smallest distance.

These are operational **short-time commitment labels**, not confirmed final products. Boundary equality follows the inequalities above. Report the distance from each active decision boundary. Labels near numerical uncertainty must be flagged; do not change the boundary to obtain a preferred label.

For each condition report all six label counts, completed count out of four, fractions using all completed primary trajectories, and Wilson 95% intervals (`z=1.95996398454`) for every label, including zero counts. Failed trajectories are missing, not deleted successes or silently assigned products. Provide worst/best bounds on each full-four fraction by assigning missing cases to nonmembership/membership. Counterfactuals and half-step controls never enter this denominator. Intervals are descriptive small-sample diagnostics, not proof that four deliberately fixed initial states represent the author's ensemble.

No prewritten “supported” verdict is required. The answer consists of these numeric contrasts, counts, intervals and their justified scope. Do not substitute the article's percentages or demand its favored product as an answer key.

## 5. Validation and deliverables

Recompute initial-state identity, velocity-Verlet updates, gradient norms, kinetic/total energy, classification, contrasts and uncertainty accounting from retained raw arrays. Check energy drift with correctly matched velocities and energies; a low electronic-energy drift alone is not NVE conservation. Relate drift and SCF failures to the timestep controls without inventing a new trajectory after an unfavorable result.

The consistency scales are: initial-coordinate difference <=1e-6 A; initial-velocity `atol=1e-12`, `rtol=1e-8`; per-step VV coordinate and velocity residuals <=5e-8 in atomic units; reported distance and fraction error <=1e-6; Wilson endpoints <=1e-4. These do not define cross-platform physical trajectory uncertainty. The supplied policy does not establish independent trajectory/electronic-state and effect-resolution error envelopes; observed sensitivity alone is not a rigorous cross-platform bound.

Deliver per-run raw frames and native logs; a primary classification/count table; geometry-versus-motion and paired-intervention curves; timestep/energy diagnostics; and a concise evidence-backed comparison with the paper. An implementation may batch, cache identical initial states within replay, or choose GPU scheduling, but may not remove requested cases or reduce force fidelity.

Out of scope: 500 fs product statistics, additional diastereomers, IRC/PES/PCA reconstruction, NBO analyses, enzyme effects and new random ensembles. Do not claim that this reduced experiment reproduces those parts of the article.

A correct RNG name, a declared success flag or a printed paper conclusion is not itself a measurement. One failed case does not erase separately valid cases in the rest of the study.
