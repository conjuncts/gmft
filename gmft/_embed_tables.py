from gmft import AutoTableFormatter, AutoTableDetector
from gmft.pdf_bindings.pdfium import PyPDFium2Document, PyPDFium2Page
from gmft.table_function import FormattedTable


def _embed_tables(doc: PyPDFium2Document, tables: list[FormattedTable]) -> list[str]:
    """
    Embeds tables into the document.
    Unforunately, line breaks are lost.
    """
    
    # require tabulate
    try:
        from tabulate import tabulate as _
    except ImportError:
        raise ImportError("You need to install tabulate to use this method (to embed tables in the preferred markdown format).")
    
    page_to_tables = {} # type: dict[int, list[FormattedTable]]
    for table in tables:
        page_to_tables.setdefault(table.page.page_number, []).append(table)
    
    result = []
    for i, page in enumerate(doc):
        if i in page_to_tables:
            builder = ""
            page_tables = page_to_tables[i]
            # bboxes = [table.bbox for table in page_tables]
            done = [False for _ in page_tables]
            for x0, y0, x1, y1, text in page.get_positions_and_text():
                for j, table in enumerate(page_tables):
                    if table.rect.is_intersecting((x0, y0, x1, y1)):
                        if not done[j]:
                            builder = builder + '\n' + table.df().to_markdown() + '\n'
                            done[j] = True
                        break
                else:
                    # no table found
                    builder += text + ' '
            result.append(builder)
        else:
            result.append(' '.join(text for _, _, _, _, text in page.get_positions_and_text()))
    return result



def _embed_tables_mu(doc: 'PyMuPDFDocument', tables: list[FormattedTable]) -> list[str]:
    """
    Embeds tables into the document.
    This is currently the only option that preserves line breaks.
    """
    
    # require tabulate
    try:
        from tabulate import tabulate as _
    except ImportError:
        raise ImportError("You need to install tabulate to use this method (to embed tables in the preferred markdown format).")
    
    try:
        from gmft_pymupdf import PyMuPDFDocument
    except ImportError:
        raise ImportError("You need to install gmft_pymupdf to use this method; see its github page for more info.")
    
    page_to_tables = {} # type: dict[int, list[FormattedTable]]
    for table in tables:
        page_to_tables.setdefault(table.page.page_number, []).append(table)
    
    result = []
    for i, page in enumerate(doc):
        if i in page_to_tables:
            builder = ""
            page_tables = page_to_tables[i]
            # bboxes = [table.bbox for table in page_tables]
            done = [False for _ in page_tables]
            mu_page = page.page # type: pymupdf.Page
            for x0, y0, x1, y1, word, blockno, lineno, wordno in mu_page.get_text('words'):
                for j, table in enumerate(page_tables):
                    if table.rect.is_intersecting((x0, y0, x1, y1)):
                        if not done[j]:
                            builder = builder + '\n' + table.df().to_markdown() + '\n'
                            done[j] = True
                        break
                else:
                    # no table found
                    if wordno == 0:
                        builder += "\n"
                    else:
                        builder += ' '
                    builder += word
            result.append(builder)
        else:
            result.append(' '.join(text for _, _, _, _, text in page.get_positions_and_text()))
    return result

# test 
if __name__ == '__main__':
    detector = AutoTableDetector()

    formatter = AutoTableFormatter()
    from gmft_pymupdf import PyMuPDFDocument

    doc = PyMuPDFDocument('test/samples/tatr.pdf')
    cts = []
    for page in doc:
    # page = doc[3]
        cts += detector.extract(page)
    
    tables = [formatter.extract(ct) for ct in cts]
    
    out = _embed_tables_mu(doc, tables)
    for i, text in enumerate(out):
        print(f"Page {i}: {text}")
    doc.close()