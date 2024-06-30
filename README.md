# gmft
**g**ive

**m**e

**f**ormatted

**tables**!

There are many pdfs out there, and many of those pdfs have tables. But despite a plethora of table extraction options, there is still no definitive extraction method. 

## About

gmft is a toolkit for converting pdf tables to many formats, including cropped image, text + positions, plaintext, csv, and pandas dataframes.

gmft is lightweight, performant, and high-throughput. gmft aims to "just work", offering strong performance with the default settings. 

gmft relies on microsoft's [Table Transformers](https://github.com/microsoft/table-transformer), which qualitatively is the most performant and reliable of many tested alternatives. See the comparison [here](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg).

Install: `pip install gmft`

Quickstart: [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb), [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb).

# Why use gmft?

**TL;DR:** gmft is fast, lightweight, configurable, and gives great results. Check out the [bulk extract](https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb) notebook for approximate extraction quality. 

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

Benchmark using Colab's **cpu** indicates an approximate rate of ~1.381 s/page; converting to df takes ~1.168 s/table. See the comparison here. This makes gmft about **10x** [**faster**](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg) than alternatives like unstructured, nougat, and open-parse/unitable on cpu. Here's how: 

- The base model, Smock et al.'s [Table Transformer](https://arxiv.org/abs/2110.00061), is blazing fast.
- gmft focuses on table extraction, so figures, titles, sections, etc. are not extracted. 
- In most cases, OCR is not necessary; pdfs already contain text positional data. Using this existing data drastically speeds up inference. With that being said, gmft can still extract tables from images and scanned pdfs through the image output. 
- PyPDFium2 is chosen for its [high throughput](https://github.com/py-pdf/benchmarks) and permissive license.



### Few dependencies

Many pdf extractors require detectron2, poppler, paddleocr, tesseract etc., many of which require additional external installation. Detectron2 is particularly difficult to install on windows. OCR models may require tesseract or paddleocr.

gmft can be installed in one line: `pip install gmft`. But it may help to have [transformers](https://pypi.org/project/transformers/) and pytorch preinstalled.

gmft mostly relies on [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [transformers](https://github.com/huggingface/transformers). On the first run, gmft downloads Microsoft's TATR from huggingface, which requires ~270mB total and is saved to `~/.cache/huggingface/hub/models--microsoft--table-{transformer-detection, structure-recognition}` and `~/.cache/huggingface/hub/models--timm--resnet18.a1_in1k`.


## Reliable

gmft uses Microsoft's Table Transformer (TATR), which is trained on a diverse dataset PubTables-1M. Many alternative methods were considered, and TATR was ultimately chosen for several reasons, among them high reliability. 

The authors are confident that the extraction quality is unmatched. When the model fails, it is usually an OCR issue, merged cell, or false positive. Even in these cases, the text is still highly useable. **Alignment** of a value to its row/column header tends to be **very accurate** because of the underlying procedural algorithm.

UniTable is a newer model which achieves SOTA results in many datasets like PubLayNet and FinTabNet. Though we plan to support Unitable in the future, Unitable is much larger (~1.5 GB) and takes about x90 longer to run on cpu. Therefore, TATR is still used for its higher throughput. In addition, experimentation shows comparable quality. Contrary to gmft, Unitable may fail first through misalignment because of misplaced html tags. This may impact use cases where alignment is critical.

We invite the reader to explore the [comparison notebooks](https://drive.google.com/drive/u/0/folders/114bWRj5H4aE-BA5UKH9S5ol8LC6vhqfR) to survey your own use cases and compare results.

## Modular
As models are loaded from huggingface hub, you can fine-tune a model and use it by specifying a huggingface path.

By subclassing the BasePDFDocument and BasePage classes, you are also able to support other PDF extraction methods (like PyMuPDF, PyPDF, pdfplumber etc.). 

By subclassing TableDetector and TableFormatter, alternative table detection and structure extraction methods are also possible.

# Limitations

Multi-indices (multiple column headers) are not yet supported.

Slightly rotated tables will probably fail, especially large tables that are not perfectly level.

# Acknowledgements

A tremendous thank you to the TATR authors: Brandon Smock, Rohith Pesala, and Robin Abraham, for making gmft possible. The image->csv step is highly inspired by TATR's inference.py code, but it has been rewritten with some adjustments for ease of use.

Thank you to Niels Rogge for porting TATR to huggingface and writing the [visualization code](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb).

## Alternatives

See [comparison](https://docs.google.com/spreadsheets/d/12IhxHZbYF71dPl32PQpF_6pg9e9S8f9W4sTHt-B0KTg).

Gmft focuses highly on pdf tables. Another great option is [img2table](https://github.com/xavctn/img2table), which is non-deep and attains great results.

[Nougat](https://github.com/facebookresearch/nougat) is excellent for both pdf table extraction and document understanding. It outputs full mathpix markdown (.mmd), which includes latex formulas, bold/italics, and fully latex-typeset tables. However, a gpu is highly recommended.

For general document understanding, I recommend checking out [open-parse](https://github.com/Filimoa/open-parse), [unstructured](https://github.com/Unstructured-IO/unstructured), [surya](https://github.com/VikParuchuri/surya), [deepdoctection](https://github.com/deepdoctection/deepdoctection), and [DocTR](https://github.com/mindee/doctr). Open-parse and unstructured do quite well on the same example pdfs in terms of extraction quality. Open-parse offers UniTable, a larger model which may achieve higher quality but runs much slower on cpu (see [reliability section](#Reliable) for more discussion.) Importantly, open-parse allows extraction of auxiliary information like headers, paragraphs, etc., useful for RAG.

## License

gmft is released under MIT. 

If you wish to use PyMuPDF, the file `gmft/pdf_bindings/bindings_mu.py` is available but is packaged [separately](https://gist.github.com/conjuncts/5a44784d6849c6966e57206da14d757d). `bindings_mu.py` alone is released under [AGPL 3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).
