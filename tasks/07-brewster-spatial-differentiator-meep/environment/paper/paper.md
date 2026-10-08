# Optics Letters

# Analog computing by Brewster effect

AmIR YoUssEFI, 1,2 FARzaD ZangenEH-NEJaD,² SAJJaD ABDoLLAHRaMEZAnI, And AMin KHaVasI2,\*

<sup>1</sup> Department of Physics, Sharif University of Technology, P.O. Box 11555-9161, Tehran, Iran

<sup>2</sup> Department of Electrical Engineering, Sharif University of Technology, P.O. Box 11555-4363, Tehran, Iran

\*Corresponding author: khavasi@sharif.edu

Received 13 May 2016; revised 28 June 2016; accepted 29 June 2016; posted 29 June 2016 (Doc. ID 265210); published 20 July 2016

Optical computing has emerged as a promising candidate for real-time and parallel continuous data processing. Motivated by recent progresses in metamaterial-based analog computing [Science 343, 160 (2014)], we theoretically investigate the realization of two-dimensional complex mathematical operations using rotated configurations, recently reported in [Opt. Lett. 39, 1278 (2014)]. Breaking the reflection symmetry, such configurations could realize both even and odd Green’s functions associated with spatial operators. Based on such an appealing theory and by using the Brewster effect, we demonstrate realization of a firstorder differentiator. Such an efficient wave-based computation method not only circumvents the major potential drawbacks of metamaterials, but also offers the most compact possible device compared to conventional bulky lens-based optical signal and data processors. © 2016 Optical Society of America

OCIS codes: (070.1170) Analog optical signal processing; (140.3300) Laser beam shaping; (070.7345) Wave propagation.

http://dx.doi.org/10.1364/OL.41.003467

Although analog computation has almost been disregarded by emergence of digital computation over the years, it has continued to be used in some specialized applications. For example, in most cases, natural computation is analog, either because it benefits from continuous natural processes or exploits discrete, but stochastic, processes [1,2]. In addition, theoretical results have shown that analog computation can escape from some restrictions of digital computation such as data conversion loss [3]. Therefore, analog computation is still known as an important alternative technology for digital computation.

To perform analog computation, several different approaches have been investigated. These approaches can basically be classified into two categories, namely temporal and spatial analog computation. Although several valuable researches concerning temporal analog computation have been reported in recent years [4–13], such proposals are complicated to be integrated due to their remarkably large size [4]. Therefore, in this Letter, we exclusively investigate the promoting spatial analog computation.

The idea of spatial computation conventionally appeared in analog computers, or “calculating machines” to make mechanical, electronic, and mechanical-electronic analog computers. However, this approach suffers from significant restrictions such as having relatively large size and slow response [4,14–17].

To go beyond the aforementioned limitations of the spatial analog computation, two approaches have been investigated recently the metasurface approach and Green’s function (GF) approach [18,19]. The metasurface approach is based on the fact that the linear convolution $b ( y ) \overset { \cdot } { = } f ( y ) * g ( y )$ between an arbitrary electromagnetic field distribution $f ( y )$ and the Green function $g ( y )$ related to the desired operator of choice can be expressed in the spatial Fourier space as $H ( k _ { y } ) = F ( k _ { y } ) G ( \hat { k } _ { y } )$ , in which $H ( \hat { k _ { y } } ) , G ( k _ { y } )$ and $\bar { F ( k _ { \gamma } ) }$ are the Fourier transform of their counterparts in the convolution equation [20]. To this end, instead of implementing the Green’s function g y directly, a spatial Fourier transform is applied to the Green’s function $g ( y )$ to obtain the transformed Green’s function $G ( k _ { y } )$ ; then, by employing a gradient metasurface structure, $G ( k _ { y } )$ is performed in the spatial Fourier domain. Therefore, in this method, the system should mainly include three cascaded subblocks: (1) a Fourier transform subblock, (2) a properly adjusted metasurface spatial filter applying the $G ( k _ { y } )$ operation in the spatial Fourier domain, and (3) an inverse Fourier transform subblock. Although this approach is applicable, it causes some fabrication complexity due to going into the spatial Fourier domain and, consequently, the need for two additional subblocks performing Fourier and inverse Fourier transforms [18,21–25]. Moreover, making use of the mentioned additional subblocks implies an increase in the size of the system. Therefore, in this Letter, we will focus our attention on the second approach.

