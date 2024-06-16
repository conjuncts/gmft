import json
import pytest
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import TableDetector
from gmft.table_function import TATRTableFormatter


@pytest.fixture
def doc_tatr():
    doc = PyPDFium2Document("test/samples/tatr.pdf")
    yield doc
    # cleanup
    doc.close()


def test_tatr_p4(doc_tatr, detector, formatter):
    """
    This tests everything: ie. table detection, structure recognition, and df formatting.
    """

    # table detection    
    tables_p4 = detector.extract(doc_tatr[4-1])
    assert len(tables_p4) == 1
    

    
    # with open("test/outputs/actual/tatr_p4.info", "w") as f:
    #     json.dump(tables_p4[0].to_dict(), f, indent=4)
    
    # with open("test/outputs/actual/tatr_p7.info", "w") as f:
    #     json.dump(tables_p7[0].to_dict(), f, indent=4)
        
    # with open("test/outputs/actual/tatr_p8.info", "w") as f:
    #     json.dump(tables_p8[0].to_dict(), f, indent=4)
    
    # structure recognition and df formatting
    ft_4 = formatter.extract(tables_p4[0])
    df_4 = ft_4.df()
    df_4.to_csv("test/outputs/actual/tatr_p4.csv", index=True)
    assert df_4.to_csv() == """\
,Dataset,Input Modality,# Tables,Cell Topology,Cell Content,Cell Location,Row & Column Location,Canonical Structure\r
0,TableBank [9],Image,145K,X,,,,\r
1,SciTSR [3],PDF∗,15K,X,X,,,\r
2,"PubTabNet [22, 23]",Image,510K‡,X,X,X†,,\r
3,FinTabNet [22],PDF∗,113K,X,X,X†,,\r
4,PubTables-1M (ours),PDF∗,948K,X,X,X,X,X\r
"""


    
def test_tatr_p7(doc_tatr, detector, formatter):
    tables_p7 = detector.extract(doc_tatr[7-1])
    assert len(tables_p7) == 1
    
    ft_7 = formatter.extract(tables_p7[0])
    df_7 = ft_7.df()
    df_7.to_csv("test/outputs/actual/tatr_p7.csv", index=True)
    assert df_7.to_csv() == """\
,Task,Model,AP,AP50,AP75,AR\r
0,TD,Faster R-CNN,0.825,0.985,0.927,0.866\r
1,,DETR,0.966,0.995,0.988,0.981\r
2,TSR + FA,Faster R-CNN,0.722,0.815,0.785,0.762\r
3,,DETR,0.912,0.971,0.948,0.942\r
"""

def test_tatr_p8(doc_tatr, detector, formatter):
    tables_p8 = detector.extract(doc_tatr[8-1])
    assert len(tables_p8) == 1
    ft_8 = formatter.extract(tables_p8[0])
    df_8 = ft_8.df()
    df_8.to_csv("test/outputs/actual/tatr_p8.csv", index=False)
    assert df_8.to_csv(index=False) == """\
Test Data,Model,Table Category,AccCont,GriTSTop,GriTSCont,GriTSLoc,AdjCont\r
Non-Canonical,DETR-NC,Simple,0.8678,0.9872,0.9859,0.9821,0.9801\r
,,Complex,0.5360,0.9600,0.9618,0.9444,0.9505\r
,,All,0.7336,0.9762,0.9761,0.9668,0.9681\r
Canonical,DETR-NC,Simple,0.9349,0.9933,0.9920,0.9900,0.9865\r
,,Complex,0.2712,0.9257,0.9290,0.9044,0.9162\r
,,All,0.5851,0.9576,0.9588,0.9449,0.9494\r
,Faster R-CNN,Simple,0.0867,0.8682,0.8571,0.6869,0.8024\r
,,Complex,0.1193,0.8556,0.8507,0.7518,0.7734\r
,,All,0.1039,0.8616,0.8538,0.7211,0.7871\r
,DETR,Simple,0.9468,0.9949,0.9938,0.9922,0.9893\r
,,Complex,0.6944,0.9752,0.9763,0.9654,0.9667\r
,,All,0.8138,0.9845,0.9846,0.9781,0.9774\r
"""
    
