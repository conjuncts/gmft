FAQ
===

Why is my table not detected?
------------------------------

Most likely, the reason is a false negative in the machine learning model. Unfortunately, there's not much to be done except for to look for a better model.

If you know exactly where the table is, you can skip the detection step by directly passing in the bbox.
You can do this by passing a bbox (tuple of `xmin, ymin, xmax, ymax`) into the :class:`~gmft.table_detection.CroppedTable` constructor.

.. code-block:: python

    from gmft.table_detection import CroppedTable
    table = CroppedTable(page, bbox=(x0, y0, x1, y0), confidence_score=1.0, label=0)

After that, the CroppedTable can be passed into formatters as usual.

How to parse my table with merged cells?
-----------------------------------------

Right now, only these types of merged cells are supported:
* top headers that are merged (with hierarchical semantic information)
* left headers that are merged (with hierarchical semantic information)

See the :ref:`semantic_spanning_cells` section for more information.

Therefore, tables with cells that are merged in the middle of the table are not supported.


ValueError: The identified boxes have significant overlap
----------------------------------------------------------

When the table structure (what gmft calls the formatter) machine learning model produces boxes that overlap significantly,
it is difficult to construct a table structure.

This error happens more frequently if you pass in large table. In this case, it may be beneficial to use a procedural algorithm instead of deep methods to parse the table. See :ref:`large_table_assumption` for a comparison.

To accomplish this, try setting `large_table_assumption` to true.


.. code-block:: python

    from gmft.table_function import TATRFormatConfig, TATRTableFormatter
    
    config = TATRFormatConfig()
    config.large_table_assumption = True
    
    formatter = TATRTableFormatter(config=config)
    ft = formatter.extract(table)

What format is best for LLMs?
------------------------------

The author finds that for simple table reading (ie. identify the cell under a header), performance for GPT-4o-mini is as follows:

.. code-block:: markdown
    
    markdown ~ latex ~ json > html >> csv_plus* >> csv ~ tsv

gpt-4o is similar to gpt-4o-mini, but with better baselines.

\*csv_plus is csv, but with an extra space after each comma. The improvement in performance might be attributable to better tokenization.

How to get tables formatted inline with text?
----------------------------------------------

This feature is a work in progress. For an interim solution, see github issue `#12 <https://github.com/conjuncts/gmft/issues/12>`_.

