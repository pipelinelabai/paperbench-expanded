# Reference reading notes

The TE86 values at 8.05/8.80 GHz are not −3 dB edges of the first passband. Do not use the resulting 0.75 GHz width or associated sparse shape samples. The approximate 0.2 GHz width is diagnostic, not an exact reference. Identify main passbands using the public fixed windows and connected-component definition; the 13.6 GHz upper limit excludes later sidelobes. The overall perspective rotation in Fig. 1 does not establish an internal X/+ orientation contradiction. The records below document graph readings; grading windows are governed by the rubric.

# refs extraction log — 03-dual-passband-angular-stable-fss

Reading method: inspect the original images in `paper_image/`, crop key curve regions, and enlarge them by 2.0–3.2× using PIL LANCZOS. Calibrate visually against axis grid lines and read anchor points. Graph values come from the paper images. Exact values from the text and Table 2 are transcribed and identified by source in `targets/key_targets.json`.

## 1. Figure-to-paper_image mapping, identified by captions

| Paper figure | paper_image file | Content | Use |
|---|---|---|---|
| — | figure-001/002.jpg | "check for updates" and CC-BY badges | Not paper figures; unused |
| Fig. 1 | figure-003.jpg | 3D FSS cell diagram; metal on the upper substrate surface, SubH labeled; the cell is rotated 45°, so crosses appear as "+" | Group-A geometry verification |
| Fig. 2(a)/(b)/(c) | figure-004/005/006.jpg | Evolution: Stage 1, two annular slots; Stage 2, added central circular aperture; final cell, added four corner X-shaped slots | Topology verification; evolution stages are not scored |
| Fig. 3(a)/(b) | figure-007/008.jpg | Stage 1 TE/TM insertion loss at 0/60/86° and 0/60/83° | Not scored; Stage 1 dimensions are not separately specified |
| Fig. 4(a)/(b) | figure-009/010.jpg | Stage 2 TE/TM insertion loss | Not scored for the same reason |
| Fig. 5(a)/(b) | figure-011/012.jpg | Final-cell TE/TM S21, with 12–14 GHz enlarged insets | Second-passband details for te_86/tm_83/60° |
| Fig. 6 | figure-013.jpg | Labeled cell parameters: R1–R5, W1–W4, L1, P, g/2 | Group-A geometry reference; crosses have "X" orientation |
| Fig. 7 | figure-014.jpg | ECM circuit and side view, with metal facing the incident side | Layer-order verification; ECM is not scored |
| Fig. 8 | figure-015.jpg | Normal-incidence ECM versus HFSS S-parameters | te_00/tm_00 cross-check using HFSS dashed curves |
| Fig. 9 | figure-016.jpg | Normal-incidence TE versus TM S11/S21 from HFSS | Main source for te_00/tm_00 references |
| Fig. 10 | figure-017.jpg | TE angular-stability S21+S11 at 0/60/86° | Main source for te_60/te_86 references |
| Fig. 11 | figure-018.jpg | TM angular-stability S21+S11 at 0/60/83° | Main source for tm_60/tm_83 references |
| Fig. 12(a)/(b) | figure-019/020.jpg | Surface current at 8.45 / 12.76 GHz | fields_normal references; original-image copies |
| Fig. 13(a)/(b) | figure-021/022.jpg | Electric field at 8.45 / 12.76 GHz | fields_normal references; original-image copies |
| Fig. 14(a)/(b) | figure-023/024.jpg | Anechoic chamber and 30×30 fabricated sample | Not scored |
| Fig. 15 / Fig. 16 | figure-025/026.jpg | TE / TM measurements versus simulations | Not scored; simulated curves corroborate transmission-zero locations |

Note: Table 2 reports insertion loss at θ=30°, but the paper has no 30° curve plot. Only the exact Table 2 values are available for grading 30° variants; there are no reference curve files.

## 2. Reference files and sources

