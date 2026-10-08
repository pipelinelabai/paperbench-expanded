# Spatial differentiation by reflection at a Brewster interface: scientific protocol

This document defines the research scope, measurements, deliverables and independent reproduction procedure.

- [Interface, coordinates and input definitions](#interface-coordinates-and-input-definitions)
- [Relation to the paper's Gaussian example](#relation-to-the-papers-gaussian-example)
- [Refractive index and usable bandwidth](#refractive-index-and-usable-bandwidth)
- [Quantitative comparison and checks](#quantitative-comparison-and-checks)
- [Study case labels](#study-case-labels)
- [Computing resources and independent reproduction](#computing-resources-and-independent-reproduction)

## Interface, coordinates and input definitions

Reproduce the analytical bandwidth and differentiation results associated with Figs. 4-7 of the article, and independently validate the fixed n=2.1 interface with Meep. The analytical index sweep and beam-width interpretation are separate from the two prescribed FDTD inputs. An ideal derivative need not apply unchanged to every finite-band input. Numerical acceptance tolerances below belong to this study; they are not additional experimental results from the article. Do not describe this scope as a reproduction of experiments or cascaded higher-order devices that the article does not demonstrate.

Use a single lossless dielectric interface, n_in=1, n_out=2.1, lambda0=1.550 um, TM polarization, central incidence theta_B=atan(2.1). The normal is +y toward glass. Let u be the transverse coordinate of the incident central beam and mirror the reflected observation coordinate into the same orientation. Define q=k_u/k0 and angular incidence theta(q)=theta_B+asin(q), |q|<=0.1. All complex amplitudes are referred to the interface; remove known homogeneous propagation phases to other planes. Use exp(-i omega t), Fourier exp(+i k_u u), and power-normalized TM basis phases chosen so
r_p(q)=(2.1 cos(theta)-cos(theta_t))/(2.1 cos(theta)+cos(theta_t)),
sin(theta_t)=sin(theta)/2.1.
Then r_p'(0)=-C, C=2.1/2-1/(2*2.1^3). The first-order operator in Fourier space is H_ideal(q)=-C q, equivalent to i C/k0 times d/du. A different Meep field basis is allowed only with the explicit basis/sign conversion; do not fit away an unexplained sign or propagation phase.

Use two incident angular spectra: Gaussian A_G(q)=exp[-0.5(q/0.025)^2] within |q|<=0.1, zero elsewhere; and Sinc-generating A_S(q)=1 within |q|<=0.09, zero elsewhere. This second input is a band-limited Sinc, not a real-space step. Use >=33 angular samples including -0.1,0,0.1 and both Sinc cutoff points. Use piecewise-linear nodal trapezoidal quadrature only on the actual input support: [-0.1,0.1] for Gaussian and [-0.09,0.09] for Sinc. The Sinc endpoints carry only their inward half-cell weights; every node outside its support has zero integration weight. Endpoint comparisons use absolute q tolerance1e-12. Report the weights/rule and quadrature convergence. Power, fixed/shape errors, RMS bandwidth, and real-space Fourier synthesis must use the same input-support quadrature. A cropped spectrum and the same spectrum stored on the full angular axis must give identical power, errors and spectral moments. The >=33 angular-sample acquisition and refinement requirements concern the actual native experiment, not the number of rows after cropping an integration interval. Do not change the prescribed input spectrum to compensate for an integration error.

You may either simulate both beams directly in 2D Meep or obtain a genuine Meep plane-wave angular basis and synthesize both responses by linear superposition. Analytic Fresnel coefficients cannot replace the native FDTD runs. Save actual raw complex incoming/reflected/transmitted basis data and native reference powers. De-embed and power-normalize every basis wave before synthesis. Each input's power must use its own spectral weights and quadrature; equal-power normalization is acceptable only with raw calibration proof.

## Relation to the paper's Gaussian example

The article describes Fig. 6 using W=0.1 k0 and a beam width of 32 lambda0, but the supplied text does not define that width as an amplitude width, an intensity width or a truncation window. Matching the angular cutoff alone therefore does not establish that the prescribed A_G is the same beam.

Derive the real-space envelope associated with the prescribed Gaussian spectrum under the stated Fourier convention. Report the full intensity FWHM and the full intensity 1/e^2 width in units of lambda0, for both the untruncated Gaussian envelope and the actual band-limited input. State the field normalization and distinguish beam width from the computational observation window. Explain whether a width convention supported by the supplied article makes the stated 32 lambda0 equivalent to this input; cite the supporting text or figure, or explicitly identify the ambiguity.

Also make an analytical comparison in which 32 lambda0 is explicitly interpreted as the full 1/e^2 intensity width of an untruncated Gaussian. Derive its angular spectrum, apply the same |q|<=0.1 cutoff and compare its realized width and fixed-operator error with the prescribed input. This is a declared comparison convention, not a recovered author definition. Retain both calculations; do not replace A_G, rescale coordinates to match a plot or choose a width to obtain the article's rounded error. No additional Meep beam calculation is required for this interpretive comparison.

## Refractive index and usable bandwidth

Reconstruct the analytical relationship in Fig. 5, not just the n=2.1 point. Use n_in=1 and vary n_out=n from 1.05 to 4.0, including n=2.1, with index spacing no larger than 0.1 and further refinement around extrema or other unresolved features. The n=1 limit is excluded because the interface reflection and ideal derivative gain both vanish; discuss this degeneracy rather than reporting a zero-over-zero error.

At each n use its own Brewster angle and the exact TM Fresnel response of the same interface. Let H_ideal,n(q) be its first-order Taylor term at q=0. For this calculation define W as the one-sided angular-spectrum cutoff, w=W/k0, and use the continuous, unweighted relative L2 error

e_G(n,w) = [integral_{-w}^{w} |r_n(q)-H_ideal,n(q)|^2 dq / integral_{-w}^{w} |H_ideal,n(q)|^2 dq]^(1/2).

The denominator is the ideal derivative response, with no fitted gain. This specifies the norm and bandwidth convention used to interpret the article's 10% criterion; a pointwise relative error at the Brewster zero is not defined. The full support width is 2W. Restrict the angular interval to propagating waves incident toward the interface. Find the largest w in the feasible interval connected to w=0 for which e_G<=0.10; do not select an isolated higher-bandwidth solution after a threshold violation.

Retain n, W/k0, error values and the calculation source. Establish quadrature and threshold-location convergence: at an interior 10% crossing require |e_G-0.10|<=1e-4 and a change in W/k0<=1e-4 on refinement. Report a domain-limited result explicitly if no crossing occurs. Plot the curve in the same units as Fig. 5, compare its magnitude, maximum and trend with the supplied figure, and retain any digitized comparison points together with a justified image-reading uncertainty. A visual curve is not exact reference data: document discrepancies and convention sensitivity rather than fitting the calculation to the image. Explain the relation between this uniform-spectrum bandwidth and the spectrum-weighted Gaussian/Sinc errors below.

An analytical Fresnel calculation is sufficient for this sweep, as for the article's analytical figure. Label it accordingly; it cannot replace the separate native Meep measurements at n=2.1.

## Quantitative comparison and checks

For each input report the complex reflected field/spectrum O(q)=r(q)A(q) and ideal derivative D(q)=-C q A(q). The fixed-gain relative L2 error is ||O-D||/||D||. Also report the best **one global complex scalar** g=<D,O>/<D,D> and shape error ||O-gD||/||O||. Use quadrature-weighted inner products. No pointwise gains, arbitrary nonlinear coordinate warps or independently fitted phases at every sample. Save real-space complex input/output/derivative on explicit u coordinates as well as spectral data, with Fourier normalization and spatial-window convergence.

Compare the Meep r(q) with independent Fresnel values using max complex absolute error <=0.005; fixed-operator L2 errors should be <=0.08 for Gaussian and <=0.14 for Sinc after convergence. These limits allow the nonzero finite-angular-band approximation error. Shape accuracy alone does not establish correct absolute gain. Compute actual absolute reflected power eta=integral |r A|^2 dq / integral |A|^2 dq and native R/T closure <=0.02. Each normalized native reflected or transmitted power must be >=-0.01, allowing small numerical subtraction error but not an unphysical normalization. Report the actual reflected-power fraction; no additional power-efficiency lower bound is imposed. Operator gain and reflected-power fraction are different observables.

### Independent power consistency

The article establishes the derivative response and its low output amplitude; it does not specify a numerical tolerance for agreement between FDTD flux and field-derived power. This study uses a 10% signal-relative power-precision budget, separately for Gaussian and Sinc. This is a stated numerical measurement requirement, not an efficiency target or a precision claimed by the article. Passing the global R/T closure check alone does not resolve weak reflection.

For an angular basis, let alpha_i=w_i|A_i|^2/sum_j(w_j|A_j|^2), using the prescribed input and exact-support quadrature. Independently obtain R_i=P_reflected,i/P_incident,i and T_i=P_transmitted,i/P_incident,i from calibrated native fluxes. Retain the measured powers, reference runs and monitor orientations. A backward signed flux needs the documented sign conversion. If the measurement is net forward power, use P_reflected=P_incident-P_net; P_net itself is not reflected power. Reference subtraction of complex fields followed by a native flux measurement is also acceptable. Either extraction needs its own calibration and uncertainty evidence; neither is assumed accurate merely because it is implemented.

Compute eta_flux=sum_i(alpha_i R_i) and eta_spectrum=sum_i(alpha_i |r_i|^2), retaining negative numerical R_i without clipping or taking absolute values. Do not construct the flux measurement from r, fit a normalization, or subtract a measured bias to force agreement. For direct-beam simulations, eta_flux is the independently normalized integrated reflected flux of that particular beam; retain its own incident and transmitted powers. Its eta_spectrum uses the same prescribed angular spectrum and measured complex response. Both solution routes remain valid; separate plane-wave jobs are not required for a direct beam.

Retain native flux and complex-response evidence for production and the specified spatial, time and angular refinements. Independently calibrate incident power for each numerical configuration. Use homogeneous-medium null measurements or an equivalent independently executed calibration to quantify the residual of the chosen reflection extraction. A null constructed by subtracting a stored array from itself is not a noise measurement. A reference may serve more than one role only when its execution and use provide a genuinely independent check; shared calibration across configurations needs evidence that its error bound covers those configurations. Separate duplicate null jobs at every setting are not an end in themselves. Identify numerical settings and run associations in source or logs; no extra manifest is required.

For each production input, establish conservative absolute error bounds u_flux and u_spectrum on the two normalized power estimates. Retain these two scalar bounds as numerical data, with their derivation and supporting measurements; no particular filename or extra file is required. Document how native calibration residuals, source/reference normalization, spatial and temporal errors, angular quadrature, and monitor/boundary effects enter the bounds or have been shown negligible. Correlated errors must not be treated as independent samples, and signed null residuals must not cancel across angles when estimating an error bound. A change between two resolutions is a convergence diagnostic, not automatically a bound on every systematic error; neither its sum with a null residual nor a solver tolerance alone defines total uncertainty. An exact-looking refinement sequence does not prove zero measurement uncertainty.

Require eta_spectrum>0, eta_flux-u_flux>0, u_flux+u_spectrum<=0.10*eta_spectrum, and |eta_flux-eta_spectrum|<=u_flux+u_spectrum. Arithmetic comparison may include 32*epsilon64*max(|eta_flux|,eta_spectrum) of floating-point slack; that is not a physical noise floor. Establish the bounds independently of the observed flux/spectrum mismatch; do not enlarge them merely to make this inequality pass. A bare claimed bound is not evidence. Every retained native configuration must still satisfy closure<=0.02 and native R/T ratios>=-0.01. An unresolved bias or a negative integrated reflection estimate cannot establish the power measurement, even when those broad tolerances pass. Preserve and report that limitation without clipping the measurement or substituting a Fresnel value. Such a limitation does not by itself invalidate independently supported operator measurements.

Fit H(q)=s q+b as continuous weighted least squares over |q|<=0.05 and |A|>=0.01 max|A|: minimize the integral of |A(q)|^2 |r(q)-s q-b|^2 dq. Discretize with quadrature weights |A_i|^2 w_i. Use the exact fitting interval endpoints +/-0.05 with absolute q tolerance1e-12; if an endpoint is absent, interpolate its amplitude from its bracketing raw samples without calling it a new native measurement. Apply the same nodal quadrature rule restricted to this fitting interval. Report s,b and weighted residual, compare slope to -C within5% and |b|<=0.003. Report RMS q bandwidth sqrt(integral q^2 |A|^2/integral |A|^2) for input and output, not the signed spectral centroid of a symmetric spectrum. Numerical power and field curves must agree with the same normalization.

Retain raw comparisons for >=1.5x spatial resolution, >=1.5x post-source time, and >=2x angular sample density. Require max complex r change <=0.003 and fixed-gain error changes <=0.01. Include a TM off-Brewster control with central angle theta_B+5 degrees using the same physical interface: demonstrate a nonzero zeroth-order component, rather than claiming it remains an ideal derivative. Use an independent power reference and retain its raw solve. Do not interpret unavoidable finite-band operator error as a failure of Maxwell convergence.

Use genuine Meep time-domain solves for the fixed-interface electromagnetic measurements. The explicitly analytical Fig. 5 sweep and Gaussian-width comparison are exceptions, not substitutes for FDTD. An independent transfer/scattering matrix or analytic calculation is useful for cross-checking, but must be labeled and cannot replace the required FDTD measurements. Do not use stored target arrays as simulation outputs. Use micrometres for length, c=1, frequencies in 1/um, and the exp(-i omega t) phasor convention; convert Meep output conventions explicitly if needed.

Retain actual native logs, geometry/material inputs, source/monitor definitions, resolutions, durations, stopping criteria, complex amplitudes, raw incident/reference and device measurements, integration coordinates and independent baseline/refinement runs. Describe units, array meanings, axis order, phasor gauge and run association. CSV, JSON, NPZ and HDF5 are equally acceptable; complex arrays or explicitly identified real/imaginary pairs are equivalent. Names and layout are not scientific requirements. No new manifest format is mandatory. Plots illustrate rather than replace numerical evidence.

Report numerical uncertainty and failed convergence honestly. Compare the same physical model, polarization, material dispersion and reference planes; do not apply undocumented phase offsets, rescale individual data points or select the better label at each wavelength. Source amplitudes may differ if each normalization is independently justified. Include a concise scientific report and enough source to regenerate the evidence offline. Report unresolved measurements explicitly rather than replacing them with literature values.

For spatial or temporal convergence on different coordinate grids, retain both original axes and compare at common physical coordinates by piecewise-linear interpolation without extrapolation (real and imaginary parts separately for complex data). For angular or wavelength sampling convergence, compare coarse-spectrum interpolation with the new independent observations on the refined grid or the union of both grids; agreement only at old points does not establish sampling convergence. Preserve the new observations and report the largest new-point error. A Fourier evaluation at a new frequency from retained native time-domain fields is permitted when its normalization and finite-time error are documented; interpolation of an existing spectrum is not a new native observation. Scalars such as fitted pole frequencies and Q may be compared directly. Storage order and split complex columns are acceptable when documented; physical channel identities cannot change.

A fixed input formula in source is sufficient evidence of its definition; no redundant standalone input file is required. Dynamically generated scientific reports belong under results/ or another explicitly cleared output root. A root-level report may instead be a static source file and must not be rewritten during replay.


## Study case labels

The supplied case labels are `reference`, `differentiate_gaussian`, `differentiate_sinc`. Their measurements and evidence requirements are defined in this document.

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
| Preparation and development | 21,600 seconds (6 hours) |
| Complete native calculation from source | 14,400 seconds (4 hours) |
| Entire reproduction and independent review | 18,000 seconds (5 hours) |
| CPU allocation | 8 CPUs |
| RAM | 32 GiB |

The native-run limit covers the complete no-argument calculation, including all
required reference runs, controls, convergence studies and generated reports.
Setup, source-integrity checks and independent review use the remaining overall
interval; that reserve is not additional simulation time. No network access is
available during independent reproduction. Preserve partial native output and
identify unfinished work rather than reducing fidelity or omitting controls.
