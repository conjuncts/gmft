import json
import os

from gmft import AutoFormatConfig
from gmft.table_function import TATRFormattedTable




def try_jth_table(docs_bulk, pdf_no, j, expected, config=None):
    
    if config is None:
        config = AutoFormatConfig()
        config.large_table_threshold = 20
        config.verbosity = 3
    # note that config_overrides and config are both not a dict
    
    doc = docs_bulk[pdf_no-1]
    with open(f"test/outputs/bulk/pdf{pdf_no}_t{j}.info", "r") as f:
        as_dict = json.load(f)
        page_no = as_dict["page_no"]
        page = doc[page_no]
        ft = TATRFormattedTable.from_dict(as_dict, page)

    # try:
    df = ft.df(config_overrides=config)
    actual = df.to_csv(index=False, lineterminator="\n")
    if not expected == actual:
        # write to file
        debug_img = ft.visualize(effective=True, show_labels=False, return_img=True)
        debug_img.save(f"test/outputs/actual/multi{pdf_no}_t{j}.png")
        df.to_csv(f"test/outputs/actual/multi{pdf_no}_t{j}.csv", index=False)
        # copy over the old csv as well
        with open(f"test/outputs/actual/multi{pdf_no}_t{j}.old.csv", "w", encoding='utf-8') as f:
            f.write(expected)
    assert expected == actual, f"Mismatch in csv files for pdf {pdf_no} and table {j}"

# class TestMultiIndex:
# relevant: 1 1, 2 2, 3 0, 7 0, 7 2
# def test_p1_t1(docs_bulk):
#     expected = """Factor,Factor,Levels,Levels,Levels,Levels
# Complete name,Coded name,Range,−1,0,1
# Temperature (°C),x1,25–35,25,30,35
# pH,x2,4–8,4,6,8
# Initial dye concen￾tration (mg L−1),x3,4–8,4,6,8
# Mesh size,x4,50–150,50,100,150
# """
#     try_jth_table(docs_bulk, 1, 1, expected)
    
# def test_p2_t2(docs_bulk):
#     expected = """ManNAc dose,Q8H for 30 days,Q8H for 30 days,Q12H for 30 days,Q12H for 30 days,Q24H for 30 days,Q24H for 30 days,is_projecting_row
# nan,Median,5th–95th percentiles,Median,5th–95th percentiles,Median,5th–95th percentiles,
# Plasma ManNAc,"Css,ave (ng/mL)",,,,,,True
# 3 g,922,501–1550,642,359–1060,365,223–570,False
# 4 g,1060,573–1790,729,404–1220,411,246–650,False
# 6 g,1290,692–2180,881,480–1480,483,281–780,False
# 10 g,1650,883–2810,1120,607–1900,603,340–989,False
# Plasma Neu5Ac,"Css,ave (ng/mL)",,,,,,True
# 3 g,633,247–2010,484,209–1420,338,174–825,False
# 4 g,702,265–2300,533,222–1610,364,181–921,False
# 6 g,818,296–2780,612,242–1930,405,190–1080,False
# 10 g,1020,344–3540,735,274–2440,464,204–1330,False
# """
#     try_jth_table(docs_bulk, 2, 2, expected)
    
# # def test_p3_t0(docs_bulk):
# #     expected = """Received: 26 January 2023,"Pau Ferri1,4, Chengeng Li 1,4, Daniel Schwalbe-Koda2 , Mingrou Xie3 ,"
# # Accepted: 8 May 2023,"Manuel Moliner 1 , Rafael Gómez-Bombarelli 2 , Mercedes Boronat 1 & Avelino Corma 1"
# # Check for updates,Approaching the level of molecular recognition of enzymes with solid catalysts
# # """
# #     try_jth_table(docs_bulk, 3, 0, expected)
    