| Reference file | Source figure | Extraction notes | Estimated uncertainty |
|---|---|---|---|
| te_00/sparams_fig9_te.csv | Fig. 9 solid TE curves | 24 anchors, with both S21 and S11; edge frequencies anchored to exact text values 6.77/9.04/12.17/16.02 | Frequency ±0.08 GHz; magnitude ±0.5 dB, or ±1 dB on steep edges |
| tm_00/sparams_fig9_tm.csv | Fig. 9 dashed TM curves | As above; endpoints 6.85/9.11/12.18/16.05 are exact text values | As above |
| te_60/sparams_fig10_te60.csv | Fig. 10 green solid curve | 22 anchors, S21 only; oblique S11 dashed curves are too dense and unreliable to score. Rows at 8.45/12.76 GHz are anchored to exact Table 2 values | Frequency ±0.1 GHz; magnitude ±0.7 dB |
| te_86/sparams_fig10_te86.csv | Fig. 10 blue solid curve and Fig. 5(a) inset | First-passband graph readings at 7.6–8.8 GHz are excluded as references; 8.45 GHz uses Table 2. The second-passband 12.5–13.0 GHz segment comes from the enlarged inset, with −3 dB edges 12.70/12.88 and peak −0.5 at 12.78 | Main plot ±0.1 GHz / ±1 dB; inset ±0.05 GHz / ±0.15 dB |
| tm_60/sparams_fig11_tm60.csv | Fig. 11 green solid curve and Fig. 5(b) inset | 23 anchors | Same as te_60 |
| tm_83/sparams_fig11_tm83.csv | Fig. 11 blue solid curve and Fig. 5(b) inset | 29 anchors; band1/band2 endpoints 3.01/9.96/11.11/13.50 are exact text values | Same as te_86; see §5 for the band2 upper-edge discrepancy |
| fields_normal/jsurf_8p45GHz_fig12a.jpg and 3 other files | Fig. 12(a)(b), Fig. 13(a)(b) | Original field-image copies, including color scales, for paired-image semantic comparison | Qualitative hotspot locations |
| targets/key_targets.json | Table 2, Sec. 3.2 text, and the graph landmarks above | Each entry identifies exact text/table data or graph-read data | Text/table values treated as exact |

## 3. Per-figure reading records

### Fig. 9: normal incidence, TE versus TM, enlarged 2.2×
- S21 transmission zeros: TE 10.42 GHz / −57 dB; TM 10.44 / −53. TE and TM nearly coincide over the full frequency range, differing by < 0.3 dB except at the bottoms of deep minima.
- In-band S11 minima: p1 at 8.20 GHz, TE −27 / TM −30, with the TM minimum shifted right by ~0.05; p2 at 13.60, TE −26 / TM −27.
- S21 starts at −14 at 3 GHz and ends near −2.6 at 16.5 GHz. Renderings differ above 16 GHz; confidence is low, as noted in §5.

### Fig. 8: normal incidence, HFSS dashed curves, cross-check, enlarged 2.0×
- HFSS S21 zero: ~10.45 / ≤ −55; HFSS S11 minima: 8.1 / −28 and 13.5 / −21.
- Compared with Fig. 9, minimum frequencies differ by ≤ 0.1 GHz and the S11 p2 depth differs by ~5 dB: 13.5/−21 versus 13.6/−26. See the rubric for broad S11 windows and one-sided thresholds; this record only documents graph-reading differences.

### Fig. 10: TE at 0/60/86°, each half enlarged 2.6×
- 60°: band1 −3 dB edges ~7.55 / ~8.90; zero 10.28 / −46; band2 edges ~12.35 / ~13.5. The main plot gives 13.4 and the Fig. 5a inset gives 13.57, recorded as 13.5 ± 0.15. An additional sharp minimum at 15.60 / −35 is in the grating region and is not scored.
- 86°: the original PDF shows approximately −11 to −13 dB at 8.05/8.80 GHz, not −3 dB edges. The approximate 0.2 GHz first-passband width is diagnostic only and does not define an exact control window. Zero 10.36 / −63; second zero 15.15 / −58; see the Fig. 5(a) inset for band2.
- The 60° dashed S11 curve has a p1 minimum near 8.35 / −32; the normal-incidence dashed curve agrees with Fig. 9.

### Fig. 11: TM at 0/60/83°, each half enlarged 2.6×
- 60°: band1 edges ~6.40 / ~9.60; zero 10.25 / −32; band2 edges ~11.70 / ~13.75; additional minima 14.50 / −33 and 15.85 / −47 are in the grating region and are not scored.
- 83°: band1 starts at the 3 GHz axis boundary, with S21(3.0) ≈ −3.05, consistent with the text's 3.01; upper edge ~9.96, also consistent. Zero 10.30 / −28; band2 plateau −0.6 to −1.3; sharp minimum 13.8 / −25; recovery to ~−1 over 14.3–15.2; deep minimum 15.45 / −52; endpoint 16.5 / −1.6.
- The normal-incidence curve agrees with TM in Fig. 9. Its rendered zero depth is −38 because of plot sampling; use the Fig. 9 value.

