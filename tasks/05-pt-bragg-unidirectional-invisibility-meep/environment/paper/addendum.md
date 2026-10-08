# Common evidence and replay contract

The task-specific contract defines the scientific question. The bundled article is the source of scientific claims; explicitly labelled benchmark adaptations are not attributed to the authors. Report a substantiated discrepancy rather than fitting an answer to the article. An unresolved result must identify the actual missing evidence, not replace an available computation with generic uncertainty language.

## Execution and evidence

Work in `/home/submission`. Submit editable source and static inputs, plus a no-argument `bash reproduce.sh`. A preparation-stage full clean replay is not required. The verifier must regenerate all production calculations and analyses offline within the separately frozen native budget. Preparation probes cannot substitute for production evidence.

Keep immutable code and data in `src/` and `inputs/`. Generated content belongs in `outputs/`; the verifier clears this directory before replay. Do not change source or static inputs during replay. Preserve partial outputs and failures without inventing missing numerical results. A fresh calculation of an identical state may be reused within the current replay if the model, coordinates and native record are exactly identified; changing a record's label is not a new calculation or an independent control.

Provide `outputs/evidence_manifest.json`, mapping logical observations to regular relative file paths, units, case IDs, array columns, native run IDs and checksums. Equivalent JSON, CSV, NPZ or HDF5 representations are acceptable. Splitting an axis across files is acceptable if sample identities are explicit, duplicates are checked, and the union has the required coverage. Native order, plot layout and optional explanatory fields do not determine scientific correctness. A particular RNG spelling or redundant reporting of the same observation is not an additional measurement.

The manifest contains an `observations` object. Each key below maps to one entry, or a list of entries for a split observation. An entry has `path` relative to `outputs/`, `sha256`, `case_id`, `units`, and, for native data, `native_run_id`. File and directory names are unrestricted. Optional `columns` maps the logical array names to stored column/dataset names; a complex array may map to `{"real": "real_column", "imag": "imag_column"}`. Optional `static_columns` lists arrays that are metadata rather than rows on the sample axis. Omit `columns` when names already agree. Split files retain identical logical columns and unchanged static metadata; consistent repeated samples are coalesced and conflicting duplicates are rejected.

| Logical observation | Required arrays or record |
|---|---|
| `linear/{passive,exceptional}/{helmholtz,coupled_mode}` | `delta`, complex `t`, `r_left`, `r_right`, `phase`, `delay` |
| `native/{baseline,grid,time,control}_{left,right}` | `wavelength_um`, raw matched `device_outgoing`, `reference_outgoing`, `device_incoming`, `reference_incoming`, `device_flux_in`, `reference_flux_in`, `device_flux_out`, `reference_flux_out`; `input_z_um`, `slab_length_um`, `gain_sign`, `direction` (`+1` left, `-1` right); actual registered `profile_position_um`, `profile_frequency`, `actual_epsilon`; reported `t`, `r`, `T`, `R` |
| `nonlinear/{n2_0p3,n2_0p5,n2_0p8}_{left,right}/continuation` | `output_intensity`, `input_intensity`, `reflected_intensity`, `stokes` with shape `(profile,4,position)`; optional `input_derivative_amplitude` |
| `nonlinear/{n2_0p3,n2_0p5,n2_0p8}_{left,right}/roots` | `input_intensity`, `branch_id`, nonnegative `output_amplitude`, `transmission`, `reflection`, signed `input_residual`; `output_amplitude**2` is transmitted power |
| `nonlinear/summary` | JSON `cases` record with turning points for each case; each turn includes `input_intensity`, `output_intensity`, `input_bracket`, and `output_bracket` or `amplitude_bracket` |
| `native/reversal_comparison` | Optional JSON interpretation of the physical reversal measurements |

For native field arrays, the leading dimension follows wavelength and the outgoing/incoming mode amplitude is in column zero. Material-registration arrays are static metadata, not wavelength rows. When using a callback-defined dispersive medium, register its susceptibility frequencies with Meep (for example through `extra_materials`) and verify the actually registered material; evaluating the intended formula alone is insufficient. Nonlinear continuation follows output power; retained computations and validated analytic exclusions together account for the entire declared domain, including its boundaries. Root records may use arbitrary branch labels; matching does not depend on their spelling. A headered six-column root table in the order above is also accepted. JSON records use a single manifest entry. Native logs, source/monitor traces, field coordinates, nonlinear profile coordinates, controls and analysis records remain required as appropriate to the scientific claim, even when not listed as an arithmetic input in this table. Manifest metadata identifies observations but does not establish native provenance.

