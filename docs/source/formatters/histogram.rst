Histogram based
================

HistogramFormatter uses the bboxes of words, interprets them as intervals, then populates
a histogram-like structure. Locations where there is almost no overlap can be detected,
and from these separating lines the table can be deduced. 

.. image:: ../images/histogram_expl.png
    :alt: histogram based
    :align: center


When to use?
-------------

HistogramFormatter is extremely fast, and so it is recommended as a starting point.


With very large tables, TATRFormatter and DITRFormatter struggle, and so often HistogramFormatter
will be your best output. To know when this is the case, we can simply count the number of 
separators lines directly. In this case, the very fast
histogram-backed algorithm means that the slow structure recognition step can be skipped entirely.

- DETR is hard capped at 100 detected objects, so it does worse approaching that limit.

HistogramFormatter works less well for tables with multi-line content or subscripts and superscripts. 

In this case, DITRFormatter will be able to semantically read the table.

Recommendation:
1. Run HistogramFormatter
2. If # of row separators + # of column separators < some threshold (ie. 60), run DITRFormatter

.. code-block:: python

    from gmft.auto import HistogramFormatter
    formatter = HistogramFormatter()
    formatted_tables = [formatter.format(table) for table in tables]

so the HistogramFormatter is
. 


Mix and Match
--------------

HistogramFormatter produces separating lines; so does DITRFormatter. Thus, you can mix and match
the separating lines from both if one method is more accurate than the other. 
For instance, if the HistogramFormatter method works well for rows but struggles on the columns, 
you can mix HistogramFormatter's the row separators and DITRFormatter's column separators.


