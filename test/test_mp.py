import multiprocessing as mp
import pickle

import pytest
from gmft.auto import CroppedTable
from gmft.formatters.tatr import TATRFormattedTable

from .test_serial import tiny_info


def _pickle_worker(table: CroppedTable) -> str:
    return table.text()


def test_pickle_roundtrip_cropped_table(doc_tiny):
    page = doc_tiny[0]
    table = CroppedTable(page, (10, 12, 300, 150), 0.9, 0)
    roundtrip: CroppedTable = pickle.loads(pickle.dumps(table))
    assert roundtrip.page.get_filename() == "data/pdfs/tiny.pdf"
    assert roundtrip.page.page_number == 0
    assert roundtrip.bbox == table.bbox
    assert roundtrip.text() == table.text()
    item = next(roundtrip.page.get_positions_and_text())
    assert item == next(table.page.get_positions_and_text())


def test_pickle_roundtrip_tatr_formatted_table(doc_tiny):
    page = doc_tiny[0]
    table = TATRFormattedTable.from_dict(tiny_info, page)
    roundtrip = pickle.loads(pickle.dumps(table))
    assert roundtrip.to_dict() == tiny_info
    csv_str = roundtrip.df().to_csv(index=False, lineterminator="\n")
    assert (
        csv_str
        == """Name,Celsius,Fahrenheit
Water Freezing Point,0,32
Water Boiling Point,100,212
Body Temperature,37,98.6
"""
    )


@pytest.mark.skip("slow")
def test_multiprocessing_spawn_pickle_smoke(doc_tiny):
    page = doc_tiny[0]
    tables = [
        CroppedTable(page, (10, 12, 300, 150), 0.9, 0),
        CroppedTable(page, (10, 12, 300, 200), 0.9, 0),
    ]
    ctx = mp.get_context("spawn")
    with ctx.Pool(2) as pool:
        results = pool.map(_pickle_worker, tables)
    assert len(results) == 2
    assert all(isinstance(text, str) and text for text in results)
