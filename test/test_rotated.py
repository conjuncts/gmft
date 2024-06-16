import json
import pytest
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import RotatedCroppedTable, TableDetector
from gmft.table_function import TATRTableFormatter


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


def test_rotated_p8(doc_9, detector, formatter):
    """
    This tests everything: ie. table detection, structure recognition, and df formatting.
    """

    # table detection    
    tables = detector.extract(doc_9[8-1])
    assert len(tables) == 1
    
    table = tables[0]
    assert isinstance(table, RotatedCroppedTable)
    
    assert table.angle == 90
    
    # structure recognition and df formatting
    ft = formatter.extract(table)
    df = ft.df()
    df.to_csv("test/outputs/actual/pdf9_p7.csv", index=True)
#     assert df.to_csv() == """\
# ,Dataset,Input Modality,# Tables,Cell Topology,Cell Content,Cell Location,Row & Column Location,Canonical Structure\r
# 0,TableBank [9],Image,145K,X,,,,\r
# 1,SciTSR [3],PDF∗,15K,X,X,,,\r
# 2,"PubTabNet [22, 23]",Image,510K‡,X,X,X†,,\r
# 3,FinTabNet [22],PDF∗,113K,X,X,X†,,\r
# 4,PubTables-1M (ours),PDF∗,948K,X,X,X,X,X\r
# """
