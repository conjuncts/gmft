import json
import pytest
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.table_detection import CroppedTable, TableDetector
from gmft.table_function import TATRFormattedTable




def test_pubt_p4(doc_pubt, detector, formatter):
    """
    This tests everything: ie. table detection, structure recognition, and df formatting.
    """

    # table detection    
    tables_p4 = detector.extract(doc_pubt[4-1])
    assert len(tables_p4) == 1
    
    # structure recognition and df formatting
    ft_4 = formatter.extract(tables_p4[0])
    df_4 = ft_4.df()
    actual = df_4.to_csv(lineterminator='\n')
    expected = """\
,Dataset,Input Modality,# Tables,Cell Topology,Cell Content,Cell Location,Row & Column Location,Canonical Structure
0,TableBank [9],Image,145K,X,,,,
1,SciTSR [3],PDF∗,15K,X,X,,,
2,"PubTabNet [22, 23]",Image,510K‡,X,X,X†,,
3,FinTabNet [22],PDF∗,113K,X,X,X†,,
4,PubTables-1M (ours),PDF∗,948K,X,X,X,X,X
"""
    if actual != expected:
        ft_4.visualize(effective=True, show_labels=False, return_img=True).save("test/outputs/actual/pubt_p4.png")
        df_4.to_csv("test/outputs/actual/pubt_p4.csv", index=True)
        assert actual == expected


def test_pubt_p6(doc_pubt, tatr_tables):
    """
    This tests solely df formatting.
    """

    # table detection    
    ft = TATRFormattedTable.from_dict(tatr_tables['pubt_p6'], doc_pubt[6-1])    

    df = ft.df()
    actual = df.to_csv(lineterminator='\n')
    expected = """\
,Dataset,Total Tables \\nInvestigated†,Total Tables \\nwith a PRH∗,Total,Tables with an oversegmented \\n% (of total with a PRH),PRH \\n% (of total investigated)
0,SciTSR,"10,431",342,54,15.79%,0.52%
1,PubTabNet,"422,491","100,159","58,747",58.65%,13.90%
2,FinTabNet,"70,028","25,637","25,348",98.87%,36.20%
3,PubTables-1M (ours),"761,262","153,705",0,0%,0%
"""
    if actual != expected:
        ft.visualize(effective=True, show_labels=False, return_img=True).save("test/outputs/actual/pubt_p6.png")
        df.to_csv("test/outputs/actual/pubt_p6.csv", index=True)
        assert actual == expected


    
def test_pubt_p7(doc_pubt, detector, formatter):
    tables_p7 = detector.extract(doc_pubt[7-1])
    assert len(tables_p7) == 1
    
    ft_7 = formatter.extract(tables_p7[0])
    df_7 = ft_7.df()
    actual = df_7.to_csv(lineterminator='\n') 
    expected = """\
,Task,Model,AP,AP50,AP75,AR
0,TD,Faster R-CNN,0.825,0.985,0.927,0.866
1,,DETR,0.966,0.995,0.988,0.981
2,TSR + FA,Faster R-CNN,0.722,0.815,0.785,0.762
3,,DETR,0.912,0.971,0.948,0.942
"""
    if actual != expected:
        ft_7.visualize(effective=True, show_labels=False, return_img=True).save("test/outputs/actual/pubt_p7.png")
        df_7.to_csv("test/outputs/actual/pubt_p7.csv", index=True)
        assert actual == expected

def test_pubt_p8(doc_pubt, detector, formatter):
    tables_p8 = detector.extract(doc_pubt[8-1])
    assert len(tables_p8) == 1
    ft_8 = formatter.extract(tables_p8[0])
    df_8 = ft_8.df()
    actual = df_8.to_csv(index=False, lineterminator='\n') 
    expected = """\
Test Data,Model,Table Category,AccCont,GriTSTop,GriTSCont,GriTSLoc,AdjCont
Non-Canonical,DETR-NC,Simple,0.8678,0.9872,0.9859,0.9821,0.9801
,,Complex,0.5360,0.9600,0.9618,0.9444,0.9505
,,All,0.7336,0.9762,0.9761,0.9668,0.9681
Canonical,DETR-NC,Simple,0.9349,0.9933,0.9920,0.9900,0.9865
,,Complex,0.2712,0.9257,0.9290,0.9044,0.9162
,,All,0.5851,0.9576,0.9588,0.9449,0.9494
,Faster R-CNN,Simple,0.0867,0.8682,0.8571,0.6869,0.8024
,,Complex,0.1193,0.8556,0.8507,0.7518,0.7734
,,All,0.1039,0.8616,0.8538,0.7211,0.7871
,DETR,Simple,0.9468,0.9949,0.9938,0.9922,0.9893
,,Complex,0.6944,0.9752,0.9763,0.9654,0.9667
,,All,0.8138,0.9845,0.9846,0.9781,0.9774
"""
    if actual != expected:
        ft_8.visualize(effective=True, show_labels=False, return_img=True).save("test/outputs/actual/pubt_p8.png")
        df_8.to_csv("test/outputs/actual/pubt_p8.csv", index=False)
        assert actual == expected
    
