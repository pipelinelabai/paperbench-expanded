# Guided-mode resonances in a slotted multilayer grating

Use Meep FDTD to characterize the specified three-pair multilayer at all four full-depth air-slot widths. Distinguish the infinite unetched crystal's stopband, the finite unetched film's low-transmission interval, and the patterned structure's optically excited response. Identify and track two dominant optically excited resonance branches at each of the four widths in the requested band. Establish the specified complex single-pole fits and independent decay-mode comparisons for both required branches; document absent, unresolved or overlapping features with their detection limits. Retain the original fields and fluxes and establish the required spatial, temporal and spectral-sampling controls without importing the paper's resonance parameters.

## Agent preparation and verification

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

## Deliverables and starting materials

Deliver the complete four-width spectral comparison, branch and fit-applicability assessment, independent decay evidence, and a report separating film band edges from patterned resonances. A supported absence of a resolvable resonance is a characterization result, not a fitted pole; missing measurements are not an absence result.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure. Use the supplied article and figures for context.

A supported absence or failure of single-pole applicability must be reported, but does not complete the missing two-branch, fit or convergence requirements. Do not invent a physical pole or substitute a descriptive result for the requested measurement.

---

# Guided-mode resonances in a slotted multilayer grating: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

- [Fixed geometry and scope](#fixed-geometry-and-scope)
- [Three different spectral systems](#three-different-spectral-systems)
- [Resonances and fitting protocol](#resonances-and-fitting-protocol)
- [Basis of accuracy and applicability requirements](#basis-of-accuracy-and-applicability-requirements)
- [Study case labels](#study-case-labels)
- [Computing resources and independent reproduction](#computing-resources-and-independent-reproduction)

## Fixed geometry and scope

Use 2D x-y Meep, invariant z, TE Ez, normal incidence propagating +y, x-period P=0.900 um with Bloch kx=0. The exterior on both sides is air. From the incident side, layers are [As2S3(nH=2.38,dH=0.1628 um), SiO2(nL=1.46,dL=0.2672 um)] repeated three times, total thickness 1.290 um. Indices are real, nondispersive constants for this model. Center the stack about y=0. In each period an **air slot** centered at x=0 cuts through all six layers. Slot width w is the air opening, not the remaining dielectric width P-w. Run w=0.030,0.050,0.070,0.150 um. Use PML only along propagation, with source/reference/flux planes in homogeneous air.

This explicit full-depth-slot model is paper-inspired, not an independently established replica of every paper condition. The required study nevertheless retains two dominant optically excited branches at each of the four widths over lambda=1.25..1.75 um, with the specified identifiable fits and independent validation. Establish excitation, mode overlap/parity and continuity across widths. A weak or unexcited numerical pole is not an optical resonance. Missing, dark or overlapping branches must remain unresolved requirements, and any conflict between the fixed model and the requested outcome requires independent scientific review. Do not substitute the paper's q, Q or linewidths, invent branches, or silently exchange labels. Nonlinear bistability remains outside this constant-index task.

## Three different spectral systems

1. For the **infinite, unetched high/low bilayer**, compute its normal-incidence transfer trace and define stopband by |Tr(M)/2|>1. For this model the first gap surrounds 1.55 um. Find both crossings to <=0.002 um. This mathematical auxiliary does not stand in for a Meep spectrum.
2. Run the **finite unetched three-pair stack** in Meep and an independent finite-stack calculation. Its operational low-transmission interval is the connected T<=0.5 interval containing 1.55 um, with linear boundary interpolation on a spectrum covering 1.1..2.5 um at <=0.002 um spacing. It is not an infinite-crystal bandgap. Compare powers within 0.02.
3. Run the **patterned four-width grating** and report actual resonances, not either of the preceding band edges. The paper's MDG range 1145..2394 nm must not be substituted for the unetched bilayer trace gap.

Normalize with matched empty-air reference flux and subtract the incident reference for backward flux. Background transmission need not be near unity. For every finite lossless spectrum verify signed reflected flux, T>=-0.01, R>=-0.01 and max |R+T-1|<=0.02 on the analyzed samples. Preserve raw reference/device fluxes and complex reflected fields, with interface-reference phase deembedding stated.

The fitted reflection is the complex **zero-order reflected port amplitude**, not an arbitrary local field. At kx=0, project Ez onto the constant transverse mode over one complete period: E0=(1/P) integral Ez(x) dx, with retained native coordinates/quadrature and matched reference/device planes; form (E0_device-E0_reference)/E0_reference before the stated deembedding. An equivalent signed incoming/outgoing mode decomposition is acceptable. Although only order zero propagates for lambda>P, evanescent orders can contaminate a finite-distance point sample. A point-based approximation therefore needs reflected-side complex projection or an independent port-distance comparison bounding that error in the reported pole uncertainty. Power closure or a transmitted-side flux check alone cannot certify reflected phase. Do not introduce a fitted phase offset or change the physical reference plane.

## Resonances and fitting protocol

Fit **complex reflected amplitude** against frequency f=1/lambda (in 1/um), not directly a wavelength-intensity curve. For each isolated resonance use
r(f)=r_bg+a/(f-f0+i Gamma/2),
with constant complex r_bg and complex residue a, real f0 and Gamma>0. Define Q=f0/Gamma, pole wavelength=1/f0, and narrow-line wavelength equivalent Gamma/f0^2. This Gamma is the pole linewidth, not the direct half-height width of an asymmetric Fano intensity. The optional complex asymmetry parameter is q=i+2a/(Gamma r_bg), undefined when r_bg is zero. Do not impose the same q on T and R, or a universal q_R=-1/q_T rule.

Use at least **33 actual samples** per isolated fit window, maximum frequency spacing <=Gamma/8 and a total window spanning 4..12 Gamma. Evaluate normalized complex residual against spectral variation; require <=0.05 and nonzero variation resolved above numerical uncertainty. Refit windows differing by >=25% and report f0/Q sensitivity. Compare each branch with independently extracted post-source Harminv decay modes: |delta f0|<=0.2 Gamma and relative Q disagreement <=15%. Inspect mode amplitude, parity, fit error and duration, not just an arbitrary listed mode. There is no predetermined minimum Q or scalar q range for this fixed model.

Establish pole identifiability, separately from optimizer success. Report spectral variation, amplitude/residue uncertainty, conditioning of the six-real-parameter Jacobian and fit-boundary sensitivity. The review calculation flags roundoff-flat spectra using 64 machine eps times amplitude scale, uses column-scaled Jacobian rank at relative sqrt(machine eps), and checks nonzero variation/residue and resolved linewidth with a 1.959964 local uncertainty multiplier. The noise floor is the maximum of roundoff, residual-based RMS with six-parameter degrees of freedom and any independently justified RMS estimate. These are disclosed local observability diagnostics, not proof of independent Gaussian errors or native FDTD convergence. An unidentifiable or inapplicable fit has no valid physical f0/Gamma/Q; retain its optimizer output only as explicitly invalid diagnostics.

The constant-background single-pole model is a local approximation, not a universal identity for a multilayer with overlapping modes. Assess its applicability to each detected feature using residuals, changed windows, mode content and independent decay. Where applicable, all specified fit and corroboration criteria remain required. For overlapping features or demonstrable background drift, retain the failed-fit diagnostics and explain why individual single-pole parameters cannot be identified. Polynomial-background, additional-pole or intensity fits may be reported separately, but cannot be presented as a validated fit of the specified model. The required result remains two dominant optically excited branches at each of the four widths, with identifiable fits satisfying the stated criteria. An absent, overlapping or non-identifiable branch must be reported as unresolved or contradicted, not counted as a successful required fit. Do not invent poles to fill the requested count.

For every width, retain a full-band native search spectrum, reference/device fluxes and complex reflected amplitudes, and post-source decay/search evidence with excitation, probe positions, duration, sampling and numerical uncertainty. Report all detected features and explain the resolution limits of the search. A finding of no resolvable optical resonance is limited to these conditions and sensitivity, not proof that no eigenmode exists. Justify spectral coverage and search resolution with time and sampling evidence; a coarse or flat spectrum alone cannot exclude a missed narrow line. Use targeted native samples and changed windows for detected features. Classify results in ordinary tables or prose as resolved isolated, overlapping/inapplicable, not resolved above demonstrated sensitivity, or incomplete. No new file layout or status manifest is required. Missing spectra, unexamined features, unsupported absence claims and incomplete controls do not establish the required result. Even a supported absence cannot satisfy a missing required branch or fit. A flat spectrum or zero/uncertain residue must never yield a physical pole or Q.

For w=0.030 and one wider case, compare independently retained raw runs at >=1.5x resolution, >=1.5x post-source duration and half the frequency step, irrespective of the observed branch count. For resolved isolated poles report lambda/f0/Gamma/Q changes separately. Spatial refinement requires relative pole-frequency changes <=0.002 and Q changes <=10%; also report the frequency shift in linewidth units. If spatial shifts exceed 0.2 Gamma, explicitly mark the continuum resonance center as not known to a linewidth, even when its Q has stabilized. Time and frequency-step refinement at fixed geometry/grid require frequency shifts <=0.2 Gamma and Q changes <=10%. Continue refinement if needed to support those claims. When pole parameters are not identifiable, compare the measured complex spectra, powers, feature visibility and detection limits instead, and explain whether the classification changes under each independent refinement. Do not invent Q changes or treat null values as passing pole tolerances. Residual uncertainty must bound the conclusion actually made; an unstable classification remains unresolved. No new universal spectral-change cutoff is imposed. Include the unetched control showing which observed features change or disappear without slots, or bounding any difference if none are resolved. Explain unresolved convergence without copying paper Q values.

## Basis of accuracy and applicability requirements

The layer indices, quarter-wave thicknesses, period and width study are motivated by the supplied paper's Computational Setup and Figure 2. The explicit six-layer full-depth air-slot geometry and search band are fixed model definitions. The infinite bilayer trace and finite-film interval are different mathematical/operational definitions, not the paper's patterned MDG gap. Complex port projection, reference subtraction, positive linewidth and nonzero identifiable residue are measurement-validity requirements. The stated sampling counts, fit residual, window change, mode agreement, power closure and refinement tolerances are disclosed numerical policies for credible measurements, not paper-reported performance targets. They are unchanged for any claimed isolated pole. Unknown outcomes do not relax normalization, native evidence or independent controls.

Use genuine Meep time-domain solves for the electromagnetic measurements requested below. An independent transfer/scattering matrix or analytic calculation is useful for cross-checking, but must be labeled and cannot replace FDTD. Do not use stored target arrays as simulation outputs. Use micrometres for length, c=1, frequencies in 1/um, and the exp(-i omega t) phasor convention; convert Meep output conventions explicitly if needed.

Retain actual native logs, geometry/material inputs, source/monitor definitions, resolutions, durations, stopping criteria, complex amplitudes, raw incident/reference and device measurements, integration coordinates and independent baseline/refinement runs. Describe units, array meanings, axis order, phasor gauge and run association. CSV, JSON, NPZ and HDF5 are equally acceptable; complex arrays or explicitly identified real/imaginary pairs are equivalent. Names and layout are not scientific requirements. No new manifest format is mandatory. Plots illustrate rather than replace numerical evidence.

Report numerical uncertainty and failed convergence honestly. Compare the same physical model, polarization, material dispersion and reference planes; do not apply undocumented phase offsets, rescale individual data points or select the better label at each wavelength. Source amplitudes may differ if each normalization is independently justified. Include a concise scientific report and enough source to regenerate the evidence offline. Report unresolved measurements explicitly rather than replacing them with literature values.

For convergence scans on different coordinate grids, retain both original axes and compare on the baseline grid by piecewise-linear interpolation of the refined values (real/imaginary parts separately for complex data), without extrapolation. Scalars such as fitted pole frequencies and Q values can be compared directly. Array storage order, matrix axis order and split component columns are acceptable when their meaning is documented; do not alter physical channel identities.


## Study case labels

The supplied case labels are `bandgap`, `w30`, `w50`, `w70`, `w150`. Their measurements and evidence requirements are defined in this document.

All specified formats, source restrictions, controls and computing limits remain requirements of the complete calculation.

Work in `/home/submission`. Paper resources are in `/home/paper`. Implement a no-argument `bash reproduce.sh` that regenerates all results from editable source and static inputs. Keep static inputs in `src/` or the submission root, not in generated `config/`, `geometry/`, `results/` or `views/`, which are cleared for replay. The empty starter config is intentional: populate it from the scientific protocol or encode the parameters in source. No particular config schema is required.

The supplied numerical environment includes Meep 1.17.1, NumPy, SciPy and h5py. Use physically equivalent reductions only where the model explicitly allows them.

The reproduction process freezes the delivered source and static inputs before replay. Newly generated regular files are outputs, not modifications of those inputs; changing, deleting or replacing a frozen input is still an integrity failure. The conventional root `report.md` is generated and cleared together with the generated directories. Other newly created report names and layouts are equally acceptable. Keep reusable static input documents in `src/`; no locally generated input manifest is required. Report infrastructure failures separately from physical or numerical findings.

## Computing resources and independent reproduction

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 25,200 seconds (7 hours) |
| Complete native calculation from source | 18,000 seconds (5 hours) |
| Entire reproduction and independent review | 21,600 seconds (6 hours) |
| CPU allocation | 8 CPUs |
| RAM | 32 GiB |

The native-run limit covers the complete no-argument calculation, including all
required reference runs, controls, convergence studies and generated reports.
Setup, source-integrity checks and independent review use the remaining overall
interval; that reserve is not additional simulation time. No network access is
available during independent reproduction. Preserve partial native output and
identify unfinished work rather than reducing fidelity or omitting controls.

## Required two-branch result

For each of the four widths, identify and track two dominant optically excited branches and establish their complex single-pole fits, independent post-source Harminv agreement and required window/refinement stability. Full-band search and supported absence diagnostics remain valuable evidence, but do not satisfy the missing branch, fit, mode-agreement or pole-convergence requirements. The unchanged isolated-pole thresholds apply to both required branches. A demonstrated incompatibility between this fixed geometry and the requested outcome requires review of task validity, not a redefinition of success.
