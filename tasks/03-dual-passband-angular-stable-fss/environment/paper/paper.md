Article

# A Dual-Passband Frequency Selective Surface with High Angular Stability and Polarization Insensitivity

Yi Li \* , Yan Ma, Peng Ren, Minrui Wang and Zheng Xiang

The State Key Laboratory of Integrated Services Networks, Xidian University, Xi’an 710071, China; 22011210589@stu.xidian.edu.cn (Y.M.); pren@xidian.edu.cn (P.R.); mrwang614@163.com (M.W.); zhx@mail.xidian.edu.cn (Z.X.)

\* Correspondence: liyi01@xidian.edu.cn

Abstract: In this paper, a dual-passband frequency selective surface (FSS) with high angular stability and polarization insensitivity is proposed. The unit structure consists of a circular aperture, two annular apertures and four cross apertures. The designed FSS can achieve a double-passband at the interested frequencies of 8.45 GHz and 12.76 GHz with an insertion loss of less than 1 dB, and it can retain a stable transmission characteristic with the incident angle ranging from 0° to 86° for TE mode and from 0° to 83° for TM mode. Good agreement between the experimental results and the simulated response verifies the feasibility of the proposed FSS.

Keywords: frequency selective surface (FSS); dual passband; high angular stability; polarization insensitivity

![Figure 1](paper_image/figure-001.jpg)

## 1. Introduction

Citation: Li, Y.; Ma, Y.; Ren, P.; Wang, M.; Xiang, Z. A Dual-Passband Frequency Selective Surface with High Angular Stability and Polarization Insensitivity. Micromachines 2024, 15, 690. https:// doi.org/10.3390/mi15060690

Academic Editor: Isabelle Huynen

Received: 30 April 2024   
Revised: 21 May 2024   
Accepted: 23 May 2024   
Published: 24 May 2024

![Figure 2](paper_image/figure-002.jpg)

Copyright: © 2024 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https:// creativecommons.org/licenses/by/ 4.0/).

Frequency selective surface (FSS) has garnered significant attention over the past few decades [1]. FSS, serving as a spatial filter, finds extensive applications in diverse fields, including antenna design, electromagnetic shielding, and microwave and millimeter-wave devices [2–5]. Notably, the radar stealth capabilities of the FSS have been a subject of considerable interest [6]. In order to diminish the radar cross-section (RCS) and improve radar stealth effectiveness, specialized FSS designs have been proposed to address variations in incident angles [7]. Changes in incidence angle or polarization state typically lead to alterations in the transmission characteristics of the FSS structure, thereby impacting signal transmission performance. Consequently, researchers are increasingly focusing on the development of FSS that exhibit improved angular stability and reduced sensitivity to polarization.

In recent years, numerous methods have been proposed to improve and enhance angular stability and polarization insensitivity [8–18]. For example, Lee et al. proposed a 3D-shaped FSS that utilizes through-holes in a multilayer printed circuit board structure to achieve a stable frequency response within an incident angle range of 0° to 60° [8]. Similarly, Zhao et al. proposed a quasi-fractal strip structure. This structure comprises a ‘swastika’- shaped metal strip surrounded by four rotationally symmetrical ‘H’-shaped metal strips, which achieve angular stability up to 80° [10]. As spectral resources become increasingly scarce, the need for dual-band capabilities in applications such as modern communication systems and radar technologies grows. Single-band solutions are inadequate, especially in situations requiring high angular stability and polarization insensitivity.

Due to the growing demand for multi-frequency applications, researchers have conducted relevant investigations [15,19–21]. For instance, Venkatesh et al. designed a dualband-stop FSS where the actual measurement results of angular stability reached 60° [15]. Kumar et al. presented a triband band-stop FSS with a stable frequency response up to 60° incidence angle for both TE and TM polarizations [21]. Although some simulated results achieve an angle stability of up to 80°, the actual measured outcomes do not meet the simulated results.

In recent studies, various aspects of dual-band FSS have been explored to enhance performance. Alwahishi et al., focusing on 6G technology, proposed a reconfigurable design that targets the 28 GHz and 38 GHz bands to improve spectrum management and frequency selection [22]. Additionally, they introduced an intelligent FSS unit that optimizes spectrum utilization and system performance, demonstrating significant advancements for future communication systems [23]. Furthermore, their other research investigated a design that allows for adjustable frequency responses through structural modifications, providing flexibility in application [24]. Complementing these studies, Dicandia and Genovesi designed a transmission-type polarization-insensitive and angularly stable polarization rotator using the characteristic modes theory, offering significant advancements in achieving polarization insensitivity and angular stability [25].

