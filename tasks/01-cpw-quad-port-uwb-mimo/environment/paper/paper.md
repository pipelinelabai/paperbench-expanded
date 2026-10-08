Communication

# CPW Fed Compact UWB 4-Element MIMO Antenna with High Isolation

Wenfei Yin 1,\*, Shaoxiang Chen 1, Junjie Chang 1, Chunhua Li 1 and Salam K. Khamas 2

1 School of Computer Science and Information Engineering, Hefei University of Technology, Hefei 230009, China; shaoxiangc2020@sina.com (S.C.); junjiec2021@sina.com (J.C.); lch2014@hfut.edu.cn (C.L.)

2 Department of Electronic and Electrical Engineering, University of Sheffield, Sheffield S10 2TN, UK; s.khamas@sheffield.ac.uk

\* Correspondence: wenfeiyin@hfut.edu.cn

Abstract: In the paper, an extremely compact multiple-input-multiple-output (MIMO) antenna is proposed for portable wireless ultrawideband (UWB) applications. The proposed prototype consists of four monopole antenna elements, which are placed perpendicularly to achieve polarization diversity. In addition, the mutual coupling between antenna elements is suppressed by designing the gap between the radiation element and the ground plane. Moreover, a matching stub has been connected to the feedline to ensure impedance matching in high frequency. Both simulated and measured results indicate that the proposed antenna has a bandwidth of 3–20 GHz, with a high isolation better than 17 dB. In addition, the designed MIMO antenna offers excellent radiation characteristics and stable gain over the whole working band. The envelope correlation coefficient (ECC) is less than 0.1, which shows that the antenna can meet the polarization diversity characteristics well.

Citation: Yin, W.; Chen, S.; Chang, J.; Li, C.; Khamas, S.K. CPW Fed Compact UWB 4-Element MIMO Antenna with High Isolation. Sensors 2021, 21, 2688. https://doi.org/10.3390/s21082688

Academic Editor: Francisco Falcone

Received: 12 March 2021   
Accepted: 8 April 2021   
Published: 11 April 2021

Publisher’s Note: MDPI stays neutral with regard to jurisdictional claims in published maps and institutional affiliations.

![Figure 1](paper_image/figure-001.jpg)

