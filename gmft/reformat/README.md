Old customization: (deprecated)
```python
from gmft.auto import FormattedTable
ft: FormattedTable = formatter.extract(cropped) # 

df = ft.df(config_overrides={
    'large_table_assumption': True
})

```

New customization:
```python
ft: FormattedTable = formatter.extract(cropped) # 
new_ft = (
    ft
    .reformat()
    .with_strategy("lta")
    .to_table()
)
df = new_ft.df()
```


Legacy customization can also be directly ported with `with_legacy`.

```python
ft: FormattedTable = formatter.extract(cropped) # 
df = (
    ft
    .reformat()
    .with_legacy({
        'large_table_assumption': True
    })
).to_pandas()
```



New customization:
```python
ft: FormattedTable = formatter.extract(cropped) # 
plan = (
    reformat(ft)
    .with_strategy("lta")
    .with_verbosity(4)
)
new_ft = plan.to_table()
df = new_ft.df()

# alternatively:
# df = plan.to_pandas()
```


Grammar:
```python
plan = (
    reformat(ft)

    # 1. general stage

    .with_strategy("lta")
    .with_settings(...) # strategy-specific settings
    .with_verbosity(DEBUG)

    # 2. split/merge stage ()

    # .max_row_height(1, "lines")
    .max_row_height(12, "px")
    .merge_rows_by_whitespace(

        how='down'
    )
    .split_multi_headers()
    .panic_when(
        overlap_area_exceeds=0.9,
    )
    .panic_when(
        overlap_area_exceeds=0.1,
        rows_removed_exceeds=5,
        warn=True,
    )




)
```

Plan types:
```
GeneralPlan

```



## v0.5.0


## Changes:

- Top-level imports are now available with lazy-loading, reducing import times. 
    - Deprecation warnings are improved.
- Default device is now 'auto', which just-in-time resolves to cuda/cpu depending on cuda availability.
    - This allows torch to be imported only when needed.
- Many internal variables are now wrapped in `self.predictions`
- CroppedTable now directly has `angle`.