In this paper, a dual-passband FSS with high angular stability is proposed, which can achieve angular stability above 83° in TE and TM polarization only by the metal ring gap and the Jerusalem cross. The passbands are located in the X-band and Ku-band, respectively. The organization of this paper is as follows: Section 2 includes a detailed introduction to the unit structure and design process of the FSS, supplemented by an equivalent circuit model (ECM) to elucidate the working principles of the FSS. Section 3 covers simulations of the proposed FSS, including comparisons with the related circuit model. Section 4 details the production process of the FSS prototype and the experimental results obtained, and Section 5 concludes the article.

## 2. Design and Analysis of FSS

## 2.1. Structure Description

The proposed FSS structural design is based on a periodic unit structure, as shown in Figure 1. The unit structure primarily consists of a metallic plate and a dielectric substrate. The metallic plate adopts a gap-type design and covers the upper layer of the dielectric substrate.

![Figure 3](paper_image/figure-003.jpg)  
Figure 1. Schematic diagram of FSS unit structure.

The construction is based on the double square loop (DSL) structure, which is gradually assembled by joining double circular ring slots. The formation process of the unit cell is illustrated step by step in Figure 2.

In the initial stage, a dual-band structure is designed according to the DSL specifications, as shown in Figure 2a. The performance is depicted in Figure 3. As the incident angle increases, a partial shift in the resonance frequency of the second band can be observed. For TE polarization, the center frequency of the second band is 13.5 GHz at a $0 ^ { \circ }$ incident angle. When the incident angle reaches $8 6 ^ { \circ }$ , the center frequency shifts left to 12.76 GHz. For TM polarization, the center frequency of the second band is 13.9 GHz at a $0 ^ { \circ }$ incident angle, which significantly differs from that of TE polarization.

![Figure 4](paper_image/figure-004.jpg)  
(a)

![Figure 5](paper_image/figure-005.jpg)  
(b)

![Figure 6](paper_image/figure-006.jpg)  
(c)

Figure 2. Evolution of proposed FSS unit. (a) Stage 1. (b) Stage 2. (c) Proposed unit.  
![Figure 7](paper_image/figure-007.jpg)  
(a)

![Figure 8](paper_image/figure-008.jpg)  
(b)  
Figure 3. Insertion loss of Stage 1. (a) TE polarization. (b) TM polarization.

To enhance polarization insensitivity, the second stage incorporates circular slots symmetrically positioned at the center, as shown in Figure 2b. As indicated in Figure 4, for TM polarization, the center frequency of the second band shifts from 13.9 GHz to 13.5 GHz, aligning with the TE polarization. This reduces resonance frequency shifting and marginally improves angular stability.

![Figure 9](paper_image/figure-009.jpg)  
(a)

![Figure 10](paper_image/figure-010.jpg)  
(b)  
Figure 4. Insertion loss of Stage 2. (a) TE polarization. (b) TM polarization.

Furthermore, reducing unit cell spacing improves the angular stability of the FSS. The double circular ring structure remains the primary configuration for maintaining stability. Therefore, lattice spacing is adjusted appropriately without affecting the double-circular rings. In the third stage, four centrally symmetric cross-shaped slots are incorporated around the circular ring slots, as shown in Figure 2c. As demonstrated in Figure 5, for TE polarization, the insertion loss decreases from 1.2 dB to 0.5 dB at an incident angle of

86°. For TM polarization, the insertion loss decreases from 1.0 dB to 0.8 dB at an incident angle of 83°. The insertion loss for both TE and TM polarizations is reduced, improving angular stability.

![Figure 11](paper_image/figure-011.jpg)  
(a)

![Figure 12](paper_image/figure-012.jpg)  
(b)  
Figure 5. Insertion loss of proposed unit. (a) TE polarization. (b) TM polarization.

These adjustments and optimized designs ensure that the FSS maintains good performance under different incident angles and polarization conditions, significantly enhancing its angular and polarization stability.

The dielectric substrate is arranged in a quadrilateral periodic pattern. The results of the analysis indicate that the quadrilateral exhibits better resonance stability for the TE and TM modes than the triangle design. The dielectric substrate is of a duroid material with a relative dielectric constant of 2.2 and a loss tangent of 0.0009. Copper cladding is applied to the dielectric substrate with a thickness ranging from 0.017 mm to 0.035 mm. The unit cell is shown in Figure 6, and the optimized dimensions of the proposed structure for obtaining the desired response are given in Table 1.