### Fig. 5(a)/(b) insets: 12–14 GHz, enlarged 3.2×
- TE 86°, blue: narrow triangular peak, −3 dB edges 12.70 / 12.88, width ~0.18 GHz, peak −0.45 to −0.5 at 12.78; the 12.76 row is approximately −0.6.
- TE 60°, green: peak 0 at ~12.92; the 12.76 row is approximately −0.3, consistent with Table 2 = 0.30.
- TM 83°, blue: plateau −0.6 to −0.75, peaking near −0.6 at 13.2; falling −3 dB crossing ~13.68, as discussed in §5; the 12.76 row is approximately −0.75 to −0.85.
- TM 60°, green: peak ~0 at 13.0; the 12.76 row is approximately −0.1, consistent with Table 2 = 0.10.
- TE/TM 0°, orange: the 12.76 row is approximately −1.0, consistent with Table 2 = 0.98/0.98.

### Fig. 12/13: field maps
- 8.45 GHz: Jsurf peaks at 439.8 A/m, with hotspots on metal edges on both sides of the outer annular slot, strongest at the top and bottom. The electric field peaks at 18733 V/m and concentrates inside the outer slot.
- 12.76 GHz: Jsurf peaks at 321.1 A/m, with hotspots shifting toward the inner annular slot/central disk. The electric field peaks at 41113 V/m and concentrates in the inner slot.
- References are copies of the original images, not redrawings. Assessment concerns semantic hotspot locations.

## 4. Cross-check records

1. **Table 2 versus graph readings**: the normal-incidence 12.76 row is −1.0 in the graph versus 0.98/0.98 in the table; TE 60° gives −0.3 versus 0.30; TM 60° gives −0.1 versus 0.10; the TE 86° inset gives −0.6 ± 0.15 versus 0.70. All agree within reading uncertainty.
2. **Text bandwidths versus graph readings**: normal-incidence TE −3 dB crossings are ~6.8/~9.0/~12.2/~16.0 in the graph versus 6.77/9.04/12.17/16.02 in the text, in agreement. TM 83° readings 3.0/9.95/11.1 agree with 3.01/9.96/11.11 in the text; see §5 for the band2 upper edge.
3. **Normal-incidence curves in Fig. 8, Fig. 9, and Fig. 10/11**: three independent renderings of the same HFSS normal-incidence solution agree on zero frequencies, 10.42–10.45, and S11 minimum frequencies within ±0.1. Rendered deep-minimum depths differ from −37 to −57 because of plot sampling, so zero-depth criteria use one-sided thresholds only.
4. **Fig. 5 versus Fig. 10/11**: the final-cell S21 families appear in both places, with landmarks at 60°/86°/83° agreeing within ±0.1 GHz.
5. **Grating onset**: formula-based onset estimates of 13.69 GHz at 83° and 14.6 GHz at 60° agree with the additional sharp minima, supporting exclusion of grating-region dips from scoring.

## 5. Known discrepancies and low-confidence regions

1. **tm_83 band2 upper edge**: the text gives 13.50 GHz, while the Fig. 5(b) inset gives a −3 dB crossing near 13.65–13.70. Endpoint windows are defined only in the rubric; this extraction record does not maintain a separate set.
2. **Nonmonotonic TM second-passband width with angle**: 3.87 GHz at 0° → ~2.05 at 60° → 2.39 at 83°, with the 60°/83° bands truncated by grating-region dips at 14.5/13.8 GHz. The text statement "passband widths consistently increase" holds only for the first passband; the TM trend criterion therefore uses the band1 width sequence only.
3. **Tail above 16 GHz**: Fig. 8 and Fig. 9/10 disagree, showing −4.5 versus −2.6 at 16.5. Confidence is low; the 16.02/16.05 upper-edge windows allow ±0.35, and no criterion is imposed at the 16.5 row.
4. **Deep-minimum depths are plot-sampling lower bounds on depth**: different renderings of the same solution differ by up to 20 dB. All depth criteria are therefore one-sided.
5. **Oblique S11 dashed-curve families in Fig. 10/11**: curves are too dense and overlap too much to separate reliably. Oblique S11 is not scored, and its numerical columns are absent from refs.
6. **Normal-incidence TE versus TM text endpoint differences of 0.01–0.08 GHz**, such as 6.77 versus 6.85: a fourfold-symmetric structure should have coincident TE/TM responses at normal incidence. These differences reflect the paper's own simulation/reporting scatter. The rubric defines coincidence criteria and common endpoint windows; graph-reading records do not override grading requirements.
7. Stage 1/2 dimensions in Figs. 2a/b, 3, and 4 are not separately specified. The text explicitly states that the lattice spacing was adjusted in the third stage, leaving Stage 1/2 P unknown. Evolution stages are excluded from scoring, and no references were extracted for them.
