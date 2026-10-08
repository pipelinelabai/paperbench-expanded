# Guided-mode resonances in a slotted multilayer grating

Use Meep FDTD to characterize the specified three-pair multilayer at all four full-depth air-slot widths. Distinguish the infinite unetched crystal's stopband, the finite unetched film's low-transmission interval, and the patterned structure's optically excited response. Identify and track two dominant optically excited resonance branches at each of the four widths in the requested band. Establish the specified complex single-pole fits and independent decay-mode comparisons for both required branches; document absent, unresolved or overlapping features with their detection limits. Retain the original fields and fluxes and establish the required spatial, temporal and spectral-sampling controls without importing the paper's resonance parameters.

## Agent preparation and verification

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

## Deliverables and starting materials

Deliver the complete four-width spectral comparison, branch and fit-applicability assessment, independent decay evidence, and a report separating film band edges from patterned resonances. A supported absence of a resolvable resonance is a characterization result, not a fitted pole; missing measurements are not an absence result.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure. Use the supplied article and figures for context.

A supported absence or failure of single-pole applicability must be reported, but does not complete the missing two-branch, fit or convergence requirements. Do not invent a physical pole or substitute a descriptive result for the requested measurement.

## External resources

See `/home/paper/blacklist.md` for resource-use notes. There is no additional
task-specific external-resource denylist; the scientific and offline
reproduction requirements in the addendum remain unchanged.