# def test_p7_t0(docs_bulk):
#     expected = """nan,nan,nan,nan,nan,Core amino acid,Core amino acid,nan
# Patient,Genotype,Viral load,Sex,Age,70,91,rs12979860,End of treatment
# no,nan,(106 IU/ml),nan,(years),nan,nan,nan,response a
# R1,1a,4.36,M,52.6,R,C,CC,SVR
# R2,1a,6.37,M,34.9,R,C,CC,SVR
# R3,1a,7.84,M,45.8,R,C,CC,SVR
# R4,1a,7.77,F,42.3,R,C,CC,SVR
# R5,1a,7.05,M,45.3,R,C,CC,SVR
# R6,1a,7.19,F,45.5,R,C,CC,SVR
# R7,1a,5.54,F,46.9,R,C,CC,SVR
# R8,1a,5.46,M,29.1,R,C,CT,SVR
# R9,1a,6.18,M,50.7,R,C,CC,SVR
# R10,1a,6.42,M,59.9,R,C,CC,SVR
# R11,1a,5.85,M,46.4,R,C,CC,SVR
# R12,1a,7.25,M,36.4,R,C,CT,SVR
# R13,1a,6.43,M,57.5,R,C,CC,SVR
# R14,1a,6.06,M,39.2,R,C,CT,SVR
# R15,1a,6.63,F,47.1,R,C,CT,SVR
# R21,1a,5.36,F,29.6,R,C,CT,SVR
# R22,1a,5.55,F,28.7,R,C,CT,SVR
# R23,1a,6.43,F,41.2,R,C,CC,SVR
# R24,1a,6.10,M,51.3,R,C,CC,SVR
# R25,1a,7.49,F,55.7,R,C,CC,SVR
# R28,1a,7.79,M,41.5,R,C,CT,SVR
# N1,1a,6.28,M,40.5,R,C,CT,non-SVR
# N2,1a,6.25,M,50.3,R,C,CT,non-SVR
# N3,1a,6.10,M,55.9,R,C,TT,non-SVR
# N4,1a,7.05,M,47.9,R,C,TT,non-SVR
# N5,1a,5.89,M,50.8,R,C,CT,non-SVR
# N6,1a,6.42,F,48.1,P,C,CT,non-SVR
# N7,1a,6.72,M,48.9,R,C,TT,non-SVR
# N8,1a,7.35,M,54.6,R,C,TT,non-SVR
# N9,1a,6.13,F,57.8,R,C,TT,non-SVR
# N10,1a,6.72,M,54.6,R,C,TT,non-SVR
# N11,1a,6.42,M,48.0,R,C,CT,non-SVR
# N12,1a,7.32,F,48.4,R,C,CT,non-SVR
# N13,1a,6.09,M,24.3,R,C,TT,non-SVR
# N14,1a,6.31,M,35.0,R,C,CT,non-SVR
# N20,1a,6.73,F,35.0,R,C,CC,non-SVR
# N21,1a,7.15,F,45.0,R,C,CC,non-SVR
# R16,1b,4.13,F,46.5,R,M,CC,SVR
# R17,1b,4.94,M,31.5,R,M,CC,SVR
# R18,1b,5.40,F,58.7,R,M,CT,SVR
# R19,1b,6.23,F,38.4,R,L,CT,SVR
# R20,1b,7.39,F,47.8,R,M,CT,SVR
# R26,1b,7.17,M,46.6,R,L,CT,SVR
# R27,1b,6.81,M,56.8,R,M,CT,SVR
# R29,1b,7.55,M,57.0,Q,M,CT,SVR
# N15,1b,6.08,F,56.5,Q,M,CT,non-SVR
# N16,1b,6.57,F,58.5,Q,M,TT,non-SVR
# N17,1b,7.37,M,48.9,Q,L,CT,non-SVR
# N18,1b,6.69,M,62.8,Q,L,CT,non-SVR
# N19,1b,6.70,F,54.2,Q,M,CT,non-SVR
# """
#     try_jth_table(docs_bulk, 7, 0, expected)
    
# def test_p7_t2(docs_bulk):
#     expected = """,Amino acid 70,Amino acid 70,Amino acid 70,Amino acid 70,Amino acid 91,Amino acid 91,Amino acid 91,
# Genotype,Q,R,P,H,C,M,L,Total
# 1a,2%,98%,-,-,100%,-,-,920
# 1b,60%,35%,-,4%,1%,71%,28%,2022
# 2,-,100%,-,-,39%,4%,58%,83
# 3,-,93%,6%,-,99%,-,-,204
# 4,5%,95%,-,-,100%,-,-,19
# 5,86%,14%,-,-,-,-,100%,14
# 6,60%,13%,13%,15%,100%,-,-,55
# """
#     try_jth_table(docs_bulk, 7, 2, expected)

# also, pubt_p6
    