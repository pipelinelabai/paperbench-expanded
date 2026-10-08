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

---

# Thickness-dependent polarization-selective transmission of a cholesteric helix: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

- [Material tensor and polarization conventions](#material-tensor-and-polarization-conventions)
- [Native observations and normalization](#native-observations-and-normalization)
- [Spectra and independent checks](#spectra-and-independent-checks)
- [Computing resources and independent reproduction](#computing-resources-and-independent-reproduction)

## Material tensor and polarization conventions

Reference: Jaka Zaplotnik et al., Scientific Reports 13,16868 (2023), DOI 10.1038/s41598-023-43912-2. Fig.2 contains four thickness panels D/p=5,10,20,40 for linearly polarized gamma=0 input; they are not separate circular-input panels. Reproduce all four finite thicknesses with independent circular and linear inputs, retaining the thick-slab narrow spectral features. Use the identical-tensor independent Maxwell calculation for circular-channel comparisons. The numerical tolerances below define measurement accuracy for this fixed model; they are not additional experimental observations attributed to the article.

Use a 1D anisotropic Meep slab at normal incidence propagating +z, nonmagnetic, no loss/dispersion, p=1.000 um, no=1.5, ne=1.8, exterior glass n_g=1.5. For 0<=z<=D the director is d(z)=(cos(2 pi z/p),sin(2 pi z/p),0), and epsilon=no^2 I+(ne^2-no^2) d d^T. At both boundaries the director lies along x for integer D/p. Use the actual anisotropic tensor, not a scalar effective index. PML and source/reference planes lie in homogeneous glass.

Fix exp(-i omega t). Circular vectors referred to fixed laboratory x,y axes are e+=(1,+i)/sqrt(2), e-=(1,-i)/sqrt(2). This basis is used for both forward and backward output coefficients; names alone do not define helicity. The **matching stopband input for this positive helix is e-** throughout the spectrum. Never choose the smaller output channel or swap labels independently by wavelength.

## Native observations and normalization

For each of the four required thicknesses (5p, 10p, 20p and 40p) run e+ input, e- input, and independent linear Ex input, plus their uniform-glass references (shared references are allowed if exact linear rescaling is demonstrated). The 20p and 40p cases are part of the paper's Fig. 2 thickness comparison, not optional extrapolations from thinner slabs. Preserve raw complex Ex,Ey,Hx,Hy at input/output planes, reflected background subtraction, reference fields and powers, source phases, and separately calculated normalized amplitudes. Real time signals followed by complex DFT can preserve phase; a particular force_complex_fields option is not mandatory.

Use Jones matrices J_ij and K_ij with first index output circular component (+,-), second input circular component (+,-), normalized to unit input power in the same glass. De-embed common uniform reference propagation consistently for all columns. Then channel powers are T_j=sum_i |J_ij|^2 and R_j=sum_i |K_ij|^2. For unit Ex input the predicted output is (J_i+ + J_i-)/sqrt(2), not half a diagonal/channel power. Compare it with the independently run linear-input complex output, max complex difference<=0.02. Save these as distinct observations.

## Spectra and independent checks

Cover lambda=1.150..2.500 um inclusive with maximum spacing0.005 um and refine to0.0025 um for comparisons. Keep every sample and its finite wavelength coordinate, without duplicate points or silent truncation. File row order may vary: analysis sorts coordinates and corresponding data together before checking coverage or interpolation. For each thickness require max |T_j+R_j-1|<=0.02 and physically nonnegative powers from the native flux. Compare full channel spectra with an independent continuous Maxwell/Berreman or converged anisotropic-layer scattering calculation of the **identical** tensor/boundaries: max absolute power difference<=0.03 for both Jones-derived and independently normalized native channel powers. Continuous theory does not prove Meep convergence by itself. Independently compare native transmitted and reflected fluxes with Jones powers, requiring maximum absolute differences<=0.02; internal Jones closure alone cannot certify native calibration. Remeasure incident polarization in the uniform-glass reference rather than assuming a source amplitude setting produces the desired channel.

Minimum matching-input T_minus and its wavelength may be reported as descriptive diagnostics. A minimum-transmission suppression threshold, a monotonic-minimum condition, or a minimum-location condition is not a requirement. All four thicknesses remain mandatory for spectral coverage and independent model comparison; a missing thick-slab result remains unresolved.

Keep theoretical material edges [no*p,ne*p]=[1.5,1.8] um separate from measured finite-spectrum edges. Define spectral edges as the linearly interpolated boundary crossings of the connected T_minus<=0.5 component containing1.65 um. First insert the center by piecewise-linear interpolation if it was not sampled; if T_minus(1.65)>0.5, that component is absent even when a nearby raw sample is below0.5. Equivalently compute every piecewise-linear feasible component and select the one that actually contains the center. Record absence or censoring honestly. An analytic constant cannot substitute for a spectrum-derived boundary. Outside-band transmission is the wavelength-integral average over [1.15,1.40] union [1.90,2.50] um; interpolate window endpoints, add both integrals and divide by total window width. Do not weight each interval equally or average a different sampling range.

For 5p, 10p and 40p retain independent >=1.5x-grid and >=1.5x-time comparisons at common physical wavelengths, with maximum channel-power changes<=0.02. Refine space and time separately, retaining each independently acquired reference/device pair; extending a saved record or comparing two windows of one trajectory is only a diagnostic, not an independent temporal solve. Independently test wavelength sampling with at least one half-step refinement to maximum spacing 0.0025 um: compare coarse interpolation with newly evaluated native observations on the refined grid or union, The initial half-step comparison diagnoses whether the starting grid is adequate; retain a failed comparison rather than counting it as passed. If narrow peaks or threshold crossings remain unresolved, continue adaptive new-frequency evaluation. The final successive comparison must include new native observations throughout the full band and have maximum channel-power changes<=0.02. Merely adding a few favorable points near selected extrema does not establish full-band sampling convergence. Agreement only at shared wavelengths is not convergence. Report the measured changes in center-connected edges, minima and the outside-band integral under each refinement, with absence, censoring and remaining uncertainty stated honestly. Retain valid stopping criteria and after-source field traces, plus all reference and CLC data for every refinement. The 20p case requires its own sampling-convergence evidence and either independent spatial/time comparisons or an explicit conservative justification of its discretization. Copying another thickness's settings is not sufficient. Resolve 40p narrow peaks and threshold crossings with adaptive new-frequency observations rather than relying on agreement at old samples.

Include a genuinely simulated 10p helix-reversed control (d_y sign reversed), with both circular inputs, the independent linear input and their references. Compare it against the positive-helix 10p slab using one global exchange of the input-channel identities, not wavelength-dependent relabeling: maximum differences in full-spectrum T and R must be <=0.02. Calibration, independent-model comparison and physical consistency remain required for this control. Any unresolved control discretization requires further native refinement; a negative-helix label alone is not evidence. Source-only replay must regenerate geometry from static inputs under src/ or the root, not a config file deleted with geometry/.

Use genuine Meep time-domain solves for the electromagnetic measurements requested below. An independent transfer/scattering matrix or analytic calculation is useful for cross-checking, but must be labeled and cannot replace FDTD. Do not use stored target arrays as simulation outputs. Use micrometres for length, c=1, frequencies in 1/um, and the exp(-i omega t) phasor convention; convert Meep output conventions explicitly if needed.

Retain actual native logs, geometry/material inputs, source/monitor definitions, resolutions, durations, stopping criteria, complex amplitudes, raw incident/reference and device measurements, integration coordinates and independent baseline/refinement runs. Describe units, array meanings, axis order, phasor gauge and run association. CSV, JSON, NPZ and HDF5 are equally acceptable; complex arrays or explicitly identified real/imaginary pairs are equivalent. Names and layout are not scientific requirements. No new manifest format is mandatory. Plots illustrate rather than replace numerical evidence.

Report numerical uncertainty and failed convergence honestly. Compare the same physical model, polarization, material dispersion and reference planes; do not apply undocumented phase offsets, rescale individual data points or select the better label at each wavelength. Source amplitudes may differ if each normalization is independently justified. Include a concise scientific report and enough source to regenerate the evidence offline. Report unresolved measurements explicitly rather than replacing them with literature values.

For spatial or temporal convergence on different coordinate grids, retain both original axes and compare at common physical coordinates by piecewise-linear interpolation without extrapolation (real and imaginary parts separately for complex data). For angular or wavelength sampling convergence, compare coarse-spectrum interpolation with the new independent observations on the refined grid or the union of both grids; agreement only at old points does not establish sampling convergence. Preserve the new observations and report the largest new-point error. A Fourier evaluation at a new frequency from retained native time-domain fields is permitted when its normalization and finite-time error are documented; interpolation of an existing spectrum is not a new native observation. Scalars such as fitted pole frequencies and Q may be compared directly. Storage order and split complex columns are acceptable when documented; physical channel identities cannot change.

For theory comparison, evaluate the identical continuous-Maxwell reference at the actual submitted wavelengths. The bundled 271-point table is a sample of the reference, not evidence that every narrow feature is resolved; do not use coarse-reference interpolation when comparing newly resolved native peaks. For complex transmission, state whether the phase spans the slab boundaries or has the uniform-glass propagation over the slab thickness removed, and apply that one declared convention to both Jones columns and the independently run linear input.

Local Jones superposition and calibration can be evaluated on their actual local wavelength samples independently of full-spectrum coverage. Return explicit coverage and maximum-gap information; local data cannot establish full-spectrum agreement, band edges, or outside-window integrals. Generated reports belong under results/; static root-level reports must remain unchanged during source-only replay.

All specified formats, source restrictions, controls and computing limits apply to the complete four-thickness calculation at D/p=5,10,20,40. Both 20p and 40p are required. Independent grid/time comparisons at 5p, 10p and 40p, justified 20p discretization, sampling convergence for all four thicknesses, and the 10p negative-helix control remain mandatory. Missing cases are unresolved work, not exempted or passed observations.

Work in `/home/submission`. Paper resources are in `/home/paper`. Implement a no-argument `bash reproduce.sh` that regenerates all results from editable source and static inputs. Keep static inputs in `src/` or the submission root, not in generated `config/`, `geometry/`, `results/` or `views/`, which are cleared for replay. The empty starter config is intentional: populate it from the scientific protocol or encode the parameters in source. No particular config schema is required.

The supplied numerical environment includes Meep 1.17.1, NumPy, SciPy and h5py. Use physically equivalent reductions only where the model explicitly allows them.

## Computing resources and independent reproduction

Use the agent/preparation stage for implementation, syntax checks, unit tests and small representative native probes. A complete clean replay is not required before submission; reserve the mandatory full replay for the verifier. Submit the complete editable pipeline, required static inputs, methods and a no-argument `bash reproduce.sh` that generates all required numerical outputs, analyses and reports. Do not invent scientific results that have not been computed.

The verifier performs the complete clean replay from the submitted source under the separately stated native and verifier budgets. It does not finish the implementation or supply missing scientific results. All production calculations, controls, convergence checks and reports remain required; small preparation-stage probes do not replace them. Only freshly regenerated verification evidence establishes the scientific result.

Use the supplied computing environment and retain measured runtime and resource use.

| Stage or resource | Available limit |
|---|---:|
| Preparation and development | 25,200 seconds (7 hours) |
| Complete calculation from source | 19,800 seconds (5 hours 30 minutes) |
| Entire reproduction and independent review | 25,200 seconds (7 hours) |
| CPU allocation | 8 CPUs |
| RAM | 32 GiB |

The calculation limit covers the complete no-argument calculation, including
native simulations, reference calculations, controls, convergence studies and
generated reports. The remaining 5,400 seconds cover setup, process termination,
source-integrity checks and independent review; that reserve is not additional
simulation time. The seven-hour interval applies to one clean verification, not
the separate preparation window or the sum of all development attempts.

Schedule work within the shared eight-CPU and 32-GiB allocation, including all
child processes. Shared native references require the calibration equivalence
already specified; parallel execution does not waive independent acquisitions.
New frequency evaluation from retained time-domain data must retain the stated
finite-time and sampling checks. Interpolation alone is not a new observation.
Neither a larger time limit nor a faster independent theory calculation waives
20p/40p acquisition, native flux checks, the reversed-helix control or any
accuracy and convergence condition. Verify the complete calculation on the
declared resources before claiming feasibility; a software timeout or a
thin-slab-only timing record is not that verification.

No network access is available during independent reproduction. Preserve
partial native output and identify unfinished work rather than reducing
fidelity or omitting controls. Record a scientific limit separately from an
environment, build or grading-service failure.