![Figure 13](paper_image/figure-013.jpg)  
Figure 6. Parameter diagram of FSS unit structure.

Table 1. Unit structure parameters.
<table><tr><td>Parameter Value</td><td> $R _ { 1 }$  5.0 mm</td><td> $R _ { 2 }$  4.5 mm</td><td> $R _ { 3 }$  3.0 mm</td><td> $R _ { 4 }$  1.5 mm</td><td> $R _ { 5 }$  6.0 mm</td><td>SubH 1.0 mm</td></tr><tr><td>Parameter Value</td><td> $W _ { 1 }$  0.5 mm</td><td> $W _ { 2 }$  1.0 mm</td><td> $W _ { 3 }$  0.5 mm</td><td> $W _ { 4 }$  0.4 mm</td><td> $P$  11.0 mm</td><td> $L _ { 1 }$  2.0 mm</td></tr></table>

## 2.2. Operation Principle

Utilizing the theoretical derivations from traditional filters such as the DSL and gridded square loop (GSL), the equivalent circuit of the unit cell of the proposed FSS is shown in Figure 7. The equivalent circuit representation of the double circular ring patch consists of two shunt serial LC resonators. The values of inductance (L) and capacitance (C) in these LC circuits are influenced by the spacing between conductive elements and components. Lee et al. have summarized the normalized equations for calculating the inductance and capacitance of strip gratings [26], as follows.

![Figure 14](paper_image/figure-014.jpg)  
Figure 7. ECM of the proposed FSS. $L _ { 1 } = 1 . 0 4 3$ nH, $L _ { 2 } = 0 . 0 2 8$ nH, $L _ { 3 } = 0 . 3 5 8$ nH, $C _ { 1 } = 0 . 2 2 1 \mathrm { p H }$ $C _ { 2 } = 0 . 1 6 5 \mathrm { p H } , C _ { 3 } = 1 0 . 0 0 0 \mathrm { p H } , C _ { 4 } = 0 . 5 6 1 \mathrm { p F }$

$$
\begin{array} { l } { { X _ { \mathrm { T E } } = F ( p , w , \lambda , \theta ) } } \\ { { \displaystyle \ = { \frac { p \cos \theta } { \lambda } } \left[ \ln \left( \csc { \frac { \pi w } { 2 p } } \right) + G ( p , w , \lambda , \theta ) \right] } } \end{array}\tag{1}
$$

$$
\begin{array} { l } { { \displaystyle B _ { \mathrm { T M } } = 4 F ( p , g , \lambda , \varphi ) } } \\ { { \displaystyle \quad = \frac { 4 p \cos \varphi } { \lambda } \left[ \ln \left( \csc \frac { \pi g } { 2 p } \right) + G ( p , g , \lambda , \varphi ) \right] } } \end{array}\tag{2}
$$

$$
X _ { \mathrm { T M } } = \frac { p \sec \varphi } { \lambda } \left[ \ln \left( \csc \frac { \pi w } { 2 p } \right) + G ( p , w , \lambda , \varphi ) \right]\tag{3}
$$

$$
B _ { \mathrm { T E } } = \frac { 4 p \sec \theta } { \lambda } \left[ \ln \left( \csc \frac { \pi g } { 2 p } \right) + G ( p , g , \lambda , \theta ) \right]\tag{4}
$$

where G is the specified correction term, $p$ is the period, w is the width of the metal strip, and $g$ is the distance between two adjacent rings. θ and φ are the incidence angles, and λ is the incident wavelength. Therefore, following the equivalent circuit for square ring apertures, the ECM for circular apertures in this structure can be derived. The formula for calculating the normalized inductance component of circular ring apertures is provided.

$$
L _ { 1 } = \frac { 1 } { 2 \pi f } ( X _ { L 1 \_ 2 } + \frac { w _ { 1 } } { 2 R _ { 2 } + g + 2 M } X _ { L 1 \_ 1 } )\tag{5}
$$

$$
L _ { 2 } = { \frac { 1 } { 2 \pi f } } ( { \frac { 1 } { 1 0 } } X _ { L 2 \_ 1 } + { \frac { w _ { 3 } } { 2 R _ { 3 } + g + 2 M } } X _ { L 1 \_ 2 } )\tag{6}
$$

$$
L _ { 3 } = \frac { 1 } { 2 \pi f } \left\{ \frac { 2 \pi ( R _ { 3 } - R _ { 4 } ) } { 2 p } F ( p , 2 R _ { 3 } - 2 R _ { 4 } , \lambda , \theta ) \right\}\tag{7}
$$