Copyright: © 2021 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (http://creativecommons.org/licenses/by/4.0/).

Keywords: UWB; MIMO antenna; coplanar waveguide (CPW); high isolation; stub

## 1. Introduction

Federal Communications Commission (FCC) has developed a frequency range (3.1– 10.6 GHz) for commercial applications but limits the power transmission to low levels [1]. This could result in a severe multipath signal fading owing to substantial surrounding’s scattering and deterioration of the transmission overall performance of the ultrawideband (UWB) devices [2]. Multiple-input-multiple-output (MIMO) technology has been applied successfully to improve the channel capacity and link quality by producing multiplexing gain as well as diversity gain, respectively [3]. Additionally, the main challenge faced by many researchers is the design of UWB-MIMO antennas with high isolation when placed within a compact portable device size [4]. The antenna miniaturization affects the working bandwidth and radiation efficiency to a great extent. Therefore, when numerous antennas are integrated into a rather small terminal, a strong mutual coupling between elements is inevitable, which leads to antenna impedance mismatching, pattern deterioration and lower channel capacity.

In recent years, the design of a compact high isolation MIMO antenna has become a major issue. Many scholars have studied different methods to improve the isolation of MIMO antennas. One of the most effective approaches is to place the feedlines perpendicularly to each other, which results in considerable polarization and pattern diversity [5– 7]. In addition, various defected ground plane structures incorporating slots and stubs have been used to improve the isolation of MIMO antennas [8–12]. Furthermore, novel miniaturized two-layer electromagnetic band gap (EBG) structures have been presented to minimize the electromagnetic coupling between closely spaced UWB planar monopoles on a common ground plane [13]. In addition, a wideband neutralization line has been proposed to reduce the mutual coupling of a compact UWB-MIMO antenna [14].

Recently, MIMO designs that support wider working frequency bands have received considerable research interests [15–17]. For example, a compact 4-element MIMO antenna has been proposed for portable wireless UWB applications with a wide frequency band that extends from 3.1 to 12 GHz [15]. In addition, a highly isolated compact 4-element planar UWB-MIMO antenna that operates over a bandwidth of 3–15 GHz has been reported [16]. In a recent study, a novel UWB-MIMO antenna system with high isolation has been proposed with a frequency range of 2.9 to 40 GHz and a mutual coupling that is less than $- 1 7 \ \mathrm { d B }$ [17]. Moreover, it can also be observed from the recent literature that 4- element antennas have become the mainstream of UWB-MIMO antenna research. However, a compact 4-element UWB-MIMO antenna with UWB (3.1–20 GHz) has not been reported earlier in the open literature.

In this study, a compact UWB 4-element MIMO antenna with high isolation is proposed. The proposed antenna has sufficient channel capacity and can be used for precision positioning applications. To the best of authors’ knowledge, the novelty of this work is the size of whole antenna is extremely compacted designed in the working frequency band extends from 3.1–20 GHz. Furthermore, the 4 antenna elements allow for a significant increase in channel capacity compared to the 2 elements design. In addition, a stub is specially designed to ensure the impedance matching during the working frequency. Furthermore, the proposed antenna offers a radiation efficiency of more than 75%. The achieved envelope correlation coefficient (ECC) demonstrates that the antenna satisfies the polarization diversity characteristic requirements. These appealing characteristics have been achieved with an overall antenna size of $3 8 \times 3 8 \times 1 . 6$ mm3. The simulations have been conducted using the High Frequency Structure Simulator (HFSS). A prototype has been built and measured with close agreement between experimental and simulated results.

## 2. Antenna Design and Structure

## 2.1. CPW Feed

A coplanar waveguide (CPW)-fed microstrip patch antenna structure has been considered using an FR4 substrate with dielectric constant of $\varepsilon _ { r } = 4 . 4 ,$ , loss tangent of 0.02 and thickness of 1.6 mm. The effective permittivity of the coplanar waveguide configuration is given by [18]:

$$
\varepsilon _ { \scriptscriptstyle { \mathrm { s c } } } = { \frac { \varepsilon _ { r } + 1 } { 2 } } \left\{ \operatorname { t a n h } [ 0 . 7 7 5 \ln ( h / G ) + 1 . 7 5 ] + { \frac { k G } { h } } \times \left[ 0 . 0 0 4 - 0 . 7 k + 0 . 0 1 \left( 1 - 0 . 1 \varepsilon _ { r } \right) \left( 0 . 2 5 + k \right) \right] \right\}\tag{1}
$$

where

$$
k = { \frac { W } { W + 2 G } } \cdotp\tag{2}
$$

W is the width of the central conduction band, G is the gap between the conduction band and the ground and h is the thickness of the dielectric substrate, the characteristic impedance of the CPW line can be expressed by the elliptic function K (k) of the first kind [18]:

$$
Z _ { 0 _ { \it C P W } } = { \frac { 3 0 \pi } { \sqrt { \varepsilon } _ { r e } } } { \frac { K ^ { ' } ( k ) } { K ( k ) } } .\tag{3}
$$

in which

$$
{ \frac { K ^ { ' } ( k ) } { K ( k ) } } = \left[ { \frac { \pi } { \ln \left( 2 { \frac { 1 + { \sqrt { k } } } { 1 - { \sqrt { k } } } } \right) } } \right] \quad { \mathrm { i f ~ } } 0 < k < 0 . 7 0 7 = \left[ { \frac { \ln \left( 2 { \frac { 1 + { \sqrt { k } } } { 1 - { \sqrt { k } } } } \right) } { \pi } } \right] \quad { \mathrm { i f ~ } } 0 . 7 0 7 < k < 1\tag{4}
$$

where, $\stackrel { \cdot } { k ^ { \prime } } = \sqrt { 1 - k ^ { 2 } } , K ^ { \prime } ( k ) = K ( k ^ { \prime } )$

The width of the central guide band, gap between the guide band and the ground have been chosen as 1.5 mm and 0.5 mm, respectively. Substituting the relevant parameters into Equation (3), the characteristics impedance of the CPW feeder can be calculated as $Z _ { 0 _ { C P W } } \approx 5 1 \Omega$

## 2.2. Antenna Configuration

## 2.2.1. Single Element

The configuration of the proposed UWB MIMO antenna is showed as Figure 1. At first, we consider a single element, the initial model is described as Figure 1a. The antenna structure is simulated in HFSS, and the S parameters of the antenna are obtained, as shown in Figure 1b.

![Figure 2](paper_image/figure-002.jpg)  
(a)

![Figure 3](paper_image/figure-003.jpg)  
(b)  
Figure 1. The initial single element antenna: (a) geometry (b) S11.

It can be seen from the S parameter that the single element antenna has the possibility of working in UWB. However, the performance of the antenna deteriorates after 17 GHz. In order to improve the performance of the antenna further, we add parasitic branches to the feeder. The antenna structure with stub is shown in Figure 2a, and the antenna S parameters are shown in Figure 2b.

![Figure 4](paper_image/figure-004.jpg)  
(a)

![Figure 5](paper_image/figure-005.jpg)  
(b)  
Figure 2. The single element antenna with stub: (a) geometry (b) S11.

Obviously, after adding the stub, the matching of single element antenna in the frequency band high than 10.6 GHz has been greatly improved. Next, we can further design the 4-element MIMO antenna.

## 2.2.2. MIMO Antenna

The final geometry of the proposed UWB-MIMO antenna is illustrated in Figure 3 and the design parameters are listed in Table 1. The antenna structure and size have been selected to meet the operating frequency requirements. The first resonant frequency of the proposed monopole antenna can be approximately calculated as [19]:

$$
f _ { r } = \frac { 1 4 4 } { l _ { 1 } + l _ { 2 } + g + \frac { A _ { 1 } } { 2 \pi l _ { 1 } \sqrt { \varepsilon _ { r e } } } + \frac { A _ { 2 } } { 2 \pi l _ { 2 } \sqrt { \varepsilon _ { r e } } } }\tag{5}
$$

![Figure 6](paper_image/figure-006.jpg)  
Figure 3. Geometry of the proposed multiple-input-multiple-output (MIMO) antenna.

Table 1. Antenna dimensions shown in Figure 1 (unit: mm).
<table><tr><td>W</td><td>Wf</td><td>W1</td><td>W2</td><td>W3</td><td> $W _ { 4 }$ </td><td>H</td><td>H1</td><td>H2</td><td> $H _ { 3 }$ </td><td>g</td></tr><tr><td>38</td><td>1.5</td><td>0.5</td><td>1</td><td>0.1</td><td>0.4</td><td>1.6</td><td>8.6</td><td>11.2</td><td>5</td><td>1.56</td></tr><tr><td>L</td><td> $L p$ </td><td> $L _ { 1 }$ </td><td> $L _ { 2 }$ </td><td>L3</td><td>L4</td><td>R1</td><td>R2</td><td>R3</td><td>l1</td><td>l2</td></tr><tr><td>38</td><td>4</td><td>2</td><td>0.7</td><td>1.6</td><td>5.8</td><td>3.2</td><td>7.2</td><td>1.1</td><td>19</td><td>13.7</td></tr></table>

In Equation (5), A1 and A2 represent the areas of the ground plane and radiating patch, respectively, l1 and l2 represent the length of the ground plane and radiating patch respectively and g represents the distance between the ground and the radiation patch. All parameters are in the units of mm. For the considered antenna, $l _ { 1 } = 1 9$ mm, $l _ { 2 } = 1 3 . 7$ mm, $g = 1 . 5 6$ mm, $A _ { 1 } = 4 2 . 2$ mm2 and A2 = 224.06 mm2. The calculated and simulated fr have been obtained as 4 and 3.7 GHz, respectively. It can be seen that the estimated value is close to the simulated value.

The radiating patch and ground plane have been printed on the surface of the substrate. The used patch shape is evolved from a circular monopole. The size of the half around ground structure greatly affects the impedance matching of the antenna. The semicircular protrusion structure, with a radius of $R _ { 3 } ,$ at the top of the patch and the stub connected to the feeder line can both improve the antenna matching to achieve the ultrawideband operation. In particular, the stub that plays an important role in the impedance matching. In addition, the small rectangular notches on the left and right-hand sides of the semicircular protrusion are denoted as W2 and L2 and they help with the impedance matching.

## 3. Influence of Special Structure

## 3.1. Semi Surround Ground Structure

The half around ground structure has a great influence on the impedance matching bandwidth over the whole frequency band, especially its position H2. The effects of different values of H2 are studied and the results are shown in Figure 4.

![Figure 7](paper_image/figure-007.jpg)  
Figure 4. Simulated $\mathrm { S } _ { 1 1 }$ with different H2.

It can be noted from Figure 4 that that by increasing $H _ { 2 } ,$ the first resonant frequency point shifts from 3.2 to 3.8 GHz. This is because when H2 is increased, the gap between the radiating patch and the surrounding ground plane is reduced, that is to say, g in Equation (5) is decreased, resulting in the shift of the first resonant frequency point. In addition, it can be observed that when H2 is shorter, a narrower bandwidth is achieved since the match is lost around 5 GHz and 8–9 GHz. When H2 is longer, the cutoff frequency is about 3.2 GHz, and the matching is lost around 15 GHz, which fails to meet the requirements. Therefore, by adjusting H2 to a suitable value, the matching can be achieved in the range of 3–20 GHz.

## 3.2. Length of Radiating Patch

The length of the radiating patch, lp, has slight effect on the antenna matching beyond 10.6 GHz, but has a greater influence on the ultrawideband. Figure 5 presents the variations of S11 for various patch lengths.

![Figure 8](paper_image/figure-008.jpg)  
Figure 5. Simulated S11 with different $L p .$

From Figure 5, it can be noted that with the increase of $L p ,$ , the first resonant frequency point moves to the left. This is because when $L p$ increases, the length of radiating patch will increase, that is, l1 in Equation (5) will increase, which will cause the first resonant frequency shift to the lower frequency, meanwhile, the cut-off frequency of low frequency will also shift to the lower frequency. When $L p$ is small, the cut-off frequency is approximately 3.2 GHz, which fails to satisfy the requirements of UWB. In addition, with the increase of $L p ,$ the antenna matching in the 4–6 and 7–10 GHz bands becomes worse. Selecting appropriate $L p$ can make the antenna achieve better impedance matching in the UWB operating frequency range.

## 3.3. A Stub Connected to Feedline

The stub connected to feedline plays an important role in the improvement of matching in the 10.6–20 GHz band. Figure 6 illustrates the comparison of S11 with and without stub, where it can be observed that a sufficiently wide matching bandwidth has been achieved up to 17 GHz. Moreover, this can be extended by adding the matching stub that has created another resonance point around 15 GHz, which effectively extends the impedance matching to cover the whole frequency range.

![Figure 9](paper_image/figure-009.jpg)  
Figure 6. Simulated S11 without stub and with stub.

## 4. Results and Discussions

## 4.1. S-Parameters

As can be seen in Figure 7, the proposed antenna in this paper has been fabricated, and S-parameter measurement has been tested by using Rohde & Schwarz (Munich, Germany) ZVA 40. It can be seen from Figure 8 that the measurement results are basically consistent with the simulation results, and antenna ports show very good impedance matching bandwidth from 3 to 20 GHz. The isolation between the four ports is better than 17 dB in the whole bandwidth. However, it should be noted that the measured S11 of the proposed UWB-MIMO antenna system are not totally identical with the simulated results at high frequencies. This could be attributed to fabrication and experimental tolerances with respect to the antenna printing, welding as well as testing conditions.

![Figure 10](paper_image/figure-010.jpg)  
Figure 7. Fabrication photograph of proposed coplanar waveguide (CPW) fed compact ultrawideband (UWB)-MIMO antenna.

![Figure 11](paper_image/figure-011.jpg)  
Figure 8. Measured and simulated S-parameters for the proposed UWB-MIMO antenna.

## 4.2. Surface Current Distribution

In order to achieve the antenna easy fabrication and meet the requirements of high isolation between antenna ports. Firstly, the four antenna elements are placed perpendicularly to achieve polarization diversity. In addition, the mutual coupling between antenna elements is suppressed by designing the gap between the radiation element and the ground plane. Figure 9 describes the surface current distribution of the antenna at 3.5 GHz, 9 GHz, 14 GHz and 19 GHz. When port 1 is excited, each one of the remaining ports is terminated with a 50 Ω load. It can be seen from the figure that the current is concentrated around the source-fed element, limited coupling currents flow into other elements. These results confirm the achieved good isolation performance of the proposed design through the whole frequency band. Moreover, a high current density for the stub at 19 GHz, which also reflects that the introduction of stub has considerably improved the matching of the antenna at high frequency.

(a)

![Figure 12](paper_image/figure-012.jpg)

![Figure 13](paper_image/figure-013.jpg)

![Figure 14](paper_image/figure-014.jpg)  
(c)

![Figure 15](paper_image/figure-015.jpg)  
(d)  
Figure 9. Surface current distributions of the MIMO antenna at: (a) 3.5 GHz, (b) 9 GHz, (c) 14 GHz, (d) 19 GHz.

## 4.3. Radiation Patterns and Gain

The far field radiation patterns of the proposed antenna are presented in Figure 10 at the four operating frequencies of 3.5 GHz, 6.5 GHz and 14 GHz. The patterns demonstrate good omnidirectional characteristics on the xy, xz and yz planes, which means the antenna receives electromagnetic waves from all directions. The results also confirm that stable radiation characteristics have been maintained at various frequencies. Figure 11 presents the radiation efficiency in the case of port 1 excitation, where it can be observed that the typical efficiency of the proposed MIMO antenna is above 75% over the entire frequency band of 3–20 GHz.

![Figure 16](paper_image/figure-016.jpg)  
(a)

![Figure 17](paper_image/figure-017.jpg)  
(b)

![Figure 18](paper_image/figure-018.jpg)  
(c)

Figure 10. Radiation pattern for the proposed MIMO antenna at: (a) 3.5 GHz, (b) 6.5 GHz, (c) 14 GHz.  
![Figure 19](paper_image/figure-019.jpg)  
Figure 11. Radiation efficiency of the proposed MIMO antenna.

## 4.4. MIMO Performance

As an index to evaluate the correlation of MIMO antenna radiation patterns, Envelope correlation coefficient (ECC) can usually be calculated by far field radiation parameters. What is more, the ECC is required to be less than 0.5 to ensure the antenna performance. The ECC is calculated according to Equation (6) [20]:

$$
\rho _ { e i j } = \frac { \left| \int _ { 0 } ^ { 2 \pi } \int _ { 0 } ^ { \pi } \left( X P R \cdot E _ { \theta i } \cdot E _ { \theta j } ^ { * } \cdot P _ { \theta } + E _ { \varphi i } \cdot E _ { \varphi j } ^ { * } \cdot P \varphi \right) d \Omega \right| ^ { 2 } } { \int _ { 0 } ^ { 2 \pi } \int _ { 0 } ^ { \pi } \left( X P R \cdot E _ { \theta i } \cdot E _ { \theta i } ^ { * } \cdot P _ { \theta } + E _ { \varphi i } \cdot E _ { \varphi } ^ { * } \cdot P \varphi \right) d \Omega \times \int _ { 0 } ^ { 2 \pi } \int _ { 0 } ^ { \pi } \left( X P R \cdot E _ { \theta j } \cdot E _ { \theta j } ^ { * } \cdot P _ { \theta } + E _ { \varphi j } \cdot E _ { \varphi j } ^ { * } \cdot P \varphi \right) d \Omega }\tag{6}
$$

The envelope correlation coefficient (ECC) ρeij is calculated when $N = 4$ throughout the whole bandwidth. Diversity gain (DG) can also be used to express the correlation of antennas, which can be calculated by Equation (7) [21]. The smaller the ECC value, the larger the diversity gain of the antenna.

$$
{ \mathrm { D G } } = 1 0 { \sqrt { 1 - { \mathrm { E C C } } ^ { 2 } } } \ .\tag{7}
$$

The ECC and DG of the proposed UWB-MIMO antenna system are plotted in Figure 12, where it can be observed that for all the elements, ECC is rather less than 0.08 over the entire impedance bandwidth and is less than 0.02 from 6 to 20 GHz, while the DG is greater than 9.97. These results reveal that the designed antenna fulfill the requirement of achieving smaller ECC and larger DG at the same time.

![Figure 20](paper_image/figure-020.jpg)  
Figure 12. ECC and diversity gain of the proposed MIMO antenna.

The signal-to-noise ratio between imperfect MIMO antenna and the ideal antenna is defined as multiplexing efficiency $( \eta _ { m u x } )$ and written by Equation (8) [22]:

$$
\eta _ { { \scriptscriptstyle m u x } } = \sqrt { \eta _ { i } \eta _ { j } ( 1 - \big | \rho _ { c } \big | ^ { 2 } ) } .\tag{8}
$$

As demonstrated in Figure 13, ηmux is higher than −3 dB throughout the whole frequency range. In addition, the peak gain is more than 1.3 dBi across the entire bandwidth. Therefore, both parameters satisfy the requirements of MIMO wireless communication systems.

![Figure 21](paper_image/figure-021.jpg)  
Figure 13. Peak Gain and multiplexing efficiency of the proposed MIMO antenna.

## 4.5. Performance Comparison

In order to highlight the advantages of proposed antennas, the performances of antennas in different literatures are summarized in Table 2. Compared with [6,9,14], the proposed antenna has a wider bandwidth. Secondly, the proposed antenna has more ports

than [6,9,11,12,15]. In terms of antenna compactness, the proposed antenna saves the most space than [17,18] in the case of the same number of ports.

Table 2. Performance comparisons with the recently published designs.
<table><tr><td>Reference</td><td>Antenna Size (mm²)</td><td>Bandwidth (GHz)</td><td>Gain (dBi)</td><td>Isolation (dB)</td><td>ECC</td><td>Ports</td></tr><tr><td>[6]</td><td> $3 5 \times 3 5$ </td><td>3.012</td><td>NA</td><td>&gt;20</td><td>&lt;0.3</td><td>2</td></tr><tr><td>[9]</td><td> $3 0 \times 4 0$ </td><td>3.110.6</td><td>NA</td><td>&gt;15</td><td>&lt;0.15</td><td>2</td></tr><tr><td>[11]</td><td> $3 4 \times 1 8$ </td><td>2.9320</td><td>0-7</td><td>&gt;22</td><td>&lt;0.01</td><td>2</td></tr><tr><td>[12]</td><td> $5 0 \times 3 0$ </td><td>2.514.5</td><td>0.14</td><td>&gt;20</td><td>&lt;0.04</td><td>2</td></tr><tr><td>[15]</td><td> $3 6 \times 1 8$ </td><td>3.212</td><td>0-7</td><td>&gt;22</td><td>&lt;0.01</td><td>2</td></tr><tr><td>[17]</td><td> $5 8 \times 5 8$ </td><td>2.940</td><td>4.313.5</td><td>&gt;17</td><td>&lt;0.01</td><td>4</td></tr><tr><td>[18]</td><td> $8 0 \times 8 0$ </td><td>2.120</td><td>5.8 average</td><td>&gt;25</td><td>&lt;0.02</td><td>4</td></tr><tr><td>This work</td><td> $3 8 \times 3 8$ </td><td>3.020</td><td>1.36.2</td><td>&gt;17</td><td>&lt;0.08</td><td>4</td></tr></table>

## 5. Conclusion

A novel 4-element UWB-MIMO CPW-fed antenna has been proposed with a compact size of only $3 8 \times 3 8 \times 1 . 6 \mathrm { m m } ^ { 3 } .$ . The antenna achieves a considerably wide impedance bandwidth from 3–20 GHz. Easy fabrication decoupling structure is utilized to design the proposed antenna. The isolation between various elements is less than −17 dB. The incorporation of a matching stub is placed on the feeder of the antenna to improve the impedance matching in the high frequency band. All the simulated and measured results demonstrate that the proposed antenna offers important characteristics such as ultra-wide bandwidth, low mutual coupling, stable gain and radiation patterns. In addition, low ECC demonstrates the potential of the proposed antenna with presented diversity characteristics. A comparison of the proposed MIMO antenna with the other reported antenna structures has been presented to highlight the novelty and significance of our proposed work. Therefore, the CPW Fed Compact UWB 4-Element MIMO Antenna can be considered as a promising candidate for UWB applications.

Author Contributions: Conceptualization, ${ \sf W } . { \sf Y } . ;$ methodology, W.Y.; software, $S . C . { \dot { \mathbf { \zeta } } }$ validation, W.Y. and $S . C . { \dot { \prime } }$ formal analysis, W.Y. and $S . C . { \dot { \mathbf { \zeta } } }$ investigation, W.Y. and S.C.; writing—original draft preparation, S.C.; writing—review and editing, W.Y., S.K.K., J.C., C.L.; supervision, S.K.K. All authors have read and agreed to the published version of the manuscript.

Funding: This research was funded by the HFUT Doctoral Special Research Grant Fund under Grant JZ2019HGBZ0149.

Institutional Review Board Statement: Not applicable.

Informed Consent Statement: Not applicable.

Data Availability Statement: Data is contained within the article or we confirm that this paper does not have any supplementary material.

Acknowledgments: Not applicable.

Conflicts of Interest: The authors declare no conflicts of interest.

## References

1. Federal Communications Commission. Federal Communications Commission Revision of Part 15 of the Commission’s Rules Regarding Ultra-Wideband Transmission System from 3.1 to 10.6 GHz, ET-Docket; Federal Communications Commission, Washington, DC, USA, 2002, pp. 98–153.

2. Oppermann, I.; Hamalainen, M.; Iinatti, J. UWB Theory and Applications; Wiley, Chichester, U.K., 2004; pp. 3–4.

3. Zheng, L.; Tse, D.N.C. Diversity and multiplexing: A fundamental trade off in multiple-antenna channels. IEEE Trans. Inf. Theory 2003, 49, 1073–1096.

4. Balanis, C.A. Antenna Theory: Analysis and Design, 3rd ed.; Wiley: Hoboken, NJ, USA, 2005.

5. Liu, L.; Cheung, S.W.; Yuk, T.I. Compact MIMO Antenna for portable devices in UWB applications. IEEE Trans. Antennas Propag. 2013, 61, 4257–4264.

6. Zhu, J.; Li, S.; Feng, B.; Deng, L.; Yin, S. Compact dual-polarized UWB quasi-self-complementary MIMO/diversity antenna with band-rejection capability. IEEE Antennas Wirel. Propag. Lett. 2016, 15, 905–908.

7. Khan, M.S.; Braaten, B.D.; Iftikhar, A.; Capobianco, A.D.; Ijaz, B.; Asif, S. Compact 4×4 UWB-MIMO antenna with WLAN band rejected operation. Electron. Lett. 2015, 51, 1048–1050.

8. Anitha, R.; Sarin, V.P.; Mohanan, P.; Vasudevan, K. Enhanced isolation with defected ground structure in MIMO antenna. Electron. Lett. 2014, 50, 1784–1786.

9. Deng, J.-Y.; Guo, L.-X.; Liu, X.-L. An ultrawideband MIMO Antenna with a high isolation. IEEE Antenna Wirel. Propag. Lett. 2016, 15, 182–185.

10. Chandel, R.; Gautam, A.K. Compact MIMO/diversity slot antenna for UWB applications with band-notched characteristic. Electron. Lett. 2016, 52, 336–338.

11. Chandel, R.; Gautam, A.K.; Rambabu, K. Tapered fed compact UWB MIMO-diversity antenna with dual band-notched characteristics. IEEE Trans. Antennas Propag. 2018, 66, 1677–1684.

12. Iqbal, A.; Saraereh, O.A.; Ahmad, A.W.; Bashir, S. Mutual coupling reduction using F-Shaped stubs in UWB-MIMO antenna. IEEE Access 2018, 6, 2755–2759.

13. Li, Q.; Feresidis, A.P.; Mavridou, M.; Hall, P.S. Miniaturized double-layer EBG structures for broadband mutual coupling reduction between UWB monopoles. IEEE Trans. Antennas Propag. 2015, 63, 1168–1171.

14. Zhang, S.; Pedersen, G.F. Mutual coupling reduction for UWB MIMO antennas with a wideband neutralization line. IEEE Antennas Wirel. Propag. Lett. 2016, 15, 166–169.

15. Srivastava, G.; Mohan, A. Compact MIMO slot antenna for UWB applications. IEEE Antennas Wirel. Propag. Lett. 2016, 15, 1057– 1060.

16. Sipal, D.; Abegaonkar, M.P.; Koul, S.K. Easily extendable compact planar UWB MIMO antenna array. IEEE Antennas Wirel. Propag. Lett. 2017, 16, 2328–2331.

17. Yu, C.; Yang, S.; Chen, Y.; Wang, W.; Zhang, L.; Li, B.; Wang, L. A super-wideband and high isolation MIMO antenna system using a windmill-shaped decoupling structure. IEEE Access 2020, 8, 115767–115777.

18. Rekha, V.S.D.; Pardhasaradhi, P.; Madhav, B.T.P.; Devi, Y.U. Dual band notched orthogonal 4-element MIMO Antenna with isolation for UWB applications. IEEE Access 2020, 8, 145871–145880.

19. Thomas, K.G.; Sreenivasan, M. A simple ultrawideband planar rectangular printed Antenna with band dispensation. IEEE Trans. Antennas Propag. 2010, 58, 27–34.

20. Khan, M.S.; Capobianco, A.; Najam, A.I.; Shoaib, I.; Autizi, E.; Shafique, M.F. Compact ultra-wideband diversity antenna with a floating parasitic digitated decoupling structure. Microw. Antennas Propag. 2014, 8, 747–753.

21. Alsath, M.; Kanagasabai, M. Compact UWB monopole antenna for automotive communications. IEEE Trans. Antennas Propag. 2015, 63, 4204–4208.

22. Tian, R.; Lau, B.K.; Ying, Z. Multiplexing efficiency of MIMO antennas. IEEE Antennas Wirel. Propag. Lett. 2011, 10, 183–186.