In the second approach, namely, Green’s function method, mathematical computation is directly realized by suitably designing a multilayered slab which is homogeneous along the x and y axes, as shown in Fig. 1. The multilayered metamaterial is designed such that it realizes an output function h y regarding an input field distribution $f ( \boldsymbol { y } )$ , consistent with the Green’s function $g ( \boldsymbol { y } )$ associated with the operator of choice. Since in this approach the Green’s function g y is straightly performed, there is no need to go into the Fourier domain. Hence, one avoids the need for subblocks that perform Fourier and inverse Fourier transforms in the first method. As a result, not only can the fabrication complexity of the system be reduced, but also the whole structure will be miniaturized.

![](paper_image/a573884c8e6f8a2637840594067405a6f1925ed8b33a4dfed5f70289f2dab935.jpg)  
Configuration of a multilayered slab performing Green’s <sup>Fig. 1.</sup>function of a desired mathematical operation. All layers are transversely homogeneous, but can be longitudinally inhomogeneous.

There are, however, two major drawbacks regarding the multilayered system proposed in [18]. First, only Green’s functions with even symmetry in the spatial Fourier domain such as the operator of second-order derivative could be realized by means of the multilayered structure shown in Fig. 1. This is due to the reflection symmetry of the system [18]. However, there are many appealing and important Green’s functions having odd symmetry in the Fourier domain such as first-order derivative and integration operators. The second problem is that the relative permittivity and the thickness of each layer of the multilayered slab are calculated using a fast synthesis approach based on the simplex optimization method which leads to nonpractical values of relative permittivities and thicknesses. As already shown in [26], an odd Green’s function can be realized by a rotated configuration or, in other words, by oblique incidence. This is achieved by breaking the reflection symmetry of the structure. In this contribution, our aim is to propose a scheme to realize the basic differentiator by just an interface using the Brewster effect to tackle the second drawback.

The schematic of the system under study is shown in Fig. 2(a). As is seen, the reflection symmetry of the system is broken by employing a rotated structure instead of a straight one. An input wave characterized by field distribution of $f ( \bar { y } ) \hat { x }$ with the bandwidth of $W$ in the spatial Fourier domain propagates along z direction and incident on the structure rotated by an angle of $\theta .$ The transformed Green’s functions of the designed structure in the primed and unprimed coordinates are assumed to be $G ( k _ { y } )$ and $G ^ { \prime } ( k _ { y } ^ { \prime } )$ , respectively, in which $k _ { y }$ and $k _ { y } ^ { \prime }$ are the Fourier variables in the unprimed and primed coordinates. Moreover, the detection direction is defined along the y-axis. Since the whole system has reflection symmetry in the primed coordinate system, the Green’s function $G ^ { \prime } ( k _ { y } ^ { \prime } )$ has to be even in the spatial Fourier domain. However, under certain circumstances, the Green’s function $G ( k _ { \nu } )$ associated with the unprimed coordinate can be considered odd.

To clarify the aforementioned circumstances, the relation between wave numbers $k _ { y }$ and $k _ { \gamma } ^ { \prime }$ associated with the primed and unprimed spatial Fourier domain has been expressed as follows:

![](paper_image/c026b3df4eaa46b413e46074373c2f3b398b9e15a7dc62a00277bed9fd9fd7ae.jpg)  
(a)

![](paper_image/0b3b631c82e8ad4bb842a7c5cbe5a01b4894220a365eb474644666c7f4a52d89.jpg)  
(b)  
(a) Configuration with rotated angle θ for realizing an even <sup>Fig. 2.</sup>or odd Green’s function. (b) Input signal ${ \bf \bar { \boldsymbol { F } } } ( \boldsymbol { k } _ { \nu } )$ , a defined Green’s function $G ( k _ { y } )$ (left), and their corresponding transformations in the primed coordinate $( { \mathrm { r i g h t } } )$

