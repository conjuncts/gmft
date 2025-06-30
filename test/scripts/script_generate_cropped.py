from gmft.detectors.base import CroppedTable
from gmft.pdf_bindings.pdfium import PyPDFium2Document


def generate_cropped_positions_tsv():
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
    with open("data/test/references/tiny_cropped_positions.tsv", "w") as f:
        for pos in table.text_positions():
            f.write("\t".join(map(str, pos)) + "\n")
