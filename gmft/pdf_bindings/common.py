# Allow for different pdf extractors to be used

from abc import ABC, abstractmethod
from typing import Generator

import numpy as np

from gmft.common import Rect
from PIL.Image import Image as PILImage

class BasePage(ABC):
    
    width: float
    height: float
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
    
    def _get_positions_and_text_and_breaks(self) -> Generator[tuple[float, float, float, float, str, int, int, int], None, None]:
        """
        warning: experimental, subject to change
        """
        return _infer_line_breaks(self.get_positions_and_text())
    
    def _get_text_with_breaks(self) -> str:
        """
        warning: experimental, subject to change
        """
        result = ""
        for x0, y0, x1, y1, text, _, _, wordno in self._get_positions_and_text_and_breaks():
            if wordno == 0:
                result += "\n"
            else:
                result += ' '
            result += text
        return result.lstrip()

    

class BasePDFDocument(ABC):
    @abstractmethod
    def get_page(self, n: int) -> BasePage:
        """
        Get 0-indexed page
        """
        raise NotImplementedError
    
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def get_filename(self) -> str:
        raise NotImplementedError
    
    def __getitem__(self, n: int) -> BasePage:
        return self.get_page(n)
    
    def __iter__(self) -> Generator[BasePage, None, None]:
        for i in range(len(self)):
            yield self.get_page(i)
    
    def close(self):
        pass


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
    
    # def __del__(self):
        # pass
        # if self.img is not None:
        #     self.close()

def _infer_line_breaks(generator_in: Generator[tuple[float,float,float,float,str],None,None]):
    """
    warning: experimental
    
    won't work for rotated text
    """
    # pass 1: set the line height to the average line height
    all_words = list(generator_in)
    # sort by y, then x
    all_words.sort(key=lambda x: (x[1], x[0]))
    
    if not all_words:
        return
    
    word_heights = [y1 - y0 for x0, y0, x1, y1, text in all_words]
    if not len(word_heights):
        avg_line_height = 10
    else:
        avg_line_height = np.mean(word_heights) * 0.8
        # let's keep it sensible
        avg_line_height = max(avg_line_height, 0.1)
    
    # pass 2: infer line breaks
    line_ctr = 0
    prev_anchor = all_words[0][1]
    word_ctr = 0
    for i, (x0, y0, x1, y1, text) in enumerate(all_words):
        if abs(y0 - prev_anchor) > avg_line_height:
            line_ctr += 1
            prev_anchor = y0
            word_ctr = 0
        else:
            word_ctr += 1
        yield x0, y0, x1, y1, text, 0, line_ctr, word_ctr
    
    
    
    