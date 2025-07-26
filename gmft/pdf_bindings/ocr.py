from gmft.base import Rect
from gmft.pdf_bindings.base import BasePage


class OCRPage(BasePage):
    """
    A page where **text and bboxes must be provided** by the user.

    A common use case is when they are obtained from OCR.
    """

    def __init__(
        self,
        *,
        positions_and_text: list[tuple[float, float, float, float, str]],
        width: float,
        height: float,
        filename: str = None,
        page_number: int = 0,
        image = None,
    ):
        self.page_number = page_number
        self._positions_and_text = positions_and_text
        self.width = width
        self.height = height

        if filename is None:
            filename = f"ocr_page_{page_number}.txt"
        self.filename = filename
        self.image = image

    def get_positions_and_text(self) -> list[tuple[float, float, float, float, str]]:
        return self._positions_and_text

    def get_filename(self) -> str:
        return self.filename

    def get_image(self, dpi: int = None, rect: Rect = None):
        # TODO: In the future, we could
        # support a mock image by drawing the text on a blank image.
        # TODO: also implement rect handling
        return self.image
