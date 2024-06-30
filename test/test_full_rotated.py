import json
import pytest
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import RotatedCroppedTable, TableDetector
from gmft.table_function import TATRFormattedTable, AutoTableFormatter


# @pytest.fixture
# def doc_8():
#     # note: this document is poor because the text bboxes are intrinsically misaligned
#     # (tested with both PyPDFium2 and PyMuPDF)
#     doc = PyPDFium2Document("test/samples/8.pdf")
#     yield doc
#     # cleanup
#     doc.close()

@pytest.fixture
def doc_9():
    doc = PyPDFium2Document("test/samples/9.pdf")
    yield doc
    # cleanup
    doc.close()


def test_rotated(doc_9, detector, formatter):
    
    # Note: page 8 is WIP
    # page 9 is rotated table
    # page 10 is smaller

    # table detection    
    tables = detector.extract(doc_9[9-1])
    assert len(tables) == 1
    
    table = tables[0]
    assert isinstance(table, RotatedCroppedTable)
    
    assert table.angle == 90

def test_rotated_df(doc_9):
    with open("test/outputs/bulk/pdf9_t4.info", encoding="utf-8") as f:
        as_dict = json.load(f)
    page_no = as_dict["page_no"]
    page = doc_9[page_no]
    ft = TATRFormattedTable.from_dict(as_dict, page)
    
    assert ft.angle == 90
    
    df = ft.df()
    df.to_csv("test/outputs/actual/pdf9_t4.csv", index=False)
    assert df.to_csv(index=False, lineterminator='\n') == """\
Electrode nanomodification,Modification method,ET,Surface modification,Surface functionality,Measurement method,pH and substrate concentration,Current density (μAcm−2 ),Reference
GE+SWCNT+CDH;,Drop-casting,DET,Co-immobilisation with CNTs,Not studied,LSV; 1 mV s−1,"5.0, 100 mM lactose",45,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,DET,Co-immobilisation with CNTs,Not studied,LSV; 1 mV s−1,"5.5, 100 mM lactose",30,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,DET,Co-immobilisation with CNTs,Not studied,LSV; 1 mV s−1,"6.0, 100 mM lactose",13,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,MET,Co-immobilisation with CNTs+,Not studied,LSV; 0.2 mV s−1,"3.5, 100 mM lactose",300,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,MET,PEGDGE Co-immobilisation with CNTs+,Not studied,LSV; 0.2 mV s−1,"4.0, 100 mM lactose",500,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,MET,PEGDGE Co-immobilisation with CNTs+,Not studied,LSV; 0.2 mV s−1,"4.5, 100 mM lactose",650,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,MET,PEGDGE Co-immobilisation with CNTs+,Not studied,LSV; 0.2 mV s−1,"5.0, 100 mM lactose",700,[93]
PsCDH GE+SWCNT+CDH;,Drop-casting,MET,PEGDGE Co-immobilisation with CNTs+,Not studied,LSV; 0.2 mV s−1,"6.0, 100 mM lactose",700,[93]
PsCDH Au+AuNP; CtCDH,Drop-casting,DET,PEGDGE ATP/MBA+GA,OH,LSV; 2 mV s−1,"7.4, 5 mM lactose; 100 mM",40; 26,[49]
Au+AuNP; CtCDH,Drop-casting,DET,ATP/MBA+GA,OH,LSV 2 mV s−1,"glucose 7.4, 5 mM glucose",7.5,[51]
SPCE+SWCNT;,Drop-casting,DET,PEDGDE,Not studied,FIA,"7.4, 300 mM glucose",18.41,[57]
CtCDH,,,,,,,,
SPCE+MWCNT;,Drop-casting,DET,PEDGDE,Not studied,FIA,"7.4, 300 mM glucose",15.58,[57]
CtCDH,,,,,,,,
MtCDH,,DET,PEGDGE,Not studied,FIA,10 mM lactose,6.16,
GE+SWCNT;,Drop-casting,,,,,"5.3,",,[89]
GE+SWCNT; MtCDH,Drop-casting,DET,PEGDGE,Not studied,LSV; 1 mV s−1,"4.5, 100 mM lactose",5,[89]
GE+SWCNT; MtCDH,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,LSV; 1 mV s−1,"3.5, 100 mM lactose",68.4,[89]
GE+SWCNT; MtCDH,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,LSV; 1 mV s−1,"4.5, 100 mM lactose",102.6,[89]
GE+SWCNT; MtCDH,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,LSV; 1 mV s−1,"6.0, 100 mM lactose",205,[89]
GE+SWCNT,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,LSV; 1 mV s−1,"7.0, 100 mM lactose",465,[89]
GE+SWCNT; MtCDH,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,CV; 1 mV s−1,"8.0, 100 mM lactose",800,[89]
GE+SWCNT; MtCDH,Drop-casting,MET,Os-polymer+PEGDGE,Not studied,CV; 1 mV s−1,"7.4, 100 mM lactose; 50 mM glucose",450; 100,[89]
GC+SWCNTs; CtCDH,Drop-casting,DET,p-Aminobenzoic acid,COOH,CV; 1 mV s−1,"7.4, 10 mM lactose; 50 mM glucose",30; 15,(Ortiz et al. submitted)
GC+SWCNTs; CtCDH,Drop-casting,DET,Aniline,None,CV; 1 mV s−1,"7.4, 10 mM lactose; 50 mM glucose",21; 9,(Ortiz et al. submitted)
GC+SWCNTs; CtCDH,Drop-casting,DET,p-Phenylenediamine,NH2,CV; 1 mV s−1,"7.4, 10 mM lactose; 50 mM glucose",25; 13,(Ortiz et al. submitted)
GC+SWCNTs; CtCDH,Drop-casting,DET,p-Phenylenediamine+GA,NH2,CV; 1 mV s−1,"7.4, 10 mM lactose; 50 mM glucose",43; 21,(Ortiz et al. submitted)
"""
    
    
    
    
    # structure recognition and df formatting
    # ft = formatter.extract(table)
    # df = ft.df()
    # df.to_csv("test/outputs/actual/pdf9_p7.csv", index=True)
#     assert df.to_csv() == """\
# ,Dataset,Input Modality,# Tables,Cell Topology,Cell Content,Cell Location,Row & Column Location,Canonical Structure\r
# 0,TableBank [9],Image,145K,X,,,,\r
# 1,SciTSR [3],PDF∗,15K,X,X,,,\r
# 2,"PubTabNet [22, 23]",Image,510K‡,X,X,X†,,\r
# 3,FinTabNet [22],PDF∗,113K,X,X,X†,,\r
# 4,PubTables-1M (ours),PDF∗,948K,X,X,X,X,X\r
# """
