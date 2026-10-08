# Broadband differential phase in two periodic SWG waveguides

Use three-dimensional Meep FDTD to determine the complex transmission, differential phase and transmitted power of the two fixed subwavelength-grating waveguides described in the addendum. Characterize the 1.35–1.75 μm response and its deviation from a 90° phase shift, without adding transitions or changing the geometry. Compare the measured phase with an independent three-dimensional Bloch-mode calculation, and establish spatial, temporal and spectral convergence with the specified physical controls. Report the measured bandwidth and uncertainty, including zero bandwidth or unresolved convergence when supported by the data.

## Agent preparation and verification

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

## Deliverables and starting materials

Deliver the two arms' complex transmission and power spectra, the differential-phase and Bloch comparisons, and a report of bandwidth and numerical uncertainty.

The primary result is a valid native phase/power measurement of the fixed periodic arms, not achievement of 90°. The paper's complete-device performance is context only. A supported non-90° result or zero design-reference bandwidth is acceptable; incorrect normalization, unresolved phase or missing validity controls is not.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure. Use the supplied article and figures for context.

## Resource use

Start with the supplied article, figures and protocol in `/home/paper/`.
The resource note at `/home/paper/blacklist.md` introduces no additional
task-specific URL or repository blacklist. External context does not replace
the required native measurements or offline reproduction.
