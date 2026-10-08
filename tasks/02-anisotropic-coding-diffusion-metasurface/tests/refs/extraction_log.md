# Reference extraction notes: Anisotropic Coding Diffusion Metasurface

Reference CSVs record paper readings, not native HFSS control solutions. Current
rubric descriptions and the public contract are authoritative. Absolute paper
phase references are unknown: absolute phases and zero crossings below are
diagnostic readings, not acceptance windows. Directed phase differences use the
declared common-reference-plane convention. Finite-array RCS criteria follow
their current characterization requirements, not reference performance cutoffs.

## Figure index

| Paper figure | Image files | Content |
|---|---|---|
|1(a)/(b)/(c)|figure-001/002/003.jpg|Element dimensions, dual-polarization reflection magnitude, phases and difference|
|2(a)/(b)|figure-004/005.jpg|Annealing flowchart and AF convergence, not a numerical acceptance target|
|3 full panel|figure-007.jpg|Printed matrices and three patterns|
|3(a)/(b)/(c) patterns|figure-006/008/009.jpg|Uniform, initial and optimal AF views|
|4|figure-010.jpg|6 x6 layout; x points down and y right|
|5|figure-011.jpg|Normal-incidence reference-plate and x/y RCS|
|6(a)-(f)|figure-012/013/014/015/016/017.jpg|Current, near field and3D far field at5.86 GHz; near-field panels are not required comparisons|
|7(a)|figure-018.jpg|TM phase differences at15/30/45 degrees|
|7(b)|figure-019.jpg|Oblique array-level specular reduction, outside scope|
|8|figure-020.jpg|Spatial backscatter map, outside scope|
|9|figure-021.jpg|Prototype and chamber photographs|
|10(a)/(b)|figure-022/023.jpg|Simulated/measured reduction and oblique measurements;10(a) supplies a simulation cross-check|

figure-024.jpg is a license icon, not a scientific figure.

## Method and files

The recorded extraction method detects axis/tick locations and fits linear
pixel-coordinate calibrations with residuals below one pixel. RGB curve masks use
column-median coordinates, excluding legends, text and dashed guides; despiking
and a seven-point median filter precede0.2-0.25-GHz anchor sampling. AF references
are independent evaluations of Eq.(2), not digitized full-wave data.

| Reference | Source | Estimated reading uncertainty |
|---|---|---|
|unit_normal/reflection_phase_fig1c.csv|17 anchors at0.25 GHz; three curves, with150/210-degree guides and legends excluded|+/-0.03 GHz; +/-3-5 degrees|
|unit_normal/reflection_amplitude_fig1b.csv|Dual curves,0.25-GHz anchors, calibrated at1.050/1.000/0.950/0.900|+/-0.002|
|unit_oblique/phase_diff_fig7a.csv|Three curves,0.25-GHz anchors; unobscured ticks fitted, labels/legend excluded|+/-0.04 GHz; +/-3-5 degrees|
|array_ms/rcs_fig5.csv and array_pec/rcs_pec_fig5.csv|Three curves at0.2-GHz anchors, excluding legend pixels405-660 by315-425|+/-0.03 GHz; +/-0.3-0.5 dB|
|array_ms/rcs_reduction_x/y_fig5fig10a.csv|Digitized metasurface minus digitized plate, with reference interpolation; cross-checked against Fig.10(a)|+/-0.6 dB|
|af_patterns/af_targets.json|Eq.(2),5.8 GHz,1-degree grid,theta0-90,phi0-360 excluding duplicate endpoint,EF=1,d=40 mm,M=N=6|Deterministic grid calculation; discretization below0.1%|
|af_patterns/af_pattern_fig3a/b/c.png|Original figure-006/008/009 copies|Qualitative|
|array_ms/current_fig6a/b.png and farfield3d_fig6e/f.png|Original figure-012/013/016/017 copies|Qualitative|
|array_ms/layout_fig4.png|Original figure-010 copy|Layout inspection aid|
|targets/key_targets.json|Text statements and digitized landmarks|Distinguishes text_exact and figure_read|

## Recorded landmarks

- Fig.1(c): x/y phase zero crossings4.553/6.930 GHz; phase-difference peak205.2
  degrees across a5.45-5.80-GHz plateau; >=150-degree band4.691-6.853 GHz.
  At4 GHz, x/y/difference are82/139.5/53.6 degrees; at8 GHz,-156.4/-70.2/85.1.
  Digitized difference versus y-x differs by less than4 degrees at the anchors.
- Fig.1(b): minimum x/y magnitudes0.9957/0.9944, consistent with the stated >0.99.
- Fig.7(a):15-degree peak182.8 near6.0 GHz, plateau6.0-6.25;30-degree peak175.7
  near6.15;45-degree peak157.6 near6.35.
- Fig.5: plate8.77 dBsm at4 GHz and14.96 at8. The physical-optics comparison
  4*pi*A^2/lambda^2 gives about8.7/14.7 dBsm. x-polarized minima are-5.11 near
  5.83 and+0.31 near6.47 GHz, separated by a rise to+3.0 near6.2 GHz. The
  y-polarized minimum is-1.85 near5.94 GHz.
- Derived x reduction reaches-17.31 dB near5.85 GHz, with outer-envelope
  crossings5.185/6.854 GHz and a near-9.7-dB rise over6.13-6.27 GHz. The y
  minimum is-14.18 near5.96, with crossings5.423/6.914. The text gives bands
  5.2-6.86 and5.44-6.9 GHz. These envelope readings do not establish uninterrupted
  10-dB suppression; report connected components separately.

## Matrix and cross-checks

Printed Fig.3(c) rows are111000/100110/001000/101101/101010/010111, with18 ones.
The independently inspected Fig.4 layout agrees in all36 cells. One overprinted
cell required corner sampling rather than mean brightness. Bit1 uses patches
long along x, as in the upper-left example and the text. Symbol relabeling must
preserve this physical layout through the matching decoding convention.

Fig.5-derived reduction agrees with Fig.10(a) within reading uncertainty:
x minima-17.31 versus about-17.3, y-14.18 versus about-14, the6.2-GHz rise-9.67
versus about-9.8, and the second x minimum-12.71 versus about-13.5 dB.
Eq.(2) gives initial AF maximum26.712, consistent with the Fig.2(b) starting
value near26.5, and uniform maximum36. Full-hemisphere optimal maximum12.000
occurs near theta66/phi45 degrees, whereas Fig.2(b) converges near7.7-7.8.
A principal-plane-only evaluation gives about8.0; the paper optimization domain
is underspecified. Use the public numerical AF contract, not the convergence
plot, and do not require this already-disclosed ambiguity as an original finding.

## Limitations

The Fig.1(b) magnitude legend may interchange resonance/polarization associations
relative to Fig.1(c); the dual-polarization magnitude bounds do not depend on that
ambiguity. The15-degree curve at4 GHz in Fig.7(a) is axis-censored and its reference
cell is empty. Pattern/current references are original image copies, not numerical
fields. The near-10-dB rise is about-9.7 +/-0.5 dB, so an outer envelope must not be
described as a strict continuous band. No reference extraction establishes a new
native-solver calibration or changes the current rubric's characterization scope.
