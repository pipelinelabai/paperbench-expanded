# Reference extraction notes: CPW Quad-Port UWB MIMO

The reference CSVs contain paper readings, not native HFSS control solutions.
Their recorded method is visual axis/grid calibration and anchor extraction from
the original paper images. Only the current rubric and public contract define
acceptance conditions; the notes below do not introduce additional thresholds.

## Figure index

| Paper figure | Image files | Content |
|---|---|---|
| 1(a)/(b) | figure-002/003.jpg | Initial 19 x 19 mm single-element geometry and S11 |
| 2(a)/(b) | figure-004/005.jpg | Single element with stub and S11 |
| 3 | figure-006.jpg | Dimensioned four-element MIMO geometry and Table 1 symbols |
| 4 | figure-007.jpg | H2=10.7/11.2/11.7 mm S11 sweep |
| 5 | figure-008.jpg | Lp=3.5/4/4.5 mm sweep, outside the required comparison |
| 6 | figure-009.jpg | With/without-stub S11 comparison |
| 7 | figure-010.jpg | Prototype photograph, consecutive perimeter port labels |
| 8 | figure-011.jpg | MIMO simulated solid and measured dashed S-parameter curves |
| 9(a)-(d) | figure-012/013/014/015.jpg | Surface currents at3.5/9/14/19 GHz |
| 10(a)-(c) | figure-016/017/018.jpg | xy/xz/yz patterns at3.5/6.5/14 GHz |
| 11 | figure-019.jpg | Radiation efficiency |
| 12 | figure-020.jpg | ECC12/13/14 and DG on separate axes |
| 13 | figure-021.jpg | Peak gain and multiplexing efficiency on separate axes |

figure-001.jpg is a license icon, not a scientific figure. The residual (a)/(b)
labels above figure-014/015 belong to the preceding row of the original montage.
Use the figure captions, not those residual labels, for current frequencies.

## Files and uncertainty

| Reference | Source and extraction | Estimated reading uncertainty |
|---|---|---|
| mimo_final/s11_fig8.csv | Black simulated curve,34 anchors, denser near minima | +/-0.1 GHz; +/-1.5 dB; deep14.3-GHz minimum +/-4 dB |
| mimo_final/isolation_fig8.csv | Red S12, blue S13, green S14;24 anchors each | +/-0.15 GHz; +/-2 dB; deep minima +/-4 dB |
| mimo_final/efficiency_fig11.csv | Red curve,31 anchors | +/-0.1 GHz; +/-0.004 |
| mimo_final/ecc_dg_fig12.csv |19 ECC anchors; no usable digitized DG column | ECC +/-0.003, or +/-0.002 near zero |
| mimo_final/gain_muxeff_fig13.csv | Red solid gain and blue dashed multiplexing efficiency,30 anchors | +/-0.1 GHz; gain +/-0.15 dB; multiplexing efficiency +/-0.1 dB |
| mimo_final/pattern_landmarks_fig10.csv | Simulated polar-plot ripple/minimum landmarks | About +/-3 dB for circular cuts and +/-5 dB for deep nulls |
| mimo_final/current_fig9a_3p5GHz.jpg and current_fig9d_19GHz.jpg | Original figure-012/015 copies | Qualitative |
| single_initial/s11_fig1b.csv |30 anchors;14.15-GHz minimum reaches the -50-dB axis floor | +/-0.1 GHz; +/-0.8 dB, or +/-1.5 dB at minima; censored floor |
| single_stub/s11_fig2b.csv |28 anchors, axis from0 to-30 dB | +/-0.1 GHz; +/-0.6 dB |
| sweeps/fig4_h2_landmarks.csv | First/deepest minima and8.14/8.80/15.20-GHz rows | +/-0.12 GHz; +/-1 dB, or +/-1.5 dB where curves overlap |
| sweeps/fig6_stub_landmarks.csv | First minima,14.34/18.30-GHz rows and upper -10-dB crossing | +/-0.12 GHz; +/-1 dB |
| targets/key_targets.json | Abstract/text/Table2 statements and figure landmarks | Entries distinguish reported text values from figure readings |

S11 axes were calibrated linearly against2-GHz horizontal ticks and5/10-dB
vertical ticks. Fig.8 labels are0/-20/-40/-60 dB with10-dB subdivisions. Selected
feature rows lie on the public0.02-GHz grid. Eight interleaved curves in Fig.8 make
13-18-GHz coupling readings less certain, approximately +/-3 dB in that region.
Deep-null amplitudes are particularly sensitive to plot sampling; axis-censored
readings are not exact finite depths.

## Cross-figure interpretation

Fig.4 H2=11.2, Fig.6 with-stub and Fig.8 simulated S11 identify the same final
array: first minima near3.50/3.50/3.60 GHz, minima near6.3 GHz at-18.5/-18.6/-18 dB,
near11.4 GHz at-20.3/-21/-21 dB, and deep14.3-GHz minima with plot-dependent
depths-47.3/-38.3/-48 dB. Their18-20-GHz sections are about-13 to-11 dB. This
supports treating the H2 and stub sweeps as four-port-array comparisons, not
single-element sweeps. The single-stub Fig.2(b) instead has a4.35-GHz mismatch
near-8.7 dB and a16.7-GHz minimum near-17.8 dB.

The text's3.7 GHz denotes the first resonance, not the band edge. Other reported
comparisons are efficiency above75%, isolation above17 dB, ECC below0.08, DG above
9.97 and Table2 gain1.3-6.2 dBi. Their rough figure counterparts are minimum
efficiency0.766 near20 GHz, worst S12 about-17.5 dB near3 GHz, ECC peak0.0745 near
3 GHz and gain about1.35 near3 GHz/6.20 near18.9 GHz. Eq.(7) with ECC0.0745 gives
DG about9.972209, consistent with the text; this is a formula check, not a
replacement digitized DG point.

The H2 text describes a first-resonance shift from3.2 to3.8 GHz; figure minima
were read near3.35 to3.75 GHz. Retain the current rubric's explicit interpretation.
Fig.10 does not establish its axes relative to the antenna. Its sparse landmarks
do not justify fixed local-plane ripple/null acceptance cutoffs. Evaluate genuine
patterns, the declared basis and the public comparison requirements. Current
images provide qualitative excited-element and high-frequency stub morphology,
not calibrated field-amplitude targets. The public DG and worst-pair
total-efficiency multiplexing definitions govern derived quantities; these paper
readings do not independently calibrate their HFSS implementation.
