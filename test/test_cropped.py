# test to_dict and from_dict


import pytest
import gmft
from gmft.pdf_bindings import PyPDFium2Document
from gmft.table_detection import CroppedTable, RotatedCroppedTable


def are_bboxes_close(reference, actual, EPS=0.01):
    for ref, pos in zip(reference, actual):
        ref_bbox = ref[:4]
        ref_text = ref[4]
        act_bbox = pos[:4]
        act_text = pos[4]
        assert ref_text == act_text, (
            f"Different text: expected {ref_text}, got {act_text}"
        )
        for ref, pos in zip(ref_bbox, act_bbox):
            # ref = float(ref)
            # pos = float(pos)
            # assert abs(ref - pos) < EPS, f"Different positions: expected {ref}, got {pos}"
            assert ref == pytest.approx(pos, EPS), (
                f"Different positions: expected {ref}, got {pos}"
            )


def test_CroppedTable_positions(doc_tiny):
    page = doc_tiny[0]
    table = CroppedTable.from_dict(
        {
            "filename": "data/pdfs/tiny.pdf",
            "page_no": 0,
            "bbox": (10, 12, 300, 150),
            "confidence_score": 0.9,
            "label": 0,
        },
        page,
    )

    # get reference positions from tiny_pdfium.txt
    with open("test/outputs/tiny_cropped_positions.tsv") as f:
        reference = f.readlines()
    for i, line in enumerate(reference):
        x0, y0, x1, y1, text = line.strip().split("\t")
        reference[i] = (float(x0), float(y0), float(x1), float(y1), text)

    actual = list(table.text_positions())

    EPS = 0.001
    are_bboxes_close(reference, actual, EPS)

    reference = [(a - 10, b - 12, c - 10, d - 12, txt) for a, b, c, d, txt in reference]
    actual = list(table.text_positions(remove_table_offset=True))
    are_bboxes_close(reference, actual, EPS)

    # outside
    with open("data/test/references/tiny_pdfium.tsv") as f:
        reference = list(f.readlines())
    reference = [reference[9], *reference[14:]]
    for i, line in enumerate(reference):
        x0, y0, x1, y1, text = line.strip().split("\t")
        reference[i] = (float(x0), float(y0), float(x1), float(y1), text)

    actual = list(table.text_positions(outside=True))
    are_bboxes_close(reference, actual, EPS)


def test_CroppedTable_text(doc_tiny):
    page = doc_tiny[0]
    table = CroppedTable.from_dict(
        {
            "filename": "data/pdfs/tiny.pdf",
            "page_no": 0,
            "bbox": (10, 12, 300, 200),
            "confidence_score": 0.9,
            "label": 0,
        },
        page,
    )

    assert (
        table.text()
        == """Simple document
Lorem ipsum dolor sit amet, consectetur adipiscing
Table 1. Selected Numbers
Name Celsius
Water Freezing Point 0"""
    )


def test_RotatedCroppedTable_positions(doc_tiny):
    page = doc_tiny[0]
    table = RotatedCroppedTable.from_dict(
        {
            "filename": "data/pdfs/tiny.pdf",
            "page_no": 0,
            "bbox": (10, 12, 300, 150),
            "confidence_score": 0.9,
            "label": 0,
            "angle": 0,
        },
        page,
    )

    # get reference positions from tiny_pdfium.txt
    with open("test/outputs/tiny_cropped_positions.tsv", "r") as f:
        reference = f.readlines()
    for i, line in enumerate(reference):
        x0, y0, x1, y1, text = line.strip().split("\t")
        reference[i] = (float(x0), float(y0), float(x1), float(y1), text)

    actual = list(table.text_positions())

    EPS = 0.001
    are_bboxes_close(reference, actual, EPS)

    reference = [(a - 10, b - 12, c - 10, d - 12, txt) for a, b, c, d, txt in reference]
    actual = list(table.text_positions(remove_table_offset=True))
    are_bboxes_close(reference, actual, EPS)

    # outside
    with open("data/test/references/tiny_pdfium.tsv", "r") as f:
        reference = list(f.readlines())
    reference = [reference[9], *reference[14:]]
    for i, line in enumerate(reference):
        x0, y0, x1, y1, text = line.strip().split("\t")
        reference[i] = (float(x0), float(y0), float(x1), float(y1), text)

    actual = list(table.text_positions(outside=True))
    are_bboxes_close(reference, actual, EPS)


def test_RotatedCroppedTable_text(doc_tiny):
    page = doc_tiny[0]
    table = RotatedCroppedTable.from_dict(
        {
            "filename": "data/pdfs/tiny.pdf",
            "page_no": 0,
            "bbox": (10, 12, 300, 200),
            "confidence_score": 0.9,
            "label": 0,
            "angle": 0,
        },
        page,
    )

    assert (
        table.text()
        == """Simple document
Lorem ipsum dolor sit amet, consectetur adipiscing
Table 1. Selected Numbers
Name Celsius
Water Freezing Point 0"""
    )


if __name__ == "__main__":
    page = PyPDFium2Document("data/pdfs/tiny.pdf")[0]
    table = CroppedTable.from_dict(
        {
            "filename": "data/pdfs/tiny.pdf",
            "page_no": 0,
            "bbox": (10, 10, 300, 150),
            "confidence_score": 0.9,
            "label": 0,
        },
        page,
    )

    # create the tsv
    with open("test/outputs/tiny_cropped_positions.tsv", "w") as f:
        for pos in table.text_positions():
            f.write("\t".join(map(str, pos)) + "\n")