$$
k _ { y } ^ { \prime } = k _ { 0 } \ \mathrm { s i n } \bigg ( \theta + \mathrm { s i n } ^ { - 1 } \bigg ( \frac { k _ { y } } { k _ { 0 } } \bigg ) \bigg ) ,\tag{1}
$$

in which $k _ { 0 }$ is the free space wave number, and θ is the rotated angle of the structure. In this approach, the spatial spectrum of the input signal $f ( \boldsymbol { y } )$ is completely mapped to the right-half plane of primed coordinate through the nonlinear transformation expressed in Eq. (1). Using this equation and, under the condition of $\mathrm { s i n \bar { \Omega } } \mathrm { \hat { ( } } W / k _ { 0 } ) \leq \breve { \theta } \leq \mathrm { c o s \bar { \Omega } } ^ { 1 } \mathrm { ( } W / k _ { 0 } \mathrm { ) }$ , the corresponding relationship between $G ( k _ { y } )$ and $G ^ { \prime } ( k _ { y } ^ { \prime } )$ is then obtained as

$$
G ^ { \prime } ( k _ { y } ^ { \prime } ) = G { \biggl ( } k _ { 0 } \sin { \biggl ( } \sin ^ { - 1 } { \biggl ( } { \frac { | k _ { y } ^ { \prime } | } { k _ { 0 } } } { \biggr ) } - \theta { \biggr ) } { \biggr ) } .\tag{2}
$$

It is notable that under the applied restriction on the rotation angle θ, the overall spectrum of signal is not only transformed to the right-half plane, but also remains in the span $[ 0 , k _ { 0 } ]$ . The approach to perform an arbitrary Green’s function $G ( k _ { y } )$ is now obvious. First, one should apply the transformation given in Eq. (2) to the Green’s function $G ( k _ { y } )$ to obtain the associated Green’s function $G ^ { \prime } ( k _ { y } ^ { \prime } )$ and then implement $G ^ { \prime } ( k _ { \nu } ^ { \prime } )$ in the primed coordinate. Accordingly, the effect of $G ^ { \prime } ( \vec { k _ { \nu } ^ { \prime } } )$ on $F ^ { \prime } ( \dot { k } _ { y } ^ { \prime } )$ is the same as the effect of $G ( k _ { y } )$ on $G ( k _ { \nu } )$ , as shown in Fig. 2(b).

We further focus our attention on implementing the Green’s function of the first-order derivative operators as an important example of odd Green’s functions. Figure 3 depicts our suggested structure to realize the Green’s function of the first-order derivative operator. As it is observed, our proposed structure is only composed of one interface. A beam with an arbitrary profile $f ( y )$ is obliquely incident from free space onto the boundary of another medium with the refractive index n. According to Eq. (2), since the Green’s function $G ( k _ { y } )$ of the first-order derivative operator is zero at $k _ { \gamma } = 0$ , the corresponding Green’s function $\vec { G ^ { \prime } } ( k _ { \nu } ^ { \prime } )$ in the primed coordinate should be zero at $k _ { y } ^ { \prime } = k _ { 0 }$ sin θ . Since neither TE nor TM-polarized waves have zero transmission coefficients, it is not possible to obtain the first-order derivative of the incident wave on the transmission side. However, it is well known that the reflection coefficient of an incident TM-polarized wave becomes zero at the Brewster angle defined as

![](paper_image/1ef9e6582dbb91aaefc15c2a1e8b905ce3bd4d635245bbbf0688ade754f1bbe5.jpg)  
Sketch of the system under study, as well as a perspective <sup>Fig. 3.</sup>view of the signal waves incident on and reflected from the interface at the Brewster angle to realize first-order differentiation. The primed coordinate is orthogonal to the structure in which $z ^ { \prime }$ is parallel to nˆ . The reflected signal is received in $( x ^ { \prime \prime } , y ^ { \prime \prime } , z ^ { \prime \prime } )$ coordinates.

