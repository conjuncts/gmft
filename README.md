# gmft
**g**ive

**m**e

**f**ormatted

**tables**!

[![Documentation Status](https://readthedocs.org/projects/gmft/badge/?version=latest)](https://gmft.readthedocs.io/en/latest/?badge=latest)

There are many pdfs out there, and many of those pdfs have tables. But despite a plethora of table extraction options, there is still no definitive extraction method. 

## About

gmft is a toolkit for converting pdf tables to [many formats](#many-formats). It is lightweight, modular, and performant.

Batteries included: it *just works*, offering strong performance with the default settings. 

It relies on microsoft's [Table Transformers](https://github.com/microsoft/table-transformer), qualitatively the most performant and reliable of the [many alternatives](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg).

Install: `pip install gmft`

Quickstarts: [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb), [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb), [readthedocs](https://gmft.readthedocs.io/en/latest/usage.html).

Documentation: [readthedocs](https://gmft.readthedocs.io/en/latest/)

# Why use gmft?

Fast, lightweight, and performant, gmft is a great choice for extracting tables from pdfs. 

The extraction quality is superb: check out the [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb) notebook for approximate quality. When testing the same tables across many table extraction options, gmft fares [extremely well](https://drive.google.com/drive/u/0/folders/114bWRj5H4aE-BA5UKH9S5ol8LC6vhqfR), with arguably the best extraction quality.

## Many Formats

gmft supports the following export options:
- Pandas dataframe (!)
- By extension: markdown, latex, html, csv, json, etc. 
- List of text + positions
- Cropped image of table
- Table caption

Cropped images can be passed into a vision recognizer, like: 
- GPT-4 vision
- Mathpix/Adobe/Google/Amazon/Azure/etc.

Cropped images are useful for verifying correctness of output.

## Lightweight

### No GPU necessary

Because of the few dependencies, gmft is very lightweight. The architecture (Table Transformer) allows gmft to run on cpu. 

### High throughput

Benchmark using Colab's **cpu** indicates an approximate rate of ~1.381 s/page; converting to df takes ~1.168 s/table. See the comparison here. This makes gmft about **10x** [**faster**](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg) than alternatives like unstructured, nougat, and open-parse/unitable on cpu. Here's how: 

- The base model, Smock et al.'s [Table Transformer](https://arxiv.org/abs/2110.00061), is blazing fast.
- gmft focuses on table extraction, so figures, titles, sections, etc. are not extracted. 
- In most cases, OCR is not necessary; pdfs already contain text positional data. Using this existing data drastically speeds up inference. With that being said, gmft can still extract tables from images and scanned pdfs through the image output. 
- PyPDFium2 is chosen for its [high throughput](https://github.com/py-pdf/benchmarks) and permissive license.



### Few dependencies

Many pdf extractors require detectron2, poppler, paddleocr, tesseract etc., which may require external installation. Detectron2 is particularly difficult to install on windows. OCR models may require tesseract or paddleocr.

To install gmft, install [transformers](https://pypi.org/project/transformers/) and [pytorch](https://pytorch.org/get-started/locally/) with the necessary GPU/CPU options. Then run `pip install gmft`. 

gmft relies on [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [transformers](https://github.com/huggingface/transformers). On the first run, gmft downloads Microsoft's TATR from huggingface, which requires ~270mB total and is saved to `~/.cache/huggingface/hub/models--microsoft--table-{transformer-detection, structure-recognition}` and `~/.cache/huggingface/hub/models--timm--resnet18.a1_in1k`.


## Reliable

gmft uses Microsoft's Table Transformer (TATR), which is trained on a diverse dataset PubTables-1M. Many alternative methods were considered, and TATR was ultimately chosen for several reasons, among them high reliability. 

Compared to existing options, the performance is *especially good* on tables with **implicit structure**, like those in scientific papers. When the model fails, it is usually an OCR issue, merged cell, or false positive. Even in these cases, the text is still highly useable. **Alignment** of a value to its row/column header tends to be **very accurate** because of the underlying procedural algorithm.

We invite you to explore the [comparison notebooks](https://drive.google.com/drive/u/0/folders/114bWRj5H4aE-BA5UKH9S5ol8LC6vhqfR) to survey use cases and compare results.


## Configurable

See the [config guide](https://gmft.readthedocs.io/en/latest/config.html) for discussion on gmft settings.

The library aims to be configurable through subclassing. By subclassing the BasePDFDocument and BasePage classes, gmft's design supports interchanging PDF providers like PyMuPDF and PyPDFium2.

By subclassing BaseDetector and BaseFormatter, the library is extensible to different table detection and structuring methods. By default, TATRDetector, TATRFormatter, and Img2TableDetector are supported.

# Quickstart

See the [docs](https://gmft.readthedocs.io/en/latest/usage.html) and the [config guide](https://gmft.readthedocs.io/en/latest/config.html) for more information. The [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb) and [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb) contain more comprehensive code examples.

```python
# new in v0.3: gmft.auto
from gmft.auto import CroppedTable, TableDetector, AutoTableFormatter
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

# Discussion


## New features

In `v0.3`, integrated support of other providers like Img2Table.

[Experimental] Multi-indices (multiple column headers) are now supported in `v0.2` with `TATRFormatConfig.enable_multi_header = True`.

[Experimental] Spanning cells are now supported in `v0.2` with `TATRFormatConfig.semantic_spanning_cells = True`.

Rotated tables are now supported in `v0.0.4`.


## Limitations

False detection of references, indexes, and large columnar text.
Slightly askew tables.
False negatives.

# Acknowledgements

A tremendous thank you to the PubTables1M (and Table Transformer) authors: Brandon Smock, Rohith Pesala, and Robin Abraham, for making gmft possible. The image->csv step is based on from TATR's inference.py code, but it has been rewritten with some adjustments for ease of use.

Thank you to Niels Rogge for porting TATR to huggingface and writing the [visualization code](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb).

## Alternatives

See [comparison](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg).

Gmft focuses highly on pdf tables. For tables, another great option is [img2table](https://github.com/xavctn/img2table), which is non-deep and attains great results.

[Nougat](https://github.com/facebookresearch/nougat) is excellent for both pdf table extraction and document understanding. It outputs full mathpix markdown (.mmd), which includes latex formulas, bold/italics, and fully latex-typeset tables. However, a gpu is highly recommended. 

[marker](https://github.com/VikParuchuri/marker) similar to Nougat, but is more recent and offers better performance and accuracy.

For general document understanding, I recommend checking out [open-parse](https://github.com/Filimoa/open-parse), [unstructured](https://github.com/Unstructured-IO/unstructured), [surya](https://github.com/VikParuchuri/surya), [deepdoctection](https://github.com/deepdoctection/deepdoctection), and [DocTR](https://github.com/mindee/doctr). Open-parse and unstructured do quite well on the same example pdfs in terms of extraction quality. 

Open-parse allows extraction of auxiliary information like headers, paragraphs, etc., useful for RAG. In addition to the Table Transformer, open-parse also offers UniTable, a newer model which achieves SOTA results in datasets like PubLayNet and FinTabNet. Though UniTable support in gmft is slated for the future, UniTable is much larger (~1.5 GB) and runs much slower (almost x90 longer) on cpu, so TATR is still the default for its speed. In addition, contrary to TATR, Unitable may fail first through misalignment and misplaced html tags. 


## License

gmft is released under MIT. 

PyMuPDF support is available in a [separate repository](https://github.com/conjuncts/gmft_pymupdf) in observance of pymupdf's AGPL 3.0 license.

