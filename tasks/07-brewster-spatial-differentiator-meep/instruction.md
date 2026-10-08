# Spatial differentiation by reflection at a Brewster interface

Investigate the Brewster-interface spatial differentiator in the supplied article, including its refractive-index-dependent usable bandwidth and its Gaussian and Sinc demonstrations. Distinguish reproduction of the article's analytical results from independent electromagnetic validation of the specified interface.

Use Meep FDTD to measure the complex angular response at n=2.1 and reconstruct the prescribed Gaussian and rectangular-angular-spectrum Sinc responses. Quantify fixed-operator error, shape error, reflected power and RMS spatial bandwidth. Establish spatial, temporal and angular-sampling convergence and perform the off-angle control. Independently compare native reflected flux with field-derived power for each input; a small conservation residual alone does not establish a reliable weak-reflection measurement.

Reconstruct the usable-bandwidth curve in Fig. 5 with an analytical Fresnel calculation, and explain how the prescribed Gaussian relates to the article's stated 32-lambda0 beam width. Where the article leaves a convention unspecified, state the interpretation and test its consequences rather than claiming an exact match.

## Agent preparation and verification

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

## Deliverables and starting materials

Deliver the native angular and power measurements, both reconstructed input responses, the refractive-index/bandwidth calculation, the beam-width comparison and their editable source. In the report, separate paper agreement, fixed-model FDTD accuracy and unresolved measurements. Retain numerical arrays, calibration evidence and convergence results, not just plots or summary values.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure. Use the supplied article and figures for context.

## External resources

See `/home/paper/blacklist.md` for resource-use notes. There is no additional
task-specific external-resource denylist; the scientific and offline
reproduction requirements in the addendum remain unchanged.
