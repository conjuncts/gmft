FAQ
===

Why is my table not detected?
------------------------------

Most likely, the reason is a false negative in the machine learning model. Unfortunately, there's not much to be done except to search for a better model.

If you know exactly where the table is, you can skip the detection step by directly passing in the bbox.
You can do this by passing a bbox (tuple of `xmin, ymin, xmax, ymax`) into the :class:`~gmft.detectors.common.CroppedTable` constructor.

.. code-block:: python

    from gmft.detectors.common import CroppedTable
    table = CroppedTable(page, bbox=(x0, y0, x1, y0), confidence_score=1.0, label=0)

Afterwards, the CroppedTable can be passed into formatters as usual.

How to parse my table with merged cells?
-----------------------------------------

Right now, only these types of merged cells are supported:

* top headers that are merged (with hierarchical semantic information)
* left headers that are merged (with hierarchical semantic information)

See the :ref:`semantic_spanning_cells` section for more information.

Likewise, tables with merged cells in the center are not supported.


I need to tweak something (location/rotation) about a table. How do I do this?
---------------------------------------------------------------------------------

When modifying a table's location, bbox, or rotation, make sure to do so *before* passing the table to the formatter.


If you need to nudge a table, you can modify the bbox parameter.

.. code-block:: python
    
    for table in tables:
        table.bbox[1] -= 15 # moves y0 up by 15 pdf units
    fts = [formatter.extract(table) for table in tables]


Likewise, you can force tables to always be unrotated (or rotated!)

.. code-block:: python

    from gmft.presets import ingest_pdf
    
    tables, doc = ingest_pdf("path/to/pdf")
    for table in tables:
        if isinstance(table, RotatedCroppedTable):
            table.angle = 0
        # always rotated: 
        # tables[i] = RotatedCroppedTable(page=table.page, bbox=table.bbox, confidence_score=table.confidence_score, label=table.label, angle=90)
        ft = formatter.extract(table)
        # ...

ValueError: The identified boxes have significant overlap
----------------------------------------------------------

When the table structure (what gmft calls the formatter) machine learning model produces boxes that overlap significantly,
it is difficult to construct a table structure.

This error happens more frequently if you pass in large table. In this case, it may be beneficial to use a procedural algorithm instead of deep methods to parse the table. See :ref:`large_table_assumption` for a comparison.

To accomplish this, try setting `large_table_assumption` to true.


.. code-block:: python

    from gmft.formatters.tatr import TATRFormatConfig, TATRTableFormatter
    
    config = TATRFormatConfig()
    config.large_table_assumption = True
    
    formatter = TATRTableFormatter(config=config)
    ft = formatter.extract(table)



What format is best for LLMs?
------------------------------

See the section, :ref:`rag`.

How to get tables formatted inline with text?
----------------------------------------------

See the section, :ref:`rag`.

Cannot close object, library is destroyed. 
------------------------------------------

.. code-block:: text
    
    -> Cannot close object, library is destroyed. This may cause a memory leak!
    
This warning may be an indication that you forgot to explicitly call PyPDFium2Document.close(), which is **required**.