#  test to_dict and from_dict


from gmft.config._dataclasses import with_config
from gmft.formatters.tatr import TATRFormatConfig


def test_overrides():
    config = TATRFormatConfig(verbosity=99, enable_multi_header=True)

    overrides = TATRFormatConfig(
        force_large_table_assumption=True, enable_multi_header=False
    )

    result = with_config(config, overrides)
    assert result.verbosity == 1  # CAUTION! since overrides completely replaces config,
    # it gets reset to the setting default, which is 1
    assert result.force_large_table_assumption == True
    assert result.enable_multi_header == False

    # now, try using the dict method
    result = with_config(
        config, {"force_large_table_assumption": True, "enable_multi_header": False}
    )
    assert (
        result.verbosity == 99
    )  # dict preserves set/unset, which was the old behavior
    assert result.force_large_table_assumption == True
    assert result.enable_multi_header == False
