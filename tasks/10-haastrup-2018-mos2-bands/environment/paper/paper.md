# The Computational 2D Materials Database: high-throughput modeling and discovery of atomically thin crystals

**Authors:** Sten Haastrup et al.
**Year:** 2018
**Venue:** 2D Materials 5, 042002
**DOI:** https://doi.org/10.1088/2053-1583/aacfc1
**Provenance:** Open-access manuscript PDF, bundled with the task.
**Licence:** Open-access author manuscript; bundled verbatim.

## How to read this file

The sections below are the machine-extracted text of the bundled article, one
section per PDF page, in reading order. PDF text extraction reorders and
de-columnises tables, so a table you find here may have its header row and its
value rows separated. When a number matters, confirm it against the rendered
page images in `/home/paper/paper_image/page_NNN.png` (95 pages, 150 dpi) or
against `/home/paper/paper.pdf` before you rely on it.

Figures are not separately cropped; each `page_NNN.png` is a full page render
that contains whatever figures and tables appear on that page.

---

## Page 1

The Computational 2D Materials Database:
High-Throughput Modeling and Discovery of
Atomically Thin Crystals
Sten Haastrup,∗,† Mikkel Strange,† Mohnish Pandey,† Thorsten Deilmann,† Per
S. Schmidt,† Nicki F. Hinsche,† Morten N. Gjerding,† Daniele Torelli,† Peter M.
Larsen,† Anders C. Riis-Jensen,† Jakob Gath,† Karsten W. Jacobsen,† Jens
Jørgen Mortensen,† Thomas Olsen,† and Kristian S. Thygesen†,‡
†CAMD, Department of Physics, Technical University of Denmark
‡Center for Nanostructured Graphene (CNG), Technical University of Denmark
E-mail: sthaa@fysik.dtu.dk
1
arXiv:1806.03173v2  [cond-mat.mes-hall]  9 Oct 2018


## Page 2

Abstract
We introduce the Computational 2D Materials Database (C2DB), which organ-
ises a variety of structural, thermodynamic, elastic, electronic, magnetic, and optical
properties of around 1500 two-dimensional materials distributed over more than 30 dif-
ferent crystal structures. Material properties are systematically calculated by density
functional theory and many-body perturbation theory (G0W0 and the Bethe-Salpeter
Equation for ∼250 materials) following a semi-automated workﬂow for maximal con-
sistency and transparency.
The C2DB is fully open and can be browsed online at
c2db.fysik.dtu.dk or downloaded in its entirety. In this paper, we describe the work-
ﬂow behind the database, present an overview of the properties and materials currently
available, and explore trends and correlations in the data. Moreover, we identify a large
number of new potentially synthesisable 2D materials with interesting properties tar-
geting applications within spintronics, (opto-)electronics, and plasmonics. The C2DB
oﬀers a comprehensive and easily accessible overview of the rapidly expanding family
of 2D materials and forms an ideal platform for computational modeling and design of
new 2D materials and van der Waals heterostructures.
2


## Page 3

Contents
1
Introduction
5
2
Workﬂow
9
2.1
Structure relaxation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
13
2.2
Crystal structure classiﬁcation . . . . . . . . . . . . . . . . . . . . . . . . . .
15
2.2.1
Symmetry . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
15
2.2.2
Prototypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
15
2.3
Thermodynamic stability . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
18
2.4
Phonons and dynamic stability
. . . . . . . . . . . . . . . . . . . . . . . . .
19
2.4.1
Stability criteria . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
23
2.5
Elastic constants
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
25
2.6
Magnetic anisotropy
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
26
2.7
Projected density of states . . . . . . . . . . . . . . . . . . . . . . . . . . . .
27
2.8
Band structures . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
28
2.8.1
PBE band structure
. . . . . . . . . . . . . . . . . . . . . . . . . . .
28
2.8.2
HSE band structure
. . . . . . . . . . . . . . . . . . . . . . . . . . .
29
2.8.3
GLLBSC fundamental gap . . . . . . . . . . . . . . . . . . . . . . . .
29
2.8.4
G0W0 band structure . . . . . . . . . . . . . . . . . . . . . . . . . . .
33
2.9
Band extrema . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
35
2.10 Fermi surface
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
37
2.11 Eﬀective masses . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
38
2.12 Work function . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
40
2.13 Deformation potentials . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
40
2.14 Plasma frequencies . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
43
2.15 Electronic polarisability
. . . . . . . . . . . . . . . . . . . . . . . . . . . . .
44
2.16 Optical absorbance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
46
3


## Page 4

3
Database overview
50
3.1
Materials
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
50
3.2
Properties: Example applications . . . . . . . . . . . . . . . . . . . . . . . .
55
3.2.1
Band gaps and band alignment
. . . . . . . . . . . . . . . . . . . . .
55
3.2.2
Eﬀective masses and mobilities
. . . . . . . . . . . . . . . . . . . . .
58
3.2.3
Magnetic properties . . . . . . . . . . . . . . . . . . . . . . . . . . . .
61
3.2.4
Plasmons
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
64
3.2.5
Excitons . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
67
4
Conclusions and Outlook
70
5
Acknowledgements
73
References
74
4


## Page 5

1
Introduction
Over the past decade, atomically thin two-dimensional (2D) materials have made their way to
the forefront of several research areas including batteries, (electro-)catalysis, electronics, and
photonics.1,2 This development was prompted by the intriguing and easily tunable properties
of atomically thin crystals and has been fueled by the constant discovery of new 2D mate-
rials and the emergent concepts of lateral3 and vertical4 2D heterostructures, which opens
completely new possibilities for designing materials with tailored and superior properties.
So far more than ﬁfty compounds have been synthesised or exfoliated as single layers
(see Figure 7). These include the well known monoelemental crystals (Xenes, e.g. graphene,
phosphorene)5 and their ligand functionalised derivatives (Xanes, e.g. CF, GeH),6 transition
metal dichalcogenides (TMDCs, e.g. MoS2, TaSe2),7 transition metal carbides and -nitrides
(MXenes, e.g. Ti2CO2),8 group III-V semiconductors and insulators (e.g. GaN, BN),9,10
transition metal halides (e.g. CrI3),11,12 post-transition metal chalcogenides (e.g. GaS and
GaSe)13,14 and organic-inorganic hybrid perovskites (e.g. Pb(C4H9NH3)2I4).15 However, the
already known monolayers are only the tip of a much larger iceberg. Indeed, recent data
mining studies indicate that several hundred 2D materials could be exfoliated from known
layered bulk crystals.16–19 In the present work we take a complementary approach to 2D ma-
terials discovery based on combinatorial lattice decoration and identify another few hundred
previously unknown and potentially synthesisable monolayers.
In the search for new materials with tailored properties or novel functionalities, ﬁrst-
principles calculations are playing an increasingly important role. The continuous increase
in computing power and signiﬁcant advancements of theoretical methods and numerical al-
gorithms have pushed the ﬁeld to a point where ﬁrst-principles calculations are comparable
to experiments in terms of accuracy and greatly surpass them in terms of speed and cost.
For more than a century, experimental databases on e.g. structural, thermal, and electronic
properties, have been a cornerstone of materials science, and in the past decade, the ex-
perimental data have been augmented by an explosion of computational data obtained from
5


## Page 6

ﬁrst-principles calculations. Strong eﬀorts are currently being focused on storing and organis-
ing the computational data in open repositories.20,21 Some of the larger repositories, together
containing millions of material entries, are the Materials Project,22 the Automatic Flow for
Materials Discovery (AFLOWLIB),23 the Open Quantum Materials Database (OQMD),24,25
and the Novel Materials Discovery (NOMAD) Repository.26
The advantages of computational materials databases are many. Most obviously, they
facilitate open sharing and comparison of research data whilst reducing duplication of eﬀorts.
In addition, they underpin the development and benchmarking of new methods by providing
easy access to common reference systems.27 Finally, the databases enable the application
of machine learning techniques to identify deep and complex correlations in the materials
space and to use them for designing materials with tailored properties and for accelerating the
discovery of new materials.28–30 Among the challenges facing the computational databases
is the quality of the stored data, which depends both on the numerical precision (e.g. the
employed k-point grid and basis set size) and the accuracy of the employed physical models
(e.g. the exchange-correlation functional). Most of the existing computational databases
store results of standard density functional theory (DFT) calculations. While such methods,
when properly conducted, are quite reliable for ground state properties such as structural
and thermodynamic properties, they are generally not quantitatively accurate for excited
state properties such as electronic band structures and optical absorption spectra.
Compared to databases of bulk materials, databases of 2D materials are still few and
less developed.
Early work used DFT to explore the stability and electronic structures
of monolayers of group III-V honeycomb lattices31,32 and the class of MX2 transition metal
dichalcogenides and oxides.33 Later, by data-ﬁltering the inorganic crystal structure database
(ICSD), 92 experimentally known layered crystals were identiﬁed and their electronic band
structures calculated at the DFT level.34 Another DFT study, also focused on stability and
band structures, explored around one hundred 2D materials selected from diﬀerent structure
classes.35 To overcome the known limitations of DFT, a database with many-body G0W0
6


## Page 7

band structures for 50 semiconducting TMDCs was established.36 Very recently, data mining
of the Materials Project and experimental crystal structure databases in the spirit of Ref.
34, led to the identiﬁcation of close to one thousand experimentally known layered crystals
from which single layers could potentially be exfoliated.16–19 These works also computed
basic energetic, structural and electronic properties of the monolayers (or at least selected
subsets) at the DFT level.
In this paper, we introduce the open Computational 2D Materials Database (C2DB)
which organises a variety of ab-initio calculated properties for more than 1500 diﬀerent 2D
materials. The key characteristics of the C2DB are:
• Materials: the database focuses entirely on 2D materials, i.e. isolated monolayers,
obtained by combinatorial lattice decoration of known crystal structure prototypes.
• Consistency: all properties of all materials are calculated using the same code and
parameter settings following the same workﬂow for maximum transparency, repro-
ducibility, and consistency of the data.
• Properties: the database contains a large and diverse set of properties covering struc-
tural, thermodynamic, magnetic, elastic, electronic, dielectric and optical properties.
• Accuracy: Hybrid functionals (HSE06) as well as beyond-DFT many-body perturba-
tion theory (G0W0) are employed to obtain quantitatively accurate band structures,
and optical properties are obtained from the random phase approximation (RPA) and
Bethe-Salpeter Equation (BSE).
• Openness: the database is freely accessible and can be directly downloaded and
browsed online using simple and advanced queries.
The systematic combinatorial approach used to generate the structures in the database
inevitably produces many materials that are unstable and thus unrealistic and impossible
to synthesise in reality. Such “hypothetical” structures may, however, still be useful in a
7


## Page 8

number of contexts, e.g. for method development and benchmarking, testing and training
of machine learning algorithms, identiﬁcation of trends and structure-property relationships,
etc.
For this reason we map out the properties of all but the most unstable (and thus
chemically unreasonable) compounds. Nevertheless, the reliable assessment of stability and
synthesisability of the candidate structures is an essential issue. Using the 55 materials in
the C2DB, which have been experimentally synthesised in monolayer form, as a guideline,
we set down the criteria that a hypothesised 2D material should fulﬁll in order for it to be
“likely synthesisable”. On the basis of these criteria, we introduce a simple stability scale to
quantify a candidate material’s dynamic and thermodynamic stability. Out of an initial set
of more than 1900 monolayers distributed over 32 diﬀerent crystal structures, we ﬁnd 350
in the most stable category. In addition to the 55 experimentally synthesised monolayers,
this set also includes around 80 monolayers from experimentally known vdW layered bulk
materials, and thus around 200 completely new and potentially synthesisable 2D materials.
In Section 2, we describe the computational workﬂow behind the database. The struc-
ture and properties of the materials are calculated using well established state-of-the-art
methodology. Technical descriptions of the diﬀerent steps in the workﬂow are accompanied
by illustrative examples and comparisons with literature data. Since documentation and val-
idation is the main purpose of the section, we deliberately focus on well known 2D materials
like the Xenes and transition metal dichalcogenides where plenty of both computational and
experimental reference data is available. It should be clear that the novelty of the present
work does not lie in the employed methodology nor in the type of materials properties that
we calculate. The signiﬁcance of our work is rather reﬂected by the fact that when large
and consistently produced data sets are organised and made easily accessible, new scientiﬁc
opportunities arise. As outlined below, this paper presents several examples of this eﬀect.
In Section 3 we give an overview of the materials and the data contained in the C2DB
and provide some speciﬁc examples to illustrate its use. Using an extensive set of many-body
G0W0 calculations as a reference, we establish the performance of various DFT xc-functionals
8


## Page 9

for predicting band gaps, band edge positions, and band alignment at hetero-interfaces, and
we propose an optimal strategy for obtaining accurate band energies at low computational
cost.
Similarly, the 250 BSE calculations allow us to explore trends in exciton binding
energies and perform a statistically signiﬁcant and unbiased assessment of the accuracy and
limitations of the widely used Mott-Wannier model for 2D excitons. From the data on more
than 600 semiconductor monolayers, we present strong empirical evidence against an often
employed relation between eﬀective masses and band gaps derived from k · p perturbation
theory. Inspired by the potential of using 2D materials as building blocks for plasmonics
and photonics, we propose a model to predict the plasmon dispersion relations in 2D metals
from the (intraband) plasma frequency and the onset of interband transitions and use it
to identify 2D metals with plasmons in the optical frequency regime. We propose several
new magnetic 2D materials (including both metals and semiconductors) with ferromagnetic
or anti-ferromagnetic ordering and signiﬁcant out-of-plane magnetic anisotropy. Finally, we
point to new high-mobility 2D semiconductors including some with band gaps in the range
of interest for (opto)electronic applications.
In Section 4 we provide our conclusions together with an outlook discussing some op-
portunities and possible future directions for the C2DB.
2
Workﬂow
The workﬂow used to generate the data in the C2DB is illustrated in Figure 1. It consists
of two parts: In the ﬁrst part (left panel) the unit cell and atom positions are optimised for
diﬀerent magnetic conﬁgurations: non-magnetic (NM), ferro-magnetic (FM) and antiferro-
magnetic (AFM). Materials satisfying certain stability and geometry criteria (indicated by
green boxes) are subject to the second part (right panel) where the diﬀerent properties
are computed using DFT and many-body methods. The G0W0 band structure and BSE
absorbance calculations have been performed only for semiconducting materials with up to
9


## Page 10

four atoms in the unit cell. Per default, properties shown in the online database include spin-
orbit coupling (SOC); however, to aid comparison with other calculations, most properties
are also calculated and stored without SOC.
1. Relax cell and atoms in all 
magnetic states (NM, FM, AFM)* 
N 
PBE band gap > 0 ? 
Y 
N 
6. Magnetic anisotropy 
12. Work function 
10. Fermi surface 
7. Projected DOS 
Structure and stability 
Properties 
8. Band structure 
8. Band structure 
11. Effective masses 
14. Plasma frequency 
15. Polarisability 
Dynamical stability:  
4. Γ-point phonons of 2×2 cell 
5. Elastic constants 
 
Y 
* Run flow for all (meta)stable magnetic states 
Crystal classification:  
2. Symmetry and prototype 
Thermodynamic stability:  
3. Heat of formation and convex hull 
N  
Material disintegrated (0D/1D) ?  
Material already in C2DB ?  
Y 
ΔH > 0.2 eV/atom ? 
Y 
 Imaginary phonon frequencies or 
negative elastic constants? 
N 
N 
9. Band extrema 
13. Deformation potentials 
15. Polarisability 
16. Absorbance 
PBE 
HSE@PBE 
G0W0@PBE 
Methods: 
RPA@PBE 
BSE@PBE-G0W0 
Y 
Figure 1: The workﬂow used to calculate the structure and properties of the materials in
C2DB. The cross indicates that the material is not included in the database at all, while the
stop sign indicates that no more of the workﬂow is performed.
All DFT and many-body calculations are performed with the projector augmented wave
code GPAW37 using plane wave basis sets and PAW potentials version 0.9.2. The workﬂow
is managed using the Python based Atomic Simulation Environment (ASE).38 We have
developed a library of robust and numerically accurate (convergence veriﬁed) ASE-GPAW
scripts to perform the various tasks of the workﬂow, and to create the database afterwards.
The library is freely available, under a GPL license.
10


## Page 11

Below we describe all steps of the workﬂow in detail. As the main purpose is to document
the workﬂow, the focus is on technical aspects, including numerical convergence and bench-
marking. An overview of the most important parameters used for the diﬀerent calculations
is provided in Table 1.
11


## Page 12

Table 1: Overview of the methods and parameters used for the diﬀerent steps
of the workﬂow. If a parameter is not speciﬁed at a given step, its value equals
that of the last step where it was speciﬁed.
Workﬂow step(s)
Parameters
Structure and energetics (1-4)†
vacuum = 15 ˚A; k-point density = 6.0/˚A−1; Fermi
smearing = 0.05 eV; PW cutoﬀ= 800 eV; xc func-
tional = PBE; maximum force = 0.01 eV/˚A; max-
imum stress = 0.002 eV/˚A3; phonon displacement
= 0.01˚A
Elastic constants (5)
k-point density = 12.0/˚A
−1; strain = ±1%
Magnetic anisotropy (6)
k-point density = 20.0/˚A
−1; spin-orbit coupling =
True
PBE electronic properties (7-10 and 12)
k-point density = 12.0/˚A
−1 (36.0/˚A
−1 for step 7)
Eﬀective masses (11)
k-point density = 45.0/˚A
−1; ﬁnite diﬀerence
Deformation potential (13)
k-point density = 12.0/˚A−1; strain = ±1%
Plasma frequency (14)
k-point density = 20.0/˚A−1; tetrahedral interpola-
tion
HSE band structure (8-12)
HSE06@PBE; k-point density = 12.0/˚A−1
G0W0 band structure (8, 9)
G0W0@PBE; k-point density = 5.0/˚A
−1; PW cut-
oﬀ= ∞(extrapolated from 170, 185 and 200 eV);
full frequency integration; analytical treatment of
W(q) for small q; truncated Coulomb interaction
RPA polarisability (15)
RPA@PBE; k-point density = 20.0/˚A
−1; PW cut-
oﬀ= 50 eV; truncated Coulomb interaction; tetra-
hedral interpolation
BSE absorbance (16)
BSE@PBE with G0W0 scissors operator; k-point
density = 20.0/˚A
−1; PW cutoﬀ= 50 eV; trun-
cated Coulomb interaction; at least 4 occupied and
4 empty bands
†For the cases with convergence issues, we set a k-point density of 9.0 and a smearing of 0.02 eV.
12


## Page 13

2.1
Structure relaxation
The workﬂow is initiated with a crystal structure deﬁned by its unit cell (Bravais lattice and
atomic basis). The crystal lattice is typically that of an experimentally known prototype
(the “seed structure”) decorated with atoms picked from a subset of the periodic table, see
Figure 2. We refer to materials by the chemical formula of their unit cell followed by the
crystal structure. The latter is indicated by a representative material of that prototype, as
described in Sec 3.1. For example, monolayer MoS2 in the hexagonal H and T phases are
denoted MoS2-MoS2 and MoS2-CdI2, respectively. Now, MoS2 is in fact not stable in the
T phase, but undergoes a 2 × 1 distortion to the so-called T′ phase. Because the T′ phase
is the thermodynamically stable phase of WTe2, we denote MoS2 in the distorted T phase
by Mo2S4-WTe2. In the following, we shall refer to the unit cell with which the workﬂow is
initiated, i.e. the unit cell of the seed structure, as the primitive cell or the 1 × 1 cell, even
if this cell is not dynamically stable for the considered material (see Section 2.4).
Figure 2: The materials in the C2DB are initially generated by decorating an experimentally
known crystal structure prototype with atoms chosen from a (chemically reasonable) subset
of the periodic table.
The unit cell and internal coordinates of the atoms are relaxed in both a spin-paired
(NM), ferromagnetic (FM), and anti-ferromagnetic (AFM) conﬁguration. Calculations for
the AFM conﬁguration are performed only for unit cells containing at least two metal atoms.
13


## Page 14

The symmetries of the initial seed structure are kept during relaxation. All relevant compu-
tational details are provided in Table 1.
After relaxation, we check that the structure has remained a covalently connected 2D
material and not disintegrated into 1D or 0D clusters. This is done by deﬁning clusters of
atoms using the covalent radius39 + 30% as a measure for covalent bonds between atoms.
The dimensionality of a cluster is obtained from the scaling of the number of atoms in a
cluster upon repetition of the unit cell following the method described by Ashton et al.40 Only
materials containing exactly one cluster of dimensionality 2 are given further consideration
(an exception is made for the metal-organic perovskites (prototype PbA2I4) for which the
metal atom inside the octahedron represents a 0D cluster embedded in a 2D cluster). To
illustrate the eﬀect of the covalent radius + 30% threshold, Figure 3 shows the distribution
of the candidate structures in the database as a function of the covalent factor needed to
fully connect the structure. Most materials have a critical covalent factor below 1.3 and fall
in the green shaded region. There is, however, a tail of around 100 disconnected materials
(red region); these materials are not included in the database.
1.0
1.5
2.0
critical covalent factor
distribution of materials
2D
Disconnected
×10
Figure 3: The distribution of candidate structures for the C2DB with respect to the critical
covalent factor at which they become 2D. Materials in the red region are excluded from the
database.
We also check that the material is not already contained in the database. This is done
14


