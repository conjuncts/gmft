Advanced
=========

Specify locations of headers/rows
----------------------------------

With known locations of headers, rows, or cells, you can configure a :class:`.TATRFormattedTable` of your choice. 
One option is through the :meth:`.TATRFormattedTable.from_dict()` method. 
To see the necessary format, check out `github <https://github.com/conjuncts/gmft/blob/main/test/refs/tatr_tables.info>`_.

This example is taken from the `internal test for serialization <https://github.com/conjuncts/gmft/blob/main/test/test_serial.py>`_.

.. code-block:: python
    
    tiny_info = {
        "filename": "test/samples/tiny.pdf",
        "page_no": 0,
        "bbox": [76.66205596923828, 162.82687377929688, 440.9659729003906, 248.67056274414062],
        "confidence_score": 0.9996763467788696,
        "label": 0,
        "config": {},
        "outliers": {},
        "fctn_results": {
            "scores": [
                0.9999045133590698,
                0.9998310804367065,
                0.9999147653579712,
                0.9998205304145813,
                0.9999688863754272,
                0.9998650550842285,
                0.9998096823692322,
                0.9897574186325073,
                0.9998759031295776
            ],
            "labels": [2, 2, 1, 2, 1, 1, 2, 3, 0],
            "boxes": [
                [-0.3175201416015625, 43.53631591796875, 362.50933837890625, 67.26876831054688],
                [-0.5251426696777344, 19.269771575927734, 362.5640869140625, 43.460350036621094],
                [-0.41268157958984375, 0.794677734375, 128.8265838623047, 86.2611312866211],
                [-0.4305534362792969, 0.80535888671875, 362.67877197265625, 18.99618148803711],
                [129.67820739746094, 0.8213462829589844, 252.4720458984375, 86.1773452758789],
                [251.82122802734375, 0.8133773803710938, 362.7557678222656, 86.11017608642578],
                [-0.3641777038574219, 67.27252197265625, 362.414794921875, 86.34217834472656],
                [-0.4329795837402344, 0.8099098205566406, 362.6827087402344, 18.966079711914062],
                [-0.43839263916015625, 0.771270751953125, 362.543212890625, 86.21470642089844]
            ]
        }
    }
    table = TATRFormattedTable.from_dict(tiny_info, page)

These are the labels for bboxes: (the source location is :attr:`.TATRFormattedTable.id2label`)

.. code-block:: python
    
    id2label = {
        0: 'table',
        1: 'table column',
        2: 'table row',
        3: 'table column header',
        4: 'table projected row header',
        5: 'table spanning cell',
        6: 'no object',
    }

The ``fctn_results`` field of a FormattedTable can also be specified with the appropriate structure. 
Changing the bboxes in this way should affect subsequent calls to :meth:`.FormattedTable.df()`.
