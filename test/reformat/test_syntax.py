from gmft.reformat._executor.standard import _execute_plan, _reformat


if __name__ == "__main__":
    # Example usage (minimal)
    ft = None
    old_plan = _reformat(ft).with_strategy("lta").with_verbosity(4)

    # instructions = _collect_instructions(old_plan)
    # print(f"Collected {len(instructions)} instructions from the plan.")

    # --- Comprehensive example: all settings from REFACTOR.md ---
    from gmft.reformat._strategy.hybrid import HybridSettings

    # Settings from REFACTOR.md

    # Hybrid strategy settings

    # Comprehensive plan
    full_plan = (
        _reformat(ft)
        # Set verbosity (0=errors, 1=warnings, 2=info, 3=debug, 4=trace)
        .with_verbosity(3)
        # Filter predictions by confidence thresholds
        .filter_predictions(
            formatter_base_threshold=0.3,
            cell_required_confidence={
                0: 0.3,  # table
                1: 0.3,  # column
                2: 0.3,  # row
                3: 0.3,  # column header
                4: 0.5,  # projected row header
                5: 0.5,  # spanning cell
                6: 99,  # no object
            },
            _nms_overlap_threshold=0.1,
        )
        # Set the reformatting strategy and its settings
        .with_strategy(
            HybridSettings(
                large_table_if_n_rows_removed=8,
                large_table_threshold=10,
                large_table_row_overlap_threshold=0.2,
                force_large_table_assumption=None,
            )
        )
        .drop_nulls()
        .normalize_left_header(how="algorithm")
        .normalize_top_header()
        .max_top_headers(limit=1)
        .normalize_spans()
        .exclude_text_when(iob_threshold=0.05, smallest_supported_text_height=0.1)
        .raise_when(total_overlap_threshold=0.9, nms_threshold=5, iob_threshold=0.05)
        .warn_when(total_overlap_threshold=0.1, iob_threshold=0.5)
        # .with_executor("standard")
    )

    _execute_plan(full_plan)
