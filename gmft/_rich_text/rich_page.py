from gmft._rich_text.common import Paragraph, RichComponent, TableComponent
from gmft.formatters.common import FormattedTable
from gmft.pdf_bindings.common import BasePDFDocument, BasePage


class FormattedPage:
    def __init__(self, orig_page: BasePage, components: list[RichComponent]) -> None:
        self.components = components
        self.page = orig_page

    # def __str__(self):
    #     return "\n".join([component.rich_text() for component in self.components])
    
    def get_text(self) -> str:
        return "\n".join([component.rich_text() for component in self.components])

def embed_tables_into_page(page: BasePage, tables: list[FormattedTable]) -> FormattedPage:
    # require tabulate
    try:
        from tabulate import tabulate as _
    except ImportError:
        raise ImportError("You need to install tabulate to use this method (to embed tables in the preferred markdown format).")
    
    if not tables:
        return FormattedPage(page, components=[Paragraph(page._get_text_with_breaks()) ])
    
    pagestuff = []
    # if i in page_to_tables:
    
    text_builder = ""
    # page_tables = page_to_tables[i]
    # bboxes = [table.bbox for table in page_tables]
    done = [False for _ in tables]
    # mu_page = page.page # type: pymupdf.Page
    # for x0, y0, x1, y1, word, blockno, lineno, wordno in mu_page.get_text('words'):
    for x0, y0, x1, y1, word, blockno, lineno, wordno in page._get_positions_and_text_and_breaks():
        for j, table in enumerate(tables):
            if table.rect.is_intersecting((x0, y0, x1, y1)):
                if not done[j]:
                    # builder = builder + 
                    pagestuff.append(Paragraph(text_builder))
                    text_builder = ""
                    pagestuff.append(TableComponent(table))
                    done[j] = True
                break
        else:
            # no table found
            if wordno == 0:
                text_builder += "\n"
            else:
                text_builder += ' '
            text_builder += word
        
    if text_builder:
        pagestuff.append(Paragraph(text_builder))
        text_builder = ""
    # remove leading space from first paragraph
    if pagestuff and isinstance(pagestuff[0], Paragraph):
        pagestuff[0].content = pagestuff[0].content.lstrip()
    return FormattedPage(page, pagestuff)


def embed_tables(doc: BasePDFDocument, tables: list[FormattedTable]) -> list[FormattedPage]:
    """
    Embeds tables into the document.
    This is currently the only option that preserves line breaks.
    """
    
    # require tabulate
    try:
        from tabulate import tabulate as _
    except ImportError:
        raise ImportError("You need to install tabulate to use this method (to embed tables in the preferred markdown format).")
    
    page_to_tables = {} # type: dict[int, list[FormattedTable]]
    for table in tables:
        page_to_tables.setdefault(table.page.page_number, []).append(table)
    
    formatted_pages = []
    for i, page in enumerate(doc):
        formatted_pages.append(embed_tables_into_page(page, page_to_tables.get(i, [])))
    
    return formatted_pages

