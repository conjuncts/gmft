
import json

import pytest
from gmft.detectors.common import CroppedTable
from gmft.pdf_bindings.pdfium import PyPDFium2Document

def test_tabled_format(cropped_tables):
    # passes for 0.1.4
    pytest.skip("skipping tabled")

    from gmft.formatters.with_tabled import TabledFormatter
    tf = TabledFormatter()
    doc = PyPDFium2Document('test/samples/tatr.pdf')
    ct = CroppedTable.from_dict(cropped_tables['pubt_p4'], doc[3])

    # ct.page.page_number = 0
    ft = tf.extract(ct)
    result = ft.df().to_csv(index=False, sep='\t', lineterminator='\n')
    print(result)
    assert result == """Dataset	Input	# Tables	Cell	Cell.1	Cell.2	Row & Column	Canonical
	Modality		Topology	Content	Location	Location	Structure
TableBank [9]	Image	145K	X				
SciTSR [3]	PDF∗	15K	X	X			
PubTabNet [22, 23]	Image	510K‡	X	X	X†		
FinTabNet [22]	PDF∗	113K	X	X	X†		
PubTables-1M (ours)	PDF∗	948K	X	X	X	X	X
"""