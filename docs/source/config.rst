Config Guide
============

The AutoTableDetector and AutoTableFormatter have separate configurations. This guide focuses on the **formatter** side.

Basics
-------

The :class:`AutoFormatConfig` object can be passed into either the :class:`AutoTableFormatter` constructor or the :meth:`TATRTableFormatter.df` method.

For example:

.. code-block:: python

    from gmft import AutoFormatConfig, AutoTableFormatter

    # ... code here
    
    config = AutoFormatConfig()
    config.verbosity = 3
    formatter = AutoTableFormatter(config=config)
    
    ft = formatter.format(table)
    df = ft.df() # formatter's tables automatically uses settings of config
    
    config_overrides = AutoFormatConfig()
    config.enable_multi_header = True
    df = ft.df(config_overrides=config_overrides) # uses settings of config + config_overrides


.. _semantic_spanning_cells:

Semantic Spanning
------------------

The **semantic spanning cells** setting supports headers with multiple rows or columns. 

Supported spanning cells can either be on the top or left header of the table.



.. figure:: /images/spanning_hier_left.png
    :alt: spanning hierarchical left

    Fig 1. Spanning Hierarchical Left Header

.. figure:: /images/spanning_hier_top.png
    :alt: spanning hierarchical top

    Fig 2. Spanning Hierarchical Top Header


.. raw:: html
    
    <div>
    <table border="1" class="dataframe">
    <caption>Table 1. <code>semantic_spanning_cells=True</code></caption>
    <thead>
        <tr style="text-align: right;">
        <th></th>
        <th>Dataset</th>
        <th>Total Tables \nInvestigated†</th>
        <th>Total Tables \nwith a PRH∗</th>
        <th>Tables with an oversegmented PRH \nTotal</th>
        <th>Tables with an oversegmented PRH \n% (of total with a PRH)</th>
        <th>Tables with an oversegmented PRH \n% (of total investigated)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <th>0</th>
        <td>SciTSR</td>
        <td>10,431</td>
        <td>342</td>
        <td>54</td>
        <td>15.79%</td>
        <td>0.52%</td>
        </tr>
        <tr>
        <th>1</th>
        <td>PubTabNet</td>
        <td>422,491</td>
        <td>100,159</td>
        <td>58,747</td>
        <td>58.65%</td>
        <td>13.90%</td>
        </tr>
        <tr>
        <th>2</th>
        <td>FinTabNet</td>
        <td>70,028</td>
        <td>25,637</td>
        <td>25,348</td>
        <td>98.87%</td>
        <td>36.20%</td>
        </tr>
        <tr>
        <th>3</th>
        <td>PubTables-1M (ours)</td>
        <td>761,262</td>
        <td>153,705</td>
        <td>0</td>
        <td>0%</td>
        <td>0%</td>
        </tr>
    </tbody>
    </table>
    </div>
    <br>

Enable Multi Header
--------------------

A slight **misnomer**, **enable multi header** only enforces that the pandas dataframe has multiple headers. 

This setting does not need to be enabled for semantic spanning cells (ie. hierarchical top or left headers) to be processed.

If this setting is false, then all the headers are condensed into one header. 
Multi-line (and hence hierarchical) information is preserved through ``\n`` characters.

.. raw:: html
    
    <div>
    <table border="1" class="dataframe">
    <caption>Table 2. <code>semantic_spanning_cells=True, enable_multi_header=True</code></caption>
    <thead>
        <tr>
        <th>Header 2</th>
        <th>NaN</th>
        <th>NaN</th>
        <th>NaN</th>
        <th>Tables with an oversegmented PRH</th>
        <th>Tables with an oversegmented PRH</th>
        <th>Tables with an oversegmented PRH</th>
        </tr>
        <tr>
        <th>Header 1</th>
        <th>Dataset</th>
        <th>Total Tables \nInvestigated†</th>
        <th>Total Tables \nwith a PRH∗</th>
        <th>Total</th>
        <th>% (of total with a PRH)</th>
        <th>% (of total investigated)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <th>0</th>
        <td>SciTSR</td>
        <td>10,431</td>
        <td>342</td>
        <td>54</td>
        <td>15.79%</td>
        <td>0.52%</td>
        </tr>
        <tr>
        <th>1</th>
        <td>PubTabNet</td>
        <td>422,491</td>
        <td>100,159</td>
        <td>58,747</td>
        <td>58.65%</td>
        <td>13.90%</td>
        </tr>
        <tr>
        <th>2</th>
        <td>FinTabNet</td>
        <td>70,028</td>
        <td>25,637</td>
        <td>25,348</td>
        <td>98.87%</td>
        <td>36.20%</td>
        </tr>
        <tr>
        <th>3</th>
        <td>PubTables-1M (ours)</td>
        <td>761,262</td>
        <td>153,705</td>
        <td>0</td>
        <td>0%</td>
        <td>0%</td>
        </tr>
    </tbody>
    </table>
    </div>
    <br>

.. _large_table_assumption:

Large Table Assumption
-----------------------

The **large table assumption** is a mechanic that improves performance on large tables. 
Here, algorithmically generated rows are used instead of deep learning. 


By default, large table assumption activates under these conditions:

At least one of these:
1. More than ``large_table_if_n_rows_removed`` rows are removed (default: >= 8)
2. OR all of the following are true:

   * Measured overlap of rows exceeds ``large_table_row_overlap_threshold`` (default: 20%)
   * AND the number of rows is greater than ``large_table_threshold`` (default: >= 10)

Large table assumption can be directly turned on/off with ``config.large_table_assumption = True/False``.


.. list-table:: 

    * - .. figure:: /images/lta_off.png

           Fig 3. Deep bboxes

      - .. figure:: /images/lta_on.png

           Fig 4. Large Table Assumption on


.. raw:: html

    <small>Fig. 3 and 4 Credits: © C. Dougherty 2001, 2002 (c.dougherty@lse.ac.uk). These tables have been computed to accompany the text C. Dougherty Introduction to Econometrics (second edition 2002, Oxford University Press, Oxford). They may be reproduced freely provided that this attribution is retained.</small>
