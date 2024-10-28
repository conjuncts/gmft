
from gmft import TATRFormattedTable
from gmft._rich_text.rich_page import embed_tables
from gmft.formatters.tatr import TATRFormatConfig


def test_rich_pdf7(docs_bulk, pdf7_tables):
    doc = docs_bulk[6] # n-1
    # look at page 12

    config = TATRFormatConfig()
    for ft in pdf7_tables:
        ft = ft # type: TATRFormattedTable
        ft.df(config_overrides=config) # reset config to defaults


    rich_pages = embed_tables(doc=doc, tables=pdf7_tables)
    
    # print(rich_pages[2])
    assert rich_pages[2].get_text() == """Infectious of Alestig al. BMC Diseases Page 2011, 11:124 3 7 et
http://www.biomedcentral.com/1471-2334/11/124
of infection Table Virological and clinical characteristics with hepatitis patients virus C 1
|    | Patient no   | Genotype   |   Viral load (106 IU/ml) | Sex   |   Age (years) | Core \\n70   | amino acid \\n91   | rs12979860   | End of treatment response a   |
|---:|:-------------|:-----------|-------------------------:|:------|--------------:|:------------|:------------------|:-------------|:------------------------------|
|  0 | R1           | 1a         |                     4.36 | M     |          52.6 | R           | C                 | CC           | SVR                           |
|  1 | R2           | 1a         |                     6.37 | M     |          34.9 | R           | C                 | CC           | SVR                           |
|  2 | R3           | 1a         |                     7.84 | M     |          45.8 | R           | C                 | CC           | SVR                           |
|  3 | R4           | 1a         |                     7.77 | F     |          42.3 | R           | C                 | CC           | SVR                           |
|  4 | R5           | 1a         |                     7.05 | M     |          45.3 | R           | C                 | CC           | SVR                           |
|  5 | R6           | 1a         |                     7.19 | F     |          45.5 | R           | C                 | CC           | SVR                           |
|  6 | R7           | 1a         |                     5.54 | F     |          46.9 | R           | C                 | CC           | SVR                           |
|  7 | R8           | 1a         |                     5.46 | M     |          29.1 | R           | C                 | CT           | SVR                           |
|  8 | R9           | 1a         |                     6.18 | M     |          50.7 | R           | C                 | CC           | SVR                           |
|  9 | R10          | 1a         |                     6.42 | M     |          59.9 | R           | C                 | CC           | SVR                           |
| 10 | R11          | 1a         |                     5.85 | M     |          46.4 | R           | C                 | CC           | SVR                           |
| 11 | R12          | 1a         |                     7.25 | M     |          36.4 | R           | C                 | CT           | SVR                           |
| 12 | R13          | 1a         |                     6.43 | M     |          57.5 | R           | C                 | CC           | SVR                           |
| 13 | R14          | 1a         |                     6.06 | M     |          39.2 | R           | C                 | CT           | SVR                           |
| 14 | R15          | 1a         |                     6.63 | F     |          47.1 | R           | C                 | CT           | SVR                           |
| 15 | R21          | 1a         |                     5.36 | F     |          29.6 | R           | C                 | CT           | SVR                           |
| 16 | R22          | 1a         |                     5.55 | F     |          28.7 | R           | C                 | CT           | SVR                           |
| 17 | R23          | 1a         |                     6.43 | F     |          41.2 | R           | C                 | CC           | SVR                           |
| 18 | R24          | 1a         |                     6.1  | M     |          51.3 | R           | C                 | CC           | SVR                           |
| 19 | R25          | 1a         |                     7.49 | F     |          55.7 | R           | C                 | CC           | SVR                           |
| 20 | R28          | 1a         |                     7.79 | M     |          41.5 | R           | C                 | CT           | SVR                           |
| 21 | N1           | 1a         |                     6.28 | M     |          40.5 | R           | C                 | CT           | non-SVR                       |
| 22 | N2           | 1a         |                     6.25 | M     |          50.3 | R           | C                 | CT           | non-SVR                       |
| 23 | N3           | 1a         |                     6.1  | M     |          55.9 | R           | C                 | TT           | non-SVR                       |
| 24 | N4           | 1a         |                     7.05 | M     |          47.9 | R           | C                 | TT           | non-SVR                       |
| 25 | N5           | 1a         |                     5.89 | M     |          50.8 | R           | C                 | CT           | non-SVR                       |
| 26 | N6           | 1a         |                     6.42 | F     |          48.1 | P           | C                 | CT           | non-SVR                       |
| 27 | N7           | 1a         |                     6.72 | M     |          48.9 | R           | C                 | TT           | non-SVR                       |
| 28 | N8           | 1a         |                     7.35 | M     |          54.6 | R           | C                 | TT           | non-SVR                       |
| 29 | N9           | 1a         |                     6.13 | F     |          57.8 | R           | C                 | TT           | non-SVR                       |
| 30 | N10          | 1a         |                     6.72 | M     |          54.6 | R           | C                 | TT           | non-SVR                       |
| 31 | N11          | 1a         |                     6.42 | M     |          48   | R           | C                 | CT           | non-SVR                       |
| 32 | N12          | 1a         |                     7.32 | F     |          48.4 | R           | C                 | CT           | non-SVR                       |
| 33 | N13          | 1a         |                     6.09 | M     |          24.3 | R           | C                 | TT           | non-SVR                       |
| 34 | N14          | 1a         |                     6.31 | M     |          35   | R           | C                 | CT           | non-SVR                       |
| 35 | N20          | 1a         |                     6.73 | F     |          35   | R           | C                 | CC           | non-SVR                       |
| 36 | N21          | 1a         |                     7.15 | F     |          45   | R           | C                 | CC           | non-SVR                       |
| 37 | R16          | 1b         |                     4.13 | F     |          46.5 | R           | M                 | CC           | SVR                           |
| 38 | R17          | 1b         |                     4.94 | M     |          31.5 | R           | M                 | CC           | SVR                           |
| 39 | R18          | 1b         |                     5.4  | F     |          58.7 | R           | M                 | CT           | SVR                           |
| 40 | R19          | 1b         |                     6.23 | F     |          38.4 | R           | L                 | CT           | SVR                           |
| 41 | R20          | 1b         |                     7.39 | F     |          47.8 | R           | M                 | CT           | SVR                           |
| 42 | R26          | 1b         |                     7.17 | M     |          46.6 | R           | L                 | CT           | SVR                           |
| 43 | R27          | 1b         |                     6.81 | M     |          56.8 | R           | M                 | CT           | SVR                           |
| 44 | R29          | 1b         |                     7.55 | M     |          57   | Q           | M                 | CT           | SVR                           |
| 45 | N15          | 1b         |                     6.08 | F     |          56.5 | Q           | M                 | CT           | non-SVR                       |
| 46 | N16          | 1b         |                     6.57 | F     |          58.5 | Q           | M                 | TT           | non-SVR                       |
| 47 | N17          | 1b         |                     7.37 | M     |          48.9 | Q           | L                 | CT           | non-SVR                       |
| 48 | N18          | 1b         |                     6.69 | M     |          62.8 | Q           | L                 | CT           | non-SVR                       |
| 49 | N19          | 1b         |                     6.7  | F     |          54.2 | Q           | M                 | CT           | non-SVR                       |

a sustained virologic sustained virologic SVR, non-SVR, response; no response"""
    assert rich_pages[3].get_text() == """Infectious of Alestig al. BMC Diseases Page 2011, 11:124 4 7 et
http://www.biomedcentral.com/1471-2334/11/124
Table and viral baseline with and without in patients Host 2 parameters treatment response
|    |                                     | SVR n = 29           | non-SVR n = 21      | Univariate p value   |
|---:|:------------------------------------|:---------------------|:--------------------|:---------------------|
|  0 | Age (mean)                          | 45.2                 | 48.8                | 0.09a                |
|  1 | Number of patients < 45 / > 45 yrs  | 11 / 18              | 4 / 17              | 0.21b                |
|  2 | Gender (m/f)                        | 17 / 12              | 13 / 8              | 1.0b                 |
|  3 | Baseline HCV RNA (mean log IU/mL)   | 6.37                 | 6.59                | 0.56a                |
|  4 | Number with < 5.6 / > 5.6 log IU/mL | 8 / 21               | 0 / 21              | 0.01b                |
|  5 | Genotype 1a/1b                      | 21 / 8               | 16 / 5              | 1.0b                 |
|  6 | Fibrosis (F0/F1/F2/F3/F4)c          | 0 / 10 / 13 / 4 / 0  | 2 / 4 / 4 / 7 / 2   | 0.19d                |
|  7 | Core aa 70                          | 28 R / 1 Q           | 15 R / 5 Q & 1 P    | 0.03b                |
|  8 | Core aa 91                          | 21 C / 6 M / 2 L     | 16 C / 3 M / 2 L    | 0.82e                |
|  9 | rs12979860                          | 16 CC / 13 CT / 0 TT | 2 CC / 11 CT / 8 TT | 0.0001e              |

a Mann-Whitney U test.
b Fisher’s exact test.
c for Fibrosis scored according Ludwig and and available Batts, patients. 34 to was was
d Logistic regression.
e Chi test. square
the correlation of responders Subgenotypes, and mutations strains, 8 7 treatment strong: core response was
substitu\ufffetions The virologic associated with (R70) had and non-responders had glutamine 5 arginine not response was
residue (Q70) (p 0.005). residue the However, 91. In in 37 70 at at contrast, asso\ufffeciated poor response was a =
with substitutions of residue of the with infection, all the with One SVR 70: patients patients 1a 21 core
(14%) (six with substitutions residue carried with while of the patients HCV non-SVR 70 7 R70, 15 16 at car\uffferied
subtype 1b with and subtype with Q70 strains strain 1a R70. strains one
P70) with achieved compared with of SVR, 43 28 of Phylogenetic analysis and substitutions NS5A ISDR as
(65%) (p 0.03). with order find if the variability and R70 patients carrying strains In positions 70 to out at =
Substitutions of residues and closely linked subgroups of HCV-1b phylogenetic 70 91 91 to core were was
(5 non-SVR) linked subgenotype 1b: of Six analysis of performed, including the 13 NS5A 13 to geno\ufffetype was
subgeno\ufffetype 1b had while only of from the study well database Q70, strains 37 strains present one as as
(P70) (p had substitution this The different found strain site 1a 70/91 variants at a sequences. core were =
0.0007). Similarly, all had residue sub-branches of the without clustering, strains cysteine 1a in at tree many
(p while 1b had methionine and had leucine indicating that they the result of few historical in 91, 9 4 not < are a
0.0001). This between variability and (data shown). but evolve continuously association mutations not core
further explored by analysis of (as substitution within compared with the 3313 One ISDR genotype was
(http://hcv. from the Database sequence) HCV reference observed of the Project HCV-J in 13 9 sequences was
(≥93%) lanl.gov/), showing predominance of (7 H2218N), subgenotype 1b and R70 in H2218R, strains 2 2 a
and and high of 1b, (H2219Y D2225E) substitutions and Q70 5 in 3 1a, 2, 4, in genotypes rates seen were one
(Table 3). and the subtype 1b substitu\ufffetion There between 6 In patients carrying 13 ISDR strain. association was no
and treatment response.
SNP IL28B of Table Distribution acids residue and amino 3 70 91 at
The allele frequency T 40% rs12979860 was as of com\ufffepared the region core
with health subjects without HCV 46% 163 in
|    | Genotype   | Q   | Amino \\nR   | acid 70 \\nP   | H   | Amino \\nC   | acid \\nM   | 91 \\nL   |   Total |
|---:|:-----------|:----|:------------|:--------------|:----|:------------|:-----------|:---------|--------:|
|  0 | 1a         | 2%  | 98%         | -             | -   | 100%        | -          | -        |     920 |
|  1 | 1b         | 60% | 35%         | -             | 4%  | 1%          | 71%        | 28%      |    2022 |
|  2 | 2          | -   | 100%        | -             | -   | 39%         | 4%         | 58%      |      83 |
|  3 | 3          | -   | 93%         | 6%            | -   | 99%         | -          | -        |     204 |
|  4 | 4          | 5%  | 95%         | -             | -   | 100%        | -          | -        |      19 |
|  5 | 5          | 86% | 14%         | -             | -   | -           | -          | 100%     |      14 |
|  6 | 6          | 60% | 13%         | 13%           | 15% | 100%        | -          | -        |      55 |

infection. The which has been associated CC genotype,
with better several in previous stu\ufffedies, treatment response (89%) identified and of them 16 in patients, 18
was achieved The unfavourable SVR. SNP genotype were (TT) found and of them in patients 8
was was none responder. hetero\ufffezygous, The CT remaining patients 24 were (54%) of them achieved SVR. In 13
attempt an explore whether might have variation impact
to core an of the viral kinetics rs12979860, irrespective
response on
31st of found of total March the The C in Hepatitis A 3317 2010 sequences on the and different CT SNP in patients carrying genotype
Database (http://hcv.lanl.gov/) analysed. Values less (HCV) Project Virus were
compared. shown As HCV Figure variants in 1 was core than shown. 1% not"""
    # control
    assert rich_pages[0].get_text() == """Infectious Alestig al. BMC Diseases 2011, 11:124 et
http://www.biomedcentral.com/1471-2334/11/124
Open S EARCH TIC R AR E L E Access
polymorphisms and Core IL28B mutations,
peginterferon/ribavirin in to treatment response
Swedish with hepatitis C patients virus genotype
infection 1
Alestig1*, Arnholm2 Nilsson3 Eilard1 Lagging1 Norkrans1 Staffan Erik Anders Gunnar Birgitta Martin
, , , , , Wahlberg4 Wejstål1 Westin1 Lindh1
Johan and Thomas Rune Magnus
, ,
Abstract
infected Background: with hepatitis respond poorly standard with (HCV) C Patients virus 1 genotype to treatment
less achieving sustained virologic Predicting essential and could help avoid 50% is outcome or response.
of and reduce health Recently, acid substitutions the association amino in treatment cost. unnecessary an core
of and observed the study, the these Japanese In region in patients. impact treatment outcome present was
kinetics and explored Caucasian mutations in patients. treatment outcome on response was
of from peginterferon/ Methods: The samples obtained treated with HCV 50 region patients pre-treatment core
infection ribavirin Swedish clinical trial with sequenced. The alleles rs12979860, in previous 1 genotype at a were a
identify single nucleotide polymorphism assessed order with this (SNP), in co-association to strong were any
predictor. response
of found. Results: between and substitutions residue No In 91 association treatment contrast, response core was
of of substitutions residue observed non-responders, but only responders (29%) (p 6/21 70 29 in in core were one =
of of and subgenotype 1b than 0.03), (R70Q strains) (R70P 6 13 37 in in in in strains, 1a 1 were more common p =
of The the overall the predictor 0.004). (p 0.0001). SNP IL28B rs12979860 upstream strongest gene was response =
substitutions associated with kinetics the Core CT 70 in patients carrying genotype at were poorer response
rs12979860.
of Conclusions: The results indicate that substitutions residue related 70 in to treatment core are response
infection, of with HCV-1b but less than polymorphism. Caucasian IL28B patients importance are
Background and frequent side effects, identify it is important costs to
(HCV) factors that predict the likelihood of infection of C Hepatitis virus is major response. cause can a
Several host factors such of liver fibrosis, cirrhosis and hepatocellular affecting approxi\ufffemately stage age, as cancer
(BMI), [1]. body index liver insulin million worldwide Combination steatosis, resistance 170 mass persons
(Peg\ufffeIFN/RBV), and ethnicity, well viral influence the therapy with pegylated interferon and ribavirin genotype as as
[5]. While the for weeks, eradicate the impact given 24 72 treatment outcome outcome to on may
[2-4], by undisputed, with of with infection and of liver damage but 80% is patients progression genotype stop
achieving compared with do achieve sustained virologic SVR 50% patients 3 2 genotype not as or many
(SVR). [6], for the of subtypes regional this and light of high For importance in 1, genotype response reason,
variability controversial. 1995 mutations In it was or are
reported from that of the Japan mutations in part a
Correspondence: erik.alestig@gu.se * associated with NS5A region treatment
response were 1 of Infection of and Virology, Gothenburg, Department University
1b The between in patients. association genotype Gothenburg, Sweden
of information of Full list author available the end the article is at
of Alestig al; licensee BioMed Central Ltd. This article distributed under the the Open Creative Commons Access 2011 is © et terms an
Attribution (http://creativecommons.org/licenses/by/2.0), which unrestricted distribution, and reproduction License permits in use,
medium, provided the original work properly cited. is any"""