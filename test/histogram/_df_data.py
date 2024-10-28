pdf1_t1 = """Factor,,Levels,,,
Complete name,Coded name,Range,−1,0,1
Temperature (°C),x1,25–35,25,30,35
pH,x2,4–8,4,6,8
Initial dye concen￾tration (mg L−1),x3,4–8,4,6,8
Mesh size,x4,50–150,50,100,150
"""

# needs merging
pdf1_t5 = """Adsorbent(s),Adsorbent dosage,Removal percentage,Reference
,(g/L),,
HCMM,1,77.24–95.14,This work
Activated carbon from Rumex abyssinicus plant,0.2–0.6,82.16–99.96,Fito et al. (2023)
Barley straw and corn stalks modifed by citric acid,6–14,48–97,Soldatkina & Yanar (2023)
Activated carbon from Scrap Tire,2.5,89.18–90.48,Kassahun et al. (2022)
Barley Bran and Enset Midrib Leaf,2.5,96–98,Mekuria et al. (2022)
Raspberry (Rubus idaeus) leaves powder,1–5,30–44,Mosoarca et al. (2022)
Activated carbon from grape leaves waste,0.25–12.25,0–97.4,Mousavi et al. (2022a)
Activated carbon from grape wood wastes,0.25–12.25,0–95.66,Mousavi et al. (2022b)
Black tea wastes,13.3,30–72,Ullah et al. (2022)
Carboxymethyl cellulose grafted by polyacrylic acid and,100,38–97,Hosseini et al. (2022)
decorated with graphene oxide,,,
Activated carbon from Parthenium hysterophorus,20,86–94,Fito et al. (2020)
Kaolin,1,67–97,Mouni et al. (2018)
Modifed sawdust,1.5–5,34.4–96.6,Zou et al. (2013)
Raw and modifed mango seed,0.1–1.2,68–99.8,Senthil Kumar et al. (2014)
Montmorillonite modifed with iron oxide,0.1,26.78–60.98,Cottet et al. (2014)
Activated carbon from barley straw,0.1,5–70,Husseien et al. (2007)
Fly ash,8–20,45.16–96,Kumar et al. (2005)
"""

# needs merging
pdf2_t0 = """Stage of phar￾macokinetic,Data utilized,Modeling activities
modeling,,
Stage 1,ManNAc single dose pharmacokinetic data (Study 12-HG￾0207),Design of structural pharmacokinetic model Explore absorption models
Stage 2,ManNAc BID pharmacokinetic data (Study 15-HG-0068),Covariate analysis
,,Determination of non-linear and stationary pharmacokinetic
Stage 3,Stage 2 population pharmacokinetic model for ManNAc and,Monte Carlo simulations of dosing regimens
,Neu5Ac,Recommendation for evaluation of additional TID dosing
,,regimens in an extension of Study 15-HG-0068
Stage 4,"All available data, including the additional TID dosing phar￾macokinetic data generated during extension conducted in",Finalize pharmacokinetic model
,same patients from Study 15-HG-0068,
"""

# needs vertical splitting due to proj
pdf2_t2 = """ManNAc dose Q8H for 30 days,Q12H for 30 days,Q24H for 30 days
Median 5th–95th percentiles,Median 5th–95th percentiles,Median 5th–95th percentiles
"Plasma ManNAc Css,ave (ng/mL)",,
3 g 922 501–1550,642 359–1060,365 223–570
4 g 1060 573–1790,729 404–1220,411 246–650
6 g 1290 692–2180,881 480–1480,483 281–780
10 g 1650 883–2810,1120 607–1900,603 340–989
"Plasma Neu5Ac Css,ave (ng/mL)",,
3 g 633 247–2010,484 209–1420,338 174–825
4 g 702 265–2300,533 222–1610,364 181–921
6 g 818 296–2780,612 242–1930,405 190–1080
10 g 1020 344–3540,735 274–2440,464 204–1330
"""

