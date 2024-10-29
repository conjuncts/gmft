import json
import os

from gmft.formatters.tatr import TATRFormatConfig
from gmft.table_function import TATRFormattedTable
from ..conftest import REDETECT_TABLES

def dump_debug(pdf_no, j, actual, expected, ft: TATRFormattedTable):
    with open(f"test/outputs/actual/span{pdf_no}_t{j}.csv", "w", encoding='utf-8') as f:
        f.write(actual)
    with open(f"test/outputs/actual/span{pdf_no}_t{j}.old.csv", "w", encoding='utf-8') as f:
        f.write(expected)
    debug_img = ft.visualize(effective=True, show_labels=False, return_img=True)
    debug_img.save(f"test/outputs/actual/span{pdf_no}_t{j}.png")
    if REDETECT_TABLES:
        with open(f"test/outputs/actual/span{pdf_no}_t{j}.info", "w") as f:
            json.dump(ft.to_dict(), f, indent=2)
def try_jth_table(tables, pdf_no, j, expected, config=None):
    
    if config is None:
        config = TATRFormatConfig()
        config.large_table_threshold = 20
        config.verbosity = 3
        config.semantic_spanning_cells = True
        config.semantic_hierarchical_left_fill = 'algorithm'
        
    # note that config_overrides and config are both not a dict

    ft = tables[j]
    # try:
    ft._df = None
    df = ft.df(config_overrides=config)
    actual = df.to_csv(index=False, lineterminator="\n")
    if expected != actual:
        dump_debug(pdf_no, j, actual, expected, ft)
    assert expected == actual, f"Mismatch in csv files for pdf {pdf_no} and table {j}"

# class TestMultiIndex:
# relevant: 1 1, 2 2, 3 0, 7 0, 7 2

