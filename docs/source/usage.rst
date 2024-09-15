Usage
=====

.. _installation:

Installation
------------

gmft can be installed with pip: 

.. code-block:: console

   (.venv) $ pip install gmft

However, it may be helpful to install `pytorch <https://pytorch.org/get-started/locally/>`_ and transformers first, especially if you want to use GPU. 

Quickstart
----------------

The `quickstart <https://github.com/conjuncts/gmft/blob/main/notebooks/quickstart.ipynb>`_ notebook is a good place to start.

To extract many tables, the `bulk extract <https://github.com/conjuncts/gmft/blob/main/notebooks/bulk_extract.ipynb>`_ notebook is a good place to start.

For example, 

.. code-block:: python

    from gmft import CroppedTable, AutoTableDetector, AutoTableFormatter
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

Overview
--------

Documents are represented by a :class:`gmft.pdf_bindings.BasePDFDocument` object. The default implementation is :class:`gmft.pdf_bindings.PyPDFium2Document`, which uses the `PyPDFium2 <https://github.com/pypdfium2-team/pypdfium2>`_ library. 
Within a document, the :class:`gmft.pdf_bindings.BasePage` is implemented by default with :class:`gmft.pdf_bindings.PyPDFium2Page`. 
    
The :class:`gmft.AutoTableDetector` is the recommended table detection tool, which currently uses Microsoft's `Table Transformer <https://github.com/microsoft/table-transformer>`_. They produce :class:`gmft.table_detection.CroppedTable` objects, from which :meth:`gmft.table_detection.CroppedTable.image` permits image export. 

The :class:`gmft.AutoTableFormatter` is the recommended table formatting tool, from which :meth:`gmft.table_function.FormattedTable.df` permits dataframe export. All TableFormatters produce :class:`gmft.table_function.FormattedTable` objects, which contain the original CroppedTable and the formatted dataframe.