pdf3_t0 = """Received: 26 January 2023,"Pau Ferri1,4, Chengeng Li 1,4, Daniel Schwalbe-Koda2 , Mingrou Xie3 ,"
Accepted: 8 May 2023,"Manuel Moliner 1 , Rafael Gómez-Bombarelli 2 , Mercedes Boronat 1 & Avelino Corma 1"
Check for updates,Approaching the level of molecular recognition of enzymes with solid catalysts
,"is a challenging goal, achieved in this work for the competing transalkylation"
,and disproportionation of diethylbenzene catalyzed by acid zeolites. The key
,diaryl intermediates for the two competing reactions only differ in the number
,"of ethyl substituents in the aromatic rings, and therefore finding a selective"
,zeolite able to recognize this subtle difference requires an accurate balance of
,the stabilization of reaction intermediates and transition states inside the
,"zeolite microporous voids. In this work we present a computational metho￾dology that, by combining a fast high-throughput screeening of all zeolite"
,structures able to stabilize the key intermediates with a more computationally
,"demanding mechanistic study only on the most promising candidates, guides"
,the selection of the zeolite structures to be synthesized. The methodology
,presented is validated experimentally and allows to go beyond the conven￾tional criteria of zeolite shape-selectivity.
"""

# needs vertical splitting due to proj
pdf3_t2 = """Channels system,Ea1,Ea2,Ea3,Ea4,Ea5,Ea6
transalkylation,,,,,,
BEC 12 × 12 × 12,98,35,44,48,85,98
BOG 12 × 10 × 10,75,29,65,50,88,96
IWR 12 × 10 × 10,71,31,60,44,91,90
IWV 12 × 12,56,21,52,47,60,86
MOR 12 × 8,95,33,78,50,84,87
UTL(int) 14 × 12,59,29,49,49,82,97
UTL(cha) 14 × 12,64,28,57,45,68,80
disproportionation,,,,,,
BEC 12 × 12 × 12,113,30,56,55,78,118
IWV 12 × 12,72,30,75,59,67,104
UTL(int) 14 × 12,90,29,69,58,71,98
UTL(cha) 14 × 12,80,22,73,46,82,97
"""

# needs vertical splitting
pdf4_t1 = """Data Platform Number of Features,,Number of tumors
Number of features and tumors in different data platforms,,
Radiomics 38,,91
Gene expressions 20531 genes (186 pathways),,91
Copy number variations 19950 genes (186 pathways),,91
miRNA expressions 1046,,91
Protein expressions 142,,62
Mutated genes 3734,,91
Number of tumors with different pathological stages,,
Pathological Stage T M,N,Overall
0 91,46,
I 38,34,22
II 50,6,58
III 3,4,11
X,1,
Number of tumors with different molecular receptor statuses,,
Receptor Status ER PR,,HER2
Negative 14 19,,72
Positive 77 72,,19
"""

# needs vertical splitting
pdf5_t1 = """Data collection,
Wavelength range (A˚ ),3.05–4.00
No. of images,20
Setting spacing (),7
Average exposure time (h),18
Space group a = b = c (A˚ ),P213 97.98
 =  =  ( ) Resolution (A˚ ),90 40–1.80 (1.90–1.80)
Rp.i.m. (%),6.3 (12.7)
hI/(I)i,7.9 (3.7)
Completeness (%),85.5 (69.8)
Multiplicity,6.5 (2.9)
Refinement,
No. of unique reflections,24728
Rwork/Rfree (%),23.17/27.64
No. of atoms,
Total,5659
Protein,5109
Cu,2
D2O,182 D2O [546 atoms]
O,2
B factors (A˚ 2 ),
Protein,15.2
Cu,8.6
Water,20.2
R.m.s. deviations,
Bond lengths (A˚ ),0.004
Bond angles (),0.884
PDB code,6gtj
"""