class TestHierLeft:
    def test_pdf1_t4(self, pdf1_tables):
        expected = """Source,DF,Adjusted SS,Adj MS,F value,p value
Model,14,401.025,28.6446,218.33,0.000
x1,1,6.457,6.4568,49.21,0.000
x2,1,2.068,2.0680,15.76,0.001
x3,1,0.014,0.0141,0.11,0.748
x4,1,2.209,2.2090,16.84,0.001
x2 1,1,10.260,10.2603,78.20,0.000
x2 2,1,0.291,0.2908,2.22,0.157
x2 3,1,0.687,0.6872,5.24,0.037
x2 4,1,3.638,3.6382,27.73,0.000
x1x2,1,12.443,12.4433,94.84,0.000
x1x3,1,2.933,2.9327,22.35,0.000
x1x4,1,18.598,18.5977,141.75,0.000
x2x3,1,0.001,0.0005,0.00,0.951
x2x4,1,2.616,2.6163,19.94,0.000
x3x4,1,1.632,1.6320,12.44,0.003
Error,15,1.968,0.1312,,
Lack-of-ft,10,1.323,0.1323,1.02,0.523
Pure error,5,0.645,0.1291,,
Total,29,402.993,,,
R2= 99.51%,Adj R2,,,,
R2= 99.51%,= 99.06%,,,,
"""
        config = TATRFormatConfig()
        config.verbosity = 3
        config.semantic_spanning_cells = True
        config.semantic_hierarchical_left_fill = 'deep'
        try_jth_table(pdf1_tables, 1, 4, expected, config=config)

    def test_pdf1_t7(self, pdf1_tables):
        expected = """Model,Parameters,
Langmuir,qm(mg g−1),159
Langmuir,kL(L mg−1),0.0956
Langmuir,R2,0.984
Freundlich,n,2.52
Freundlich,kF(mg g−1),26.42
Freundlich,R2,0.891
Temkin,B,29.245
Temkin,kT(L mg−1),1.518
Temkin,b(J g mg−1 mol−1),87
Temkin,R2,0.970
Dubinin–Radushkevich,kD,3.71×10−9
Dubinin–Radushkevich,qD(mg g−1),420.0
Dubinin–Radushkevich,E (kJ mol−1),11.60
Dubinin–Radushkevich,R2,0.910
"""
        try_jth_table(pdf1_tables, 1, 7, expected)
    
    def test_pdf1_t8(self, pdf1_tables):
        expected = """Kinetic model,Parameters,Parameters
Linear driving force,k1(min−1),0.0604
Linear driving force,"qe,calc(mg g−1)",22.39
Linear driving force,"qe,exp(mg g−1)",54.28
Linear driving force,R2,0.927
Pseudo-second-order,"qe,calc(mg g−1)",55.57
Pseudo-second-order,k2(g.mg−1 min−1),0.018
Pseudo-second-order,R2,0.999
Intra-particle difusion,"k3,1(mg g−1 min−0.5)",1.766
Intra-particle difusion,I1(mg g−1),39.36
Intra-particle difusion,R2 1,0.992
Intra-particle difusion,"k3,2(mg g−1 min−0.5)",0.131
Intra-particle difusion,I2(mg g−1),52.96
Intra-particle difusion,R2 2,1.000
"""
        try_jth_table(pdf1_tables, 1, 8, expected)
    def test_pdf6_t0(self, pdf6_tables):
        expected = """Year,Variety,Treatment,Spikelets per panicle,1000-grain weight (g),Seed setting rate (%),Seed setting rate (%)
2019,CJ03,T0,267.67a,21.87c,87.67c,
2019,,T1,91.17b,20.10d,93.00b,
2019,W1844,T0,275.67a,22.91b,84.92d,
2019,,T1,97.92b,25.95a,95.58a,
2020,CJ03,T0,259.75a,22.38c,92.25b,
2020,,T1,77.50c,20.97d,94.17a,
2020,W1844,T0,273.67a,24.35b,85.17c,
2020,,T1,92.58b,25.19a,94.67a,
Year,Variety,Treatment,SG per panicle,IG per panicle,SG rate (%),IG rate (%)
2019,CJ03,T0,104.65a,163.02b,39.10a,60.90b
2019,,T1,31.04c,60.13d,34.05a,65.95b
2019,W1844,T0,68.31b,207.36a,24.78b,75.22a
2019,,T1,24.15d,73.77c,24.67b,75.33a
2020,CJ03,T0,80.83a,178.92b,31.12a,68.88b
2020,,T1,23.25c,54.25d,30.00a,70.00b
2020,W1844,T0,67.33b,206.34a,24.60b,75.40a
2020,,T1,22.42c,70.16c,24.21b,75.79a
"""
        try_jth_table(pdf6_tables, 6, 0, expected)
    def test_pdf6_t1(self, pdf6_tables):
        expected = """Year,Variety,Treatment,Net photosynthetic rate (umol·m−2 s−1 ),Stomatal conductance (mmol·m−2 s−1 ),Intercellular CO2 concentration (μmol·mol−1 ),Trmmol rate (mmol·m−2 s−1 )
2019,CJ03,T0,22.51a,0.65b,285.30b,6.53a
2019,,T1,20.06c,0.52c,268.55c,5.32c
2019,W1844,T0,21.91a,0.74a,305.32a,6.28a
2019,,T1,20.72b,0.60bc,274.15b,5.68b
2020,CJ03,T0,25.40a,0.86a,225.50ab,13.73a
2020,,T1,20.92c,0.54c,210.57c,11.72c
2020,W1844,T0,24.91a,0.89a,233.63a,13.78a
2020,,T1,21.92b,0.75b,220.72b,12.71b
"""
        try_jth_table(pdf6_tables, 6, 1, expected)
    

config2 = TATRFormatConfig()
config2.verbosity = 3
config2.enable_multi_header = True
config2.semantic_spanning_cells = True

