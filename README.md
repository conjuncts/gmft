# gmft
**g**ive

**m**e

the

**f**ormatted

**tables**!

There are many pdfs out there, and many of those pdfs have tables. But despite a plethora of table extraction options, there is still no consensus on a definitive extraction method. 

# About gmft

gmft is a high-throughput, configurable, and out-of-the-box toolkit for converting pdf tables to many formats, including cropped image, text + positions, plaintext, csv, and pandas dataframes.

gmft aims to work "out-of-the-box", offering strong performance with the default settings. 

gmft relies on microsoft's [Table Transformers](https://github.com/microsoft/table-transformer), which qualitatively is the most reliable of all tested alternatives. 

# Why use gmft?

### Reliable

gmft uses Microsoft's TATR, which is trained on a diverse dataset, PubTables-1M. Of all the alternatives tested, TATR was qualitatively the most reliable by far.

### Many Formats

gmft supports the following export options:
- Pandas dataframe (!)
- By extension: csv, html, json, etc. 
- List of text + positions
- Cropped image of table

Cropped images are useful for directly feeding into a vision recognizer, like: 
- GPT4 vision
- Mathpix/Adobe/Google/Amazon/Azure/etc.

Cropped images are also excellent for verifying correctness of output.


### High throughput

In most cases, OCR is not necessary; pdfs already contain text positional data. Using this existing data drastically speeds up inference. With that being said, gmft can still extract tables from images and scanned pdfs through the image output.

Gmft focuses on table extraction, so figures, titles, sections, etc. are not extracted.

PyPDFium2 is chosen for its [high throughput](https://github.com/py-pdf/benchmarks) and permissive license.

### Few dependencies

Many pdf extractors require detectron2, poppler, paddleocr, tesseract etc., many of which require additional external installation. Detectron2 requires mac or linux/WSL. OCR models may require tesseract or paddleocr.

gmft aims for a convenient installation process. First, install [transformers](https://pypi.org/project/transformers/). Then, run
`pip install gmft`

gmft mostly relies on [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) and [transformers](https://github.com/huggingface/transformers). On the first run, gmft downloads Microsoft's TATR from huggingface, which requires ~270mB total and is saved to ~/.cache/huggingface/hub/models--microsoft--table-{transformer-detection, structure-recognition} and ~/.cache/huggingface/hub/models--timm--resnet18.a1_in1k.

#### No GPU necessary

Because of the relatively few dependencies and high throughput, gmft is very lightweight. This allows gmft to run on cpu. 

#### Modular
As models are loaded from huggingface hub, you can homebrew a model and use it simply by specifying your own huggingface model.

By subclassing the BasePDFDocument and BasePage classes, you are also able to support other PDF extraction methods (like PyMuPDF, PyPDF, pdfplumber etc.) if you so desire.

# Acknowledgements

A tremendous thank you to the TATR authors: Brandon Smock, Rohith Pesala, and Robin Abraham.

Thank you to Niels Rogge for porting TATR to huggingface and writing the [visualization code](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/Table%20Transformer/Using_Table_Transformer_for_table_detection_and_table_structure_recognition.ipynb).

gmft is released under MIT. 