## Page 15

by measuring the root mean square distance (RMSD)41 relative to all other materials in the
C2DB with the same reduced chemical formula. A threshold of 0.01 ˚A is used for this test.
In case of multiple metastable magnetic conﬁgurations (in practice, if both a FM and
AFM ground state are found), these are regarded as diﬀerent phases of the same material
and will be treated separately throughout the rest of the workﬂow. To indicate the magnetic
phase we add the extensions “FM” or “AFM” to the material name. The total energy of the
spin-paired ground state is always stored, even when it is not the lowest. If the energy of the
non-magnetic state is higher than the most stable magnetic state by less than 10 meV/atom,
the workﬂow is also performed for the non-magnetic state. This is done in recognition of
the ﬁnite accuracy of DFT for predicting the correct energetic ordering of diﬀerent magnetic
states.
We have compared the lattice constants of 29 monolayers with those reported in Ref. 42,
which were obtained with the VASP code using PBE and very similar numerical settings
and ﬁnd a mean absolute deviation of 0.024 ˚A corresponding to 0.4%. The small yet ﬁnite
deviations are ascribed to diﬀerences in the employed PAW potentials.
2.2
Crystal structure classiﬁcation
2.2.1
Symmetry
To classify the symmetries of the crystal structure the 3D space group is determined using
the crystal symmetry library Spglib43 on the 3D supercell with a tolerance of 10−4 ˚A.
2.2.2
Prototypes
The materials are classiﬁed into crystal structure prototypes based on the symmetry of the
crystals. For two materials to belong to the same prototype, we require that they have the
same space group, the same stoichiometry, and comparable thicknesses. The last requirement
is included to distinguish between materials with the same symmetry and stoichiometry but
with diﬀerent number of atomic layers, see for example monolayer hBN and GaS in Fig-
15


## Page 16

ure 4. Each prototype is labelled by a speciﬁc representative material. For prototypes which
have been previously investigated, we comply with the established conventions. However,
since the ﬁeld of 2D materials is still young and because C2DB contains a large number of
never-synthesised materials, some of the considered crystal structures fall outside the known
prototypes. In these cases we have chosen the representative material to be the one with
the lowest energy with respect to the convex hull. Some of the crystal structure prototypes
presently contained in the C2DB are shown in Figure 4.
16


## Page 17

Figure 4: Examples of crystal structure prototypes currently included in the C2DB.
17


## Page 18

2.3
Thermodynamic stability
The heat of formation, ∆H, is deﬁned as the energy of the material with respect to the
standard states of its constituent elements. For example, the heat of formation per atom of
a binary compound, AxBy, is
∆H = (E(AxBy) −xE(A) −yE(B))/(x + y),
(1)
where E(AxBy) is the total energy of the material AxBy, and E(A) and E(B) are the total
energies of the elements A and B in their standard state. When assessing the stability of a
material in the C2DB, it should be kept in mind that the accuracy of the PBE functional for
the heat of formation is only around 0.2 eV/atom on average.44 Other materials databases,
e.g. OQMD, Materials Project, and AFLOW, employ ﬁtted elementary reference energies
(FERE)45 and apply a Hubbard U term46 for the rare earth and transition metal atoms (or
a selected subset of them). While such correction schemes in general improve ∆H they also
introduce some ambiguity, e.g. the dataset from which the FERE are determined or the
exact form of the orbitals on which the U term is applied. Thus in order not to compromise
the transparency and reproducibility of the data we use the pure PBE energies.
For a material to be thermodynamically stable it is necessary but not suﬃcient that ∆H <
0. Indeed, thermodynamic stability requires that ∆H be negative not only relative to its pure
elemental phases but relative to all other competing phases, i.e. its energy must be below
the convex hull.47 We stress, however, that in general, but for 2D materials in particular,
this deﬁnition cannot be directly applied as a criterion for stability and synthesisability.
The most important reasons for this are (i) the intrinsic uncertainty on the DFT energies
stemming from the approximate xc-functional (ii) substrate interactions or other external
eﬀects that can stabilise the monolayer (iii) kinetic barriers that separate the monolayer from
other lower energy phases rendering the monolayer (meta)stable for all practical purposes.
We calculate the energy of the 2D material relative to the convex hull of competing bulk
18


## Page 19

phases, ∆Hhull. The convex hull is currently constructed from the 2836 most stable binary
bulk compounds which were obtained from the OQMD.24 The energies of the bulk phases
were recalculated with GPAW using the PBE xc-functional and the same numerical settings
as applied for the 2D materials (but the structure was not re-optimised). Because the bulk
reference structures from OQMD were optimised with the VASP code and with Hubbard
U-corrections for materials containing 3d elements, and because the PBE misses attractive
vdW interaction, the bulk energies could be slightly overestimated relative to the monolayers.
As a consequence, monolayers that also exist in a layered bulk phase could have ∆Hhull < 0,
even if the layered bulk phase is part of the convex hull and thus should be energetically
more stable than the monolayer. Comparing our ∆Hhull values for 35 compounds with the
exfoliation energies calculated in Ref. 18 employing vdW compliant xc-functionals for both
bulk and monolayer, we estimate the errors in the convex hull energies to be below 0.1
eV/atom.
As an example, the convex hull for FexSe1−x is shown in Figure 5. The convex hull as
deﬁned by the bulk binaries is indicated by the blue lines. The labels for the 2D materials
refer to the crystal prototype and magnetic order. Clearly, most 2D materials lie above
the convex hull and are thus predicted to be thermodynamically unstable in freestanding
form under standard conditions. However, as mentioned above, depending on the material,
errors on the PBE formation energies can be sizable and thus the hull diagram should only
be taken as guideline. Nevertheless, in the present example we ﬁnd that FeSe (which is
itself a prototype) with anti-ferromagnetic ordering lies slightly below the convex hull and is
thus predicted to be thermodynamically stable. This prediction is consistent with the recent
experimental observation that monolayer FeSe deposited on SrTiO3 exhibits AFM order.48
2.4
Phonons and dynamic stability
Due to the applied symmetry constraints and/or the limited size of the unit cell, there is
a risk that the structure obtained after relaxation does not represent a local minimum of
19


## Page 20

0.0
0.5
1.0
FexSe1−x
−0.3
−0.2
−0.1
0.0
∆H [eV/atom]
Fe
Se
Fe2Se4
Fe2Se2
FeSe (AFM)
CdI2 (FM)
MoS2 (FM)
TiS3 (NM)
WTe2 (NM)
Bulk
2D
Figure 5: Convex hull for FexSe1−x. The convex hull as deﬁned by the bulk phases is rep-
resented by the blue lines. Blue squares denote bulk binary reference phases while orange
triangles represent 2D materials. The labels for the 2D materials refer to the crystal proto-
type and magnetic order.
the potential energy surface, but only a saddle point. We test for dynamical stability by
calculating the Γ-point phonons of a 2×2 repeated cell (without re-optimising the structure)
as well as the elastic constants (see Section 2.5). These quantities represent second-order
derivatives of the total energy with respect to atom displacements and unit cell lengths,
respectively, and negative values for either quantity indicate a structural instability.
The Γ-point phonons of the 2 × 2 supercell are obtained using the ﬁnite displacement
method.49 We displace each atom in the primitive cell by ±0.01 ˚A , and calculate the forces
induced on all the atoms in the supercell. From the forces we construct the dynamical matrix,
which is diagonalised to obtain the Γ-point phonons of the 2 × 2 cell (or equivalently the
Γ-point and zone boundary phonons of the primitive cell). The eigenvalues of the dynamical
matrix correspond to the square of the mass-renormalised phonon frequencies, ˜ω. Negative
eigenvalues are equivalent to imaginary frequencies and signal a saddle point.
Our procedure explicitly tests for stability against local distortions of periodicities up
to 2 × 2 and thus provides a necessary, but not suﬃcient condition for dynamic stability.
We stress, however, that even in cases where a material would spontaneously relax into a
structure with periodicity larger than 2 × 2, the Γ-point dynamical matrix of the 2 × 2
20


## Page 21

cell could exhibit negative eigenvalues. Our test is thus more stringent than it might seem
at ﬁrst glance. In principle, a rigorous test for dynamic stability would require the calcu-
lation of the full phonon band structure. Mathematically, the instabilities missed by our
approach are those that result in imaginary phonons in the interior of the BZ but not at
the zone boundary. Physically, such modes could be out of plane buckling or charge density
wave-driven reconstructions with periodicities of several unit cells. In general, these types
of instabilities are typically rather weak (as measured by the magnitude of the imaginary
frequency) as compared to more local distortions such as the T to T′ distortion considered
below. Moreover, they could well be a special property of the isolated monolayer and be-
come stabilised by the ubiquitous interactions of the 2D material with its environment, e.g.
substrates. This is in fact supported by the full phonon calculations by Mounet et al. for
∼250 isolated monolayers predicted to be easily exfoliable from experimentally known lay-
ered bulk phases.18 Indeed, most of the instabilities revealed by their calculations are of the
type described above and would thus be missed by our test. However, these instabilities
cannot be too critical as the monolayers are known to be stable in the vdW bonded layered
bulk structure.
As an example, Figure 6 compares the dynamical stability of a subset of transition metal
dichalcogenides and -oxides in the T and T′ phases (CdI2 and WTe2 prototypes). The two
upper panels show the smallest eigenvalue of the Γ-point dynamical matrix of the 2 × 2 cell.
Only materials above the dashed line are considered dynamically stable (for this example
we do not consider the sign of the elastic constants which could further reduce the set of
dynamically stable materials). Since the unit cell of the T′ phase contains that of the T
phase it is likely that a material initially set up in the T′ phase relaxes back to the T phase.
To identify these cases, and thereby avoid the presence of duplicates in the database, the
third panel shows the root mean square distance (RMSD) between the structures obtained
after relaxations starting in the T- and T′ phase, respectively. Structures below the dashed
line are considered identical. The color of each symbol refers to the four diﬀerent potential
21


## Page 22

