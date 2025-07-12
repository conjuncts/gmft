import pytest
from gmft import TATRFormattedTable
from gmft.formatters.page.embed import embed_tables
from gmft.formatters.page.auto import AutoPageFormatter
from gmft.impl.tatr.config import TATRFormatConfig
from test.conftest import dump_text

from .data import (
    _rich_page_0_text,
    _rich_page_2_text,
    _rich_page_3_text,
)


def test_rich_pdf7_new(docs_bulk):
    pytest.skip("this test is flaky - not sure why")
    doc = docs_bulk[6]  # n-1
    # look at page 12

    fmtr = AutoPageFormatter()

    rich_page_2 = fmtr.extract(doc[2])

    # print(rich_pages[2])
    assert rich_page_2.get_text() == _rich_page_2_text


def test_rich_pdf7(docs_bulk, pdf7_tables):
    doc = docs_bulk[6]  # n-1
    # look at page 12

    config = TATRFormatConfig()
    for ft in pdf7_tables:
        ft = ft  # type
        ft.df(config_overrides=config)  # reset config to defaults

    rich_pages = embed_tables(doc=doc, tables=pdf7_tables)

    assert rich_pages[2].get_text() == _rich_page_2_text, dump_text(
        rich_pages[2].get_text(), "rich_page_2.txt"
    )
    assert rich_pages[3].get_text() == _rich_page_3_text, dump_text(
        rich_pages[3].get_text(), "rich_page_3.txt"
    )
    # control
    assert rich_pages[0].get_text() == _rich_page_0_text, dump_text(
        rich_pages[0].get_text(), "rich_page_0.txt"
    )