where

$$
X _ { L 1 \_ 1 } = F ( p , g + 2 M , \lambda , \theta )\tag{8}
$$

$$
X _ { L 1 \_ 2 } = \frac { \pi R _ { 2 } } { p } F ( p , 2 w _ { 2 } , \lambda , \theta )\tag{9}
$$

$$
X _ { L 2 \_ 1 } = \frac { \pi R _ { 3 } } { p } F ( p , 2 R _ { 3 } , \lambda , \theta )\tag{10}
$$

In the above formulas, p denotes the structural period. In Equation (1), which calculates the inductance of the strip metal, w represents the width of the strip metal. In Equation (5), w is defined as $M + 2 g ,$ indicating the total width of the outermost metal, where M represents the average width of the circular gaps. Since the outer metal is circular, the width of the metal varies at every point. In this case, the average of a function formula is employed.

$$
f _ { \mathrm { a v g } } = \frac { \int _ { a } ^ { b } f ( x ) d x } { b - a }\tag{11}
$$

The average width of the outer metal is $M + 2 g$

$$
M = \frac { \int _ { - d / 2 } ^ { d / 2 } \left[ \left( d / 2 \right) - \sqrt { \left( d / 2 \right) ^ { 2 } - x ^ { 2 } } \right] d x } { d }\tag{12}
$$

The branch $( L _ { 1 } - C _ { 1 } )$ represents the impedance of the outermost metal conductor containing cross-shaped slots. The branch $( L _ { 2 } - C _ { 2 } )$ refers to the impedance of the metal ring formed in relation to the conductor $g$ and the width of the circular ring $W _ { 2 }$ . The branch $\left( L _ { 3 } - C _ { 3 } \right)$ represents the impedance formed by the interaction between the conductor of the circular ring with width $W _ { 2 }$ and the innermost metal ring. Due to the parameters of capacitance and inductance being influenced not just by individual slots or conductors, an intermediate variable is introduced. The calculation process for capacitance is as follows:

$$
C _ { 1 } = \frac { 1 } { 2 \pi f } \varepsilon _ { e f f } \times [ F ( p , 2 R _ { 1 } - 2 M , \lambda , \varphi ) + F ( 2 R _ { 1 } - w _ { 1 } , w _ { 1 } , \lambda , \varphi ) ]\tag{13}
$$

$$
C _ { 2 } = \frac { 1 } { 2 \pi f } \varepsilon _ { e f f } \times \left[ F ( 2 R _ { 1 } - w _ { 1 } , w _ { 1 } , \lambda , \varphi ) + F ( 2 R _ { 3 } , w _ { 3 } , \lambda , \varphi ) \right]\tag{14}
$$

In (13) and $( 1 4 ) , \varepsilon _ { e f f }$ represents the effective relative permittivity of the dielectric substrate. If one side of the FSS contains a thick dielectric substrate, the equivalent capacitance increases by a coefficient of $\varepsilon _ { e q } = \left( \varepsilon _ { r } + 1 / 2 \right)$ . For a thin dielectric substrate, the equivalent capacitance is a function of the substrate thickness and permittivity, and its normalized equation is derived:

$$
\varepsilon _ { e q } = \varepsilon _ { r } + { \left( { \varepsilon _ { r } - 1 } \right) } \times { \bigl ( } \frac { - 1 } { \left( e ^ { x } \right) ^ { N } } { \bigr ) } ; x = \frac { 1 0 h } { p }\tag{15}
$$

where h denotes the thickness of the dielectric substrate, and N is the exponential factor related to the unit shape, ranging from 1.3 to 1.8. For this analysis, a value of 1.8 is selected for N. The transmission coefficients can be derived along with the normalized admittance, expressed as $\begin{array} { r } { | \tau | ^ { 2 } = \frac { 4 } { 4 + Y ^ { 2 } } } \end{array}$ . The equivalent circuit theory for the circular ring, covered by Equations (5) to (15), accounts for the interaction between the inductance and capacitance of the unit components of the circular ring. These equations facilitate a preliminary estimation of the initial physical dimensions. However, due to mutual coupling between the metals, these formulas may still contain errors. The circuit is simulated using the advanced design system (ADS), with the lumped elements subsequently optimized. The optimized values of these elements are depicted in Figure 7.

## 3. Results and Discussion

## 3.1. Simulation of ECM and Polarization Stability