$$
\theta _ { B } = \tan ^ { - 1 } ( n ) .\tag{3}
$$

Therefore, to satisfy the aforementioned criteria for the Green’s function $G ^ { \prime } ( \dot { k _ { \nu } ^ { \prime } } )$ , we consider the case in which a TM-polarized input field $f ( y )$ obliquely incidents from air onto the boundary of the other medium at the Brewster angle, and choose the reflected field $b ( \boldsymbol { y } )$ to be the output of the system depicted in Fig. 3. Employing the Taylor series expansion of $G ^ { \prime } ( \dot { k } _ { y } ^ { \prime } )$ or, equivalently, the reflection coefficient, about the Brewster angle $\theta _ { B } { \mathrm { : } }$ , one obtains

$$
\begin{array} { r l r } {  { G ( k _ { y } ) = G ^ { \prime } \bigg ( k _ { 0 } \sin \bigg ( \theta + \sin ^ { - 1 } \bigg ( \frac { k _ { y } } { k _ { 0 } } \bigg ) \bigg ) \bigg ) } } \\ & { } & { = G ^ { \prime } ( k _ { 0 } \sin ( \theta _ { B } ) ) + \frac { \partial G ^ { \prime } ( k _ { y } ^ { \prime } ) } { \partial k _ { y } ^ { \prime } } \bigg | _ { k _ { 0 } \sin ( \theta _ { B } ) } \times k _ { y } \cos ( \theta _ { B } ) + O ( k _ { y } ^ { 2 } ) } \\ & { } & { = - \bigg ( \frac { n } { 2 } - \frac { 1 } { 2 n ^ { 3 } } \bigg ) \frac { k _ { y } } { k _ { 0 } } + O ( k _ { y } ^ { 2 } ) , \qquad ( 4 ) } \end{array}
$$

where we have used the fact that $G ^ { \prime } ( k _ { 0 } \ \sin ( \theta _ { B } ) ) = 0$ . It should be mentioned that the calculated Taylor series expansion in $\operatorname { E q . } \ ( 4 )$ is under the assumption that $k _ { y } \ll k _ { 0 }$ or, equivalently, $\hat W \ll k _ { 0 }$ . This assumption satisfies the restriction on the rotation angle θ applied in Eq. (2). Figure 4 depicts the exact Green’s function $G ( k _ { y } )$ and its approximation around $k _ { \nu } = 0$ based on the Taylor series for $n = 2 . 1$ and $\theta _ { B } = 6 4 . 6 ^ { \circ }$ . As it is observed in this figure, making use of the linear first-order approximation of $G ( k _ { y } )$ proposed in Eq. (4), its exact value can be estimated to around $\bar { k } y = 0$

![](paper_image/9c12dfa3d7290e097698b4e3077fa0f9e4f42a443a0451c540a17d2c9289c1a8.jpg)  
Distribution of the exact and approximated Green’s function <sup>Fig. 4.</sup>associated with the first-order derivative operation for $n = 2 . 1$ and $\theta _ { B } = 6 4 . 6 ^ { \circ }$

Using $\operatorname { E q } .$ . (4), the corresponding operator to the Green’s function $G ( k _ { y } )$ can easily be obtained as

$$
L [ f ( y ) ] \approx \frac { i } { k _ { 0 } } \left( \frac { n } { 2 } - \frac { 1 } { 2 n ^ { 3 } } \right) \frac { d } { d y } f ( - y ) ,\tag{5}
$$

which is the operator of the first-order derivative multiplied by a definite scale factor. We note that the intrinsic drawback of any differentiator is the low amplitude of its output, because the Green’s function of the ideal differentiator is zero at $k _ { \nu } = 0$ . However, the proposed Brewster differentiator’s efficiency is larger than 1 (compared to the ideal differentiator) for $n > 2 . 1$ , according to Eq. (5).