# needs merging
pdf6_t0 = """Year,Variety,Treatment,Spikelets per panicle,1000-grain weight (g),Seed setting rate,
,,,,,(%),
2019,CJ03,T0,267.67a,21.87c,87.67c,
,,T1,91.17b,20.10d,93.00b,
,W1844,T0,275.67a,22.91b,84.92d,
,,T1,97.92b,25.95a,95.58a,
2020,CJ03,T0,259.75a,22.38c,92.25b,
,,T1,77.50c,20.97d,94.17a,
,W1844,T0,273.67a,24.35b,85.17c,
,,T1,92.58b,25.19a,94.67a,
Year,Variety,Treatment,SG per panicle,IG per panicle,SG rate (%),IG rate (%)
2019,CJ03,T0,104.65a,163.02b,39.10a,60.90b
,,T1,31.04c,60.13d,34.05a,65.95b
,W1844,T0,68.31b,207.36a,24.78b,75.22a
,,T1,24.15d,73.77c,24.67b,75.33a
2020,CJ03,T0,80.83a,178.92b,31.12a,68.88b
,,T1,23.25c,54.25d,30.00a,70.00b
,W1844,T0,67.33b,206.34a,24.60b,75.40a
,,T1,22.42c,70.16c,24.21b,75.79a
"""

# needs merging
pdf6_t1 = """Year,Variety,Treatment,Net photosynthetic,Stomatal conductance,Intercellular CO2,Trmmol rate
,,,rate,(mmol·m−2 s−1 ),concentration,(mmol·m−2 s−1 )
,,,(umol·m−2 s−1 ),,(μmol·mol−1 ),
2019,CJ03,T0,22.51a,0.65b,285.30b,6.53a
,,T1,20.06c,0.52c,268.55c,5.32c
,W1844,T0,21.91a,0.74a,305.32a,6.28a
,,T1,20.72b,0.60bc,274.15b,5.68b
2020,CJ03,T0,25.40a,0.86a,225.50ab,13.73a
,,T1,20.92c,0.54c,210.57c,11.72c
,W1844,T0,24.91a,0.89a,233.63a,13.78a
,,T1,21.92b,0.75b,220.72b,12.71b
"""

# needs merging
pdf6_t2 = """IS,Inferior spikelets
SS,Superior spiklelets
OsSWEET11,Oryza sativa Sugar will eventually be exported transporter 11
OsSUTs,Oryza sativa Sucrose transporters
SPS,Sucrose-phosphate synthase
SuSase,Sucrose synthase
AGPase,ADP-glucose pyrophosphorylase
T6P,Trehalose-6-phosphate
SnRK1,Snf1-related protein kinase-1
TPS,Trehalose-6-phosphate synthase
TPP,Trehalsoe-6-phosphate phosphatase
ABA,Abscisic acid
CKs,Cytokinins
ZT,Zeatin
IAA,Auxin
SG,Superior spikelets
IG,Inferior spikelets
DPA,Days post anthesis
HPLC–MS/MS,High-performance liquid chromatography–tandem mass
,spectrometry
ANOVA,Analysis of variance
"""