This design employs the software Ansys HFSS 2021 R1 to perform filtering analysis on the loaded metal unit structure, and the simulation results are compared with ECM results. Figure 8 illustrates the comparison between the simulation results and ECM results at a $0 ^ { \circ }$ incident angle. The ECM simulation yielded similar results to those of simulated results, which confirms the accuracy of the ECM. When the angle of incidence is at 0 degrees, the S-parameters demonstrate uniformity for both TE and TM polarizations, as shown in Figure 9.

![Figure 15](paper_image/figure-015.jpg)

Figure 8. Comparison of S-parameters between ECM and HFSS.  
![Figure 16](paper_image/figure-016.jpg)  
Figure 9. Comparison of S-parameters between TE mode and TM mode.

## 3.2. Simulation of Angular Stability

The simulated results of angular stability in TE and TM polarizations are shown in Figures 10 and 11. In addition, the specific performance parameters are shown in Table 2.

Table 2. Insertion loss under TE/TM mode.
<table><tr><td>Angle (deg)</td><td>Insertion Loss of Center Frequency in First Passband (dB)</td><td>Insertion Loss of Center Frequency in Second Passband (dB)</td></tr><tr><td>0</td><td>0.36/0.24</td><td>0.98/0.98</td></tr><tr><td>30</td><td>0.12/0.23</td><td>0.84/0.59</td></tr><tr><td>60</td><td>0.71/0.08</td><td>0.30/0.10</td></tr><tr><td>86/83</td><td>0.76/0.52</td><td>0.70/0.99</td></tr></table>

In Figure 10, the structure demonstrates high angular stability in TE polarization, maintaining an insertion loss of less than −1 dB for incident angles ranging from 0° to 86°. As the incident angle increases, the passband bandwidth progressively narrows. At an incidence angle of $0 ^ { \circ } .$ , the −3 dB bandwidths $( S _ { 2 1 } \ \ge \ - 3 \ \mathrm { d B } )$ range from 6.77 GHz to 9.04 GHz and from 12.17 GHz to 16.02 GHz, with relative bandwidths of 28.6% and 27.3%, respectively.

![Figure 17](paper_image/figure-017.jpg)  
Figure 10. Performance of angular stability in TE mode.

Similarly, Figure 11 depicts the TM polarization filtering performance, where the structure maintains an insertion loss of less than −1 dB for incident angles ranging from $0 ^ { \circ }$ to $8 3 ^ { \circ } . \mathrm { A t } 0 ^ { \circ }$ incidence angle, the −3 dB bandwidths $( S _ { 2 1 } \ge - 3$ dB) range from 6.85 GHz to 9.11 GHz and from 12.18 GHz to 16.05 GHz, with relative bandwidths of 28.3% and 27.4%, respectively. As the incidence angle increases, the passband widths consistently increase. At 83° incidence angle, the −3 dB bandwidths $( S _ { 2 1 } \ge - 3$ dB) ranged from 3.01 GHz to 9.96 GHz and from 11.11 GHz to 13.50 GHz.

![Figure 18](paper_image/figure-018.jpg)  
Figure 11. Performance of angular stability in TM mode.

From Figures 10 and 11, it can be observed that as the incident angle increases, the transmission bandwidth for TE-polarized waves gradually diminishes, whereas that for TMpolarized waves broadens. This variation in wave impedance is attributed to changes in the incident angle [15].

The equation used to determine the wave impedance for the TE mode is expressed as $\begin{array} { r } { Z _ { T E } = \frac { Z _ { 0 } } { \cos \theta } , } \end{array}$ where $\theta$ represents the angle of incidence relative to the perpendicular of the FSS surface. With an increase in the incident angle, the impedance rises, leading to an increased quality factor of the load and a resultant reduction in the transmission bandwidth of the resonator. Consequently, in TE polarization, the dual-bandwidth continuously decreases. In contrast, the wave impedance for the TM mode, calculated by the formula

$Z _ { T M } ~ = ~ Z _ { 0 }$ sin θ, decreases with an increase in the incident angle. As a result, in TM polarization, there is a noticeable reduction in out-of-band suppression, and the bandwidth of the dual-band transmission consistently increases.

## 3.3. Surface Current and Electric Field Distribution

The surface current and electric field distributions at the first and second resonant frequencies are shown in Figures 12 and 13. The distribution of electric field and current is predominantly concentrated around the outer ring at the first resonance frequency of 8.45 GHz. At this frequency, there is a complementary relationship between surface current and electric field, with the electric field exhibiting greater strength while the current is relatively weaker. Conversely, at the second resonance frequency of 12.76 GHz, the current and electric field tend to disperse around the inner ring. Regions characterized by high current exhibit significant electric inductance, whereas areas with low current contribute to the capacitance of the FSS.