Native logs, input decks, raw coordinates/fields/eigenvalues, analysis source and machine-readable final measurements must be available to the isolated read-only grader. An inaccessible evidence file is a replay/reader problem to diagnose, not proof that the scientific observation is zero. A candidate-written receipt alone is not trusted engine provenance. Private evaluation resources and reference result arrays are not candidate inputs.

Include a concise generated report and the task's requested figures. Figures illustrate retained data; a picture is neither a substitute for raw values nor an additional full scientific result. Interpretation must cite the regenerated observations. An LLM judge may assess whether reasoning follows the evidence, but must not replace deterministic arithmetic, state matching or native-provenance checks.

## Numerical precision

The object being reproduced is fixed; numerical implementation is not. State numerical uncertainties and retain controls that justify them. Controls measure sensitivity and do not automatically constitute rigorous mathematical error bounds. Comparison with a paper using a different computational model is distinct from same-model agreement.

Numeric reference envelopes require independent numerical validation and may not be selected from a tested model's output. Do not introduce a hidden method, a new target, or a retrospective change to obtain agreement.

Missing native evidence invalidates dependent numerical claims, not unrelated successfully computed cases. Zero, negative and inconclusive scientific findings are not automatically wrong.

The complete finite study requires valid raw evidence, recomputation and justified interpretation. Running a pipeline, matching a broad literature window, or writing all requested headings is insufficient by itself.

# Fixed study and observable definitions — 05

## 1. Three models, not one interchangeable answer

**Paper model P.** Use Eq. (1) and the finite grating `n(z)=n0+n1*cos(2*beta*z)+i*n2*sin(2*beta*z)` on `[-L/2,L/2]`, exterior `n0=1`, `n1=0.001`, `beta=100`, `L=12.5*pi`. The two required cases are `n2=0` and `n2=0.001`. Use `exp(-i*omega*time)`; positive imaginary index is loss. Compute complex scattering from the Helmholtz equation, not by substituting the coupled-mode answer.

**Approximation C.** Independently evaluate the paper's linear coupled-mode description for exactly the same parameters. Treat removable singularities by a supported limiting procedure. Report approximation error against P, not agreement between two rearrangements of C.

**Causal model D.** Meep 1D propagation along z, Ex/Hy, exterior index 1, `lambda_B=1.550 um`, period `Lambda=0.775 um`, 1250 complete periods, length `968.750 um`, same centered modulation origin. Define `a=1+0.001*cos(2*pi*z/Lambda)`, `b=0.001*sin(2*pi*z/Lambda)`, `f0=1/1.550`, `gamma=f0`. The material is exactly

```text
epsilon_inf = a*a - b*b
sigma = 2*a*b*gamma/f0
epsilon(z,f) = epsilon_inf + sigma*f0*f0/(f0*f0-f*f-i*gamma*f)
```

Query the actually registered Meep material at the center and both workband endpoint frequencies at 16 or more distinct positions over a period. Retain epsilon and the positive-real-part square-root branch. A formula evaluated outside Meep does not establish registered material identity. A physically equivalent FDTD reduction is allowed if demonstrated; an analytic-only solution is not.

Independently solve the same dispersive D model with a non-FDTD method and retain its own refinement. Run a physical reversal control `b -> -b` without moving the origin; do not relabel left/right output arrays as a new native run. D agrees with P's scaled index at its design frequency, not at arbitrary wavelengths.

## 2. Unique reporting axes and phase gauge

For P and C report `delta=-1+0.01*index`, integer `index=0..200`, with `k=beta-delta`. For D report `lambda=1.520+0.0002*index um`, `index=0..300`. These are fixed reporting axes; additional native sampling or adaptive refinement is unrestricted. Interpolation is identified as such and cannot replace required native D frequency coverage.

