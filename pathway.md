
```python
ft = formatter.extract(tables)


# table modification API

import gmft.custom as gg

ft = gg.convert(ft)

# configure the minor rows
ft = ft.dividers.filter([
    
])

ft = ft.with_rows([
    gg.major.split_rows(max_lines=1), # .alias('major'): saves it as major
])

ft = ft.with_rows([
    gg.when(_split_predicate).then(
        gg.row('major').split_rows(max_lines=1)
    ).otherwise(
        gg.row('major')
    ).alias('major')
])

ft = ft.explode.split_rows(max_lines=1)

def _split_predicate(row: tuple):
    # split a row if a cell has >80% numeric content
    for cell in row:
        percent_numeric = sum(c.isdigit() for c in cell) / len(cell)
        if percent_numeric > 0.8:
            return True
    return False

ft = ft.explode.when(lambda row: )

ft = ft.with_rows([
    
])
```
