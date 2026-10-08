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

# Fixed study and observable definitions — 10

## 1. One physical system and explicit implementation variants

Use a neutral nonmagnetic three-atom H-phase MoS2 primitive cell, vectors `(a,0,0)`, `(-a/2,sqrt(3)*a/2,0)`, `(0,0,c)`, with Mo at fractional `(1/3,2/3,1/2)` and S at `(2/3,1/3,1/2 +/- h/c)`. For the primary study fix `c=20 A`; start with `a=3.18 A`, `h=1.56 A`. These are benchmark starting conditions, not a paper equilibrium result. Preserve the H-phase and center/mirror conventions; do not substitute another polymorph or optimize vacuum height.

For the primary property study use the supplied QE image and exactly the four public scalar/fully-relativistic Mo/S PAW files identified by the source manifest. PBE and Fermi-Dirac smearing 0.05 eV are fixed. The PAW baseline is 60 Ry wavefunction cutoff, charge-density cutoff at least 8x larger, and the article's even Monkhorst-Pack density convention: `mesh_i=max(1,2*ceil(density*norm(reciprocal_i)/2))`, where reciprocal vectors include `2*pi`; use one point along z and no fractional grid shift. Baseline densities are 6 A for relaxation and 12 A for post-relaxation SCF. Retain the actual meshes, not just nominal densities.

Use scalar-relativistic no-SOC relaxation to define the common geometry. Hold this geometry fixed across the electronic comparisons. Choose tighter numerical settings as needed and retain baseline versus refined results; do not change the functional, smearing, pseudopotentials or physical boundary condition when calling a change “numerical convergence”. A separate larger-c calculation is a finite-vacuum control and must not silently replace the fixed-c primary answer.

The two primary electronic variants remain S (scalar-relativistic PAW datasets, no SOC) and F1 (the supplied fully-relativistic PAW datasets, SOC enabled with the spinor implementation). Both require the complete path, two-dimensional edge and mass studies. Do not replace these primary datasets with the auxiliary datasets below.

The installed QE/PAW non-SOC averaging route rejects the supplied fully-relativistic ultrasoft/PAW datasets. The auxiliary norm-conserving pair is N0 (SOC off) and N1 (SOC on), using the same two fully-relativistic PseudoDojo UPFs in `inputs/soc_control_pseudo/`, provided as `Mo-sp_r.upf` and `S_r.upf` with their original upstream headers. Do not edit their headers or interchange PAW and NC results. The supplied NC datasets retain Mo 14 and S 6 valence electrons, PBE and the same common PAW-relaxed geometry and smearing. Use matched numerical settings within N0/N1, choose and validate NC-appropriate cutoffs, and independently refine both members. N0/N1 require native SCF and K-point band measurements, not additional full paths, fundamental-gap searches, vacuum studies or mass campaigns. This auxiliary comparison is a benchmark diagnostic, not the paper's PAW calculation or an isolated PAW SOC measurement.

The unique primary target is this fixed-model H-phase solution and its observables within independently validated numerical precision, not exact equality to a different code's rounded literature numbers. If a distinct self-consistent or structural branch survives the declared model, retain the evidence; a single-branch conclusion is not established until that ambiguity is resolved.

## 2. Geometry and elastic response

Retain initial/final structures, maximum per-atom force norm and full in-plane stress. Require native relaxation convergence, force <=0.01 eV/A, maximum absolute in-plane stress <=0.002 eV/A^3, and at least 15 A between outer S planes of periodic images. A already-converged starting geometry needs no artificial displacement or minimum iteration count.

Measure relaxed-ion normal strains independently in x and y: retain the article's +/-1% points plus at least one smaller symmetric pair of your choice. Hold each strained cell fixed while relaxing internal coordinates. Report independent `C11=d(tau_xx)/d(epsilon_xx)`, `C22=d(tau_yy)/d(epsilon_yy)`, `C12=d(tau_xx)/d(epsilon_yy)` and `C21=d(tau_yy)/d(epsilon_xx)` at zero strain. Do not impose hexagonal equalities before measurement. The headline target is the zero-strain derivative; finite-range fits and sensitivity to range are retained measurements, not interchangeable definitions of the target.

Determine the native stress sign and convert to 2D N/m using the actual c. Demonstrate fit quality and the effect of a smaller strain range; a high R-squared alone does not bound a biased derivative. Separate geometry, SCF/k/cutoff and finite-strain sensitivity. Native-confirmed relaxed ions at every strain are required; one convenient clamped-ion fit does not answer the question.

## 3. Bands, SOC and vacuum

For S and F1 retain at least 400 distinct native path samples on Gamma-M-K-Gamma. Use reciprocal fractional coordinates Gamma=(0,0), M=(1/2,0), K=(1/3,1/3) for the cell above, and cumulative Cartesian reciprocal distance for the path axis. Endpoint duplicates do not count twice. Additional path sampling is a method choice, not a different answer. Retain all occupied bands and enough unoccupied bands for the defined edge/mass windows; electron/band-count arithmetic is a consistency check, not an additional physical measurement.

Locate VBM/CBM for S and F1 over the two-dimensional first Brillouin zone with native supporting samples and report whether the fundamental gap is direct; a path minimum alone does not prove the global edge. Report both the fundamental gap and direct K gap for S and F1. State the searched region and refinement; do not assume the literature's location as a substitute for evidence. A K-only N0/N1 calculation must not be described as its fundamental gap.