−20
−10
0
T phase
(3 atoms/cell)
−20
−10
0
T′ phase
(6 atoms/cell)
MoS2
WTe2
OsS2
WS2
CrSe2
TaI2
HfI2
ZrBr2
IrS2
RhCl2
IrBr2
NbCl2
VO2
CoSe2
AlBr2
GaBr2
AuBr2
SnBr2
YBr2
AuO2
TiO2
RhTe2
CrCl2
GeTe2
PbTe2
WCl2
AuTe2
CdCl2
CuSe2
BaI2
TlI2
CuI2
ScBr2
HgTe2
MoCl2
RhO2
ScS2
0.0
0.2
0.4
dist(T,T′) [˚A]
min(˜ω2) [eV/˚A2]
T
T′
T
T′
T
T′
T
T′
Figure 6: Dynamical stability of a set of transition metal dichalcogenides and -oxides in the
T and T′ phases (CdI2 and WTe2 prototypes), respectively. The ﬁrst and second panels show
the minimum eigenvalue of the Γ-point dynamical matrix of the 2 × 2 unit cell (containing
12 and 24 atoms for the T and T′ phase, respectively.
The lower panel shows the root
mean square distance (RMSD) between the relaxed structures. The color indicates whether
the material is dynamically stable in the T phase (black), the T′ phase (blue), both phases
(orange) or neither of the phases (green).
22


## Page 23

energy surfaces illustrated at the bottom of the ﬁgure.
2.4.1
Stability criteria
To assess the stability of the materials in the C2DB, we turn to the set of experimentally
synthesised/exfoliated monolayers.
For these materials, the calculated energy above the
convex hull and minimum eigenvalue of the dynamical matrix are shown on Figure 7. It is
clear that all but ﬁve known monolayers have a hull energy below 0.2 eV/atom, and three of
these have only been synthesised on a metal substrate. Turning to the dynamical stability, all
but one of the experimentally known monolayers have a minimum eigenvalue of the dynamical
matrix above −2 eV/˚A
2, and 75% have a minimum eigenvalue above −1×10−5 eV/˚A
2 (shown
in light grey).
Guided by these considerations, we assign each material in the C2DB a stability level
(low, medium or high) for both dynamical and thermodynamic stability, as illustrated in
Table 2. For ease of reference, we also deﬁne the overall stability level of a given material
as the lower of the dynamical and thermodynamic stability levels. If a material has “low”
overall stability (colored red in the table), we consider it unstable and do not carry out
the rest of the workﬂow. Materials with ”high” overall stability are considered likely to
be stable and thus potentially synthesisable. Materials in the ”medium” stability category,
while unlikely to be stable as freestanding monolayers, cannot be discarded and might be
metastable and possible to synthesise under the right conditions. For example, free-standing
silicene has a heat of formation of 0.66 eV/atom, but can be grown on a silver substrate.
Likewise, the T′ phase of MoS2 (WTe2 prototype) has an energy of 0.27 eV/atom higher
than the thermodynamically stable H phase, but can be stabilised by electron doping.
23


## Page 24

0.0
0.5
∆Hhull [eV/atom]
CrI3-BiI3
Ti2CF2-Ti2CO2
NiSe2-CdI2
FeSe-FeSe
PtS2-CdI2
BN-BN
PtSe2-CdI2
WS2-MoS2
WSe2-MoS2
ZrS2-CdI2
C-C (Graphene)
MoSe2-MoS2
TiS3-TiS3
MoS2-MoS2
HfS2-CdI2
GaSe-GaS
VSe2-CdI2
VS2-CdI2
InSe-GaS
NbTe2-MoS2
SnS2-CdI2
WTe2-WTe2
ZrSe2-CdI2
BiI3-BiI3
TiS2-CdI2
NbS2-MoS2
MoTe2-MoS2
TaS2-MoS2
TaSe2-MoS2
NbSe2-MoS2
GaTe-GaS
CH-CH (Graphane)
MoSSe-MoSSe
MoTe2-WTe2
TaS2-CdI2
HfTe3-TiS3
P-P (Phosphorene)
V2CF2-Ti2CO2
GeH-CH (Germanane)
Nb2CF2-Ti2CO2
Nb2CO2-Ti2CO2
Ti2CO2-Ti2CO2
V2CH2O2-Ti2CH2O2
TiO2-CdI2
FeSe2-MoS2
Ti2CH2O2-Ti2CH2O2
MoS2-WTe2
V2CO2-Ti2CO2
Nb2CH2O2-Ti2CH2O2
C3N-C3N
CF-CH
Mo2CO2-Ti2CO2
GaN-BN
Ge-C (Germanene)
Si-C (Silicene)
0
3
6
−˜ω2
min [eV/˚A2]
Figure 7: The calculated energy above the convex hull and minimum eigenvalue of the
dynamical matrix (evaluated at the Γ-point for the 2×2 cell) for the 55 materials in the C2DB
that have been synthesised or exfoliated in monolayer form, see Refs. 6,9,10,12,50–57,57–95.
The three materials highlighted in red have only been synthesised on metallic substrates.
The black dashed lines indicate the thresholds used to categorise the thermodynamic and
dynamical stability of materials in the C2DB.
24


## Page 25

Table 2: The materials in the C2DB distributed over the nine stability cate-
gories deﬁned by the three levels (high, medium and low) of dynamical stability
(columns) and thermodynamic stability (rows). The overall stability of the ma-
terials is deﬁned as the lower of the two separate stability scales. Materials with
low overall stability (red) are considered unstable..
Dynamic stability
|˜ω2
min| > 2 or
Cii < 0
10−5 < |˜ω2
min| < 2
Cii > 0
|˜ω2
min| < 10−5
Cii > 0
Total
∆H > 0.2 eV
6.0%
4.2%
1.7%
12.0%
∆H < 0.2 eV
14.9%
10.9%
6.4%
32.2%
∆Hhull < 0.2 eV
11.4%
24.1%
20.3%
55.8%
Total
32.3%
39.2%
28.5%
2.5
Elastic constants
The elastic constants of a material are deﬁned by the generalised Hooke’s law,
σij = Cijklεkl
(2)
where σij, Cijkl and εkl are the stress, stiﬀness and strain tensors, respectively, and where
we have used the Einstein summation convention. In two dimensions, the stress and strain
tensors have three independent components, namely planar stress/strain in the x and y direc-
tions, as well as shear stress/strain. The stiﬀness tensor is a symmetric linear map between
these two tensors, and therefore has up to six independent components. Disregarding shear
deformations, the relationship between planar strain and stress is


σxx
σyy

=


C11
C12
C12
C22




ϵxx
ϵyy


(3)
25


## Page 26

For all materials in the C2DB, we calculate the planar elastic stiﬀness coeﬃcients C11, C22,
and C12. These are calculated using a central diﬀerence approximation to the derivative of
the stress tensor: the material is strained along one of the coordinate axes, x or y, and the
stress tensor is calculated after the ions have relaxed. We use strains of ±1% which we have
found to be suﬃciently large to eliminate eﬀects of numerical noise and suﬃciently small to
stay within the linear response regime.
Table 3 shows the calculated planar stiﬀness coeﬃcients of a set of 2D materials. As can
be seen the values from the C2DB are in very good agreement with previously published
PBE results. For the isotropic materials MoS2, WSe2 and WS2, C11 and C22 should be
identical, and we see a variation of up to 0.6%. This provides a test of how well converged
the values are with respect to numerical settings.
Table 3:
Planar elastic stiﬀness coeﬃcients (in N/m) calculated at the PBE
level. The results of this work are compared to previous calculations from the
literature and the mean absolute deviation (MAD) is shown.
C11 (N/m)
C22 (N/m)
C12 (N/m)
C2DB
Literature
C2DB
Literature
C2DB
Literature
P (phosphorene)
101.9
105.296
25.1
26.296
16.9
18.496
MoS2
131.4
132.619
131.3
132.619
32.6
32.719
WSe2
120.6
119.519
121.3
119.519
22.8
22.719
WS2
146.3
145.319
146.7
145.319
32.2
31.519
MAD
1.7
-
1.4
-
0.6
-
2.6
Magnetic anisotropy
The energy dependence on the direction of magnetisation, or magnetic anisotropy (MA),
arises from spin-orbit coupling (SOC). According to the magnetic force theorem97 this can
be evaluated from the eigenvalue diﬀerences such that the correction to the energy becomes
∆E(ˆn) =
X
kn
f(εˆn
kn)εˆn
kn −
X
kn
f(ε0
kn)ε0
kn,
(4)
26


## Page 27

where εˆn
kn and f(εˆn
kn) are the eigenenergies and occupation numbers, respectively, obtained
by diagonalising the Kohn-Sham Hamiltonian including SOC in a basis of collinear spinors
aligned along the direction ˆn, while ε0
kn and f(ε0
kn) are the bare Kohn-Sham eigenenergies
and occupation numbers without SOC.
For all magnetic materials we have calculated the energy diﬀerence between out-of-plane
and in-plane magnetisation EMA(i) = ∆E(ˆz)−∆E(i), (i = ˆx, ˆy). Negative values of EMA(i)
thus indicate that there is an out-of-plane easy axis of magnetisation.
Calculations for the ground state have been performed with plane-wave cutoﬀand en-
ergetic convergence threshold set to 800 eV and 0.5 meV/atom respectively. For all calcu-
lations we have used a Γ-centered Monkhorst-Pack k-point with a density of 20/˚A
−1. The
SOC contribution is introduced via a non-self-consistent diagonalisation of the Kohn-Sham
Hamiltonian evaluated in the projector-augmented wave formalism.98
2.7
Projected density of states
The projected density of states (PDOS) is a useful tool for identifying which atomic orbitals
comprise a band. It is deﬁned as
ρS
l (ε) =
X
a∈S
X
kn
X
m
|⟨φa
l,m|ψkn⟩|2δ(ε −εkn),
(5)
where ψkn are the Kohn-Sham wave functions with eigenvalues εkn and φa
l,m are the spin-
paired Kohn-Sham orbitals of atomic species S with angular momentum l (s, p, d, f). We
sum over all atoms belonging to species S so every atomic species has one entry per angular
momentum channel. In the PAW formalism this can be approximated as
ρS
l (ε) =
X
a∈S
X
kn
X
m
|⟨˜pa
l,m| ˜ψkn⟩|2δ(ε −εkn)
(6)
27


## Page 28

where ˜ψkn are the pseudo wave functions and ˜pa
l,m are the PAW projectors associated with
the atomic orbitals φa
l,m. The PDOS is calculated from Eq. (6) using linear tetrahedron
interpolation99 (LTI) of energy eigenvalues obtained from a ground state calculation with a
k-point sampling of 36/˚A
−1. In contrast to other techniques for calculating the PDOS using
smearing, the PDOS yielded by the LTI method returns exactly zero at energies with no
states. Examples of PDOS are shown in Figure 9 (right) for respectively the ferromagnetic
metal VO2 and the semiconductor WS2 in the H phase (MoS2 prototype).
2.8
Band structures
Electronic band structures are calculated along the high symmetry paths shown in Figure 8
for the ﬁve diﬀerent types of 2D Bravais lattices. The band energies are computed within
DFT using three diﬀerent xc-functionals, namely PBE, HSE06, and GLLBSC. These single-
particle approaches are complemented by many-body G0W0 calculations for materials with
a ﬁnite gap and up to four atoms in the unit cell (currently around 250 materials). For all
methods, SOC is included by non-selfconsistent diagonalisation in the full basis of Kohn-
Sham eigenstates. Band energies always refer to the vacuum level deﬁned as the asymptotic
limit of the Hartree potential, see Figure 12. Below we outline the employed methodology
while Section 3.2.1 provides an overview and comparison of the band energies obtained with
the diﬀerent methods.
2.8.1
PBE band structure
The electron density is determined self-consistently on a uniform k-point grid of density
12.0/˚A
−1. From this density, the PBE band structure is computed non-selfconsistently at 400
k-points distributed along the band path (see Figure 8). Examples of PBE band structures
are shown in Figure 9 for the ferromagnetic metal VO2 and the semiconductor WS2 both in
the MoS2 prototype structure. The expectation value of the out-of-plane spin component,
⟨χnkσ| ˆSz|χnkσ⟩, is evaluated for each spinorial wave function, χnkσ = (ψnk↑, ψnk↓), and is
28


## Page 29

indicated by the color of the band. For materials with inversion symmetry, the SOC cannot
induce band splitting, meaning that ⟨χnkσ| ˆSz|χnkσ⟩is ill-deﬁned and no color coding is used.
The band structure without SOC is indicated by a dashed grey line. We have compared our
PBE+SOC band gaps of 29 diﬀerent monolayers with those obtained with the VASP code
in Ref. 42 and ﬁnd a mean absolute deviation of 0.041 eV.
2.8.2
HSE band structure
The band structure is calculated non-selfconsistently using the range-separated hybrid func-
tional HSE06100 on top of a PBE calculation with k-point density 12.0/˚A
−1 and 800 eV
plane wave cutoﬀ. We have checked for selected systems that the HSE band structure is
well converged with these settings. The energies along the band path are obtained by spline
interpolation from the uniform k-point grid. As an example, the HSE band structure of
WS2 is shown in the left panel of Figure 10 (black line) together with the PBE band struc-
ture (grey dashed). The PBE band gap increases from 1.52 eV to 2.05 eV with the HSE06
functional in good agreement with earlier work reporting band gaps of 1.50 eV (PBE) and
1.90 eV (HSE)101 and 1.55 eV (PBE) and 1.98 eV (HSE),102 respectively. A more system-
atic comparison of our results with the HSE+SOC band gaps obtained with the VASP code
in Ref. 42 for 29 monolayers yield a mean absolute deviation of 0.14 eV. We suspect this
small but non-zero deviation is due to diﬀerences in the employed PAW potentials and the
non-selfconsistent treatment of the HSE in our calculations.
2.8.3
GLLBSC fundamental gap
For materials with a ﬁnite PBE band gap, the fundamental gap (i.e. the diﬀerence between
the ionisation potential and electron aﬃnity) also sometimes referred to as the quasiparticle
gap, is calculated self-consistently using the GLLBSC103 xc-functional with a Monkhorst-
Pack k-point grid of density 12.0/˚A
−1. The GLLBSC is an orbital-dependent exact exchange-
based functional, which evaluates the fundamental gap as the sum of the Kohn-Sham gap
29


## Page 30

Y
H
C
Γ
H1
X
Oblique
Centered
rectangular
H
C
H1
X
Γ
Hexagonal
Γ
M
K
Γ
X
Y
S
Rectangular
Square
Γ
X
M
 
|a1| ≠ |a2|, γ ≠ 90o
|a1| ≠ |a2|, γ ≠ 90o
|a2| cos γ = |a1| / 2
a1
a2
a1
a2
a1
a2
a2
a1
a2
a1
|a1| = |a2|, γ = 120o
|a1| ≠ |a2|, γ = 90o
|a1| = |a2|, γ = 90o
γ
γ
γ
γ
γ
Figure 8: Overview of the ﬁve 2D Bravais lattices and corresponding Brillouin zones. The
unit vectors a1 and a2 are shown together with the angle between them γ. The primitive
unit cell is indicated in gray. High symmetry points of the BZ and the path along which the
band structure is evaluated, are indicated in blue.
30


## Page 31

Γ
M
K
Γ
k-points
−10
−9
−8
−7
−6
−5
E −Evac [eV]
−1.0
−0.5
0.0
0.5
1.0
⟨Sz⟩
−2
0
2
projected dos [states / eV]
−10
−9
−8
−7
−6
−5
E −Evac [eV]
V (s)
V (p)
V (d)
O (s)
O (p)
Γ
M
K
Γ
k-points
−8
−7
−6
−5
−4
−3
−2
−1
E −Evac [eV]
−1.0
−0.5
0.0
0.5
1.0
⟨Sz⟩
0
1
2
3
4
projected dos [states / eV]
−8
−7
−6
−5
−4
−3
−2
−1
E −Evac [eV]
W (s)
W (p)
W (d)
S (s)
S (p)
Figure 9: Band structure (left) and projected density of states (right) for VO2 (top) and WS2
(bottom) in the MoS2 prototype, calculated with the PBE xc-functional. The z-component
of the spin is indicated by the color code on the band structure.
31


## Page 32

Γ
M
K
Γ
−8
−7
−6
−5
−4
−3
−2
−1
E −Evac [eV]
HSE
PBE
Γ
M
K
Γ
−9
−8
−7
−6
−5
−4
−3
−2
−1
E −Evac [eV]
G0W0
PBE
Figure 10:
Band structure of WS2 calculated with the HSE06 functional (left) and G0W0
(right). For comparison the PBE result is also shown (grey dashed). Spin-orbit coupling
(SOC) is included in all calculations. The band energies refer to the vacuum level. The
points show the calculated eigenvalues from which the band structure is interpolated. The
relatively coarse k-point grid used for G0W0 is justiﬁed by the analytical treatment of the
screened interaction W(q) around q = 0, see Figure 11.
32


## Page 33

and the xc-derivative discontinuity, Egap = εKS
gap + ∆xc. The method has been shown to yield
excellent quasiparticle band gaps at very low computational cost for both bulk103,104 and 2D
semiconductors.36
In the exact Kohn-Sham theory, εKS
v
should equal the exact ionisation potential and thus
∆xc should be used to correct only the conduction band energies.105 Unfortunately, we have
found that in practice this procedure leads to up-shifted band energies (compared with the
presumably more accurate G0W0 results, see Figure 20). Consequently, we store only the
fundamental gap and ∆xc in the database. However, as will be shown in Section 3.2.1 the
center of the gap is in fact reasonably well described by PBE suggesting that eﬃcient and
fairly accurate predictions of the absolute band edge energies can be obtained by a symmetric
GLLBSC correction of the PBE band edges.
2.8.4
G0W0 band structure
For materials with ﬁnite PBE band gap the quasiparticle (QP) band structure is calculated
using the G0W0 approximation on top of PBE following our earlier work.106,107 Currently, this
resource demanding step is performed only for materials with up to four atoms in the unit cell.
The number of plane waves and the number of unoccupied bands included in the calculation
of the non-interacting density response function and the GW self-energy are always set equal.
The individual QP energies are extrapolated to the inﬁnite basis set limit from calculations
at plane wave cutoﬀs of 170, 185 and 200 eV, following the standard 1/NG dependence,108,109
see Figure 11(right). The screened Coulomb interaction is represented on a non-linear real
frequency grid ranging from 0 eV to 230 eV and includes around 250 frequency points.
The exchange contribution to the self-energy is calculated using a Wigner-Seitz truncation
scheme110 for a more eﬃcient treatment of the long range part of the exchange potential.
For the correlation part of the self-energy, a 2D truncation of the Coulomb interaction is
used.111,112 We stress that the use of a truncated Coulomb interaction is essential to avoid
unphysical screening from periodically repeated layers which otherwise leads to signiﬁcant
33


## Page 34

band gap reductions.
Importantly, the use of a truncated Coulomb interaction leads to much slower k-point
convergence because of the strong q-dependence of the 2D dielectric function around q = 0.
We alleviate this problem by using an analytical expression for the screened interaction when
performing the BZ integral around q = 0.107 This allows us to obtain well converged results
with a relatively low k-point density of 5.0/˚A
−1 (corresponding to 12 × 12 for MoS2). For
example, with this setting the G0W0 band gap of MoS2 is converged to within 0.05 eV, see
Figure 11(left). In comparison, standard BZ sampling with no special treatment of the q = 0
limit, requires around 40 × 40 k-points to reach the same accuracy.
Figure 10 (right) shows the PBE and G0W0 band structures of WS2 (including SOC).
The G0W0 self-energy opens the PBE band gap by 1.00 eV and the HSE gap by 0.47 eV, in
good agreement with previous studies.113 We note in passing that our previously published
G0W0 band gaps for 51 monolayer TMDCs36 are in good agreement with the results obtained
using the workﬂow described here. The mean absolute error between the two data sets is
around 0.1 eV and can be ascribed to the use of PBE rather than LDA as starting point and
the use of the analytical expression for W around q = 0.
A detailed comparison of our results with previously published G0W0 data is not mean-
ingful because of the rather large diﬀerences in the employed implementations/parameter
settings. In particular, most reported calculations do not employ a truncated Coulomb in-
teraction and thus suﬀer from spurious screening eﬀects, which are then corrected for in
diﬀerent ways. Moreover, they diﬀer in the amount of vacuum included the supercell, the
employed k-point grids and basis sets, the in-plane lattice constants, and the DFT starting
points. For example, published values for the QP band gap of monolayer MoS2 vary from
from 2.40 to 2.90 eV114–121 (see Ref. 120 for a detailed overview). The rather large variation
in published GW results for 2D materials is a result of the signiﬁcant numerical complexity
of such calculations and underlines the importance of establishing large and consistently
produced benchmark data sets like the present.
34


## Page 35

For bulk materials, self-consistency in the Green’s function part of the self-energy, i.e.
the GW0 method, has been shown to increase the G0W0 band gaps and improve the agree-
ment with experiments.122 The trend of band gap opening is also observed for 2D materi-
als,107,121,121,123 however, no systematic improvement with respect to experiments has been
established.123 For both bulk and 2D materials, the fully self-consistent GW self-energy sys-
tematically overestimates the band gap122,123 due to the neglect of vertex corrections.123,124
In G0W0 the neglect of vertex corrections is partially compensated by the smaller band gap of
the non-interacting Kohn-Sham Green’s function compared to the true interacting Green’s
function. In this case, the vertex corrections aﬀect mainly the absolute position of the bands
relative to vacuum while the eﬀect on the band gap is relatively minor.123
In Table 4 we compare calculated band gaps from C2DB with experimental band gaps
for three monolayer TMDCs and phosphorene. The experimental data has been corrected
for substrate interactions,123,125 but not for zero-point motion, which is expected to be small
(< 0.1eV). The G0W0 results are all within 0.2 eV of the experiments. A further (indirect)
test of the G0W0 band gaps against experimental values is provided by the comparison of
our BSE spectra against experimental photoluminescence data in Table 7, where we have
used a G0W0 scissors operator. Finally, we stress that the employed PAW potentials are not
norm-conserving, and this can lead to errors for bands with highly localised states (mainly
4f and 3d orbitals), as shown in Ref. 126. Inclusion of vertex corrections and use of norm
conserving potentials will be the focus of future work on the C2DB.
2.9
Band extrema
For materials with a ﬁnite band gap, the positions of the valence band maximum (VBM) and
conduction band minimum (CBM) within the BZ are identiﬁed together with their energies
relative to the vacuum level. The latter is deﬁned as the asymptotic value of the electrostatic
potential, see Figure 12. The PBE electrostatic potential is used to deﬁne the vacuum level
in the non-selfconsistent HSE and G0W0 calculations. For materials with an out-of-plane
35


## Page 36

102
103
Nk (number of k-points)
2.0
2.5
3.0
3.5
4.0
4.5
QP band gap [eV]
6 × 6
12 × 12
18 × 18
24 × 24
36 × 36
48 × 48
Without analytic q→0 limit.
With analytic q→0 limit.
∞
140
1/NG (1 / number of plane waves)
−5.85
−5.95
−6.05
VBM - Evac [eV]
170 eV
185 eV
200 eV
−3.45
−3.35
−3.25
CBM - Evac [eV]
170 eV
185 eV
200 eV
Figure 11: Left: Convergence of the QP band gap of MoS2 as a function of k-point sampling
with and without the analytical treatment of W(q) around q = 0. It is clear that the ana-
lytical treatment of the screened interaction signiﬁcantly improves the k-point convergence.
Right: The convergence of the CBM and VBM versus the number of plane waves. The band
energies are obtained by extrapolation of three calculations performed with PW cutoﬀup
to 200 eV. In all panels, the red dot indicates the data point calculated by the workﬂow and
available in the C2DB.
36


## Page 37

Table 4: Comparison between calculated and experimental band gaps for four
freestanding monolayers. The experimental values have been corrected for sub-
strate screening. MAD refers to the mean absolute deviation between the pre-
dicted values and the measured values.
Band gap (eV)
Material
PBE
HSE06
GLLBSC
G0W0
Experiment
MoS2
1.58
2.09
2.21
2.53
2.50127
MoSe2
1.32
1.80
1.88
2.12
2.31128
WS2
1.53
2.05
2.16
2.53
2.72129
P (phosphorene)
0.90
1.51
1.75
2.03
2.20125
MAD w.r.t. experiment
1.10
0.57
0.43
0.15
-
dipole moment, a dipole correction is applied during the selfconsistent DFT calculation, and
the vacuum level is deﬁned as the average of the asymptotic electrostatic potentials on the
two sides of the structure. The PBE vacuum level shift is also stored in the database.
−5
0
5
z [˚A]
−15
−10
−5
0
E −Evac [eV]
∆Φ = 0.75 eV
Mo
S
Se
Potential
CBM
VBM
Figure 12: Electrostatic potential proﬁle perpendicular to monolayer MoSSe (averaged in
plane). The position of the VBM and CBM are indicated together with the splitting of the
vacuum levels caused by the out-of-plane dipole moment of the MoSSe layer.
2.10
Fermi surface
The Fermi surface is calculated using the PBE xc-functional including SOC for all metallic
compounds in the database. Based on a ground state calculation with a k-point density of
37


## Page 38

at least 20/˚A−1, the eigenvalues are interpolated with quadratic splines and plotted within
the ﬁrst BZ. Figure 13 (left) shows an example of the Fermi surface for VO2-MoS2 with
color code indicating the out-of-plane spin projection ⟨Sz⟩. The band structure refers to the
ferromagnetic ground state of VO2-MoS2, which has a magnetic moment of 0.70 µB per unit
cell, characterised by alternating spin-polarised lobes with ⟨Sz⟩= ±1.
−1.0
−0.5
0.0
0.5
1.0
⟨Sz⟩
VBM
CBM
Figure 13: Left: Brillouin zone and Fermi surface calculated with PBE and spin-orbit cou-
pling for VO2 in the MoS22 crystal structure. The Fermi surface is colored by the spin
projection along the z-axis. Right: Brillouin zone, valence band maximum (VBM) and con-
duction band minimum (CBM) for WS2 in the MoS2 crystal structure. The grey areas in
both plots mark the irreducible Brillouin zone.
2.11
Eﬀective masses
For materials with a ﬁnite PBE gap, the eﬀective electron and hole masses are calculated
from the PBE eigenvalues; initially these are calculated on an ultraﬁne k-point mesh of
density 45.0/˚A
−1 uniformly distributed inside a circle of radius 0.015 ˚A
−1 centered at the
VBM and CBM, respectively. The radius is chosen to be safely above the noise level of the
calculated eigenvalues but still within the harmonic regime; it corresponds to a spread of
eigenvalues of about 1 meV within the circle for an eﬀective mass of 1 m0. For each band
within an energy window of 100 meV above/below the CBM/VBM, the band curvature is
obtained by ﬁtting a third order polynomial. Even though the masses represent the second
38


## Page 39

derivative of the band energies, we have found that the inclusion of 3rd order terms stabilises
the ﬁtting procedure and yields masses that are less sensitive to the details of the employed
k-point grids. For each band the mass tensor is diagonalised to yield heavy and light masses
in case of anisotropic band curvatures. The masses (in two directions) and the energetic
splitting of all bands within 100 meV of the band extremum are calculated both with and
without SOC and stored in the database. Other approaches exist for calculating eﬀective
masses, such as k · p perturbation theory (see e.g. 130 and references therein); the present
scheme was chosen for its simplicity and ease of application to a wide range of diﬀerent
materials.
In addition to the eﬀective masses at the VBM and CBM, the exciton reduced mass is
calculated by applying the above procedure to the direct valence-conduction band transition
energies, εv−c(k) = εc(k) −εv(k). For direct band gap materials the exciton reduced mass
is related to the electron and hole masses by 1/µex = 1/m∗
e + 1/m∗
h, but in the more typical
case of indirect band gaps, this relation does not hold.
As an example, Figure 14 shows a zoom of the band structure of SnS-GeSe around
the VBM and CBM (upper and lower panels). The second order ﬁts to the band energies
(extracted from the ﬁtted 3rd order polynomial) are shown by red dashed lines. It can be
seen that both the conduction and valence bands are anisotropic leading to a heavy and
light mass direction (left and right panels, respectively). The valence band is split by the
SOC resulting in two bands separated by ∼10 meV and with slightly diﬀerent curvatures.
The conduction band exhibits a non-trivial band splitting in one of the two directions. The
peculiar band splitting is due to a Rashba eﬀect arising from the combination of spin-orbit
coupling and the ﬁnite perpendicular electric ﬁeld created by the permanent dipole of the
SnS structure where Sn and S atoms are displaced in the out of plane direction leading to a
sizable vacuum level diﬀerence of 1.13 eV, see Figure 12.
Table 5 shows a comparison between selected eﬀective masses from the C2DB and pre-
viously published data also obtained with the PBE xc-correlation functional and including
39


## Page 40

−0.2
0.0
0.2
∆k [1/˚A]
−3.76
−3.74
E −Evac [eV]
CB, direction 1
−0.2
0.0
0.2
∆k [1/˚A]
CB, direction 2
−1.0
−0.5
0.0
0.5
1.0
⟨Sz⟩
−0.2
0.0
0.2
∆k [1/˚A]
−6.09
−6.08
−6.07
−6.06
−6.05
E −Evac [eV]
VB, direction 1
−0.2
0.0
0.2
∆k [1/˚A]
VB, direction 2
−1.0
−0.5
0.0
0.5
1.0
⟨Sz⟩
Figure 14: Zoom of the band structure of SnS in the GeSe crystal structure around the
conduction and valence band extrema (upper and lower panels). Second order ﬁts used to
determine the eﬀective masses are shown by red dashed lines. The peculiar band splitting in
the conduction band minimum (upper left panel) is caused by a Rashba eﬀect arising from
the combination of spin-orbit coupling and the ﬁnite perpendicular electric ﬁeld created by
the asymmetric SnS structure.
SOC. Overall, the agreement is very satisfactory.
2.12
Work function
For metallic compounds, the work function is obtained as the diﬀerence between the Fermi
energy and the asymptotic value of the electrostatic potential in the vacuum region, see
Figure 12. The work function is determined for both PBE and HSE band structures (both
including SOC) on a uniform k-point grid of density 12.0/˚A−1. Since the SOC is evaluated
non-selfconsistently, the Fermi energy is adjusted afterwards based on a charge neutrality
condition.
2.13
Deformation potentials
For semiconductors, the deformation potentials quantify the shift in band edge energies
(VBM or CBM) upon a linear deformation of the lattice. The uniaxial absolute deformation
40


## Page 41

Table 5: Calculated PBE eﬀective masses (in units of m0), for the highest valence
band and lowest conduction band, for diﬀerent 2D materials. All C2DB values
are calculated including spin-orbit coupling.
Electron mass (m0)
Hole mass (m0)
Material
k-point
C2DB
Literature
C2DB
Literature
MoS2
K
0.42
0.44130
0.53
0.54130
WSe2
K
0.46
0.40130
0.35
0.36130
Phosphorene (zig-zag)
Γ
1.24
1.2496
6.56
6.4896
Phosphorene (armchair)
Γ
0.14
0.1396
0.13
0.1296
MAD
0.02
-
0.03
-
potential along axis i (i = x, y) is deﬁned as131,132
Dα
ii = ∆Eα
εii
,
α = VBM, CBM
(7)
where ∆Eα is the energy shift upon strain and εii are the strains in the i-directions.
The deformation potentials are important physical quantities as they provide an estimate
of the strength of the (acoustic) electron-phonon interaction, see Section 3.2.2. Moreover,
they are obviously of interest in the context of strain-engineering of band gaps and they can
be used to can be used to infer an error bar on the band gap or band edge positions due to
a known or estimated error bar on the lattice constant.
The calculation of Dα
ii is based on a central diﬀerence approximation to the derivative. A
strain of ±1% is applied separately in the x and y directions and the ions are allowed to relax
while keeping the unit cell ﬁxed. Calculations are performed with the PBE xc-functional, a
plane wave cutoﬀof 800 eV, and a k-point density of 12/˚A−1.
The change in band energy, ∆Eα, is measured relative to the vacuum level. In cases
with nearly degenerate bands, care must be taken to track the correct bands as diﬀerent
bands might cross under strain. In this case, we use the expectation value ⟨ˆSz⟩to follow the
correct band under strain. Figure 15 shows how the band structure of MoS2 changes as a
function of strain. Both the VBM and the CBM shift down (relative to the vacuum level)
41


## Page 42

when tensile strain is applied in the x direction, but the conduction band shows a much
larger shift, leading to an eﬀective band gap closing under tensile strain.
Γ
M
K
Γ
Band structure
−7
−6
−5
−4
−3
E −Evac [eV]
Compressed
Relaxed
Strained
−5
0
5
relative change in area [%]
−7
−6
−5
−4
−3
EK −Evac [eV]
VBM
CBM
Fit
Figure 15: Left: Valence- and conduction bands of MoS2 for ±4.5% biaxial strain. Right:
Energies of the VBM and CBM at the K point as function of strain. The symbols are the
results of full DFT calculations, while the dashed lines are obtained from the deformation
potentials evaluated at ±1% strain.
Table 6 shows a comparison between the deformation potentials in the C2DB, and liter-
ature values obtained using similar methods. There is generally good agreement, and part
of the discrepancy can be ascribed to the fact that, in contrast to Ref. 133, our numbers
include spin-orbit coupling.
Table 6: Absolute deformation potentials (in eV) of the VBM and CBM for
diﬀerent materials. All results are based on the PBE xc-functional.
Valence band
Conduction band
Material
k-point
C2DB
Ref. 133
C2DB
Ref. 133
MoSe2
K
−1.43
−1.86
−5.57
−5.62
WS2
K
−1.25
−1.59
−6.66
−6.76
WSe2
K
−1.21
−1.43
−6.21
−6.35
hBN
K
−1.57
−1.63
−4.55
−4.62
MAD
0.26
-
0.14
-
42


## Page 43

2.14
Plasma frequencies
The dielectric response of a 2D material is described by its 2D polarisability, α2D (see Sec-
tion 2.15 for a general introduction of this quantity). For metals, it can be separated into
contributions from intraband and interband transitions, i.e. α2D = α2D,intra + α2D,inter. We
have found that local ﬁeld eﬀects (LFEs) are negligible for the intraband component, which
consequently can be treated separately and evaluated as an integral over the Fermi surface.
Speciﬁcally, this leads to the Drude expression for the polarisability in the long wave length
limit α2D,intra(ω) = −ω2
P,2D/(2πω2) where ωP,2D is the 2D plasma frequency, which in atomic
units is given by
ω2
P,2D = 4π
A
X
snk
|ˆq · vsnk|2δ(εsnk −εF),
(8)
where vsnk = ⟨snk|ˆp/m0|snk⟩is a velocity matrix element (with m0 the electron mass),
ˆq = q/q is the polarisation direction, s, n, k denote spin, band and momentum indices, and
A is the supercell area. The 2D plasma frequency is related to the conventional 3D plasma
frequency by ω2
P,2D(ω) = ω2
P,3D(ω)L/2 where L is the supercell height.
The plasma frequency deﬁned above determines the intraband response of the 2D metal
to external ﬁelds. In particular, it determines the dispersion relation of plasmon excitations
in the metal.
The latter are deﬁned by the condition ε2D(ωP) = 1 + 2πqα2D(ωP) = 0,
where q is the plasmon wave vector. Neglecting interband transitions (the eﬀect of which is
considered in Section 3.2.4), the 2D plasmon dispersion relation becomes
ωP(q) = ωP,2D
√q
(9)
The plasma frequencies, ωP,2D, for polarisation in the x and y directions, respectively, are
calculated for all metals in the C2DB using the tetrahedral method99 to interpolate matrix
elements and eigenvalues based on a PBE band structure calculation including SOC and
43


## Page 44

with a k-point density of 20/˚A
−1.
2.15
Electronic polarisability
The polarisability tensor αij is deﬁned by
Pi(q, ω) =
X
j
αij(q, ω)Ej(q, ω),
(10)
where Pi is the i’th component of the induced polarisation averaged over a unit cell and Ej
is the j’th component of the macroscopic electric ﬁeld. Using that Pi = (Di −Ei)/(4π) =
P
j(ϵij −δij)Ej/(4π) one observes that αij = (ϵij −δij)/(4π), where ϵij is the dielectric
function. In contrast to the dielectric function, whose deﬁnition for a 2D material is not
straightforward,120 the polarisability allows for a natural generalisation to 2D by considering
the induced dipole moment per unit area,
P 2D
i
(q, ω) =
X
j
α2D
ij (q, ω)Ej(q, ω).
(11)
Since the Pi is a full unit cell average and P 2D
i
is integrated in the direction orthogonal to
the slab, we have P 2D
i
= LPi and α2D
ij = Lαij, where L is the length of the unit cell in the
direction orthogonal to the slab.
In the following, we focus on the longitudinal components of the polarisability and dielec-
tric tensors, which are simply denoted by α and ϵ. These are related to the density-density
response function, χ, via the relations
α2D(q, ω) = L
4π(ϵ(q, ω) −1),
(12)
ϵ−1(q, ω) = 1 + ⟨vc(q)χ(ω)⟩q,
(13)
44


## Page 45

where vc is the Coulomb interaction and
⟨vcχ(ω)⟩q = 1
V
Z
Cell
drdr′dr′′vc(r, r′)χ(r′, r′′, ω)e−iq(r−r′′),
(14)
where Cell is the supercell with volume V . The response function, χ, satisﬁes the Dyson
equation134 χ = χirr +χirrvcχ, where χirr is the irreducible density-density response function.
In the random phase approximation (RPA) χirr is replaced by the non-interacting response
function, χ0, whose plane wave representation is given by135,136
χ0
GG′(q, ω) = 1
Ω
X
k∈BZ
X
mn
(fnk −fmk+q)⟨ψnk|e−i(q+G)·r|ψmk+q⟩⟨ψmk+q|ei(q+G′)·r|ψnk⟩
¯hω + εnk −εmk+q + iη
,
(15)
where G, G′ are reciprocal lattice vectors and Ωis the crystal volume.
For all materials in the database, we calculate the polarisability within the RPA for both
in-plane and out-of-plane polarisation in the optical limit q →0. For metals, the interband
contribution to the polarisability is obtained from Eq. (15) while the intraband contribution
is treated separately as described in Section 2.14. The single-particle eigenvalues and eigen-
states used in Eq. 15 are calculated with PBE, a k-point density of 20/˚A
−1 (corresponding
to a k-point grid of 48×48 for MoS2 and 60×60 for graphene), and 800 eV plane wave cutoﬀ.
The Dyson equation is solved using a truncated Coulomb potential137,138 to avoid spurious
interactions from neighboring images. We use the tetrahedron method to interpolate the
eigenvalues and eigenstates and a peak broadening of η = 50 meV. Local ﬁeld eﬀects are
accounted for by including G-vectors up to 50 eV. For the band summation we include 5
times as many unoccupied bands as occupied bands, which roughly corresponds to an energy
cutoﬀof 50 eV. The calculations are performed without spin-orbit coupling.
In Figure 16 we show the real and imaginary part of α2D for the semiconductor MoS2.
The PBE band gap of this material is 1.6 eV and we see the onset of dissipation at that
energy. We also see that the initial structure of Im α is a constant, which is exactly what
would be expected from the density of states in a 2D material with parabolic dispersion.
45


## Page 46

Finally, we note that the static polarisability Re α|ω=0 ≈6˚A, which can easily be read oﬀ
the ﬁgure. The polarisability is also shown for the metallic 1T-NbS2 where we display the
real part with and without the intraband Drude contribution ω2
P,2D/(¯hω + iη)2.
0
2
4
6
8
10
¯hω [eV]
0
5
10
15
polarisability [˚A]
real part
imaginary part
0
2
4
6
8
10
¯hω [eV]
−10
−5
0
5
10
polarisability [˚A]
real part (full)
real part (interband)
imaginary part
Figure 16: Real and imaginary part of the RPA in-plane polarisability of monolayer MoS2
in the H phase (left) and the metallic monolayer NbS2 in the T phase (right). For metals,
the real part is shown both with and without the intraband contributions.
2.16
Optical absorbance
The power absorbed by a 2D material under illumination of a monochromatic light ﬁeld with
polarisation ˆe is quantiﬁed by the dimensionless absorbance:
Abs(ω) = 4πωα2D(qˆe →0, ω)/c,
(16)
where c is the speed of light. In Section (2.15) we gave a prescription for evaluating α2D
in the RPA. However, absorption spectra of 2D semiconductors often display pronounced
excitonic eﬀects, which are not captured by the RPA. The Bethe-Salpeter equation (BSE) is
a well-known method capable of describing excitonic eﬀects and has been shown to provide
good agreement with experimental absorption spectra for a wide range of materials.139
For materials with ﬁnite band gap and up to four atoms per unit cell, we have calculated
the RPA and the BSE absorption spectra for electric ﬁelds polarised parallel and perpendic-
46


## Page 47

ular to the layers. The calculations are performed on top of PBE eigenstates and eigenvalues
with spin-orbit coupling included and all unoccupied band energies shifted by a constant in
order to reproduce the G0W0 quasiparticle gap (the scissors operator method). If the G0W0
gap is not available we use the GLLBSC gap for non-magnetic materials and the HSE gap
for magnetic materials (since GLLBSC is not implemented in GPAW for spin-polarised sys-
tems). The screened interaction entering the BSE Hamiltonian is calculated within the RPA
using a non-interacting response function evaluated from Eq. (15) with local ﬁeld eﬀects (i.e.
G-vectors) included up to 50 eV and 5 times as many unoccupied bands as occupied bands
for the sum over states. We apply a peak broadening of η = 50 meV and use a truncated
Coulomb interaction. The BSE Hamiltonian is constructed from the four highest occupied
and four lowest unoccupied bands on a k-point grid of density of 20/˚A
−1, and is diagonalised
within the Tamm-Dancoﬀapproximation. We note that the Tamm-Dancoﬀapproximation
has been found to be very accurate for bulk semiconductors.140 For monolayer MoS2 we
have checked that it reproduces the full solution of the BSE, but its general validity for 2D
materials, in particular those with small band gaps, should be more thoroughly tested.
In Figure 17 we show the optical absorption spectrum of MoS2 obtained with the electric
ﬁeld polarised parallel and perpendicular to the layer, respectively. Both RPA and BSE
spectra are shown (the in-plane RPA absorbance equals the imaginary part of the RPA
polarisability, see Figure 16(left), apart from the factor 4πω and the scissors operator shift).
The low energy part of the in-plane BSE spectrum is dominated by a double exciton peak
(the so-called A and B excitons) and is in excellent agreement with experiments.141
In general, calculations of electronic excitations of 2D materials converge rather slowly
with respect to k-points due to the non-analytic behavior of the dielectric function in the
vicinity of q = 0.142–144 In Figure 18 we show the k-point dependence of the binding energy
of the A exciton in MoS2 obtained as the diﬀerence between the direct band gap and the
position of the ﬁrst peak in Figure 17. We observe a strong overestimation of the exciton
binding energy at small k-point samplings, which converges slowly to a value of ∼0.5 eV at
47


## Page 48

0
1
2
3
4
5
¯hω [eV]
0
20
40
60
absorbance E∥[%]
RPA
BSE
0
1
2
3
4
5
¯hω [eV]
0.0
0.1
0.2
0.3
absorbance E⊥[%]
RPA
BSE
Figure 17: Optical absorbance of MoS2 obtained with the RPA and BSE methods. Left:
Electric ﬁeld polarisation parallel to the layer. The lowest energy part of the BSE spectrum
is composed of two excitonic peaks separated by 0.15 eV, which originates from the spin-orbit
splitting in the valence band at K. Right: Electric ﬁeld polarised perpendicular to the layer.
large k-point samplings. For 48 × 48 k-points, corresponding to the k-point sampling used
for the BSE calculations in the database, the exciton binding energy is 0.53 eV, whereas a
1/N 2
k extrapolation to inﬁnite k-point sampling gives 0.47 eV (see inset in Figure 18). In
general, the exciton binding energy decreases with increasing k-point sampling, and thus the
exciton binding energies reported in the C2DB might be slightly overestimated. However,
since G0W0 band gaps also decrease when the k-point sampling is increased (see Figure 11)
the two errors tend to cancel such that the absolute position of the absorption peak from
BSE-G0W0 converges faster than the band gap or exciton binding energy alone.
The BSE-G0W0 method has previously been shown to provide good agreement with exper-
imental photoluminescence and absorption measurements on 2D semiconductors. In Table 7
we show that our calculated position of the ﬁrst excitonic peak agree well with experimental
observations for four diﬀerent TMDCs and phosphorene. Experimentally, the monolayers are
typically supported by a substrate, which may alter the screening of excitons. However the
resulting decrease in exciton binding energies is largely cancelled by a reduced quasiparticle
gap such that the positions of the excitons are only slightly red-shifted as compared with
the case of pristine monolayers.145
48


## Page 49

12
18
24
30
36
42
48
N 1/2
k
0.6
0.8
1.0
1.2
exciton binding energy [eV]
0
1/482
1/362
1/Nk
0.5
0.6
0.7
Figure 18: Convergence of the binding energy of the lowest exciton in monolayer MoS2
obtained from a BSE calculation as a function of k-point mesh. The quasiparticle energies
entering the BSE Hamiltonian are obtained from a fully converged PBE calculations with
a scissors operator applied to match the G0W0 band gap. The red point represents the
k-point sampling applied in the database, which is seen to overestimate the extrapolated
exciton binding energy by ∼0.06 eV (inset).
Table 7: Comparison between calculated and experimental positions of the ﬁrst
excitonic peak for four diﬀerent transition metal dichalcogenide monolayers and
phosphorene.
Energy of the ﬁrst bright exciton (eV)
Material
BSE@PBE-G0W0
Experiment
MoS2
2.00
1.83,146 1.86,147 1.87148
MoSe2
1.62
1.57,146 1.57,149 1.58150
WS2
2.07
1.96,147 2.02150
WSe2
1.71
1.64,148 1.66149
P (phosphorene)
1.45
1.45,151 1.75152
MAD w.r.t. experiment
0.066
-
49


## Page 50

3
Database overview
Having described the computational workﬂow, we now turn to the content of the database
itself. We ﬁrst present a statistical overview of all the materials in the C2DB (i.e. without
applying any stability ﬁltering) by displaying their distribution over crystal structure proto-
types and their basic properties. We also provide a short list with some of the most stable
materials, which to our knowledge have not been previously studied. Next, the predicted
stability of the total set of materials is discussed and visualised in terms of the descriptors
for thermodynamic and dynamic stability introduced in Section 2.4.1. In Section 3.2 we
analyse selected properties in greater detail focusing on band gaps and band alignment, ef-
fective masses and mobility, magnetic properties, plasmons, and excitons. Throughout the
sections we explore general trends and correlations in the data and identify several promising
materials with interesting physical properties.
3.1
Materials
In Table 8 we list the major classes of materials currently included in the database. The
materials are grouped according to their prototype, see Section 2.2.2. For each prototype
we list the corresponding space group, the total number of materials, and the number of
materials satisfying a range of diﬀerent conditions. The atomic structure of some of the
diﬀerent prototypes were shown in Figure 4. The vast majority of the 2D materials that
have been experimentally synthesised in monolayer form are contained in the C2DB (the
55 materials in Figure 7 in addition to seven metal-organic perovskites). These materials
are marked in the database and a literature reference is provided. Additionally, 80 of the
monolayers in the C2DB could potentially be exfoliated from experimentally known layered
bulk structures.16–19 These materials are also marked and the ID of the bulk compound in
50


## Page 51

the relevant experimental crystal structure database is provided.
To illustrate how all the materials are distributed in terms of stability, we show the energy
above the convex hull plotted against ˜ω2
min in Figure 19. It can be seen that the structures
naturally sort themselves into two clusters according to the dynamic stability. The points
have been colored according to the three levels for dynamic stability introduced in section
2.4. The lower panel shows the distribution of the materials in the grey region on a linear
scale. While most of the experimentally known materials (red and black dots) have high
dynamic stability, a signiﬁcant part of them fall into the medium stability category. The
marginal distributions on the plot show that the more dynamically stable materials are also
more thermodynamically stable. The mean energy above the convex hull is 0.12 eV for the
materials with high dynamical stability, while it is 0.25 eV for the others.
In Table 9 we show the key properties of a selected set of stable materials, distributed
across a variety of diﬀerent crystal structure prototypes. To our knowledge, these materials
are not experimentally known, and they are therefore promising candidates further study
and experimental synthesis.
51


## Page 52

Table 8: Overview of the materials currently in the C2DB. The table shows the
number of compounds listed by their crystal structure prototype and selected
properties. Egap > 0 and “direct gap” refer to the PBE values, “high stability”
refers to the stability scale deﬁned in Section 2.4.1, and the last three columns
refer to the magnetic state, see Section 2.1. In this overview, separate magnetic
phases of the same structure are considered diﬀerent materials.
Number of materials
Prototype
Symmetry
Total
Egap > 0
Direct gap
High stability
NM
FM
AFM
C
P6/mmm
4
4
3
1
4
0
0
CH
P3m1
8
7
6
1
8
0
0
CH2Si
P3m1
2
2
2
1
2
0
0
BN
P3m2
10
9
5
1
10
0
0
GaS
P3m2
125
34
95
8
100
18
7
FeSe
P4/nmm
103
13
90
26
74
18
11
GeSe
P3m1
20
19
5
6
20
0
0
PbSe
P4/mmm
44
6
38
1
33
8
3
P
Pmna
9
9
0
1
9
0
0
MoS2
P3m2
241
85
176
53
156
85
0
CdI2
P3m1
315
95
231
90
218
80
17
WTe2
P21/m
75
29
48
34
57
13
5
FeOCl
Pmmn
443
92
385
65
328
63
52
MoSSe
P3m1
9
6
6
5
8
1
0
C3N
P6/mmm
25
1
24
0
25
0
0
YBr3
P6/mmm
57
11
51
0
21
24
12
TiCl3
P32m
69
35
51
2
32
23
14
BiI3
P3m1
123
69
66
15
48
54
21
TiS3
Pmmn
34
8
28
5
31
2
1
MnTe3
P21/m
29
3
27
1
22
4
3
Cr3WS8
Pmm2
35
34
18
8
35
0
0
CrWS4
Pmm2
18
17
7
8
18
0
0
Ti2CO2
P3m1
28
8
20
12
19
6
3
Ti2CH2O2
P3m1
13
3
12
3
10
2
1
Ti3C2
P3m2
12
0
12
0
7
5
0
Ti3C2O2
P3m2
26
0
26
0
20
6
0
Ti3C2H2O2
P3m2
14
0
14
0
10
4
0
PbA2I4
P1
27
27
27
0
27
0
0
Sum
1918
626
151
347
1352
416
150
52


## Page 53

Table 9: Key properties of selected stable materials in the C2DB, which have
not been previously synthesised.
The calculated properties are the magnetic
state, formation energy, energy above the convex hull, work function, PBE gap
and the nature of the gap (direct or indirect).
Prototype
Formula
Magnetic
state
∆H
(eV)
∆Hhull
(eV)
Φ
(eV)
PBE gap
(eV)
Direct
gap
BiI3
VI3
FM
−0.51
−0.15
5.3
CoCl3
NM
−0.65
−0.21
1.13
No
CoBr3
NM
−0.41
−0.16
0.96
No
CoI3
NM
−0.14
−0.14
0.53
No
CdI2
FeO2
FM
−1.14
−0.36
7.31
MnSe2
FM
−0.47
−0.18
5.09
MnS2
FM
−0.57
−0.12
5.74
PdO2
NM
−0.40
−0.08
1.38
No
CaBr2
NM
−2.09
−0.02
4.86
No
FeOCl
RhClO
NM
−0.65
−0.18
5.49
NiClO
AFM
−0.64
−0.17
6.32
NiBrO
AFM
−0.52
−0.16
5.78
ScIS
NM
−1.68
−0.14
1.66
Yes
FeSe
CoSe
FM
−0.27
0.02
4.22
RuS
NM
−0.38
0.05
4.72
MnSe
AFM
−0.50
−0.20
0.90
No
MnS
AFM
−0.64
−0.19
0.78
No
GaS
AlSe
NM
−0.72
−0.02
2.00
No
AlS
NM
−0.89
0.00
2.09
No
GeSe
GeSe
NM
−0.19
0.04
2.22
No
GeS
NM
−0.22
0.05
2.45
No
GeTe
NM
−0.01
0.09
1.47
No
SnSe
NM
−0.33
0.10
2.15
No
MoS2
VS2
FM
−0.88
−0.02
5.95
ScBr2
FM
−1.59
−0.40
0.16
No
YBr2
FM
−1.73
−0.23
0.34
No
FeCl2
FM
−0.67
−0.16
0.35
Yes
TiBr2
NM
−1.14
−0.04
0.76
No
ZrBr2
NM
−1.34
−0.04
0.83
No
Ti2CO2
Zr2CF2
NM
−2.36
−0.08
3.92
Hf2CF2
NM
−2.26
0.03
3.62
Y2CF2
NM
−2.50
−0.17
1.12
No
WTe2
NbI2
NM
−0.37
0.04
3.01
HfBr2
NM
−1.16
−0.18
0.85
No
OsSe2
NM
−0.17
0.00
0.57
No
53


## Page 54

High dynamic stability
Exp. known monolayer
Medium dynamic stability
Exp. known layered bulk
Low dynamic stability
−1.0
−0.5
0.0
0.5
1.0
10−20
10−16
10−12
10−8
10−4
100
−˜ω2
min [eV/˚A
2]
More stable
More stable
−1.0
−0.5
0.0
0.5
1.0
∆Hhull [eV/atom]
0
5
10
15
−˜ω2
min [eV/˚A
2]
Figure 19: The dynamic stability of the candidate materials as a function of the energy above
the convex hull on a log scale (top), and a linear scale (bottom). Experimentally synthesised
monolayers are circled in black, while the known layered 3D structures are marked in red.
The three diﬀerent dynamic stability levels are indicated both by the horizontal dashed lines
and the color of the points. The upper panel shows the marginal distribution of the energy
over the convex hull for the points in each of the three stability levels..
54


## Page 55

3.2
Properties: Example applications
In the following sections we present a series of case studies focusing on diﬀerent properties
of 2D materials including band gaps and band alignment, eﬀective masses and mobility,
magnetic order, plasmons and excitons.
The purpose is not to provide an in-depth nor
material speciﬁc analysis, but rather to explore trends and correlations in the data and
showcase some potential applications of the C2DB. Along the way, we report some of the
novel candidate materials revealed by this analysis, which could be interesting to explore
closer in the future.
3.2.1
Band gaps and band alignment
The band gaps and band edge positions of all semiconductors and insulators in the C2DB
have been calculated with the PBE, HSE06, and GLLBSC xc-functionals while G0W0 cal-
culations have been performed for the ∼250 simplest materials. The relatively large size of
these datasets and the high degree of consistency in the way they are generated (all calcula-
tions performed with the same code using same PAW potentials and basis set etc.) provide
a unique opportunity to benchmark the performance of the diﬀerent xc-functionals against
the more accurate G0W0 method.
Table 10: The mean absolute deviation (in eV) of the band gap and band gap
center calculated with three diﬀerent xc-functionals with respect to G0W0 .
PBE
HSE06
GLLBSC
MAD w.r.t. G0W0 (band gap)
1.49
0.82
0.38
MAD w.r.t. G0W0 (gap center)
0.37
0.32
0.76
Figure 20 compares the size and center of the band gaps obtained with the density func-
tionals to the G0W0 results. Relative to G0W0 the PBE functional underestimates the gaps by
45%, i.e. on average the PBE values must be scaled by 1.83 to reproduce the G0W0 results.
The HSE06 band gaps are closer to G0W0 but are nevertheless systematically underestimated
by more than 20%. On the other hand, GLLBSC shows very good performance with band
55


## Page 56

0
2
4
6
8
10
DFT band gap [eV]
0
2
4
6
8
10
G0W0 band gap [eV]
y = 1.83 x
y = 1.29 x
y = 1.02 x
PBE
HSE
GLLBSC
−8
−6
−4
DFT gap center [eV]
−8
−6
−4
G0W0 gap center [eV]
PBE
HSE
GLLBSC
Figure 20: Band gaps (left) and gap centers (right) obtained with diﬀerent DFT functionals
plotted against the G0W0 results.
The band gaps of PBE (blue), HSE06 (orange), and
GLLBSC (green) are ﬁtted linearly to G0W0. For the gap centers the bisector is shown.
gaps only 2% smaller than G0W0 on average. Table 10 shows the mean absolute deviations of
the DFT methods relative to G0W0 . We note that although GLLBSC provides an excellent
description of the G0W0 band gaps on average the spread is sizable with a mean absolute
deviation of 0.4 eV.
We note a handful of outliers in Figure 20 with large HSE band gaps compared to PBE
and G0W0 . For one of these, namely the ferromagnetic CoBr2-CdI2, we obtain the band gaps:
0.30 eV (PBE), 3.41 eV (HSE), and 0.91 eV (G0W0). For validation, we have performed
GPAW and QuantumEspresso calculations with the norm-conserving HGH pseudopotentials
and plane wave cutoﬀup to 1600 eV. The converged band gaps are 0.49 eV (GPAW-HGH-
PBE), 0.51 eV (QE-HGH-PBE) and 3.69 eV (GPAW-HGH-HSE), 3.52 eV (QE-HGH-HSE),
which are all in reasonable agreement with the C2DB results. It should be interesting to
explore the reason for the anomalous behavior of the HSE band gap in these materials.
Compared to the band gaps, the gap centers predicted by PBE and HSE06 are in overall
better agreement with the G0W0 results. This implies that, on average, the G0W0 correction
of the DFT band energies is symmetric on the valence and conduction band. In contrast, the
56


## Page 57

GLLBSC predicts less accurate results for the gap center. This suggests that an accurate
and eﬃcient prediction of absolute band energies is obtained by combining the GLLBSC
band gap with the PBE band gap center.
Next, we consider the band alignment at the interface between diﬀerent 2D materials.
Assuming that the bands line up with a common vacuum level and neglecting hybridisa-
tion/charge transfer at the interface, the band alignment is directly given by the VBM and
CBM positions relative to vacuum.
Type II
ΔE
−3
0
3
band oﬀset PBE [eV]
−3
0
3
band oﬀset G0W0 [eV]
G0W0 Type II
PBE Type III
G0W0 Type III
PBE Type II
−3
0
3
band oﬀset HSE [eV]
−3
0
3
band oﬀset G0W0 [eV]
G0W0 Type II
HSE Type III
G0W0 Type III
HSE Type II
Figure 21: Band alignment at heterobilayers, assuming that the bands line up with a common
vacuum level. The left panel shows the deﬁnition of the band oﬀset ∆E. The middle and
right panels show randomly selected bilayer combinations with Type II (∆E > 0) or Type
III (∆E < 0) band alignment. The black line indicates the bisector, the grey areas indicate
qualitatively wrong DFT band alignments compared to G0W0 .
We focus on pairs of 2D semiconductors for which the G0W0 band alignment is either Type
II (∆E > 0) or Type III (∆E < 0), see Figure 21(left). Out of approximately 10000 bilayers
predicted to have Type II band alignment by G0W0 , the PBE and HSE06 functionals predict
qualitatively wrong band alignment (i.e. Type III) in 44% and 21% cases, respectively (grey
shaded areas). In particular, PBE shows a sizable and systematic underestimation of ∆E as
a direct consequence of the underestimation of the band gaps in both monolayers.
57


## Page 58

3.2.2
Eﬀective masses and mobilities
The carrier mobility relates the drift velocity of electrons or holes to the strength of an
applied electric ﬁeld and is among the most important parameters for a semiconductor
material. In general, the mobility is a sample speciﬁc property which is highly dependent
on the sample purity and geometry, and (for 2D materials) interactions with substrate or
embedding layers. Here we consider the phonon-limited mobility, which can be considered
as the intrinsic mobility of the material, i.e. the mobility that would be measured in the
absence of any sample speciﬁc- or external scattering sources.
The eﬀective masses of the charge carriers have been calculated both with and without
SOC for ∼600 semiconductors. Figure 22 shows the electron mass plotted against the hole
mass. The data points are scattered, with no clear correlation between the electron and hole
masses. Overall, the electron masses are generally slightly smaller than the hole masses.
The mean electron mass is 0.9 m0, while the mean hole mass is 1.1 m0, and 80% of the
electron masses are below m0 while the fraction is only 65% for the holes. This is not too
surprising, since, on average, the energetically lower valence band states are expected to be
more localised and thus less dispersive than the conduction band states.
The right panel of Figure 22 shows the eﬀective mass for electrons and holes plotted as
a function of the inverse band gap. It can be seen that there is no clear correlation between
the two quantities, which is conﬁrmed by calculating the cross-correlation coeﬃcient: for
both electrons and holes it is less than 0.02. This provides empirical evidence against the
linear relation between eﬀective masses and inverse band gaps derived from k·p perturbation
theory. The relation is based on the assumption that the perturbative expansion is dominated
by the conduction and valence band and that the momentum matrix element between these
states, ⟨uc|ˆp|uv⟩, does not vary too much as function of the considered parameter (here
the type of material). These assumptions clearly do not hold across a large set of diﬀerent
semiconductors.
If we focus on a speciﬁc class of materials, e.g.
sulﬁdes in the MoS2
structure indicated by the highlighted symbols, we see a slightly improved trend but still
58


## Page 59

with signiﬁcant ﬂuctuations.
0
2
4
6
8
10
electron mass [m0]
0
2
4
6
hole mass [m0]
0
1
2
0
1
2
0
1
2
3
4
5
1/Egap [eV]
0
1
2
3
4
5
eﬀective mass [m0]
Holes
Electrons
XS2-MoS2 Holes
XS2-MoS2 Electrons
Figure 22: (left) Eﬀective electron mass versus hole mass. On average holes are slightly
heavier than electrons. (right) Eﬀective carrier mass versus the inverse band gap. The linear
correlation between the two quantities, expected from k · p perturbation theory, is seen
not to hold in general. Materials with the formula XS2 in the MoS2 crystal structure are
highlighted.
If one assumes energetically isolated and parabolic bands, the intrinsic mobility limited
only by scattering on acoustic phonons can be estimated from the Takagi formula,153
µi =
e¯h3ρv2
i
kBTm∗
i m∗
dD2
i
.
(17)
Here i refers to the transport direction, ρ is the mass density, vi is the speed of sound in the
material, m∗
i is the carrier mass, m∗
d is the equivalent isotropic density-of-state mass deﬁned
as m∗
d = pm∗
xm∗
y, and Di is the deformation potential. We stress that the simple Takagi
formula is only valid for temperatures high enough that the acoustic phonon population can
be approximated by the Rayleigh-Jeans law, n ≈¯hωac/kBT, but low enough that scattering
on optical phonons can be neglected.
For the semiconductors in the C2DB we have found that the denominator of Equa-
tion (17) varies more than the numerator. Consequently, a small product of deformation
potential and eﬀective mass is expected to correlate with high mobility. Figure 23 shows
the deformation potential plotted against the carrier mass for the valence and conduction
59


## Page 60

bands, respectively. The shaded area corresponds, somewhat arbitrarily, to the region for
which m∗
i Di < m0(1 eV). The 2D semiconductors which have been synthesised in monolayer
form are indicated with orange symbols while those which have been used in ﬁeld eﬀect
transistors are labeled. Consistent with experimental ﬁndings, phosphorene (P) is predicted
to be among the materials with the highest mobility for both electrons and holes.
Interestingly, a number of previously unknown 2D materials lie in this shaded region and
could be candidates for high mobility 2D semiconductors. Table 11 lists a few selected ma-
terials with high intrinsic mobility according to Equation (17), which all have “high” overall
stability (see Section 2.4.1). In the future, it will be interesting to explore the transport
properties of these candidate materials in greater detail.
To give a sense of scale for the numbers in Table 11 to scale, we consider the well stud-
ied example of MoS2. For this material we obtain an electron mobility of 240 cm2V−1s−1
while a full ab-initio calculation found a phonon-limited mobility of 400 cm2V−1s−1 (in good
agreement with experiments on hBN encapsulated MoS2 154), with the acoustic phonon con-
tribution corresponding to a mobility of 1000 cm2V−1s−1.
Similarly, for the series MX2
(M = W, Mo, X = S, Se), we calculate room-temperature electron mobilities between 200
cm2V−1s−1 and 400 cm2V−1s−1, which are all within 50% of the ab-initio results.155 Pre-
sumably, as in the case for MoS2, the good quantitative agreement is partly a result of error
cancellation between an overestimated acoustic phonon scattering and the neglect of optical
phonon scattering. Importantly, however, the relative ordering of the mobilities of the four
MX2 monolayers is correctly predicted by Equation (17) for all but one pair (MoS2 and
WSe2) out of the six pairs. These results illustrate that Equation (17) should only be used
for ”order of magnitude” estimates of the mobility whereas relative comparisons of mobilities
in diﬀerent materials are probably reliable.
60


## Page 61

0.0
0.5
1.0
1.5
2.0
hole mass [m0]
0
2
4
6
8
|DVBM| [eV]
0.0
0.5
1.0
1.5
2.0
electron mass [m0]
0
2
4
6
8
|DCBM| [eV]
Figure 23: The deformation potential of the materials plotted against the carrier eﬀective
masses for the valence band (left) and the conduction band (right). The shaded region in
each panel indicates a region of interest in the search for high-mobility semiconductors. The
2D materials which have previously been synthesised in monolayer form are highlighted in
orange and selected structures for which mobilities have been measured are labelled.
3.2.3
Magnetic properties
Recently, a single layer of CrI3 was reported to exhibit ferromagnetic order with a Curie
temperature of 45 K.12 This comprises the ﬁrst example of a pure 2D material exhibiting
magnetic order and there is currently an intense search for new 2D materials with magnetic
order persisting above room temperature.156–158
For 2D materials, magnetic order will only persist at ﬁnite temperatures in the presence of
magnetic anisotropy (MA). Indeed, by virtue of the Mermin-Wagner theorem, magnetic order
is impossible in 2D unless the rotational symmetry of the spins is broken.159 A ﬁnite MA with
an out of plane easy axis breaks the assumption behind the Mermin-Wagner theorem and
makes magnetic order possible at ﬁnite temperature. The critical temperature for magnetic
order in 2D materials will thus have a strong dependence on the anisotropy.
The MA originates from spin-orbit coupling and is here deﬁned as the energy diﬀerence
between in-plane and out-of-plane orientation of the magnetic moments, see Eq. (4). With
our deﬁnition, a negative MA corresponds to an out-of-plane easy axis. We note that most
of the materials in the C2DB are nearly isotropic in-plane. Consequently, if the easy axis
61


## Page 62

Table 11:
Key transport properties of selected materials with high intrinsic
room-temperature mobility according to Equation (17). All the materials shown
have ”high” overall stability as deﬁned in Section 2.4.1. µhigh is the larger value
of the mobilities in the x or y directions, m∗is the corresponding eﬀective mass,
and µhigh/µlow is the ratio of the mobilities in the two directions.
Carrier
Formula
Prototype
PBE gap
(eV)
µhigh
(cm2V−1s−1)
m∗
(m0)
µhigh
µlow
Holes
PbS2
MoS2
1.39
30000
0.62
1.4
OsO2
WTe2
0.17
23000
0.23
3.0
ZrCl2
MoS2
0.98
12000
0.43
1.1
WSSe
MoSSe
1.40
5500
0.37
1.0
Electrons
PtTe2
CdI2
0.30
9600
0.17
1.3
GaO
GaS
1.56
7200
0.32
1.0
NiS2
CdI2
0.58
6000
0.29
1.5
RuTe2
WTe2
0.64
4600
1.55
8.5
lies in the plane, the spins will exhibit an approximate in-plane rotational symmetry, which
prohibits magnetic order at ﬁnite temperatures. Since spin-orbit coupling becomes large
for heavy elements, we generally expect to ﬁnd larger MA for materials containing heavier
elements. In general the magnitude of the MA is small. For example, for monolayer CrI3
with a Curie temperature of 45 K12 we ﬁnd a MA of −0.85 meV per Cr atom in agreement
with previous calculations.160 Although small, the MA is, however, crucial for magnetic order
to emerge at ﬁnite temperature.
In Figure 24 we show the magnitude of the magnetic anisotropy (red triangles) and the
magnetic moment per metal atom (blue triangles) averaged over all materials with a given
chemical composition. The plot is based on data for around 1200 materials in the medium to
high stability categories (see Table 2) out of which around 350 are magnetic. It is interesting
to note that while the magnetic moment is mainly determined by the metal atom, the MA
depends strongly on the non-metal atom. For example, the halides (Cl, Br, I) generally
exhibit much larger MAs than the chalcogenides (S, Se, Te). Overall, iodine (I) stands out
as the most signiﬁcant element for a large MA while the 3d metals Cr, Mn, Fe and Co are the
most important elements for a large magnetic moment. Since the MA is driven by spin-orbit
62


## Page 63

coupling (SOC) and the spin is mainly located on the metal atom, one would expect a large
MA to correlate with a heavy metal atom. However, it is clear from the ﬁgure that it is not
essential that the spin-carrying metal atom should also host the large SOC. For example,
we ﬁnd large MA for several 3d metal-iodides despite of the relatively weak SOC on the
3d metals. This shows that the MA is governed by a rather complex interplay between the
spins, orbital hybridisation and crystal ﬁeld.
A selection of materials predicted to have high overall stability (see Section 2.4.1) and
high out-of-plane magnetic anisotropy (MA < −0.3 meV/magnetic atom) is listed in Tab. 12.
We ﬁnd several semiconductors with anisotropies comparable to CrI3 and several metals with
even higher values. Looking also at materials with medium stability, we ﬁnd semiconductors
with anisotropies up to 2 meV. It is likely that some of these materials will have Curie
temperatures similar to, or even higher than, CrI3.
Sc
Ti
V
Cr
Mn
Fe
Co
Ni
Cu
Y
Zr
Nb
Mo
Ru
Rh
Pd
Ag
Hf
Ta
W
Re
Os
Pt
Au
Hg
Bi
O
S
Se
Te
F
Cl
Br
I
0
5
10
>15
|MA|mean [meV]
0
0.5
1.0
1.5
2.0
2.5
|µ| mean [µB]
Figure 24: Absolute magnetic anisotropy (red) and magnetic moment (blue) averaged over
all materials in the C2DB with a given composition. The two red boxes highlight the halides
and 3d metals.
In addition to the MA, the critical temperature depends sensitively on the magnetic
exchange couplings. We are presently developing a workﬂow for systematic calculation of
exchange coupling constants, which will allow us to estimate the Curie temperature of all
the magnetically ordered 2D materials. The database contains several 2D materials with
anti-ferromagnetic order. As a note of caution, we mention that the magnetic interactions in
AFM materials typically arise from the super-exchange mechanism, which is poorly described
63


## Page 64

Table 12: Selection of magnetic materials with a negative MA per magnetic
atom. The prototype, the magnetic moment of the magnetic atom, the energy
gap calculated with PBE xc-functional and the magnetic state are also shown.
The experimentally synthesised ferromagnetic monolayer CrI3 is highlighted.
Formula
Prototype
Magnetic
moment
(µB)
PBE gap
(eV)
MA
(meV/atom)
Magnetic
state
∆Hhull
(eV/atom)
OsI3
BiI3
0.9
0.0
−3.17
FM
0.18
CrTe
FeSe
2.6
0.0
−1.85
AFM
0.15
FeCl3
BiI3
1.0
0.01
−1.84
FM
−0.08
FeTe
FeSe
1.9
0.0
−1.06
FM
0.08
MnTe2
CdI2
2.7
0.0
−0.94
FM
−0.10
FeBr3
BiI3
1.0
0.04
−0.88
FM
−0.04
CrI3
BiI3
3.0
0.90
−0.85
FM
−0.21
MnTe
FeSe
3.8
0.69
−0.75
AFM
−0.15
NiO
PbSe
1.1
0.0
−0.53
FM
0.05
FeBrO
FeOCl
1.1
0.0
−0.47
FM
−0.05
CrISe
FeOCl
3.0
0.0
−0.45
FM
−0.10
MnSe2
CdI2
2.8
0.0
−0.40
FM
−0.18
CrIS
FeOCl
3.0
0.35
−0.36
FM
−0.10
MnO2
CdI2
3.0
1.13
−0.36
FM
0.02
VCl3
BiI3
2.0
0.0
−0.35
FM
−0.01
MnSe
FeSe
3.7
0.90
−0.31
AFM
−0.20
CrSe
FeSe
2.0
0.0
−0.31
AFM
0.12
by PBE and requires a careful veriﬁcation using a PBE+U scheme.161
3.2.4
Plasmons
The unique optical properties of 2D materials make them highly interesting as building blocks
for nanophotonic applications.162,163 Many of these applications involve electron rich com-
ponents which can capture, focus, and manipulate light via plasmons or plasmon-polaritons.
Graphene sheets can host plasmons that are long lived, can be easily tuned via electrostatic
or chemical doping, and can be used to conﬁne light to extremely small volumes.164 However,
due to the limited charge carrier density achievable in graphene, its plasmons are limited
to the mid-infrared regime. Here we show that some metallic monolayers support plasmons
with signiﬁcantly higher energies than graphene and could potentially push 2D plasmonics
64


## Page 65

into the optical regime.
0.00
0.05
0.10
0.15
q [˚A−1]
0.0
0.5
1.0
1.5
2.0
energy [eV]
Interband losses
¯hωP
¯hωtrue
P
Andersen et al.
q0 = 2π/ 50 nm
0.0
0.5
1.0
1.5
¯hωP [eV]
0.0
0.2
0.4
0.6
0.8
1.0
1.2
¯hωtrue
P
[eV]
Stability
High
Medium
Low
Figure 25: (left) Plasmon dispersion relations for the unscreened (i.e. intraband) and true
plasmons, ¯hωP and ¯hωtrue
P
, respectively, for NbS2 in the H phase (the MoS2 crystal structure
prototype). This is compared to the full ﬁrst principles calculations of the plasmons in NbS2
by Andersen et al. (data points).165 (right) The in-plane averaged true plasmon frequency
versus the unscreened plasmon frequency for all metals in C2DB at a plasmon wavelength of
λP = 50 nm corresponding to q0 in the left panel. The data points are colored by the overall
stability level as deﬁned in Section 2.4.1, and the straight line corresponds to ¯hωP = ¯hωtrue
P
.
Figure 25 (left) shows the plasmon dispersion for monolayer NbS2 in the MoS2 crystal
structure. The eﬀect of interband transitions on the plasmon is signiﬁcant as can be seen by
comparison to the pure intraband plasmon (¯hωP). The true plasmon energies are obtained
from the poles of the (long wave length limit) dielectric function including the interband
transitions, ϵ = 1+2πq(α2D,intra +α2D,inter), yielding ωtrue
P
= ωP,2D[1+2πqα2D,inter(ωtrue
P
)]−1/2.
For simplicity we ignore the frequency dependence of the interband polarisability, i.e. we
set α2D,inter(ωtrue
P
) ≈α2D,inter(ω = 0), which should be valid for small plasmon energies (far
from the onset of interband transitions). The validity of this approximation is conﬁrmed by
comparing to the full ab initio calculations of Andersen et al. (blue dots) which include the
full q- and ω-dependence.165 The ﬁgure shows that interband screening generally reduces the
plasmon energy and becomes increasingly important for larger q.
Figure 25 (right) shows the in-plane averaged true plasmon energy of all metals in the
65


## Page 66

C2DB plotted against the intraband plasmon energy at a ﬁxed plasmon wavelength of λP =
50 nm (corresponding to q0 at the dashed vertical line in the left panel). For comparison, the
plasmon energy of freestanding graphene at this wavelength and for the highest achievable
doping level (EF = ±0.5 eV relative to the Dirac point) is around 0.4 eV. The data points
are colored according to the overall stability level as deﬁned in Section 2.4.1.
Table 13
shows a selection of the 2D metals with ”high” overall stability (see Section 2.4.1) and large
plasmon frequencies. We brieﬂy note the interesting band structures of the metals in the
FeOCl prototype (not shown) which exhibits band gaps above or below the partially occupied
metallic band(s), which is likely to lead to reduced losses in plasmonic applications.166 A
detailed study of the plasmonic properties of the lead candidate materials will be published
elsewhere. However, from Figure 25 (right) it is already clear that several of the 2D metals
have plasmon energies around 1 eV at λP = 50 nm, which signiﬁcantly exceeds the plasmon
energies in highly doped graphene.
Table 13: Selection of 2D metals with high plasmon energies ωtrue
P
for a plasmon
wavelength of λP = 50 nm.
The interband screening α2D,inter at ω = 0 and the
in-plane averaged 2D plasma frequency ωP,2D, which are required to reproduce
ωtrue
P
, are also reported.
Prototype
Formula
Magnetic
state
ωtrue
P
[eV]
α2D,inter
[˚A]
ωP,2D
[eV˚A]
TiS3
TaSe3
NM
0.99
12.54
12.48
FeOCl
PdClS
NM
0.93
4.13
9.52
FeOCl
NiClS
NM
0.90
5.60
9.66
CdI2
TaS2
NM
0.82
5.59
8.79
FeOCl
ZrIS
NM
0.75
7.68
8.43
CdI2
NbS2
NM
0.73
8.2
8.42
FeOCl
ZrClS
NM
0.73
13.6
9.35
TiS3
TaS3
NM
0.73
34.22
12.44
PbSe
NiO
FM
0.72
2.9
7.16
66


## Page 67

3.2.5
Excitons
Two-dimensional materials generally exhibit pronounced many-body eﬀects due to weak
screening and strong quantum conﬁnement. In particular, exciton binding energies in mono-
layers are typically an order of magnitude larger than in the corresponding layered bulk phase
and it is absolutely crucial to include excitonic eﬀects in order to reproduce experimental
absorption spectra.
The electronic screening is characterised by the in-plane 2D polarisability, see Eq. (12).
For a strictly 2D insulator, the screened Coulomb potential can be written as W 2D(q) =
v2D
c (q)/ϵ2D(q) with ϵ2D(q) = 1 + 2πα2Dq and v2D
c (q) = 2π/q is the 2D Fourier transform
of the Coulomb interaction. The q-dependence of ϵ2D indicates that the screening is non-
local, i.e. it cannot be represented by a q-independent dielectric constant, and that Coulomb
interactions tend to be weakly screened at large distances (small q vectors).142,167,168 This is in
sharp contrast to the case of 3D semiconductors/insulators where screening is most eﬀective
at large distances where its eﬀect can be accounted for by a q-independent dielectric constant.
For a two-band model with isotropic parabolic bands, the excitons can be modeled by a 2D
Hydrogen-like (Mott-Wannier) Hamiltonian where the Coulomb interaction is replaced by
W = 1/ϵr and the electron mass is replaced by a reduced excitonic mass µex derived from
the curvature of conduction and valence bands.
It has previously been shown that the
excitonic Rydberg series of a 2D semiconductor can be accurately reproduced by this model
if the dielectric constant, ϵ, is obtained by averaging ϵ2D(q) over the extent of the exciton in
reciprocal space.169 For the lowest exciton (n = 1), the binding energy can then be expressed
as
EB =
8µex
(1 +
p
1 + 32πα2Dµex/3)2.
(18)
It has furthermore been demonstrated that this expression gives excellent agreement with
a numerical solution of the Mott-Wannier model employing the full q-dependent dielectric
67


## Page 68

function, ϵ2D(q) = 1 + 2πα2Dq, for 51 transition metal dichalcogenides.169 We note that the
previous calculations were based on LDA and we generally ﬁnd that the PBE values for α2D
obtained in the present work are 10-20 % smaller compared with LDA.
In Figure 26, we compare the binding energy of the lowest exciton obtained from BSE-
PBE with G0W0 scissors operator and the Mott-Wannier model Eq.
(18), respectively.
Results are shown for the 194 non-magnetic semiconductors out of the total set of ∼250
materials for which BSE calculations have been performed. We focus on the optically active
zero-momentum excitons and compute the exciton masses by evaluating the curvature of the
band energies at the direct gap, see Section 2.11. For anisotropic materials we average the
heavy and light exciton masses as well as the x and y components of the polarisability, α2D,
to generate input parameters for the isotropic model Eq. (18).
Although a clear correlation with the BSE results is observed, it is also evident that the
Mott-Wannier model can produce signiﬁcant errors. The mean absolute deviation between
BSE and the model is 0.28 eV for all materials and 0.20 eV for the subset of transition metal
dichalcogenides (TMDCs). Furthermore, the Mott-Wannier model seems to overestimate EB
for more strongly bound excitons while the opposite trend is seen for weakly bound excitons.
As explained below these trends are a consequence of systematic errors in the Mott-Wannier
model which can be traced to two distinct sources.
(i) Weak screening: If α2D is small (on the order of 1 ˚A), the exciton becomes strongly
localised and the orbital character of the states comprising the exciton plays a signiﬁcant role.
In general, the Mott-Wannier model tends to overestimate the exciton binding energy in this
case as can be seen from the relatively large deviation of points with model binding energies
> 2.0 eV in Figure 26. The overestimated binding energy results from the homogeneous
electron and hole distributions implicitly assumed in the Mott-Wannier model. In reality,
the short range variation of the electron and hole distributions is determined by the shape
of the conduction and valence band states. In general these will diﬀer leading to a reduced
spatial overlap of the electron and hole and thus a lower Coulomb interaction. For example,
68


## Page 69

SrCl2 in the CdI2 prototype (α2D = 0.68 ˚A) has a BSE binding energy of 2.1 eV and a model
binding energy of 3.4 eV. From the PDOS of this material (see the C2DB webpage) it is
evident that the electron and hole are mainly residing on the Sr and Cl atoms, respectively.
(ii) Breakdown of the parabolic band approximation: Materials with small band gaps
often exhibit hyperbolic rather than parabolic band structures in the vicinity of the band
gap.
This typically happens in materials with small band gaps such as BSb in the BN
prototype. In Figure 26 these materials can be identiﬁed as the cluster of points with model
binding energies < 0.25 eV and BSE binding energies > 0.25 eV. A similar situation occurs
if the conduction and valence bands ﬂatten out away from the band gap region. In both
of these cases, the excitons tend to be delocalised over a larger area in the Brillouin zone
than predicted by the parabolic band approximation of the Mott-Wannier model. Typically,
such delocalisation will result in larger binding energies than predicted by the model. For
example, FeI2 in the CdI2 prototype exhibits shallow band minima in a ring around the
Γ-point and has a BSE binding energy of 1.1 eV and a model binding energy of 0.5 eV
because the model assumes that the exciton will be located in the vicinity of the shallow
minimum (and thus more delocalised in real space). A detailed inspection reveals that such
break down of the parabolic band approximation is responsible for most of the cases where
the model underestimates the binding energy.
Other sources of errors come from contributions to the exciton from higher/lower lying
bands, i.e. break down of the two-band approximation, and anisotropic exciton masses not
explicitly accounted for by Eq. (18).
Based on this comprehensive and unbiased assessment of the Mott-Wannier model, we
conclude that while the model can be useful for understanding trends and qualitative prop-
erties of excitons, its quantitative accuracy is rather limited when applied to a broad set of
materials without any parameter tuning. For quantitative estimates α2D should not be too
small (certainly not less than 2 ˚A) and the the validity of the eﬀective mass approximation
should be carefully checked by inspection of the band structure.
69


## Page 70

0
1
2
3
4
model binding energy [eV]
0
1
2
3
BSE binding energy [eV]
α2D > 2˚A
α2D < 2˚A
TMDCs
0
2
4
6
8
10
direct band gap [eV]
0
1
2
3
BSE binding energy [eV]
BN
AlN
GaN
WS2
MoS2
MoSe2
SnS2
P
PBE
G0W0
y = x/4
Figure 26: (left) Binding energy of the lowest exciton in 194 semiconducting monolayers
calculated from the Bethe-Salpeter Equation (BSE) and the screened 2D Mott-Wannier
model Eq. (18). The colors of the symbols indicate if screening in the material is weak
(α2D < 2˚A).
The transition metal dichalcogenides (TMDCs) are highlighted with black
circles. (right) The exciton binding energy as a function of the direct band gap, with selected
materials labelled.
It has been argued that there should exist a robust and universal scaling between the
exciton binding energy and the quasiparticle band gap of 2D semiconductors, namely EB ≈
Egap/4.170 This scaling relation was deduced empirically based on BSE-GW calculations for
around 20 monolayers and explained from Equation (18) and the relation α2D ∝1/Egap from
k · p perturbation theory. Another work observed a similar trend171 but explained it from
the 1/Egap dependence of the exciton eﬀective mass expected from k·p perturbation theory.
Based on our results we can completely refute the latter explanation (see Figure 22(right)).
In Figure 26(right) we show the exciton binding energy plotted versus the direct PBE and
G0W0 band gaps, respectively. While there is a correlation, it is by no means as clear as
found in Ref. 170.
4
Conclusions and Outlook
The C2DB is an open database with calculated properties of two-dimensional materials. It
currently contains more than 1500 materials distributed over 32 diﬀerent crystal structures.
70


## Page 71

A variety of structural, elastic, thermodynamic, electronic, magnetic and optical properties
are computed following a high-throughput, semi-automated workﬂow employing state of the
art DFT and many-body methods. The C2DB is growing continuously as new structures and
properties are being added; thus the present paper provides a snapshot of the present state
of the database. The C2DB can be browsed online using simple and advanced queries, and
it can be downloaded freely at https://c2db.fysik.dtu.dk/ under a Creative Commons
license.
The materials in the C2DB comprise both experimentally known and not previously
synthesised structures. They have been generated in a systematic fashion by combinatorial
decoration of diﬀerent 2D crystal lattices. The full property workﬂow is performed only for
structures that are found to be dynamically stable and have a negative heat of formation. We
employ a liberal stability criterion in order not to exclude potentially interesting materials
that could be stabilised by external means like substrate interactions or doping even if they
are unstable in freestanding form. As an important and rather unique feature, the C2DB
employs beyond-DFT methods, such as the many-body GW approximation, the random
phase approximation (RPA) and the Bethe-Salpeter Equation (BSE). Such methods are
essential for obtaining quantitatively accurate descriptions of key properties like band gaps
and optical spectra. This is particularly important for 2D materials due the weak dielectric
screening in reduced dimensions, which tends to enhance many-body eﬀects. For maximal
transparency and reproducibility of the data in the C2DB, all relevant parameters have been
provided in this paper. Additionally, all scripts used to generate the data are freely available
for download under a GPL license.
Beyond its obvious use as a look-up table, the C2DB oﬀers access to numerous well
documented, high-quality calculations, making it ideally suited for benchmarking and com-
parison of diﬀerent codes and methodologies. The large set of diﬀerent available properties
makes the C2DB interesting as a playground for exploring structure-property relations and
for applying and advancing machine learning approaches in materials science. Moreover, the
71


## Page 72

C2DB should be useful as a stepping stone towards the development of theoretical models
for more complex 2D structures such as van der Waals heterostructures (see below).
As reported in this work, based on the combinatorial screening approach, we have iden-
tiﬁed a number of new, potentially synthesisable 2D materials with interesting properties
including ferromagnets with large magnetic anisotropy, semiconductors with high intrinsic
carrier mobility, and metals with plasmons in the visible frequency range. These predictions
are all based on the computed properties of the perfect crystalline materials. While the pris-
tine crystal constitutes an important baseline reference it remains an idealised model of any
real material. In the future, it would be interesting to extend the database to monolayers
with adsorbed species and/or point defects. Not only would this allow for a more realistic
assessment of the magnetic and (opto)electronic properties, it would also facilitate the design
and discovery of 2D materials for e.g. battery electrodes and (electro)catalysis.172,173
The C2DB should also be useful as a platform for establishing parametrisations of com-
putationally less expensive methods such as tight-binding models174 and k · p perturbation
theory.130 Such methods are required e.g. for device modeling, description of magnetic ﬁeld
eﬀects, and van der Waals heterostructures. The database already provides band structures,
spin orbit-induced band splittings, and eﬀective masses, which can be directly used to deter-
mine model parameters. It would be straightforward to complement these with momentum
matrix elements at band extrema for modeling of optical properties and construction of full
k · p Hamiltonians. Similarly, the spread functional required as input for the construction
of Wannier functions e.g. by the ASE38 or the Wannier90175 packages, could be easily and
systematically produced. This would enable direct construction of minimal basis set Hamil-
tonians and would allow for the calculation of Born charges and piezoelectric coeﬃcients as
well as certain topological invariants.176 A workﬂow to calculate exchange couplings of mag-
netic 2D materials is currently being developed with the aim of predicting magnetic phase
transitions and critical temperatures.
Of speciﬁc interest is the modeling of the electronic and optical properties of vdW het-
72


## Page 73

erostructures. Due to lattice mismatch or rotational misalignment between stacked 2D layers,
such structures are diﬃcult or even impossible to treat by conventional ab-initio techniques.
Diﬀerent simpliﬁed models have been proposed to describe the electronic bands, including
tight-binding Hamiltonians derived from strained lattice conﬁgurations177 and perturbative
treatments of the interlayer coupling.178 In both cases, the data in the C2DB represents
a good starting point for constructing such models. The eﬀect of dielectric screening in
vdW heterostructures can be incorporated e.g. by the quantum electrostatic heterostructure
(QEH) model179 which computes the dielectric function of the vdW heterostructure from
the polarisabilities of the isolated monolayers. The latter are directly available in the C2DB,
at least in the long wavelength limit.
Finally, it would be relevant to supplement the current optical absorbance spectra by
other types of spectra, such as Raman spectra, infrared absorption or XPS, in order to assist
experimentalists in characterising their synthesised samples. The automatic ﬁrst-principles
calculation of such spectra is, however, not straightforward and will require signiﬁcant com-
putational investments.
5
Acknowledgements
The Center for Nanostructured Graphene is sponsored by the Danish National Research
Foundation, Project DNRF103. The project also received funding from the European Unions
Horizon 2020 research and innovation programme under Grant Agreement No. 676580 with
The Novel Materials Discovery (NOMAD) Laboratory, a European Center of Excellence.
This work was also supported by a research grant (9455) from VILLUM FONDEN. This
project has received funding from the European Research Council (ERC) under the European
Union’s Horizon 2020 research and innovation programme (grant agreement No 773122,
LIMA).
73


## Page 74

References
(1) Ferrari, A. C.; Bonaccorso, F.; Fal´Ko, V.; Novoselov, K. S.; Roche, S.; Bøggild, P.;
Borini, S.; Koppens, F. H.; Palermo, V.; Pugno, N. et al. Science and technol-
ogy roadmap for graphene, related two-dimensional crystals, and hybrid systems.
Nanoscale 2015, 7, 4598–4810.
(2) Bhimanapati, G. R.; Lin, Z.; Meunier, V.; Jung, Y.; Cha, J.; Das, S.; Xiao, D.;
Son, Y.; Strano, M. S.; Cooper, V. R. et al. Recent advances in two-dimensional
materials beyond graphene. Acs Nano 2015, 9, 11509–11539.
(3) Huang, C.; Wu, S.; Sanchez, A. M.; Peters, J. J.; Beanland, R.; Ross, J. S.; Rivera, P.;
Yao, W.; Cobden, D. H.; Xu, X. Lateral heterojunctions within monolayer MoSe2–
WSe2 semiconductors. Nature materials 2014, 13, 1096–1101.
(4) Geim, A. K.; Grigorieva, I. V. Van der Waals heterostructures. Nature 2013, 499,
419–425.
(5) Molle, A.; Goldberger, J.; Houssa, M.; Xu, Y.; Zhang, S.-C.; Akinwande, D. Buckled
two-dimensional Xene sheets. Nature materials 2017,
(6) Bianco, E.; Butler, S.; Jiang, S.; Restrepo, O. D.; Windl, W.; Goldberger, J. E.
Stability and exfoliation of germanane: a germanium graphane analogue. Acs Nano
2013, 7, 4414–4421.
(7) Wang, Q. H.; Kalantar-Zadeh, K.; Kis, A.; Coleman, J. N.; Strano, M. S. Electron-
ics and optoelectronics of two-dimensional transition metal dichalcogenides. Nature
nanotechnology 2012, 7, 699–712.
(8) Naguib, M.; Mashtalir, O.; Carle, J.; Presser, V.; Lu, J.; Hultman, L.; Gogotsi, Y.;
Barsoum, M. W. Two-dimensional transition metal carbides. ACS Nano 2012, 6,
1322–1331.
74


## Page 75

(9) Ci, L.; et al., Atomic layers of hybridized boron nitride and graphene domains. Nature
Materials 2010, 9, 430–435.
(10) Al Balushi, Z. Y.; Wang, K.; Ghosh, R. K.; Vil´a, R. A.; Eichfeld, S. M.; Caldwell, J. D.;
Qin, X.; Lin, Y.-C.; DeSario, P. A.; Stone, G. et al. Two-dimensional gallium nitride
realized via graphene encapsulation. Nature materials 2016, 15, 1166.
(11) Lin, S.-H.; Kuo, J.-L. Towards the ionic limit of two-dimensional materials: mono-
layer alkaline earth and transition metal halides. Physical Chemistry Chemical Physics
2014, 16, 20763–20771.
(12) Huang, B.; Clark, G.; Navarro-Moratalla, E.; Klein, D. R.; Cheng, R.; Seyler, K. L.;
Zhong, D.; Schmidgall, E.; McGuire, M. A.; Cobden, D. H. et al. Layer-dependent
ferromagnetism in a van der Waals crystal down to the monolayer limit. Nature 2017,
546, 270.
(13) J., L. D.; Bin, L.; Jiajun, L.; Aiming, Y.; Ramakrishna, M. H. S. S.; Matthew, G.;
R., R. C. N.; P., D. V. GaS and GaSe Ultrathin Layer Transistors. Advanced Materials
24, 3549–3554.
(14) Hu, P.; Wen, Z.; Wang, L.; Tan, P.; Xiao, K. Synthesis of Few-Layer GaSe Nanosheets
for High Performance Photodetectors. Acs Nano 2012, 6, 5988–5994.
(15) Dou, L.; Wong, A. B.; Yu, Y.; Lai, M.; Kornienko, N.; Eaton, S. W.; Fu, A.; Bis-
chak, C. G.; Ma, J.; Ding, T. et al. Atomically thin two-dimensional organic-inorganic
hybrid perovskites. Science 2015, 349, 1518–1521.
(16) Ashton, M.; Paul, J.; Sinnott, S. B.; Hennig, R. G. Topology-scaling identiﬁcation of
layered solids and stable exfoliated 2D materials. Physical Review Letters 2017, 118,
106101.
75


## Page 76

(17) Cheon, G.; Duerloo, K.-A. N.; Sendek, A. D.; Porter, C.; Chen, Y.; Reed, E. J.
Data mining for new two-and one-dimensional weakly bonded solids and lattice-
commensurate heterostructures. Nano Letters 2017, 17, 1915–1923.
(18) Mounet, N.; Gibertini, M.; Schwaller, P.; Merkys, A.; Castelli, I. E.; Cepel-
lotti, A.;
Pizzi, G.;
Marzari, N. Novel two-dimensional materials from high-
throughput computational exfoliation of experimentally known compounds. arXiv
preprint arXiv:1611.05234 2016,
(19) Choudhary, K.; Kalish, I.; Beams, R.; Tavazza, F. High-throughput Identiﬁcation
and Characterization of Two-dimensional Materials using Density functional theory.
Scientiﬁc Reports 2017, 7, 5179.
(20) Jain, A.; Persson, K. A.; Ceder, G. Research Update: The materials genome initiative:
Data sharing and the impact of collaborative ab initio databases. APL Materials 2016,
4, 053102.
(21) Thygesen, K. S.; Jacobsen, K. W. Making the most of materials computations. Science
2016, 354, 180–181.
(22) Jain, A.; Ong, S. P.; Hautier, G.; Chen, W.; Richards, W. D.; Dacek, S.; Cholia, S.;
Gunter, D.; Skinner, D.; Ceder, G. et al. The Materials Project: A materials genome
approach to accelerating materials innovation. APL Materials 2013, 1, 011002.
(23) Curtarolo, S.; Setyawan, W.; Hart, G. L.; Jahnatek, M.; Chepulskii, R. V.; Tay-
lor, R. H.; Wang, S.; Xue, J.; Yang, K.; Levy, O. et al. AFLOW: an automatic
framework for high-throughput materials discovery. Computational Materials Science
2012, 58, 218–226.
(24) Saal, J. E.; Kirklin, S.; Aykol, M.; Meredig, B.; Wolverton, C. Materials design and
discovery with high-throughput density functional theory: the open quantum materi-
als database (OQMD). Jom 2013, 65, 1501–1509.
76


## Page 77

(25) Kirklin, S.; Saal, J. E.; Meredig, B.; Thompson, A.; Doak, J. W.; Aykol, M.; Ruehl, S.;
Wolverton, C. The Open Quantum Materials Database (OQMD): assessing the accu-
racy of DFT formation energies. Npj Computational Materials 2015, 1, 15010.
(26) http://nomad-repository.eu;https://nomad-coe.eu.
(27) Lejaeghere, K.; Bihlmayer, G.; Bj¨orkman, T.; Blaha, P.; Bl¨ugel, S.; Blum, V.; Cal-
iste, D.; Castelli, I. E.; Clark, S. J.; Dal Corso, A. et al. Reproducibility in density
functional theory calculations of solids. Science 2016, 351, aad3000.
(28) Hautier, G.; Fischer, C. C.; Jain, A.; Mueller, T.; Ceder, G. Finding nature’s miss-
ing ternary oxide compounds using machine learning and density functional theory.
Chemistry of Materials 2010, 22, 3762–3767.
(29) Ghiringhelli, L. M.; Vybiral, J.; Levchenko, S. V.; Draxl, C.; Scheﬄer, M. Big data
of materials science: Critical role of the descriptor. Physical review letters 2015, 114,
105503.
(30) Ward, L.; Wolverton, C. Atomistic calculations and materials informatics: A review.
Current Opinion in Solid State and Materials Science 2017, 21, 167–176.
(31) S¸ahin, H.; Cahangirov, S.; Topsakal, M.; Bekaroglu, E.; Akturk, E.; Senger, R. T.;
Ciraci, S. Monolayer honeycomb structures of group-IV elements and III-V binary
compounds: First-principles calculations. Physical Review B 2009, 80, 155453.
(32) Ciraci, S.; Cahangirov, S. In 2D Materials: Properties and Devices; Avouris, P.,
Heinz, T. F., Low, T., Eds.; Cambridge University Press, 2017; p 472–484.
(33) Ataca, C.; Sahin, H.; Ciraci, S. Stable, single-layer MX2 transition-metal oxides and
dichalcogenides in a honeycomb-like structure. The Journal of Physical Chemistry C
2012, 116, 8983–8999.
77


## Page 78

(34) Leb`egue, S.; Bj¨orkman, T.; Klintenberg, M.; Nieminen, R. M.; Eriksson, O. Two-
dimensional materials from data ﬁltering and ab initio calculations. Physical Review
X 2013, 3, 031002.
(35) Miro, P.; Audiﬀred, M.; Heine, T. An atlas of two-dimensional materials. Chemical
Society Reviews 2014, 43, 6537–6554.
(36) Rasmussen, F. A.; Thygesen, K. S. Computational 2D materials database: Electronic
structure of transition-metal dichalcogenides and oxides. The Journal of Physical
Chemistry C 2015, 119, 13169–13183.
(37) Enkovaara, J. e.; Rostgaard, C.; Mortensen, J. J.; Chen, J.; Du lak, M.; Ferrighi, L.;
Gavnholt, J.; Glinsvad, C.; Haikola, V.; Hansen, H. et al. Electronic structure cal-
culations with GPAW: a real-space implementation of the projectoraugmented-wave
method. Journal of Physics: Condensed Matter 2010, 22, 253202.
(38) Larsen, A.; Mortensen, J.; Blomqvist, J.; Castelli, I.; Christensen, R.; Dulak, M.;
Friis, J.; Groves, M.; Hammer, B.; Hargus, C. et al. The Atomic Simulation Envi-
ronment—A Python library for working with atoms. Journal of Physics: Condensed
Matter 2017,
(39) Cordero, B.; Gomez, V.; Platero-Prats, A. E.; Reves, M.; Echeverria, J.; Cremades, E.;
Barragan, F.; Alvarez, S. Covalent radii revisited. Dalton Trans. 2008, 2832–2838.
(40) Ashton, M.; Paul, J.; Sinnott, S. B.; Hennig, R. G. Topology-Scaling Identiﬁcation
of Layered Solids and Stable Exfoliated 2D Materials. Phys. Rev. Lett. 2017, 118,
106101.
(41) Larsen, P. M. Structural Analysis Algorithms for Nanomaterials. Ph.D. thesis, De-
partment of Physics, DTU, 2017.
78


## Page 79

(42) ¨Oz¸celik, V. O.; Azadani, J. G.; Yang, C.; Koester, S. J.; Low, T. Band alignment of
two-dimensional semiconductors for designing heterostructures with momentum space
matching. Physical Review B 2016, 94, 035125.
(43) Togo, A. Spglib. 2009; https://atztogo.github.io/spglib/.
(44) Pandey, M.; Jacobsen, K. W. Heats of formation of solids with error estimation: The
mBEEF functional with and without ﬁtted reference energies. Phys. Rev. B 2015, 91,
235201.
(45) Stevanovi´c, V.; Lany, S.; Zhang, X.; Zunger, A. Correcting density functional theory
for accurate predictions of compound enthalpies of formation: Fitted elemental-phase
reference energies. Physical Review B 2012, 85, 115104.
(46) Anisimov, V.; Gunnarsson, O. Density-functional calculation of eﬀective Coulomb
interactions in metals. Physical Review B 1991, 43, 7570.
(47) Kuhar, K.; Crovetto, A.; Pandey, M.; Thygesen, K. S.; Seger, B.; Vesborg, P. C. K.;
Hansen, O.; Chorkendorﬀ, I.; Jacobsen, K. W. Sulﬁde perovskites for solar energy con-
version applications: computational screening and synthesis of the selected compound
LaYS3. Energy Environ. Sci. 2017, 10, 2579–2593.
(48) Zhou, Y.; Miao, L.; Wang, P.; Zhu, F.; Jiang, W.; Jiang, S.; Zhang, Y.; Lei, B.;
Chen, X.; Ding, H. et al. Antiferromagnetic Order in Epitaxial FeSe Films on SrTiO
3. Physical Review Letters 2018, 120, 097001.
(49) Alfe, D. PHON: A program to calculate phonons using the small displacement method.
Computer Physics Communications 2009, 180, 2622–2633.
(50) Novoselov, K. S.; Geim, A. K.; Morozov, S. V.; Jiang, D.; Zhang, Y.; Dubonos, S. V.;
Grigorieva, I. V.; Firsov, A. A. Electric ﬁeld eﬀect in atomically thin carbon ﬁlms.
science 2004, 306, 666–669.
79


## Page 80

(51) Sone, J.; Yamagami, T.; Aoki, Y.; Nakatsuji, K.; Hirayama, H. Epitaxial growth of
silicene on ultra-thin Ag (111) ﬁlms. New Journal of Physics 2014, 16, 095004.
(52) D´avila, M.; Xian, L.; Cahangirov, S.; Rubio, A.; Le Lay, G. Germanene: a novel
two-dimensional germanium allotrope akin to graphene and silicene. New Journal of
Physics 2014, 16, 095002.
(53) Li, L.; Yu, Y.; Ye, G. J.; Ge, Q.; Ou, X.; Wu, H.; Feng, D.; Chen, X. H.; Zhang, Y.
Black phosphorus ﬁeld-eﬀect transistors. Nature nanotechnology 2014, 9, 372.
(54) Yang, S.; Li, W.; Ye, C.; Wang, G.; Tian, H.; Zhu, C.; He, P.; Ding, G.; Xie, X.; Liu, Y.
et al. C3N—A 2D Crystalline, Hole-Free, Tunable-Narrow-Bandgap Semiconductor
with Ferromagnetic Properties. Advanced Materials 2017, 29.
(55) Kappera, R.; Voiry, D.; Yalcin, S. E.; Branch, B.; Gupta, G.; Mohite, A. D.;
Chhowalla, M. Phase-engineered low-resistance contacts for ultrathin MoS 2 tran-
sistors. Nature materials 2014, 13, 1128.
(56) Mak, K. F.; Lee, C.; Hone, J.; Shan, J.; Heinz, T. F. Atomically thin MoS 2: a new
direct-gap semiconductor. Physical review letters 2010, 105, 136805.
(57) Tonndorf, P.; Schmidt, R.; B¨ottger, P.; Zhang, X.; B¨orner, J.; Liebig, A.; Albrecht, M.;
Kloc, C.; Gordan, O.; Zahn, D. R. et al. Photoluminescence emission and Raman
response of monolayer MoS 2, MoSe 2, and WSe 2. Optics express 2013, 21, 4908–
4916.
(58) Lu, A.-Y.; Zhu, H.; Xiao, J.; Chuu, C.-P.; Han, Y.; Chiu, M.-H.; Cheng, C.-C.;
Yang, C.-W.; Wei, K.-H.; Yang, Y. et al. Janus monolayers of transition metal dichalco-
genides. Nature nanotechnology 2017, 12, 744.
(59) Naylor, C. H.; Parkin, W. M.; Ping, J.; Gao, Z.; Zhou, Y. R.; Kim, Y.; Streller, F.;
Carpick, R. W.; Rappe, A. M.; Drndic, M. et al. Monolayer single-crystal 1T´-MoTe2
80


## Page 81

grown by chemical vapor deposition exhibits weak antilocalization eﬀect. Nano letters
2016, 16, 4297–4304.
(60) Wang, Y.; Xiao, J.; Zhu, H.; Li, Y.; Alsaid, Y.; Fong, K. Y.; Zhou, Y.; Wang, S.;
Shi, W.; Wang, Y. et al. Structural phase transition in monolayer MoTe 2 driven by
electrostatic doping. Nature 2017, 550, 487.
(61) Okada, M.; Sawazaki, T.; Watanabe, K.; Taniguch, T.; Hibino, H.; Shinohara, H.; Ki-
taura, R. Direct chemical vapor deposition growth of WS2 atomic layers on hexagonal
boron nitride. ACS nano 2014, 8, 8273–8277.
(62) Fei, Z.; Palomaki, T.; Wu, S.; Zhao, W.; Cai, X.; Sun, B.; Nguyen, P.; Finney, J.;
Xu, X.; Cobden, D. H. Edge conduction in monolayer WTe 2. Nature Physics 2017,
13, 677.
(63) Xi, X.; Zhao, L.; Wang, Z.; Berger, H.; Forr´o, L.; Shan, J.; Mak, K. F. Strongly en-
hanced charge-density-wave order in monolayer NbSe 2. Nature nanotechnology 2015,
10, 765.
(64) Wang, X.; Lin, J.; Zhu, Y.; Luo, C.; Suenaga, K.; Cai, C.; Xie, L. Chemical va-
por deposition of trigonal prismatic NbS 2 monolayers and 3R-polytype few-layers.
Nanoscale 2017, 9, 16607–16611.
(65) Zhang, M.; Zhu, Y.; Wang, X.; Feng, Q.; Qiao, S.; Wen, W.; Chen, Y.; Cui, M.;
Zhang, J.; Cai, C. et al. Controlled synthesis of ZrS2 monolayer and few layers on
hexagonal boron nitride. Journal of the American Chemical Society 2015, 137, 7051–
7054.
(66) Ma˜nas-Valero, S.; Garc´ıa-L´opez, V.; Cantarero, A.; Galbiati, M. Raman spectra of
ZrS2 and ZrSe2 from bulk to atomically thin layers. Applied Sciences 2016, 6, 264.
81


## Page 82

(67) Xu, K.; Wang, Z.; Wang, F.; Huang, Y.; Wang, F.; Yin, L.; Jiang, C.; He, J. Ultra-
sensitive Phototransistors Based on Few-Layered HfS2. Advanced Materials 2015, 27,
7881–7887.
(68) Fu, W.; Chen, Y.; Lin, J.; Wang, X.; Zeng, Q.; Zhou, J.; Zheng, L.; Wang, H.; He, Y.;
He, H. et al. Controlled synthesis of atomically thin 1T-TaS2 for tunable charge density
wave phase transitions. Chemistry of Materials 2016, 28, 7613–7618.
(69) Ryu, H.; Chen, Y.; Kim, H.; Tsai, H.-Z.; Tang, S.; Jiang, J.; Liou, F.; Kahn, S.; Jia, C.;
Omrani, A. A. et al. Persistent charge-density-wave order in single-layer TaSe2. Nano
letters 2018,
(70) Zhao, W.; Dong, B.; Guo, Z.; Su, G.; Gao, R.; Wang, W.; Cao, L. Colloidal synthesis
of VSe 2 single-layer nanosheets as novel electrocatalysts for the hydrogen evolution
reaction. Chemical Communications 2016, 52, 9228–9231.
(71) Feng, J.; Sun, X.; Wu, C.; Peng, L.; Lin, C.; Hu, S.; Yang, J.; Xie, Y. Metallic
few-layered VS2 ultrathin nanosheets: high two-dimensional conductivity for in-plane
supercapacitors. Journal of the American Chemical Society 2011, 133, 17832–17838.
(72) Wang, Y.; Li, L.; Yao, W.; Song, S.; Sun, J.; Pan, J.; Ren, X.; Li, C.; Okun-
ishi, E.; Wang, Y.-Q. et al. Monolayer PtSe2, a new semiconducting transition-metal-
dichalcogenide, epitaxially grown by direct selenization of Pt. Nano letters 2015, 15,
4013–4018.
(73) Zhao, Y.; Qiao, J.; Yu, P.; Hu, Z.; Lin, Z.; Lau, S. P.; Liu, Z.; Ji, W.; Chai, Y.
Extraordinarily strong interlayer interaction in 2D layered PtS2. Advanced Materials
2016, 28, 2399–2407.
(74) Wan, C.; Gu, X.; Dang, F.; Itoh, T.; Wang, Y.; Sasaki, H.; Kondo, M.; Koga, K.;
Yabuki, K.; Snyder, G. J. et al. Flexible n-type thermoelectric materials by organic
82


## Page 83

intercalation of layered transition metal dichalcogenide TiS 2. Nature materials 2015,
14, 622.
(75) Shao, Y.; Song, S.; Wu, X.; Qi, J.; Lu, H.; Liu, C.; Zhu, S.; Liu, Z.; Wang, J.; Shi, D.
et al. Epitaxial fabrication of two-dimensional NiSe2 on Ni (111) substrate. Applied
Physics Letters 2017, 111, 113107.
(76) Tongay, S.; Sahin, H.; Ko, C.; Luce, A.; Fan, W.; Liu, K.; Zhou, J.; Huang, Y.-S.;
Ho, C.-H.; Yan, J. et al. Monolayer behaviour in bulk ReS 2 due to electronic and
vibrational decoupling. Nature communications 2014, 5, 3252.
(77) Oyedele, A. D.; Yang, S.; Liang, L.; Puretzky, A. A.; Wang, K.; Zhang, J.; Yu, P.;
Pudasaini, P. R.; Ghosh, A. W.; Liu, Z. et al. PdSe2: Pentagonal Two-Dimensional
Layers with High Air Stability for Electronics. Journal of the American Chemical
Society 2017, 139, 14090–14097.
(78) Zheng, L.; Zhou, J.; Shi, J.; Zeng, Q.; Chen, Y.; Niu, L.; Liu, F.; Yu, T.; Suenaga, K.;
Liu, X. et al. InSe monolayer: synthesis, structure and ultra-high second-harmonic
generation. 2D Materials 2018,
(79) Del Pozo-Zamudio, O.; Schwarz, S.; Sich, M.; Akimov, I.; Bayer, M.; Schoﬁeld, R.;
Chekhovich, E.; Robinson, B.; Kay, N.; Kolosov, O. et al. Photoluminescence of two-
dimensional GaTe and GaSe ﬁlms. 2D Materials 2015, 2, 035010.
(80) Zhou, Y.; Nie, Y.; Liu, Y.; Yan, K.; Hong, J.; Jin, C.; Zhou, Y.; Yin, J.; Liu, Z.;
Peng, H. Epitaxy and photoresponse of two-dimensional GaSe crystals on ﬂexible
transparent mica sheets. Acs Nano 2014, 8, 1485–1490.
(81) Island, J. O.; Buscema, M.; Barawi, M.; Clamagirand, J. M.; Ares, J. R.; S´anchez, C.;
Ferrer, I. J.; Steele, G. A.; van der Zant, H. S.; Castellanos-Gomez, A. Ultrahigh
Photoresponse of Few-Layer TiS3 Nanoribbon Transistors. Advanced Optical Materials
2014, 2, 641–645.
83


## Page 84

(82) Wang, Y.-Q.; Wu, X.; Ge, Y.-F.; Wang, Y.-L.; Guo, H.; Shao, Y.; Lei, T.;
Liu, C.; Wang, J.-O.; Zhu, S.-Y. et al. Tunable Electronic Structures in Wrinkled 2D
Transition-Metal-Trichalcogenide (TMT) HfTe3 Films. Advanced Electronic Materials
2016, 2.
(83) Song, C.-L.; Wang, Y.-L.; Jiang, Y.-P.; Li, Z.; Wang, L.; He, K.; Chen, X.; Ma, X.-C.;
Xue, Q.-K. Molecular-beam epitaxy and robust superconductivity of stoichiometric
FeSe crystalline ﬁlms on bilayer graphene. Physical Review B 2011, 84, 020503.
(84) Liu, H.-J.; Lin, J.-C.; Fang, Y.-W.; Wang, J.-C.; Huang, B.-C.; Gao, X.; Huang, R.;
Dean, P. R.; Hatton, P. D.; Chin, Y.-Y. et al. A Metal–Insulator Transition of
the Buried MnO2 Monolayer in Complex Oxide Heterostructure. Advanced Materi-
als 2016, 28, 9142–9151.
(85) Cai, L.; McClellan, C. J.; Koh, A. L.; Li, H.; Yalon, E.; Pop, E.; Zheng, X. Rapid
ﬂame synthesis of atomically thin MoO3 down to monolayer thickness for eﬀective
hole doping of WSe2. Nano letters 2017, 17, 3854–3861.
(86) Xu, S.; Han, Y.; Chen, X.; Wu, Z.; Wang, L.; Han, T.; Ye, W.; Lu, H.; Long, G.;
Wu, Y. et al. van der Waals epitaxial growth of atomically thin Bi2Se3 and thickness-
dependent topological phase transition. Nano letters 2015, 15, 2645–2651.
(87) Kong, D.; Dang, W.; Cha, J. J.; Li, H.; Meister, S.; Peng, H.; Liu, Z.; Cui, Y. Few-
layer nanoplates of Bi2Se3 and Bi2Te3 with highly tunable chemical potential. Nano
letters 2010, 10, 2245–2250.
(88) Mashtalir, O.; Lukatskaya, M. R.; Zhao, M.-Q.; Barsoum, M. W.; Gogotsi, Y. Amine-
assisted delamination of Nb2C MXene for Li-Ion energy storage devices. Advanced
Materials 2015, 27, 3501–3506.
(89) Liu, F.; Zhou, J.; Wang, S.; Wang, B.; Shen, C.; Wang, L.; Hu, Q.; Huang, Q.;
84


## Page 85

Zhou, A. Preparation of High-Purity V2C MXene and Electrochemical Properties as
Li-Ion Batteries. Journal of The Electrochemical Society 2017, 164, A709–A713.
(90) Lukatskaya, M. R.;
Mashtalir, O.;
Ren, C. E.;
Dall’Agnese, Y.;
Rozier, P.;
Taberna, P. L.; Naguib, M.; Simon, P.; Barsoum, M. W.; Gogotsi, Y. Cation interca-
lation and high volumetric capacitance of two-dimensional titanium carbide. Science
2013, 341, 1502–1505.
(91) Melchior, S. A.; Raju, K.; Ike, I. S.; Erasmus, R. M.; Kabongo, G.; Sigalas, I.;
Iyuke, S. E.; Ozoemena, K. I. High-Voltage Symmetric Supercapacitor Based on 2D
Titanium Carbide (MXene, Ti2CTx)/Carbon Nanosphere Composites in a Neutral
Aqueous Electrolyte. Journal of The Electrochemical Society 2018, 165, A501–A511.
(92) Liu, G.; Li, Z.; Hasan, T.; Chen, X.; Zheng, W.; Feng, W.; Jia, D.; Zhou, Y.; Hu, P.
Vertically aligned two-dimensional SnS 2 nanosheets with a strong photon captur-
ing capability for eﬃcient photoelectrochemical water splitting. Journal of Materials
Chemistry A 2017, 5, 1989–1995.
(93) Li, J.; Guan, X.; Wang, C.; Cheng, H.-C.; Ai, R.; Yao, K.; Chen, P.; Zhang, Z.;
Duan, X.; Duan, X. Synthesis of 2D Layered BiI3 Nanoplates, BiI3/WSe2van der
Waals Heterostructures and Their Electronic, Optoelectronic Properties. Small 2017,
13.
(94) Elias, D. C.; Nair, R. R.; Mohiuddin, T.; Morozov, S.; Blake, P.; Halsall, M.; Fer-
rari, A.; Boukhvalov, D.; Katsnelson, M.; Geim, A. et al. Control of graphene´s proper-
ties by reversible hydrogenation: evidence for graphane. Science 2009, 323, 610–613.
(95) Nair, R. R.; Ren, W.; Jalil, R.; Riaz, I.; Kravets, V. G.; Britnell, L.; Blake, P.;
Schedin, F.; Mayorov, A. S.; Yuan, S. et al. Fluorographene: A two-dimensional coun-
terpart of Teﬂon. small 2010, 6, 2877–2884.
85


## Page 86

(96) Wang, L.; Kutana, A.; Zou, X.; Yakobson, B. I. Electro-mechanical anisotropy of
phosphorene. Nanoscale 2015, 7, 9746–9751.
(97) Wang, X.; Wang, D. S.; Ruqian, W.; Freeman, A. J. Validity of the force theorem for
magnetocrystalline anisotropy. J. Magn. Magn. Mater. 1996, 159, 337–341.
(98) Olsen, T. Designing in-plane heterostructures of quantum spin Hall insulators from
ﬁrst principles: 1 T´- MoS 2 with adsorbates. Physical Review B 2016, 94, 235106.
(99) MacDonald, A. H.; Vosko, S. H.; Coleridge, P. T. Extensions of the tetrahedron method
for evaluating spectral properties of solids. Journal of Physics C: Solid State Physics
1979, 12, 2991–3002.
(100) Heyd, J.; Scuseria, G. E.; Ernzerhof, M. Hybrid functionals based on a screened
Coulomb potential. The Journal of Chemical Physics 2003, 118, 8207–8215.
(101) Ko´smider, K.; Fern´andez-Rossier, J. Electronic properties of the MoS 2-WS 2 hetero-
junction. Physical Review B 2013, 87, 075451.
(102) Kang, J.; Tongay, S.; Zhou, J.; Li, J.; Wu, J. Band oﬀsets and heterostructures of
two-dimensional semiconductors. Applied Physics Letters 2013, 102, 012111.
(103) Kuisma, M.; Ojanen, J.; Enkovaara, J.; Rantala, T. T. Kohn-Sham Potential with
Discontinuity for Band Gap Materials. Phys. Rev. B 2010, 82, 115106.
(104) Castelli, I. E.; Olsen, T.; Datta, S.; Landis, D. D.; Dahl, S.; Thygesen, K. S.; Jacob-
sen, K. W. Computational screening of perovskite metal oxides for optimal solar light
capture. Energy & Environmental Science 2012, 5, 5814–5819.
(105) Baerends, E. From the Kohn–Sham band gap to the fundamental gap in solids. An
integer electron approach. Physical Chemistry Chemical Physics 2017, 19, 15639–
15656.
86


## Page 87

(106) H¨user, F.; Olsen, T.; Thygesen, K. S. Quasiparticle GW calculations for solids,
molecules, and two-dimensional materials. Phys. Rev. B 2013, 87, 235132.
(107) Rasmussen, F. A.; Schmidt, P. S.; Winther, K. T.; Thygesen, K. S. Eﬃcient many-body
calculations for two-dimensional materials using exact limits for the screened potential:
Band gaps of MoS2, h-BN, and phosphorene. Phys. Rev. B 2016, 94, 155406.
(108) Tiago, M. L.; Ismail-Beigi, S.; Louie, S. G. Eﬀect of semicore orbitals on the electronic
band gaps of Si, Ge, and GaAs within the GW approximation. Phys. Rev. B 2004,
69, 125212.
(109) Klimeˇs, J.; Kaltak, M.; Kresse, G. Predictive GW calculations using plane waves and
pseudopotentials. Phys. Rev. B 2014, 90, 075125.
(110) Sundararaman, R.; Arias, T. A. Regularization of the Coulomb singularity in exact
exchange by Wigner-Seitz truncated interactions: Towards chemical accuracy in non-
trivial systems. Phys. Rev. B 2013, 87, 165122.
(111) Ismail-Beigi, S. Truncation of periodic image interactions for conﬁned systems. Phys.
Rev. B 2006, 73, 233103.
(112) Rozzi, C. A.; Varsano, D.; Marini, A.; Gross, E. K. U.; Rubio, A. Exact Coulomb
cutoﬀtechnique for supercell calculations. Phys. Rev. B 2006, 73, 205119.
(113) Lee, J.; Huang, J.; Sumpter, B. G.; Yoon, M. Strain-engineered optoelectronic proper-
ties of 2D transition metal dichalcogenide lateral heterostructures. 2D Materials 2017,
4, 021016.
(114) Ramasubramaniam, A. Large excitonic eﬀects in monolayers of molybdenum and tung-
sten dichalcogenides. Phys. Rev. B 2012, 86, 115409.
(115) Cheiwchanchamnangij, T.; Lambrecht, W. R. L. Quasiparticle band structure calcu-
lation of monolayer, bilayer, and bulk MoS2. Phys. Rev. B 2012, 85, 205302.
87


## Page 88

(116) Komsa, H.-P.; Krasheninnikov, A. V. Eﬀects of conﬁnement and environment on the
electronic structure and exciton binding energy of MoS2 from ﬁrst principles. Phys.
Rev. B 2012, 86, 241201.
(117) Molina-S´anchez, A.; Sangalli, D.; Hummer, K.; Marini, A.; Wirtz, L. Eﬀect of spin-
orbit interaction on the optical spectra of single-layer, double-layer, and bulk MoS2.
Phys. Rev. B 2013, 88, 045412.
(118) Shi, H.; Pan, H.; Zhang, Y.-W.; Yakobson, B. I. Quasiparticle band structures and
optical properties of strained monolayer MoS2 and WS2. Phys. Rev. B 2013, 87,
155304.
(119) Conley, H. J.; Wang, B.; Ziegler, J. I.; Haglund, R. F.; Pantelides, S. T.; Bolotin, K. I.
Bandgap Engineering of Strained Monolayer and Bilayer MoS2. Nano Lett. 2013, 13,
3626–3630.
(120) H¨user, F.; Olsen, T.; Thygesen, K. S. How dielectric screening in two-dimensional crys-
tals aﬀects the convergence of excited-state calculations: Monolayer MoS 2. Physical
Review B 2013, 88, 245309.
(121) Qiu, D. Y.; Felipe, H.; Louie, S. G. Screening and many-body eﬀects in two-
dimensional crystals: Monolayer MoS 2. Physical Review B 2016, 93, 235435.
(122) Shishkin, M.; Kresse, G. Self-consistent G W calculations for semiconductors and
insulators. Physical Review B 2007, 75, 235102.
(123) Schmidt, P. S.; Patrick, C. E.; Thygesen, K. S. Simple vertex correction improves G
W band energies of bulk and two-dimensional crystals. Physical Review B 2017, 96,
205206.
(124) Shishkin, M.; Marsman, M.; Kresse, G. Accurate quasiparticle spectra from self-
88


## Page 89

consistent GW calculations with vertex corrections. Physical review letters 2007, 99,
246403.
(125) Wang, X.; Jones, A. M.; Seyler, K. L.; Tran, V.; Jia, Y.; Zhao, H.; Wang, H.; Yang, L.;
Xu, X.; Xia, F. Highly anisotropic and robust excitons in monolayer black phosphorus.
Nature nanotechnology 2015, 10, 517.
(126) Klimeˇs, J.; Kaltak, M.; Kresse, G. Predictive G W calculations using plane waves and
pseudopotentials. Physical Review B 2014, 90, 075125.
(127) Klots, A.; Newaz, A.; Wang, B.; Prasai, D.; Krzyzanowska, H.; Lin, J.; Caudel, D.;
Ghimire, N.; Yan, J.; Ivanov, B. et al. Probing excitonic states in suspended two-
dimensional semiconductors by photocurrent spectroscopy. Scientiﬁc reports 2014,
4.
(128) Ugeda, M. M.; Bradley, A. J.; Shi, S.-F.; Felipe, H.; Zhang, Y.; Qiu, D. Y.; Ruan, W.;
Mo, S.-K.; Hussain, Z.; Shen, Z.-X. et al. Giant bandgap renormalization and excitonic
eﬀects in a monolayer transition metal dichalcogenide semiconductor. Nature materials
2014, 13, 1091.
(129) Hill, H. M.; Rigosi, A. F.; Rim, K. T.; Flynn, G. W.; Heinz, T. F. Band alignment
in MoS2/WS2 transition metal dichalcogenide heterostructures probed by scanning
tunneling microscopy and spectroscopy. Nano letters 2016, 16, 4831–4837.
(130) Kormanyos, A.; Burkard, G.; Gmitra, M.; Fabian, J.; Zolyomi, V.; Drummond, N. D.;
Fal´ko, V. k.p theory for two-dimensional transition metal dichalcogenide semiconduc-
tors. 2d Materials 2015, 2, 022001.
(131) Van De Walle, C.; Martin, R. Absolute Deformation Potentials - Formulation and ab
initio Calculations for Semiconductors. Physical Review Letters 1989, 62, 2028–2031.
89


## Page 90

(132) Resta, R.; Colombo, L.; Baroni, S. Absolute Deformation Potentials in Semiconduc-
tors. Physical Review B 1990, 41, 12358–12361.
(133) Wiktor, J.; Pasquarello, A. Absolute deformation potentials of two-dimensional ma-
terials. Phys. Rev. B 2016, 94, 245411.
(134) Marques, M.; Ullrich, C.; Nogueira, F.; Rubio, A.; Gross, E. Time-Dependent Density
Functional Theory. 2006,
(135) Hybertsen, M. S.; Louie, S. G. Ab initio static dielectric matrices from the density-
functional approach. I. Formulation and application to semiconductors and insulators.
Phys. Rev. B 1987, 35, 5585–5601.
(136) Yan, J.; Mortensen, J. J.; Jacobsen, K. W.; Thygesen, K. S. Linear density response
function in the projector augmented wave method: Applications to solids, surfaces,
and interfaces. Phys. Rev. B 2011, 83, 245122.
(137) Rozzi, C. A.; Varsano, D.; Marini, A.; Gross, E. K. U.; Rubio, A. Exact Coulomb
cutoﬀtechnique for supercell calculations. Phys. Rev. B 2006, 73, 205119.
(138) H¨user, F.; Olsen, T.; Thygesen, K. S. Quasiparticle GW calculations for solids,
molecules, and two-dimensional materials. Phys. Rev. B 2013, 87, 235132.
(139) Onida, G.; Reining, L.; Rubio, A. Electronic excitations: density-functional versus
many-body Green´s-function approaches. Rev. Mod. Phys. 2002, 74, 601–659.
(140) Sander, T.; Maggio, E.; Kresse, G. Beyond the Tamm-Dancoﬀapproximation for
extended systems using exact diagonalization. Physical Review B 2015, 92, 045209.
(141) Mak, K. F.; Lee, C.; Hone, J.; Shan, J.; Heinz, T. F. Atomically thin MoS2: A new
direct-gap semiconductor. Phys. Rev. Lett. 2010, 105, 2–5.
90


## Page 91

(142) H¨user, F.; Olsen, T.; Thygesen, K. S. How dielectric screening in two-dimensional
crystals aﬀects the convergence of excited-state calculations: Monolayer MoS2. Phys.
Rev. B 2013, 88, 245309.
(143) Latini, S.; Olsen, T.; Thygesen, K. S. Excitons in van der Waals heterostructures: The
important role of dielectric screening. Phys. Rev. B 2015, 92, 245123.
(144) Da Jornada, F. H.; Qiu, D. Y.; Louie, S. G. Nonuniform sampling schemes of the
Brillouin zone for many-electron perturbation-theory calculations in reduced dimen-
sionality. Physical Review B 2017, 95.
(145) Drueppel, M.; Deilmann, T.; Krueger, P.; Rohlﬁng, M. Diversity of trion states and
substrate eﬀects in the optical properties of an MoS¡sub¿2¡/sub¿ monolayer. Nature
Communications 2017, 8, 2117.
(146) Mouri, S.; Zhang, W.; Kozawa, D.; Miyauchi, Y.; Eda, G.; Matsuda, K. Thermal
dissociation of inter-layer excitons in MoS ¡sub¿2¡/sub¿ /MoSe ¡sub¿2¡/sub¿ hetero-
bilayers. Nanoscale 2017, 9, 6674–6679.
(147) Chen, H.; Wen, X.; Zhang, J.; Wu, T.; Gong, Y.; Zhang, X.; Yuan, J.; Yi, C.; Lou, J.;
Ajayan, P. M. et al. Ultrafast formation of interlayer hot excitons in atomically thin
MoS 2 /WS 2 heterostructures. Nat. Commun. 2016, 7, 1–8.
(148) Fang, H.; Battaglia, C.; Carraro, C.; Nemsak, S.; Ozdol, B.; Kang, J. S.; Bechtel, H. A.;
Desai, S. B.; Kronast, F.; Unal, A. A. et al. Strong interlayer coupling in van der
Waals heterostructures built from single-layer chalcogenides. Proc. Natl. Acad. Sci.
2014, 111, 6198–6202.
(149) Wilson, N. R.; Nguyen, P. V.; Seyler, K.; Rivera, P.; Marsden, A. J.; Laker, Z. P.;
Constantinescu, G. C.; Kandyba, V.; Barinov, A.; Hine, N. D. et al. Determination of
band oﬀsets, hybridization, and exciton binding in 2D semiconductor heterostructures.
Sci. Adv. 2017, 3, e1601832.
91


## Page 92

(150) Ceballos, F.; Bellus, M. Z.; Chiu, H.-Y.; Zhao, H. Probing charge transfer excitons in
a MoSe2-WS2 van der Waals heterostructure. Nanoscale 2015, 7, 17523–17528.
(151) Liu, H.; Neal, A. T.; Zhu, Z.; Luo, Z.; Xu, X.; Tom´anek, D.; Ye, P. D. Phosphorene:
An unexplored 2D semiconductor with a high hole mobility. ACS Nano 2014, 8,
4033–4041.
(152) Yang, J.; Xu, R.; Pei, J.; Myint, Y. W.; Wang, F.; Wang, Z.; Zhang, S.; Yu, Z.; Lu, Y.
Optical tuning of exciton and trion emissions in monolayer phosphorene. Light Sci.
Appl. 2015, 4, 1–7.
(153) Takagi, S.; Toriumi, A.; Iwase, M. On the universality of inversion layer mobility in
Si MOSFET’s: Part I-eﬀects of substrate impurity concentration. IEEE Transactions
on Electron Devices 1994, 41, 2357–2362.
(154) Cui, X.; Lee, G.-H.; Kim, Y. D.; Arefe, G.; Huang, P. Y.; Lee, C.-H.; Chenet, D. A.;
Zhang, X.; Wang, L.; Ye, F. et al. Multi-terminal transport measurements of MoS2
using a van der Waals heterostructure device platform. Nature nanotechnology 2015,
10, 534–540.
(155) Jin, Z.; Li, X.; Mullen, J. T.; Kim, K. W. Intrinsic transport properties of electrons and
holes in monolayer transition-metal dichalcogenides. Phys. Rev. B 2014, 90, 045422.
(156) Gong, C.; Li, L.; Li, Z.; Ji, H.; Stern, A.; Xia, Y.; Cao, T.; Bao, W.; Wang, C.;
Wang, Y. et al. Discovery of intrinsic ferromagnetism in two-dimensional van der
Waals crystals. Nature 2017, 546, 265–269.
(157) Strong room-temperature ferromagnetism in VSe2 monolayers on van der Waals sub-
strates. Nat. Nanotechnol. 2018, 13, 289–293.
(158) Huang, C.; Du, Y.; Wu, H.; Xiang, H.; Deng, K.; Kan, E. Prediction of Intrinsic
92


## Page 93

Ferromagnetic Ferroelectricity in a Transition-Metal Halide Monolayer. Phys. Rev.
Lett. 2018, 120, 147601.
(159) Mermin, N. D.; Wagner, H. Absence of Ferromagnetism or Antiferromagnetism in One-
or Two-Dimensional Isotropic Heisenberg Models. Physical Review Letters 1966, 17,
1133–1136.
(160) Lado, J. L.; Fern´andez-Rossier, J. On the origin of magnetic anisotropy in two dimen-
sional CrI3. 2017,
(161) Olsen, T. Assessing the performance of the random phase approximation for exchange
and superexchange coupling constants in magnetic crystalline solids. Phys. Rev. B
2017, 96, 125143.
(162) Low, T.; Chaves, A.; Caldwell, J. D.; Kumar, A.; Fang, N. X.; Avouris, P.; Heinz, T. F.;
Guinea, F.; Martin-Moreno, L.; Koppens, F. Polaritons in layered two-dimensional
materials. Nature materials 2017, 16, 182.
(163) Gjerding, M. N.; Petersen, R.; Pedersen, T.; Mortensen, N. A.; Thygesen, K. S. Lay-
ered van der Waals crystals with hyperbolic light dispersion. Nature communications
2017, 8, 320.
(164) Chen, J.; Badioli, M.; Alonso-Gonz´alez, P.; Thongrattanasiri, S.; Huth, F.; Os-
mond, J.; Spasenovi´c, M.; Centeno, A.; Pesquera, A.; Godignon, P. et al. Optical
nano-imaging of gate-tunable graphene plasmons. Nature 2012, 487, 77.
(165) Andersen, K.; Thygesen, K. S. Plasmons in metallic monolayer and bilayer transition
metal dichalcogenides. Physical Review B 2013, 88, 155128.
(166) Gjerding, M. N.; Pandey, M.; Thygesen, K. S. Band structure engineered layered
metals for low-loss plasmonics. Nature communications 2017, 8, 15133.
93


## Page 94

(167) Cudazzo, P.; Tokatly, I. V.; Rubio, A. Dielectric screening in two-dimensional insula-
tors: Implications for excitonic and impurity states in graphane. Phys. Rev. B 2011,
84, 085406.
(168) Chernikov, A.; Berkelbach, T. C.; Hill, H. M.; Rigosi, A.; Li, Y.; Aslan, O. B.; Reich-
man, D. R.; Hybertsen, M. S.; Heinz, T. F. Exciton binding energy and nonhydrogenic
Rydberg series in monolayer WS 2. Physical review letters 2014, 113, 076802.
(169) Olsen, T.; Latini, S.; Rasmussen, F.; Thygesen, K. S. Simple Screened Hydrogen Model
of Excitons in Two-Dimensional Materials. Physical review letters 2016, 116, 056401.
(170) Jiang, Z.; Liu, Z.; Li, Y.; Duan, W. Scaling Universality between Band Gap and
Exciton Binding Energy of Two-Dimensional Semiconductors. Phys. Rev. Lett. 2017,
118, 266401.
(171) Choi, J.-H.; Cui, P.; Lan, H.; Zhang, Z. Linear Scaling of the Exciton Binding Energy
versus the Band Gap of Two-Dimensional Materials. Phys. Rev. Lett. 2015, 115,
066403.
(172) Seh, Z. W.; Fredrickson, K. D.; Anasori, B.; Kibsgaard, J.; Strickler, A. L.;
Lukatskaya, M. R.; Gogotsi, Y.; Jaramillo, T. F.; Vojvodic, A. Two-dimensional
molybdenum carbide (MXene) as an eﬃcient electrocatalyst for hydrogen evolution.
ACS Energy Letters 2016, 1, 589–594.
(173) Xie, J.; Zhang, H.; Li, S.; Wang, R.; Sun, X.; Zhou, M.; Zhou, J.; Lou, X. W. D.;
Xie, Y. Defect-rich MoS2 ultrathin nanosheets with additional active edge sites for
enhanced electrocatalytic hydrogen evolution. Advanced materials 2013, 25, 5807–
5813.
(174) Ridolﬁ, E.; Le, D.; Rahman, T.; Mucciolo, E.; Lewenkopf, C. A tight-binding model
for MoS2 monolayers. Journal of Physics: Condensed Matter 2015, 27, 365501.
94


## Page 95

(175) Mostoﬁ, A. A.; Yates, J. R.; Lee, Y.-S.; Souza, I.; Vanderbilt, D.; Marzari, N. wan-
nier90: A tool for obtaining maximally-localised Wannier functions. Computer physics
communications 2008, 178, 685–699.
(176) Taherinejad, M.; Garrity, K. F.; Vanderbilt, D. Wannier center sheets in topological
insulators. Physical Review B 2014, 89, 115102.
(177) Bokdam, M.; Amlaki, T.; Brocks, G.; Kelly, P. J. Band gaps in incommensurable
graphene on hexagonal boron nitride. Physical Review B 2014, 89, 201404.
(178) Tritsaris, G. A.; Shirodkar, S. N.; Kaxiras, E.; Cazeaux, P.; Luskin, M.; Plech´aˇc, P.;
Canc`es, E. Perturbation theory for weakly coupled two-dimensional layers. Journal of
Materials Research 2016, 31, 959–966.
(179) Andersen, K.; Latini, S.; Thygesen, K. S. Dielectric genome of van der Waals het-
erostructures. Nano letters 2015, 15, 4616–4621.
95