pdf7_t0 = """,,,,,Core,amino,acid,,
Patient,Genotype,Viral load,Sex,Age,70,,91,rs12979860,End of treatment
no,,(106 IU/ml),,(years),,,,,response a
R1,1a,4.36,M,52.6,R,,C,CC,SVR
R2,1a,6.37,M,34.9,R,,C,CC,SVR
R3,1a,7.84,M,45.8,R,,C,CC,SVR
R4,1a,7.77,F,42.3,R,,C,CC,SVR
R5,1a,7.05,M,45.3,R,,C,CC,SVR
R6,1a,7.19,F,45.5,R,,C,CC,SVR
R7,1a,5.54,F,46.9,R,,C,CC,SVR
R8,1a,5.46,M,29.1,R,,C,CT,SVR
R9,1a,6.18,M,50.7,R,,C,CC,SVR
R10,1a,6.42,M,59.9,R,,C,CC,SVR
R11,1a,5.85,M,46.4,R,,C,CC,SVR
R12,1a,7.25,M,36.4,R,,C,CT,SVR
R13,1a,6.43,M,57.5,R,,C,CC,SVR
R14,1a,6.06,M,39.2,R,,C,CT,SVR
R15,1a,6.63,F,47.1,R,,C,CT,SVR
R21,1a,5.36,F,29.6,R,,C,CT,SVR
R22,1a,5.55,F,28.7,R,,C,CT,SVR
R23,1a,6.43,F,41.2,R,,C,CC,SVR
R24,1a,6.10,M,51.3,R,,C,CC,SVR
R25,1a,7.49,F,55.7,R,,C,CC,SVR
R28,1a,7.79,M,41.5,R,,C,CT,SVR
N1,1a,6.28,M,40.5,R,,C,CT,non-SVR
N2,1a,6.25,M,50.3,R,,C,CT,non-SVR
N3,1a,6.10,M,55.9,R,,C,TT,non-SVR
N4,1a,7.05,M,47.9,R,,C,TT,non-SVR
N5,1a,5.89,M,50.8,R,,C,CT,non-SVR
N6,1a,6.42,F,48.1,P,,C,CT,non-SVR
N7,1a,6.72,M,48.9,R,,C,TT,non-SVR
N8,1a,7.35,M,54.6,R,,C,TT,non-SVR
N9,1a,6.13,F,57.8,R,,C,TT,non-SVR
N10,1a,6.72,M,54.6,R,,C,TT,non-SVR
N11,1a,6.42,M,48.0,R,,C,CT,non-SVR
N12,1a,7.32,F,48.4,R,,C,CT,non-SVR
N13,1a,6.09,M,24.3,R,,C,TT,non-SVR
N14,1a,6.31,M,35.0,R,,C,CT,non-SVR
N20,1a,6.73,F,35.0,R,,C,CC,non-SVR
N21,1a,7.15,F,45.0,R,,C,CC,non-SVR
R16,1b,4.13,F,46.5,R,,M,CC,SVR
R17,1b,4.94,M,31.5,R,,M,CC,SVR
R18,1b,5.40,F,58.7,R,,M,CT,SVR
R19,1b,6.23,F,38.4,R,,L,CT,SVR
R20,1b,7.39,F,47.8,R,,M,CT,SVR
R26,1b,7.17,M,46.6,R,,L,CT,SVR
R27,1b,6.81,M,56.8,R,,M,CT,SVR
R29,1b,7.55,M,57.0,Q,,M,CT,SVR
N15,1b,6.08,F,56.5,Q,,M,CT,non-SVR
N16,1b,6.57,F,58.5,Q,,M,TT,non-SVR
N17,1b,7.37,M,48.9,Q,,L,CT,non-SVR
N18,1b,6.69,M,62.8,Q,,L,CT,non-SVR
N19,1b,6.70,F,54.2,Q,,M,CT,non-SVR
"""

# needs header merging
pdf7_t1 = """,SVR,non-SVR,Univariate
,n = 29,n = 21,p value
Age (mean),45.2,48.8,0.09a
Number of patients < 45 / > 45 yrs,11 / 18,4 / 17,0.21b
Gender (m/f),17 / 12,13 / 8,1.0b
Baseline HCV RNA (mean log IU/mL),6.37,6.59,0.56a
Number with < 5.6 / > 5.6 log IU/mL,8 / 21,0 / 21,0.01b
Genotype 1a/1b,21 / 8,16 / 5,1.0b
Fibrosis (F0/F1/F2/F3/F4)c,0 / 10 / 13 / 4 / 0,2 / 4 / 4 / 7 / 2,0.19d
Core aa 70,28 R / 1 Q,15 R / 5 Q & 1 P,0.03b
Core aa 91,21 C / 6 M / 2 L,16 C / 3 M / 2 L,0.82e
rs12979860,16 CC / 13 CT / 0 TT,2 CC / 11 CT / 8 TT,0.0001e
"""

pdf7_t2 = """,,Amino,acid 70,,Amino acid,91,
Genotype,Q,R,P,H,C M,L,Total
1a,2%,98%,-,-,100% -,-,920
1b,60%,35%,-,4%,1% 71%,28%,2022
2,-,100%,-,-,39% 4%,58%,83
3,-,93%,6%,-,99% -,-,204
4,5%,95%,-,-,100% -,-,19
5,86%,14%,-,-,- -,100%,14
6,60%,13%,13%,15%,100% -,-,55
"""

