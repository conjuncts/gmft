
```python
ft = formatter.extract(tables)


# table modification API

ft_orig = ft.copy()
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