![Figure 19](paper_image/figure-019.jpg)  
(a)

![Figure 20](paper_image/figure-020.jpg)  
(b)

Figure 12. Surface current distributions: (a) 8.45 GHz; (b) 12.76 GHz.  
![Figure 21](paper_image/figure-021.jpg)  
(a)

![Figure 22](paper_image/figure-022.jpg)  
(b)  
Figure 13. Electric field distributions: (a) 8.45 GHz; (b) 12.76 GHz.

## 4. Fabrication and Experimental Results

To verify the simulated results, a prototype of the proposed structure is fabricated. The dimensions of the prototype are 330 mm × 330 mm with 30 × 30 elements. The measurement equipment environment is shown in Figure 14, where two sets of horn antennas are used: one operating within a frequency range of 2 GHz to $5 \mathrm { G H z } ,$ and the other operating within a frequency range of 5 GHz to 18 GHz. After aligning the robotic arm at a 90° angle relative to the prototype, the prototype was positioned in a vertical orientation. The structure is placed in the region from the transmitting antenna and just in front of the receiving antenna to cover the entire aperture of the receiving antenna to measure the improved transmission characteristics of the structure. The antennas are connected to a vector network analyzer (VNA) to measure the transmission coefficients of the prototype. The circular placement plate beneath the prototype was rotated at fixed angles, and successive measurements of the transmission characteristics at various angles were conducted.

![Figure 23](paper_image/figure-023.jpg)  
(a)

![Figure 24](paper_image/figure-024.jpg)  
(b)  
Figure 14. (a) Evaluate environment; (b) prototype of FSS.

The comparison of the measured results with the simulated results for TE and TM polarizations is shown in Figures 15 and 16, respectively. For TE polarization, the physical model exhibits insertion losses of 0.25 dB and 0.9 dB at $0 ^ { \circ }$ incident angle and 3.59 dB and 4.68 dB at $8 6 ^ { \circ }$ incident angle. For TM polarization, the physical model demonstrates insertion losses of 1.07 dB and 2.9 dB at $0 ^ { \circ }$ incident angle and 2.88 dB and 3.05 dB at $8 6 ^ { \circ }$ incident angle. The measure results demonstrate a degree of agreement with the simulated results, consistent with the results of the experiment. However, as a result of manufacturing inaccuracies, a minor variance in the central frequency of the measured results has been observed. Moreover, a comparison of this work with previously reported structures is given in Table 3.

![Figure 25](paper_image/figure-025.jpg)  
Figure 15. Comparison of simulated and measured results in TE mode.

Table 3. Performance comparison with existing designs.
<table><tr><td>Ref.</td><td>Type</td><td>Unit Cell</td><td>Thickness</td><td>Number of Bands</td><td>Angle (Mea.)</td></tr><tr><td>[8]</td><td>3D</td><td>0.21λ</td><td>0.05λ</td><td>1</td><td>60</td></tr><tr><td>[9]</td><td>2D</td><td>0.36λ</td><td>0.02λ</td><td>1</td><td>75</td></tr><tr><td>[10]</td><td>2D</td><td>0.12λ</td><td>0.05λ</td><td>1</td><td>80</td></tr><tr><td>[13]</td><td>2D</td><td>0.17λ</td><td>0.04λ</td><td>1</td><td>85</td></tr><tr><td>[16]</td><td>2.5D</td><td>0.21λ</td><td>0.11λ</td><td>1</td><td>60</td></tr></table>

Table 3. Cont.
<table><tr><td>Ref.</td><td>Type</td><td>Unit Cell</td><td>Thickness</td><td>Number of Bands</td><td>Angle (Mea.)</td></tr><tr><td>[18]</td><td>3D</td><td>0.33λ</td><td>0.34λ</td><td>1</td><td>45</td></tr><tr><td>[19]</td><td>2D</td><td>0.08λ</td><td>0.01λ</td><td>2</td><td>60</td></tr><tr><td>[20]</td><td>2D</td><td>0.27λ</td><td>0.49λ</td><td>2</td><td>60</td></tr><tr><td>[15]</td><td>2D</td><td>0.15λ</td><td>N.A.</td><td>2</td><td>60</td></tr><tr><td>This work</td><td>2D</td><td>0.31λ</td><td>0.02λ</td><td>2</td><td>86/83</td></tr></table>

