# gmft
**g**ive

**m**e (the)

**f**ormatted

**tables**!

There are many pdfs out there, and many of those pdfs have tables. But despite a plethora of table extraction options, there is still no consensus on a definitive extraction method. 

# About gmft

gmft is a high-throughput toolkit for converting pdf tables to many formats, including cropped image, text + positions, plaintext, csv, and pandas dataframes.

gmft aims to "just work", offering strong performance with the default settings. 

gmft relies on microsoft's [Table Transformers](https://github.com/microsoft/table-transformer), which qualitatively is the most performant and reliable of many tested alternatives. See the comparison here.

Install: `pip install gmft`

Quickstart: [demo notebook](https;//github.com/conjuncts/gmft/blob/main/notebooks/demo.ipynb)

# Why use gmft?

**TL;DR:** gmft is convenient, fast, lightweight, configurable, and gives great results. Check out the [demo notebook](https;//github.com/conjuncts/gmft/blob/main/notebooks/demo.ipynb) for the approximate extraction quality.

## Many Formats

gmft supports the following export options:
- Pandas dataframe (!)
- By extension: csv, html, json, etc. 
- List of text + positions
- Cropped image of table

Cropped images are useful for directly feeding into a vision recognizer, like: 
- GPT4 vision
- Mathpix/Adobe/Google/Amazon/Azure/etc.

Cropped images are also excellent for verifying correctness of output.

## Lightweight

### No GPU necessary

Because of the relatively few dependencies and high throughput, gmft is very lightweight. This allows gmft to run on cpu. 

### High throughput

In most cases, OCR is not necessary; pdfs already contain text positional data. Using this existing data drastically speeds up inference. With that being said, gmft can still extract tables from images and scanned pdfs through the image output.

Benchmark using Colab's **cpu** indicates an approximate rate of ~1.381 s/page; converting to df takes ~0.945 s/table. See the comparison here.

Gmft focuses on table extraction, so figures, titles, sections, etc. are not extracted.

PyPDFium2 is chosen for its [high throughput](https://github.com/py-pdf/benchmarks) and permissive license.

### Few dependencies

Many pdf extractors require detectron2, poppler, paddleocr, tesseract etc., many of which require additional external installation. Detectron2 is particularly difficult to install on windows. OCR models may require tesseract or paddleocr.

gmft can be installed in one line: `pip install gmft`. But it may help to have [transformers](https://pypi.org/project/transformers/) and pytorch preinstalled.

gmft mostly relies on [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [transformers](https://github.com/huggingface/transformers). On the first run, gmft downloads Microsoft's TATR from huggingface, which requires ~270mB total and is saved to ~/.cache/huggingface/hub/models--microsoft--table-{transformer-detection, structure-recognition} and ~/.cache/huggingface/hub/models--timm--resnet18.a1_in1k.


## Modular
As models are loaded from huggingface hub, you can homebrew a model and use it simply by specifying your own huggingface model.

By subclassing the BasePDFDocument and BasePage classes, you are also able to support other PDF extraction methods (like PyMuPDF, PyPDF, pdfplumber etc.) if you so desire.

## Reliable

gmft uses Microsoft's TATR, which is trained on a diverse dataset, PubTables-1M. Of all the alternatives tested, TATR was more reliable than most alternatives. 

The authors are confident that the extraction quality is unmatched. When the model fails, it is usually an OCR issue, merged cell, or false positive. Even in these cases, the text is still highly useable. **Alignment of a value to its row/column header tends to be very accurate** because of the underlying maximization algorithm.

We acknowledge UniTable, a newer model which achieves SOTA results in many datasets like PubLayNet and FinTabNet. Though we plan to support Unitable in the future, Unitable is much larger (~1.5 GB), taking almost 2 orders of magnitude (about x90) longer to run on cpu. Therefore, TATR is still used for its higher throughput. In addition, experimentation does not necessarily show a strict improvement in quality. Contrary to gmft, Unitable may fail first through misalignment because of misplaced html tags (see example.) This may impact use cases where alignment is critical.

# Limitations

90° rotated tables are not yet supported: this is a work in progress.

Multi-indices (multiple column headers) are not yet supported.

Slightly rotated tables will probably fail, especially large tables that are not perfectly level.



# Acknowledgements

A tremendous thank you to the TATR authors: Brandon Smock, Rohith Pesala, and Robin Abraham, for making gmft possible. The image->csv step is highly inspired by TATR's inference.py code, but has been rewritten for performance.

Thank you to Niels Rogge for porting TATR to huggingface and writing the [visualization code](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb).

## Alternatives

Gmft focuses highly on pdf tables. For more general document understanding, I recommend checking out [open-parse](https://github.com/Filimoa/open-parse), [unstructured](https://github.com/Unstructured-IO/unstructured), [surya](https://github.com/VikParuchuri/surya), [deepdoctection](https://github.com/deepdoctection/deepdoctection), and [DocTR](https://github.com/mindee/doctr).

In particular, open-parse and unstructured also do quite well on the same example pdfs in terms of extraction quality. Open-parse offers Unitable, a larger model which may achieve higher quality but runs much slower on cpu (see [reliability section](#Reliable) for more discussion.) Importantly, open-parse allows extraction of auxiliary information paragraphs, etc., (not just tables) useful for RAG.

gmft is released under MIT. 