class TestHierTop:

    
    def test_pdf1_t1(self, pdf1_tables):
        # Factor \nComplete name is like this because there is an overlapping hier-top and monosemantic
        # TODO NMS needs to be applied on all header-like spanning cells at once, not just
        # on hier-top and monosemantic spans separately
        expected = """nan,nan,Levels,Levels,Levels,Levels
Factor \\nComplete name,Factor \\nCoded name,Range,−1,0,1
Temperature (°C),x1,25–35,25,30,35
pH,x2,4–8,4,6,8
Initial dye concen￾tration (mg L−1),x3,4–8,4,6,8
Mesh size,x4,50–150,50,100,150
"""
        try_jth_table(pdf1_tables, 1, 1, expected, config=config2)
    
    def test_pdf2_t2(self, pdf2_tables):
        expected = """ManNAc dose,Q8H for 30 days,Q8H for 30 days,Q12H for 30 days,Q12H for 30 days,Q24H for 30 days,Q24H for 30 days
nan,Median,5th–95th percentiles,Median,5th–95th percentiles,Median,5th–95th percentiles
Plasma ManNAc,"Css,ave (ng/mL)",,,,,
3 g,922,501–1550,642,359–1060,365,223–570
4 g,1060,573–1790,729,404–1220,411,246–650
6 g,1290,692–2180,881,480–1480,483,281–780
10 g,1650,883–2810,1120,607–1900,603,340–989
Plasma Neu5Ac,"Css,ave (ng/mL)",,,,,
3 g,633,247–2010,484,209–1420,338,174–825
4 g,702,265–2300,533,222–1610,364,181–921
6 g,818,296–2780,612,242–1930,405,190–1080
10 g,1020,344–3540,735,274–2440,464,204–1330
"""

        try_jth_table(pdf2_tables, 2, 2, expected, config=config2)
        
        assert pdf2_tables[2]._projecting_indices == [0, 5]
    
    # pdf4 t1 is arguably HierTop, but the ground truth is not yet clear
    
    def test_pdf7_t0(self, pdf7_tables):
        expected = """nan,nan,nan,nan,nan,Core amino acid,Core amino acid,nan,nan
Patient no,Genotype,Viral load (106 IU/ml),Sex,Age (years),70,91,rs12979860,End of treatment response a
R1,1a,4.36,M,52.6,R,C,CC,SVR"""
        config = TATRFormatConfig()
        config.verbosity = 3
        config.enable_multi_header = True
        config.semantic_spanning_cells = True
        
        ft = pdf7_tables[0]
        df = ft.df(config_overrides=config)
        actual = df.to_csv(index=False, lineterminator="\n")
        actual = "\n".join(actual.split("\n")[:3]) # get just first 3 lines
        if expected != actual:
            dump_debug(7, 0, actual, expected, ft)
        assert expected == actual, f"Mismatch in csv files for pdf 7 and table 0"
    
    def test_pdf7_t2(self, pdf7_tables):
        expected = """nan,Amino acid 70,Amino acid 70,Amino acid 70,Amino acid 70,Amino acid 91,Amino acid 91,Amino acid 91,nan
Genotype,Q,R,P,H,C,M,L,Total
1a,2%,98%,-,-,100%,-,-,920
1b,60%,35%,-,4%,1%,71%,28%,2022
2,-,100%,-,-,39%,4%,58%,83
3,-,93%,6%,-,99%,-,-,204
4,5%,95%,-,-,100%,-,-,19
5,86%,14%,-,-,-,-,100%,14
6,60%,13%,13%,15%,100%,-,-,55
"""
        try_jth_table(pdf7_tables, 7, 2, expected, config=config2)
    
    
    # Also of interest: attn_p8 (HierTop), pubt_p6 (HierTop)

    def test_pubt_p6(self, doc_pubt, tatr_tables):

        # table detection    
        ft = TATRFormattedTable.from_dict(tatr_tables['pubt_p6'], doc_pubt[6-1])    

        df = ft.df(config_overrides=config2)
        actual = df.to_csv(lineterminator='\n', index=False)
        expected = """\
nan,nan,nan,Tables with an oversegmented PRH,Tables with an oversegmented PRH,Tables with an oversegmented PRH
Dataset,Total Tables \\nInvestigated†,Total Tables \\nwith a PRH∗,Total,% (of total with a PRH),% (of total investigated)
SciTSR,"10,431",342,54,15.79%,0.52%
PubTabNet,"422,491","100,159","58,747",58.65%,13.90%
FinTabNet,"70,028","25,637","25,348",98.87%,36.20%
PubTables-1M (ours),"761,262","153,705",0,0%,0%
"""
        if actual != expected:
            dump_debug("_pubt", "_p6", actual, expected, ft)
        assert actual == expected