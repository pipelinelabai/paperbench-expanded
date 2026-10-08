# Thickness-dependent polarization-selective transmission of a cholesteric helix

Use genuine Meep FDTD to calculate the specified anisotropic cholesteric slabs at **5, 10, 20 and 40 pitches**. Reproduce the four-thickness linear-input study and additionally resolve both fixed circular-input channels. Retain complex Jones amplitudes, independently executed linear responses, uniform-glass references and calibrated native transmitted/reflected fluxes. Compare all four complete spectra with an independent solution of the identical tensor and boundaries.

## Agent preparation and verification

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

## Deliverables and starting materials

Deliver all four complex Jones spectra, independent linear-input checks, material and measured band edges, outside-band transmission, and a genuinely simulated 10p reversed-helix control. Retain independent >=1.5x-grid and >=1.5x-time comparisons at 5p, 10p and 40p, justified 20p discretization, and new-frequency sampling convergence for every thickness. Resolve thick-slab narrow features rather than replacing them with coarse-reference interpolation. Missing 20p/40p results or unmet convergence requirements remain unresolved work.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, data formats, computing limits and the offline no-argument `bash reproduce.sh` procedure. A complete clean reproduction and independent review must fit within **25,200 seconds (7 hours)** on 8 CPUs and 32 GiB RAM. The no-argument calculation may use at most **19,800 seconds (5 hours 30 minutes)**; the remaining 90 minutes cover setup, termination, evidence checks and grading. This is a per-verification limit, separate from the preparation window. No thickness, accuracy, calibration or convergence requirement is waived to meet it. A configured timeout is not evidence of native feasibility or complete paper coverage.

## External resources

See `/home/paper/blacklist.md` for resource-use notes. There is no additional
task-specific external-resource denylist; the scientific and offline
reproduction requirements in the addendum remain unchanged.