![Figure 26](paper_image/figure-026.jpg)  
Figure 16. Comparison of simulated and measured results in TM mode.

## 5. Conclusions

This paper proposes a dual-passband FSS characterized by superior angular stability. This structure exhibits dual-passband characteristics within the X-band and Ku-band, enabling effective operation across diverse communication scenarios. Furthermore, the center frequency point of the structure remains constant in both TE and TM polarizations, demonstrating remarkable angular and polarization stability. Specifically, the angular stability can achieve up to $8 6 ^ { \circ }$ in TE polarization and $8 3 ^ { \circ }$ in TM polarization. The consistency of the results is confirmed by the equivalent circuit method, full-wave simulation, and physical experimentation. The FSS designed in this paper has an extremely high application value in the fields of radome, multi-frequency communication, and electromagnetic shielding. It can not only improve the stealth performance of communication devices and the stability of communication systems, but also promote the integration of electronic systems.

Author Contributions: Conceptualization, Y.M. and Y.L.; methodology, Y.M.; software, Y.M.; validation, Y.M.; formal analysis, Y.M. and M.W.; investigation, P.R.; writing—original draft preparation, M.W. and P.R.; writing—review and editing, M.W. and Y.L.; visualization, M.W. and Y.L.; supervision, Z.X. All authors have read and agreed to the published version of the manuscript.

Funding: This research was funded in part by Postdoctoral fellowship program of CPSF, grant number GZC20232050.

Data Availability Statement: Data are contained with in the article.

Conflicts of Interest: The authors declare no conflicts of interest.

## References

1. Munk, B.A. Frequency Selective Surfaces: Theory and Design; John Wiley & Sons, Inc.: Hoboken, NJ, USA, 2000. [CrossRef]

2. Mei, P.; Pedersen, G.F.; Zhang, S. A Broadband and FSS-Based Transmitarray Antenna for 5G Millimeter-Wave Applications. IEEE Antennas Wirel. Propag. Lett. 2021, 20, 103–107. [CrossRef]

3. Sivasamy, R.; Moorthy, B.; Kanagasabai, M.; Samsingh, V.R.; Alsath, M.G.N. A Wideband Frequency Tunable FSS for Electromagnetic Shielding Applications. IEEE Trans. Electromagn. Compat. 2018, 60, 280–283. [CrossRef]

4. Fatima, F.; Akhtar, M.J.; Ramahi, O.M. Frequency Selective Surface Structures-Based RF Energy Harvesting Systems and Applications: FSS-Based RF Energy Harvesting Systems. IEEE Microw. Mag. 2024, 25, 47–69. [CrossRef]

5. Chen, H.; Chen, H.; Xiu, X.; Xue, Q.; Che, W. Transparent FSS on Glass Window for Signal Selection of 5G Millimeter-Wave Communication. IEEE Antennas Wirel. Propag. Lett. 2021, 20, 2319–2323. [CrossRef]

6. Chakradhary, V.K.; Baskey, H.B.; Roshan, R.; Pathik, A.; Akhtar, M.J. Design of Frequency Selective Surface-Based Hybrid Nanocomposite Absorber for Stealth Applications. IEEE Trans. Microw. Theory Tech. 2018, 66, 4737–4744. [CrossRef]

7. Liao, W.J.; Zhang, W.Y.; Hou, Y.C.; Chen, S.T.; Kuo, C.Y.; Chou, M. An FSS-Integrated Low-RCS Radome Design. IEEE Antennas Wirel. Propag. Lett. 2019, 18, 2076–2080. [CrossRef]

8. Lee, I.G.; Hong, I.P. 3D frequency selective surface for stable angle of incidence. Electron. Lett. 2014, 50, 423–424. [CrossRef]

9. Chou, H.H.; Ke, G.J. Narrow Bandpass Frequency Selective Surface with High Level of Angular Stability at Ka-Band. IEEE Microw. Wirel. Compon. Lett. 2021, 31, 361–364. [CrossRef]

10. Zhao, Z.; Shi, H.; Guo, J.; Li, W.; Zhang, A. Stopband Frequency Selective Surface with Ultra-Large Angle of Incidence. IEEE Antennas Wirel. Propag. Lett. 2017, 16, 553–556. [CrossRef]

11. Abidin, Z.U.; Cao, Q.; Shah, G. Design of a Compact Single-Layer Frequency Selective Surface with High Oblique Stability. IEEE Trans. Electromagn. Compat. 2022, 64, 2060–2066. [CrossRef]

