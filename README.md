# gmft

[![Documentation Status](https://readthedocs.org/projects/gmft/badge/?version=latest)](https://gmft.readthedocs.io/en/latest/?badge=latest)

There are many pdfs out there, and many of those pdfs have tables. But despite a plethora of table extraction options, there is still no definitive extraction method. 

# About

gmft converts pdf tables to [many formats](#many-formats). It is lightweight, modular, and performant. Batteries included: it just works, offering strong performance with the default settings. 

It relies on microsoft's [Table Transformers](https://github.com/microsoft/table-transformer), qualitatively the most performant and reliable of the [many alternatives](https://docs.google.com/spreadsheets/d/15WrU_Pr8pkYKW55LiMRf-tSRPR_KgiWgNCvY-pdbY7Q).

Install: `pip install gmft`

Quickstarts: [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb), [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb), [readthedocs](https://gmft.readthedocs.io/en/latest/usage.html).

Documentation: [readthedocs](https://gmft.readthedocs.io/en/latest/)

# Why should I use gmft?

Fast, lightweight, and performant, gmft is a great choice for extracting tables from pdfs. 

The extraction quality is superb: check out the [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb) notebook for approximate quality. When testing the same tables across many table extraction options, gmft fares [extremely well](https://drive.google.com/drive/u/0/folders/1yyWsVZBTDloekuoIPFjX6Egnw55wyosl).


## Many Formats

We support the following export options:
- **Pandas dataframe**
- By extension: markdown, latex, html, csv, json, etc. 
- List of text + positions
- Cropped image of table
- Table caption

Cropped images can be passed into a vision recognizer, like: 
- GPT-4 vision
- Mathpix/Adobe/Google/Amazon/Azure/etc.
- Or saved to disk for human evaluation

## Lightweight

gmft is very lightweight. It can run on cpu - no GPU necessary.

### High throughput

Benchmark using Colab's **cpu** indicates ~1.381 s/page; converting to df takes ~1.168 s/table. This makes gmft about **10x** [**faster**](https://docs.google.com/spreadsheets/d/15WrU_Pr8pkYKW55LiMRf-tSRPR_KgiWgNCvY-pdbY7Q) than alternatives like unstructured, nougat, and open-parse/unitable on cpu. 

- The base model, Smock et al.'s [Table Transformer](https://arxiv.org/abs/2110.00061), is very efficient.
- gmft focuses on table extraction, so figures, titles, sections, etc. are not extracted. 
- In most cases, OCR is not necessary; pdfs already contain text positional data. Using this existing data drastically speeds up inference. For images or scanned pdfs, bboxes can be exported for further processing. 
- PyPDFium2 is chosen for its [high throughput](https://github.com/py-pdf/benchmarks) and permissive license.


### Few dependencies

gmft does **not** require any external dependencies (detectron2, poppler, paddleocr, tesseract etc.)

To install gmft, first install [transformers](https://pypi.org/project/transformers/) and [pytorch](https://pytorch.org/get-started/locally/) with the necessary GPU/CPU options. We also rely on [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [transformers](https://github.com/huggingface/transformers).

## Dependable

The base model is Microsoft's Table Transformer (TATR) pretrained on PubTables-1M, which works best with scientific papers. TATR handles **implicit table structure** very well. Current failure modes include OCR issues, merged cells, or false positives. Even so, the text is highly useable, and alignment of a value to its row/column header remains **very accurate** because of the underlying procedural algorithm.

We invite you to explore the [comparison notebooks](https://drive.google.com/drive/u/0/folders/1yyWsVZBTDloekuoIPFjX6Egnw55wyosl) to survey use cases and compare results.

As of gmft v0.3, the library supports multiple-column headers (`TATRFormatConfig.enable_multi_header = True`), spanning cells (`TATRFormatConfig.semantic_spanning_cells = True`), and rotated tables.

# Why should I not use gmft?

gmft focuses on tables, and aims to maximize performance on tables alone. If you need to extract other document features like figures or table of contents, you may want a different tool. You should instead check out: (in no particular order) [marker](https://github.com/VikParuchuri/marker), [nougat](https://github.com/facebookresearch/nougat), [open-parse](https://github.com/Filimoa/open-parse), [docling](https://github.com/docling-project/docling), [unstructured](https://github.com/Unstructured-IO/unstructured), [surya](https://github.com/VikParuchuri/surya), [deepdoctection](https://github.com/deepdoctection/deepdoctection), [DocTR](https://github.com/mindee/doctr). For table detection, [img2table](https://github.com/xavctn/img2table) is excellent for tables with explicit (solid) cell boundaries.

Current limitations include: false positives (references, indexes, and large columnar text), false negatives, and no OCR support.


# Quickstart

See the [docs](https://gmft.readthedocs.io/en/latest/usage.html) and the [config guide](https://gmft.readthedocs.io/en/latest/config.html) for more information. The [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb) and [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb) contain more comprehensive code examples.

```python
# new in v0.3: gmft.auto
from gmft.auto import CroppedTable, TableDetector, AutoTableFormatter, AutoTableDetector
from gmft.pdf_bindings import PyPDFium2Document

detector = AutoTableDetector()
formatter = AutoTableFormatter()

def ingest_pdf(pdf_path): # produces list[CroppedTable]
    doc = PyPDFium2Document(pdf_path)
    tables = []
    for page in doc:
        tables += detector.extract(page)
    return tables, doc

tables, doc = ingest_pdf("path/to/pdf.pdf")
doc.close() # once you're done with the document
```

## Configuration

See the [config guide](https://gmft.readthedocs.io/en/latest/config.html) for discussion on gmft settings.

# Development

```bash
git clone https://github.com/conjuncts/gmft
cd gmft
pip install -e .
pip install pytest
```


Run tests:

tests are in ./test directory

Build docs:

```bash
cd docs
make html
```

# What does gmft stand for?

**g**ive

**m**e

**f**ormatted

**tables**!

# Acknowledgements

- I gratefully acknowledge the support of Vanderbilt Data Science Institute and the [Zhongyue Yang Lab](https://lab.vanderbilt.edu/zyang-lab/) at Vanderbilt.
- The library builds upon work by:
    - Smock, Brandon, Rohith Pesala, and Robin Abraham. "[PubTables-1M](https://arxiv.org/abs/2110.00061): Towards comprehensive table extraction from unstructured documents." Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2022.
    - Niels Rogge from huggingface.


## License

GMFT is released under MIT. 

PyMuPDF support is available in a [separate repository](https://github.com/conjuncts/gmft_pymupdf) in observance of pymupdf's AGPL 3.0 license.