It should be emphasized that there is no mechanism to control the width of the angular interval (around the zero reflection), where the reflection coefficient is able to approximate the Green’s function of the ideal differentiator accurately. To obtain the maximum bandwidth W in which the first two terms of the Taylor series approximate the Green’s function well, we set the maximum error of the estimation to be less than 10% based on the definition $e _ { G } = ( \| G - G _ { \mathrm { e x a c t } } \| ) / \| G _ { \mathrm { e x a c t } } \|$ [27]. The parameter W versus the refractive index n is plotted in Fig. 5. Using this figure, we can readily determine the maximum bandwidth of the incident wave for a specific refractive index n.

To evaluate performance of the proposed approach for realizing the Green’s function of the first-order derivative operator, we first investigate the case in which a Gaussian field $\bar { \ b f } ( \ b y )$ with the spatial bandwidth $W = 0 . 1 k _ { 0 }$ and beam width $3 2 \lambda _ { 0 }$ impinges on the boundary of a medium with refractive index $n = 2 . 1$ at the Brewster angle. Figure 6 illustrates the calculated first-order derivative of the incident wave obtained based on Brewster angle scheme compared with the exact analytical result. The results are in excellent agreement with 5% error, according to formula $e _ { f } = ( \| f ^ { \prime } - \check { f } _ { \mathrm { e x a c t } } ^ { \prime } \| ) / \| f _ { \mathrm { e x a c t } } ^ { \prime } \|$ . As another example, an electromagnetic wave that has a Sinc function profile with the bandwidth of $W = 0 . 0 9 k _ { 0 }$ is assumed to be incident on the boundary of the same secondary medium at the Brewster angle. The obtained first-order derivative of the input field according to the Brewster angle scheme, as well as the exact result, is shown in Fig. 7. An error of $e _ { f } = 1 0 \%$ in the spatial domain has been calculated between these two results. Since the Sinc function in spatial domain is mapped to a rectangular function with $W = \bar { 0 . 0 9 k _ { 0 } }$ in spectral space, we expect the spectral space error to be equal to the spatial domain error, i.e., $e _ { G } = e _ { f } = 1 0 \%$ . Finally, we remark that higher order derivative operators such as the operator of the second-order derivative can easily be implemented by cascading two first-order derivative structures.

![](paper_image/e6449a2ea1b3e9105316c7d2a4672cb99de3f843c5018e0bcd996dea65c0c837.jpg)  
Analytical result for the incident wave maximum spatial <sup>Fig. 5.</sup>bandwidth versus the refractive index of the secondary medium in the case of a 10% error.

![](paper_image/4b6dcd3a1c5fbd50e0fdf03f7a97304862b4ebeec975dba070aa9c36149c9674.jpg)  
Analytical results for a signal wave, including a Gaussian field <sup>Fig. 6.</sup>with a bandwidth of $W = 0 . 1 k _ { 0 }$ and a beam width $3 2 \lambda _ { 0 }$ incident on the secondary medium depicted in Fig. 3.

![](paper_image/f0d8b264489fc78df1ac427184c460a326ebbb454c27e2c646c9ce51730eb200.jpg)  
Analytical results for a signal wave, including a Sinc function <sup>Fig. 7.</sup>with a bandwidth of $W = 0 . 0 9 k _ { 0 }$ impinging on the secondary medium depicted in Fig. 3.

In summary, stimulated by a recent breakthrough in metamaterial-based mathematical operations [18], we reviewed how a rotated structure can realize odd Green’s functions by breaking the reflection symmetry [26,28]. On the other hand, even Green’s functions can be performed by conventional nonrotated structures [29]. Based on such rotated configurations, a Brewster differentiator was realized to derivative spatial signals more accurately. High-order differentiators could readily be realized by a well-arranged array of the proposed first-order differentiator. Such an appealing finding may lead to large improvements in image processing and analog computing.

## REFERENCES

1. B. J. MacLennan, “A review of analog computing,” Technical Report UT-CS-07-601 (University of Tennessee, 2007).

2. J. F. Miller, S. L. Harding, and G. Tufte, Evol. Intell. , 49 (2014).

<sup>7</sup>3. D. R. Solli and B. Jalali, Nat. Photonics , 704 (2015).

