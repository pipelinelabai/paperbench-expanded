# Which MoS2 properties are actually numerically determined?

Reproduce the bounded H-phase monolayer MoS2 study motivated by Haastrup et al.'s C2DB workflow. Determine its relaxed structure, relaxed-ion elastic response, scalar/SOC electronic bands, vacuum-referenced edges and effective-mass tensors under the specified model.

Make the central result an error-qualified property table: distinguish numerical uncertainty from differences between the paper's implementation and this Quantum ESPRESSO realization. Test the identifiability of the paper's mass-fitting prescription. Keep the prescribed PAW property study and measure an explicitly auxiliary, matched norm-conserving SOC contrast at K; do not attribute every change between different pseudopotential calculations to SOC or claim that the auxiliary contrast isolates the PAW SOC effect.

The material, states and observables are fixed in `/home/paper/addendum.md`. Choose the resolution, convergence strategy and two-dimensional sampling needed to determine them. Do not fit to literature targets, replace missing native results with interpolation, or select only the convenient mass branch.

## Runtime contract

Read `/home/paper/addendum.md` together with the article. Use `/home/submission/src/` and `/home/submission/inputs/` for immutable source and data, and `/home/submission/outputs/` for generated evidence.