At the common geometry report native direct K gaps and valence/conduction spin splittings for the auxiliary pair. Distinguish implicit scalar spin degeneracy in N0 from separations between different orbital bands. For the direct K gap only, compute `Delta_SOC_NC=gap_K(N1)-gap_K(N0)`, `Delta_off_model=gap_K(N0)-gap_K(S)` and `Delta_on_model=gap_K(F1)-gap_K(N1)`. Verify that the three terms sum to `gap_K(F1)-gap_K(S)`. The first term is the SOC-switch contrast within the fixed NC model; the other terms compare implementations/datasets and are not universal pseudopotential errors. This identity does not isolate the unavailable same-PAW SOC-off effect or license a claim that the NC effect equals it. All four gaps must be native measurements with numerical sensitivities. Retain native spin expectation evidence for F1 and identify the convention and units; no arbitrary basis vector in a degenerate subspace is a unique spin answer.

Use the plane-averaged electrostatic potential for vacuum referencing. Retain both far-vacuum plateau intervals and their difference; report VBM/CBM relative to their mean for this symmetric slab. Require max absolute plateau slope <0.01 eV/A, and test sensitivity to the chosen interval and finite vacuum. Do not use the interior minimum, a Fermi-level shift or a paper figure for another material as the reference.

## 4. Masses: identifiability before a fitted number

Follow Section 2.11: two-dimensional cubic fitting, every band within 100 meV of each selected edge, and diagonalization of the curvature tensor, with and without SOC. Report K-centered masses for the paper comparison, and masses at actual fundamental extrema if distinct. At each center define the window using its local valence maximum/conduction minimum; list the energies and offsets before selecting branches.

First test the literal paper disc radius 0.015 A^-1 and density 45 A. For this reproducible diagnostic, realize the density as a center-containing square Cartesian grid of spacing `1/45 A^-1`, restricted to the closed disc. This grid-origin/shape convention is a declared diagnostic because density alone does not fix sample positions. Report point count, design-matrix rank, singular values, realized energy precision and whether ten cubic coefficients are identifiable. Do not replace a rank test with distinct-energy count or infer reliable curvature from zero residual alone.

Then choose and justify a headline two-dimensional sampling/refinement plan. Keep the literal diagnostic even if it cannot support a mass. Use at least 20 distinct native points per fitted branch spanning two directions, with rank 10 for a cubic fit. Retain all Cartesian offsets, eigenvalues, center gradient, residuals and coefficients. Use `hbar^2/(2*m0)=3.8099821161548593 eV A^2`. The reported target is the local Hessian at the extremum, not arbitrary coefficients of one noisy finite-radius polynomial.

For each relevant branch report both sorted principal electron masses or positive hole-mass magnitudes and the branch energy/splitting. Match branches continuously through the sampled neighborhood with evidence; energy-rank switching can produce a false curvature. For degenerate bands compare an invariant branch/subspace description rather than requiring a particular eigenvector or spin axis. A non-smooth individual-band Hessian must be diagnosed rather than assigned a convenient finite mass.

Validate every headline mass with a genuinely distinct numerical control. Identify truncation versus quantization sensitivity, do not fit sampling radius to obtain 0.42 or 0.53. A normalized condition-number/rank statement, tensor-symmetry test, residual and one control are complementary, not substitutes for one another.

## 5. One error ledger and one bounded conclusion

For structure, elastic components, S/F1 gaps, N0/N1 direct K gaps/splittings and the three auxiliary direct-K contrasts, vacuum edges and each mass branch, report: native central value; units; numerical sensitivity; the varied setting and independent run IDs; literature comparator if available; signed discrepancy; and whether the discrepancy is resolved at the demonstrated precision. Do not add correlated sensitivities as though they were independent random errors. Separate honest sensitivity estimates from rigorous bounds.

Retain the article's Table 1 setup, Tables 3/4/5 MoS2 comparisons and the Section 2.15 rounded no-SOC gap. Do not tune to them. Broad gap/stiffness/mass literature windows are context, not sufficient evidence of convergence; a measured disagreement remains part of the result when the fixed-model calculation and its uncertainty are independently validated. It must still be explained rather than omitted.

Numerical checks use the stated force/stress, vacuum-slope, elastic isotropy (3% diagonal, 5% cross), mass rank and <=10% control-spread criteria. A starting convergence target is gap sensitivity <=0.02 eV and diagonal stiffness sensitivity <=3%; these two additional values are **unvalidated numerical targets**, not author uncertainty. Same-model reference envelopes, mass-branch matching tolerances and quantitative resolved-discrepancy thresholds are not specified by the supplied policy. They must be calibrated from independent numerical controls, not tightened to force agreement with a literature value.

Required figures: independently measured stress-strain families, S/F1 band paths with actual native samples, vacuum potential/plateaus, and two-dimensional mass-fit/control evidence. A table plus native arrays is the numerical answer; plot cosmetics and known electron counts are not additional measurements. Apply the common replay contract.

No literature match can compensate for missing native evidence. Diagnosing the limitations of the literal fit does not replace the requested headline-mass measurements.