4. F. Liu, T. Wang, L. Qiang, T. Ye, Z. Zhang, M. Qiu, and Y. Su, Opt. Express , 15880 (2008).

5. R. Slavík, Y. Park, N. Ayotte, S. Doucet, T.-J. Ahn, S. LaRochelle, and J. Azaña, Opt. Express , 18202 (2008).

<sup>16</sup>6. M. Li, D. Janner, J. Yao, and V. Pruneri, Opt. Express , 19798 (2009).

<sup>17</sup>7. Y. Park, M. H. Asghari, R. Helsten, and J. Azana, IEEE Photon. J. , 1040 (2010).

8. J. Azaa, IEEE Photon. J. , 359 (2010).

9. M. Li, L.-Y. Shao, J. Albert, and J. Yao, IEEE Photon. Technol. Lett. , 251 (2011).

<sup>23</sup>10. S. Tan, L. Xiang, J. Zou, Q. Zhang, Z. Wu, Y. Yu, J. Dong, and X. Zhang, Opt. Lett. , 3735 (2013).

<sup>38</sup>11. S. Tan, Z. Wu, L. Lei, S. Hu, J. Dong, and X. Zhang, Opt. Express , 7008 (2013).

12. T. Yang, J. Dong, L. Lu, L. Zhou, A. Zheng, X. Zhang, and J. Chen, Sci. Rep. , 5581 (2014).

<sup>4</sup>13. T. L. Huang, A. L. Zheng, J. J. Dong, D. S. Gao, and X. L. Zhang, Opt. Lett. , 5614 (2015).

<sup>40</sup>14. A. B. Clymer, IEEE Ann. Hist. Comput. , 19 (1993).

15. M. A. Preciado and M. A. Muriel, Opt. Lett. , 2458 (2008).

<sup>33</sup>16. R. Slavík, Y. Park, M. Kulishov, R. Morandotti, and J. Azaña, Opt. Express , 10699 (2006).

<sup>14</sup>17. L. M. Rivas, S. Boudreau, Y. Park, R. Slavík, S. LaRochelle, A. Carballar, and J. Azaña, Opt. Lett. , 1792 (2009).

<sup>34</sup>18. A. Silva, F. Monticone, G. Castaldi, V. Galdi, A. Alù, and N. Engheta, Science , 160 (2014).

<sup>343</sup>19. A. Sihvola, Science , 144 (2014).

20. S. AbdollahRamezani, K. Arik, A. Khavasi, and Z. Kavehvash, Opt. Lett. , 5239 (2015).

<sup>40</sup>21. M. Farmahini-Farahani, J. Cheng, and H. Mosallaei, J. Opt. Soc. Am. B , 2365 (2013).

<sup>30</sup>22. A. Pors, M. G. Nielsen, and S. I. Bozhevolnyi, Nano Lett. , 791 (2014).

<sup>15</sup>23. S. S. Kou, G. Yuan, Q. Wang, L. Du, E. Balaur, D. Zhang, D. Tang, B. Abbey, X.-C. Yuan, and J. Lin, Light Sci. Appl. , e16034 (2016).

<sup>5</sup>24. W. Zhang, C. Qu, and X. Zhang, J. Opt. , 075102 (2016).

<sup>18</sup>25. A. Chizari, S. AbdollahRamezani, M. V. Jamali, and J. A. Salehi, “Analog optical computing based on dielectric meta-reflect-array,” arXiv preprint arXiv:1605.07150 (2016).

26. L. L. Doskolovich, D. A. Bykov, E. A. Bezus, and V. A. Soifer, Opt. Lett. , 1278 (2014).

27. L. N. Binh, Photonic Signal Processing: Techniques and Applications (CRC Press, 2008).

28. N. V. Golovastikov, D. A. Bykov, L. L. Doskolovich, and E. A. Bezus, Opt. Commun. , 457 (2015).

<sup>338</sup>29. D. A. Bykov, L. L. Doskolovich, E. A. Bezus, and V. A. Soifer, Opt. Express , 25084 (2014).