Retain both incidence directions and matched uniform-background reference amplitudes at identical planes. Define complex `t` after dividing out uniform propagation, so an empty background has `t=1`; define r against the corresponding incident wave. Retain pre-normalization data. Report `T=abs(t)^2`, `R=abs(r)^2` and complex t/r, not just intensities. A passive `R+T=1` identity is not a test for an active material.

For P/C, unwrap transmission phase continuously across the reporting axis, anchoring its value at delta=0 to the principal argument in `(-pi,pi]`. If transmission vanishes, report the singular point rather than assigning a derivative through it. Report `tau=d(phi)/dk=-d(phi)/d(delta)` with independent differentiation-resolution evidence; a plotting unwrap or a single finite-difference grid alone is not convergence.

The D invisibility-band answer is a **sample-defined interval**: piecewise-linearly interpolate the two scalars `R_L/0.01` and `abs(t_L-1)/0.05` separately on the fixed wavelength axis, intersect their sublevel sets at 1, and select the component containing 1.550 um. Return null if that point fails. A boundary at the workband limit is censored there, not a demonstrated physical endpoint. This definition does not assert invisibility between arbitrary unobserved frequencies.

Map wavelengths into the paper's length units explicitly. Separate P-versus-C approximation error, D-versus-scaled-P dispersion difference, and Meep-versus-independent-D discretization error. A single curve match cannot identify all three.

## 3. Finite nonlinear answer set

Use Eq. (9), the Stokes definitions in note [30], and the boundary powers of the paper. Fig. 4 supplies `n0=1`, `n1=0.5`, `L=7`, `delta=0`, and the plotted cases `n2 in {0.3,0.5,0.8}`. The paper defines `rho=k*chi/n0`, `kappa=k*n1/(2*n0)` and `g=k*n2/(2*n0)`, but neither its Fig. 4 caption nor its supplied TeX source fixes the numerical carrier and Kerr-intensity normalization. For the **declared same-equation diagnostic**, use `k=1`, `rho=1` and the stated dimensionless intensities. These last two values are explicit benchmark conventions, not values attributed to the authors. A claim of numerical Fig. 4 reproduction must independently justify its coordinate and intensity conversion, including preservation of the coupling-length and nonlinear-intensity combinations; qualitative similarity alone does not establish this conversion.

The answer is the set of stationary physical solutions in `0<=I_in<=3.2`, `0<=I_out<=16`, for each of the six parameter/direction cases. Here `I_out` is transmitted power, not reflected power. On the outgoing boundary there is no wave incident from the far side. Require nonnegative forward/backward powers and the Stokes identity. Report the zero-input limit separately.

Provide a branch atlas with boundary intersections and turning-point brackets, plus the complete root set at `I_in in {0.2,0.8,1.6,3.2}`. Each root includes transmitted/reflected power, internal Stokes profile, residuals and branch connectivity. All branches inside the specified rectangle count, including disconnected components if present; roots outside it are out of scope, not asserted absent. Set matching is independent of branch names or root order. Near-coincident roots must retain multiplicity/topology information rather than being rounded into one root.

Use your choice of integration, shooting, continuation or root-isolation method. Demonstrate coverage and refine integration and branch resolution separately. Neither one solution per input nor a smooth interpolation through selected points establishes completeness. Stationary multiplicity is not demonstrated dynamical bistability.

This is an independently validated numerical branch study, not a requirement for a rigorous global uniqueness theorem. Retain an accounting of the entire output-power domain: searched intervals, analytically excluded intervals, stationary/contact brackets and any unresolved cells. Use stationary/tangency-sensitive investigation as well as root sign changes; refine locally around near-zero derivatives, strong curvature or inconsistent branch counts. Independently reproduce the section-root sets, boundary intersections and branch connectivity with separate integration and branch-resolution controls at the stated numerical scales. Preserve close-root multiplicity; a small numerical separation is not permission to merge roots. Merely disclaiming a mathematical theorem does not invalidate otherwise established numerical coverage, and an unsubstantiated claim of completeness does not establish it. Analytic arguments may close cases or exclude intervals without unnecessary brute-force sampling.

Stokes intensities do not fix the common complex phase. Explain what additional field equation and reference would be needed to test a nonlinear phase claim. No unique nonlinear absolute phase or exact author Fig. 4 curve is required from the underspecified normalization. Do not silently import the linear carrier or strip an intensity-dependent phase to force agreement.

## 4. Validation, precision and scope