# rotated table, weirdness on splitting vertically ??
pdf8_t0 = """,,,,,,,
Sample Temperature Time,IWa,f H2 f H2O # of Fit 1 Fit 2 Fit 3 Mean,1σ,Mean,1σ,Corrected Mean,Corrected
(K) (s),,points (bar) (bar) Absorbance Absorbance Absorbance ε = 6.3 m2/mol,,ε = 5.1 m2/mol,,ε = 6.3 m2/mol,ε = 5.1 m2/mol
,,(ppmw),,(ppmw),,(ppmw),(ppmw)
Per-1 2173 ± 21 30,5.97,0 0 3 0.036 0.037 0.038 35.4,2.0,43.7,3.0,2.9,3.5
Per-2 2166 ± 40 40,3.46,0 0 7 0.039 0.040 0.039 37.6,2.0,46.5,3.1,5.1,6.3
Per-3 2134 ± 29 32,3.42,1.28E-05 0.00071 7 0.053 0.054 0.050 50.0,3.2,61.8,4.6,17.5,21.7
Per-4 2197 ± 59 60,3.46,9.88E-07 5.74E-05 7 0.041 0.040 0.039 38.2,2.2,47.2,3.2,5.7,7.1
Per-5 2239 ± 25 36,3.46,5.17E-08 3.02E-06 6 0.036 0.033 0.033 32.5,2.3,40.2,3.2,0.0,0.0
Per-6 2151 ± 23 25,3.37,2.77E-05 0.0015 8 0.053 0.055 0.057 52.6,3.2,65.0,4.7,20.1,24.8
Per-7 2139 ± 13 27,3.23,8.41E-05 0.0038 7 0.069 0.070 0.072 67.2,3.8,83.1,5.6,34.7,42.9
Per-8 2197 ± 13 31,2.94,0.00024 0.0076 8 0.088 0.090 0.094 86.7,5.2,107.1,7.6,54.2,66.9
Per-9 2175 ± 15 30,2.03,0.0016 0.018 9 0.115 0.120 0.118 112.5,6.3,139.0,9.4,80.0,98.8
Per-10 2173 ± 21 30,0.64,0.012 0.027 9 0.141 0.142 0.143 135.8,7.1,167.7,10.9,103.3,127.5
Per-11 2169 ± 16 28,−0.77,0.041 0.018 10 0.145 0.142 0.144 137.4,7.3,169.7,11.1,104.8,129.5
Per-12 2112 ± 17 33,−1.90,0.064 0.0078 10 0.133 0.132 0.138 128.4,7.3,158.6,10.8,95.9,118.5
Per-TS1 2124 ± 13 10,3.23,8.41E-05 0.0038 8 0.066 0.066 0.068 63.7,3.5,78.7,5.2,31.2,38.6
"""

# TODO not sure why the top row is truncated
pdf8_t1 = """,,(K),,,(bar−0.5),,,,,(bar),,
This work (ε3550 = 6.3 m2/mol),Peridotite,2173,,,2.91 × 10−3,,,,,5.7 × 10−5 –,0.027,14
This work (ε3550 = 5.1 m2/mol),Peridotite,2173,,,3.59 × 10−3,,,,,5.7 × 10−5 –,0.027,14
Newcombe et al. (2017),Anorthite-Diopside eutectic,1623,,,4.22 × 10−3,,,,,9.8 × 10−3 –,0.32,14
Newcombe et al. (2017),Lunar Green Glass,1623,,,4.04 × 10−3,,,,,9.8 × 10−3 –,0.32,11
Dixon et al. (1995),Mid-Ocean Ridge Basalt,1473,,,5.36 × 10−3,,,,,17 – 709,,14
Hamilton and Oxtoby (1986),NaAlSi3O8,1123,–,1573,7.59 × 10−3,–,9.91,×,10−3,1685 – 2160,,13
"""
csvs = {
    "pdf1_t1": pdf1_t1,
    "pdf1_t5": pdf1_t5,
    "pdf2_t0": pdf2_t0,
    "pdf2_t2": pdf2_t2,
    "pdf3_t0": pdf3_t0,
    "pdf3_t2": pdf3_t2,
    "pdf4_t1": pdf4_t1,
    "pdf5_t1": pdf5_t1,
    "pdf6_t0": pdf6_t0,
    "pdf6_t1": pdf6_t1,
    "pdf6_t2": pdf6_t2,
    "pdf7_t0": pdf7_t0,
    "pdf7_t1": pdf7_t1,
    "pdf7_t2": pdf7_t2,
    "pdf8_t0": pdf8_t0,
    "pdf8_t1": pdf8_t1,
}
