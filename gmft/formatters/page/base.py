from gmft.formatters.page.components import RichComponent
from gmft.pdf_bindings.base import BasePage


class FormattedPage:
    def __init__(self, orig_page: BasePage, components: list[RichComponent]) -> None:
        self.components = components
        self.page = orig_page

    def get_text(self) -> str:
        return "\n".join([component.rich_text() for component in self.components])


class BasePageFormatter:
    """
    Base class for page formatters.
    """

    def __init__(self):
        pass

    def extract(self, page: BasePage) -> FormattedPage:
        """
        Extract content from the page.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def format(self):
        """
        Alias for extract.
        """
        return self.extract()
