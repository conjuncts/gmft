gmft.detectors.img2table module
================================

The Img2Table detector is another option for table extraction. The detector directly produces :class:`.FormattedTable` 
instances, so dataframes are available immediately (no need to pass through a formatter). The primary purpose is to
provide an alternative to the default :class:`.TATRDetector`.
The module relies on the fantastic `img2table <https://github.com/xavctn/img2table>`_ library.

The img2table library natively relies on PyMuPDF and its line detection feature. 
While line detection has been ported to PyPDFium2, the ported version only an approximation, so if you are able to
meet the AGPL-3.0 license requirements, PyMuPDF is recommended. See the :ref:`mupdf` section for more information.

.. code-block:: python
    
    from gmft_pymupdf import PyMuPDFDocument
    
    from gmft.detectors.img2table import Img2TableDetector
    
    doc = PyMuPDFDocument("path/to/pdf") # PyMuPDF is preferred
    # PyPdfium2 is possible, but line breaks and img2table performance may be less accurate
    # doc = PyPDFium2Document("path/to/pdf")
    
    detector = Img2TableDetector()
    fts = [detector.extract(table) for table in tables] # type: list[FormattedTable]


See also: the `corresponding tests <https://github.com/conjuncts/gmft/blob/main/test/compat/test_img2table.py>`_.


.. automodule:: gmft.detectors.img2table
    :members:
    :undoc-members:
    :show-inheritance: