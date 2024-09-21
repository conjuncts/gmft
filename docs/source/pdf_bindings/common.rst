gmft.pdf_bindings.common
--------------------------------

With a common interface, gmft supports interchangeable documents. The key requirements are as follows:

1. The document should be composed of multiple pages.
2. The document must expose **text** with their corresponding **locations** (bboxes).
3. The document must expose a way to obtain **images** for each page.

As a consequence of #2, OCR can be implemented as a layer which augments a PDF with redetected text.

.. automodule:: gmft.pdf_bindings.common
   :members:
   :undoc-members:
   :show-inheritance:
