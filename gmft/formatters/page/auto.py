from gmft.detectors.tatr import TATRDetector
from gmft.formatters.page.embed import embed_tables_into_page
from gmft.formatters.page.base import BasePageFormatter, FormattedPage
from gmft.formatters.tatr import TATRFormatter
from gmft.pdf_bindings.base import BasePage


class _TATRPageFormatter(BasePageFormatter):
    """
    Format page with the TATR method.

    [Experimental] Functionality is subject to change without warning.
    """

    def __init__(self):
        super().__init__()
        self.detector = TATRDetector()
        self.formatter = TATRFormatter()

    def extract(self, page: BasePage) -> FormattedPage:
        """
        Extract content from the page.
        """
        cropped = self.detector.extract(page)
        formatted = [self.formatter.extract(ct) for ct in cropped]

        _ = formatted[0].df()
        return embed_tables_into_page(page, formatted)


class AutoPageFormatter(_TATRPageFormatter):
    """
    Format a page in whatever way is most appropriate.

    Exact implementation is not guaranteed and is subject to change.
    """