12. Liu, N.; Sheng, X.; Zhang, C.; Guo, D. Design of Frequency Selective Surface Structure with High Angular Stability for Radome Application. IEEE Antennas Wirel. Propag. Lett. 2018, 17, 138–141. [CrossRef]

13. Hong, T.; Xing, W.; Zhao, Q.; Gu, Y.; Gong, S. Single-Layer Frequency Selective Surface with Angular Stability Property. IEEE Antennas Wirel. Propag. Lett. 2018, 17, 547–550. [CrossRef]

14. Zhou, X.; Sun, R.; Zhao, P.; Cao, Y.; Yuan, B.; Chen, S.; Wang, G. A Novel Design of a Compact Frequency-Selective Surface with High Selectivity and Angular Stability. IEEE Microw. Wirel. Compon. Lett. 2022, 32, 931–934. [CrossRef]

15. Feng, L.; Zhen, Y.; Xiaoyu, P. High Angle Stability Frequency Selective Surface Design and Simulation. In Proceedings of the 2023 6th World Conference on Computing and Communication Technologies (WCCCT), Chengdu, China, 6–8 January 2023; pp. 57–60. [CrossRef]

16. Li, D.; Li, T.W.; Li, E.P.; Zhang, Y.J. A 2.5-D Angularly Stable Frequency Selective Surface Using Via-Based Structure for 5G EMI Shielding. IEEE Trans. Electromagn. Compat. 2018, 60, 768–775. [CrossRef]

17. Deng, G.; Yu, Z.; Yang, J.; Yin, Z.; Li, Y.; Chi, B. A Miniaturized 3-D Metamaterial Absorber with Wide Angle Stability. IEEE Microw. Wirel. Compon. Lett. 2022, 32, 1111–1114. [CrossRef]

18. Wang, P.; Jiang, W.; Hong, T.; Li, Y.; Pedersen, G.; Shen, M. A 3-D Wide Passband Frequency Selective Surface with Sharp Roll-Off Sidebands and Angular Stability. IEEE Antennas Wirel. Propag. Lett. 2022, 21, 252–256. [CrossRef]

19. Ghosh, S.; Srivastava, K.V. An Angularly Stable Dual-Band FSS with Closely Spaced Resonances Using Miniaturized Unit Cell. IEEE Microw. Wirel. Compon. Lett. 2017, 27, 218–220. [CrossRef]

20. Liu, N.; Sheng, X.; Zhang, C.; Guo, D. Design of Dual-Band Composite Radome Wall with High Angular Stability Using Frequency Selective Surface. IEEE Access 2019, 7, 123393–123401. [CrossRef]

21. Kumar, T.R.S.; Vinoy, K.J. A Miniaturized Angularly Stable FSS for Shielding GSM 0.9, 1.8, and Wi-Fi 2.4 GHz Bands. IEEE Trans. Electromagn. Compat. 2021, 63, 1605–1608. [CrossRef]

22. Alwahishi, R.; Ali, M.M.M.; Elzwaw, G.; Denidni, T.A. Reconfigurable Dual-Band 28/38 GHz Frequency Selective Surface for 6G Applications. In Proceedings of the 2021 IEEE 19th International Symposium on Antenna Technology and Applied Electromagnetics (ANTEM), Montreal, QC, Canada, 8–11 August 2021; pp. 1–2. [CrossRef]

23. Alwahishi, R.; PourMohammadi, P.; Ali, M.M.M.; Denidni, T.A. A Dual-Band Intelligent Frequency Selective Surface Unit Cell For Future Communication Systems. In Proceedings of the 2022 IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/URSI), Denver, CO, USA, 10–15 July 2022; pp. 986–987. [CrossRef]

24. Alwahishi, R.; Ahmed, F.; Ali, M.M.M.; Denidni, T.A. A Dual-Band Frequency Selective Surface with Reconfigurable Properties. In Proceedings of the 2023 IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (USNC-URSI), Portland, OR, USA, 23–28 July 2023; pp. 1785–1786. [CrossRef]

25. Dicandia, F.A.; Genovesi, S. Design of a Transmission-Type Polarization-Insensitive and Angularly Stable Polarization Rotator by Using Characteristic Modes Theory. IEEE Trans. Antennas Propag. 2023, 71, 1602–1612. [CrossRef]

26. Lee, C. Equivalent-circuit models for frequency-selective surfaces at oblique angles of incidence. IEE Proc. H (Microw. Antennas Propag.) 1985, 132, 395–399. [CrossRef]