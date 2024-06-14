# Allow for different pdf extractors to be used

from abc import ABC, abstractmethod
from typing import Generator

from gmft.common import Rect
from PIL.Image import Image as PILImage

class BasePage(ABC):
    
    def __init__(self, page_number: int):
        self.page_number = page_number
    
    @abstractmethod
    def get_positions_and_text(self) -> Generator[tuple[float, float, float, float, str], None, None]:
        """
        A generator of text and positions.
        The tuple is (x0, y0, x1, y1, "string")
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_filename(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def get_image(self, dpi: int=None, rect: Rect = None) -> PILImage:
        """
        Get an image of the page, constrained to be within the given rect.
        (x0, y0, x1, y1)
        """
        raise NotImplementedError
    

class BasePDFDocument(ABC):
    @abstractmethod
    def get_page(self, n: int) -> BasePage:
        raise NotImplementedError
    
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError
    
    def __getitem__(self, n: int) -> BasePage:
        return self.get_page(n)
    
    def __iter__(self) -> Generator[BasePage, None, None]:
        for i in range(len(self)):
            yield self.get_page(i)


class ImageOnlyPage(BasePage):
    """
    This is a dummy page that only contains an image.
    """
    
    def __init__(self, img: PILImage):
        self.img = img
        self.width, self.height = img.size
        super().__init__(0)
    
    def get_positions_and_text(self) -> Generator[tuple[float, float, float, float, str], None, None]:
        """
        This ImageOnlyPage has no text to extract.
        """
        return
    
    def get_filename(self) -> str:
        return None
    
    def get_image(self, dpi: int=None, rect: Rect=None) -> PILImage:
        # clip to rect
        if rect is not None:
            img = self.img.crop(rect.bbox)
        else:
            img = self.img
        return img
    
    def close(self):
        self.img.close()
        self.img = None
    
    def __del__(self):
        if self.img is not None:
            self.close()