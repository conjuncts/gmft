gmft package
============

Top Level Aliases
------------------

.. automodule:: gmft
   :members:
   :undoc-members:
   :show-inheritance:
   
PDF providers
--------------

In gmft, multiple documents and PDF providers are supported through a common interface. 
PyPDFium2 is the default PDF reader. `Pymupdf <https://github.com/conjuncts/gmft_pymupdf>`_ offers
more accurate performance but requires the more restrictive AGPL license.

.. toctree::
   :maxdepth: 2
   
   pdf_bindings/index
   pdf_bindings/common
   pdf_bindings/pdfium


Detectors
---------

In gmft, detectors locate the positions and bounds (bbox) of tables on a page. 

.. toctree::
   :maxdepth: 2
   
   detectors/common
   detectors/tatr
   detectors/img2table
   
Formatters
----------

In gmft, formatters take a located table (CroppedTable) and produces machine-readable output (ie. pandas DataFrame). 
This task is known in the literature as *table structure recognition* and *functional analysis*.

.. toctree::
   :maxdepth: 2
   
   formatters/common
   formatters/tatr
   formatters/histogram
   
Modules
----------

.. toctree::
   :maxdepth: 2
   
   gmft.auto
   gmft.common
   gmft.presets
   gmft.table_detection
   gmft.table_function
   gmft.table_visualization