Retain independent native baseline, at least 1.5x observation duration and at least 1.5x spatial resolution for D, including raw source/monitor times and material identity. Required accuracy checks are: registered real and imaginary index errors each <=5% of 0.001; complex-t reference error <=0.03; duration/spatial complex-t change <=0.02; design R_R reference and refinement differences <=5%; left/right complex-t reciprocity error <=0.02. For power comparisons with a near-zero reference use `abs(R-R_ref)<=max(0.05*abs(R_ref),1e-6)` instead of division by zero. At the design point where right reflection is not near zero, the relative 5% requirement is unchanged. The absolute floor is a benchmark numerical rule; the Fig. 2 residual-reflection scale is a physical observation, not an author-quoted solver error bound.

Test the design-point diagnostics `R_L<=0.01`, `abs(T_L-1)<=0.03`, `abs(arg(t_L))<=0.03 rad`. Record measured pass/fail, with uncertainty; a correctly established physical failure is not replaced by a desired pass. Numerical acceptance and the physical invisibility diagnostic are distinct.

For nonlinear profiles require normalized Stokes-identity and conserved-quantity residuals <=1e-6 using declared nonzero component scales. Away from folds, require T/R changes divided by `1+abs(refined_value)` <=0.001. Turning-point input brackets must stabilize within 0.001. These are numerical study criteria, not uncertainties quoted by the paper.

Retain full source-on/off traces. For a defensible last direct-arrival time A and final time E, use the terminal half `[A+(E-A)/2,E]`, split into six equal physical-time blocks. Report each block maximum and its actual timestamp, the log-linear slope, and last/first maximum ratio. At least two samples per block are needed. Report regrowth, inadequate sampling and sub-noise ambiguity honestly. If using a background noise estimate, retain an independent matched trace and propagate its uncertainty; a clipped positive slope is not zero. This is a finite-observation diagnostic, not global stability. It is method-dependent control evidence, not an extra universal answer number. Unresolved growth cannot support a stationary-scattering claim.

Use the following fixed same-model comparisons. These are benchmark numerical acceptance criteria, not uncertainties quoted by the paper. They do not require P and C, or P and D, to agree within a same-model tolerance.

| Quantity | Acceptance |
|---|---|
| P/C complex `t`, `r_left`, `r_right` against an independent evaluation of that same model | `max(abs(value-reference)/max(1,abs(reference)))<=1e-3` |
| P/C continuously unwrapped phase with the specified center anchor | Maximum absolute difference `<=1e-3 rad`; phase must also agree with the retained complex t at this scale |
| P/C delay and independent derivative refinement | `max(abs(tau-tau_ref)/(1+abs(tau_ref)))<=1e-3`; compare in the declared `dphi/dk` units |
| Nonlinear section-root T/R against independent same-equation roots | Each `abs(value-reference)/(1+abs(reference))<=1e-3` |
| Recomputed nonlinear input boundary residual | `abs(I_in_computed-I_in_target)/(1+abs(I_in_target))<=1e-3` |
| Nonlinear reported T/R and signed residual versus recomputation | The corresponding normalized differences `<=1e-3` |
| Turning-point input/output coordinates and brackets | Input error and bracket width `<=1e-3`; output error and bracket width `<=1e-3*(1+abs(I_out_ref))`. Endpoint comparison allows only this bounded coordinate tolerance, not arbitrarily enlarged intervals. Retain a stationary-point residual and refinement evidence. |

At a true transmission zero, phase and delay remain undefined rather than replaced by zero. Phase gauge and derivative sign are still required; wrapped-angle agreement alone does not establish a correct continuous phase. Root matching is one-to-one, independent of labels and ordering, and must preserve count, near-root multiplicity, branch membership and connectivity. A root residual or small coordinate error alone cannot establish completeness. A coarse polyline is an explicitly identified interpolation diagnostic, not an independent root solve. Independent integration and branch-resolution controls must resolve ambiguous contacts; disagreement is not removed by merging roots or widening tolerances.

Native spectra, model-error curves, the interval record and nonlinear branch atlas form the required figures/tables. Keep controls distinguishable from reused production data.

Missing nonlinear evidence cannot erase valid linear measurements; missing native D evidence invalidates D-derived measurements, not a separately valid P calculation.
