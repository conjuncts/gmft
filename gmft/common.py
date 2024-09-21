from typing import TypeVar, Union


class Rect:
    """
    A floating-point rectangle.
    """
    def __init__(self, bbox: tuple[float, float, float, float]):
        # (xmin, ymin, xmax, ymax)
        self.bbox = bbox
    

    
    def intersect(self, other: tuple[float, float, float, float]):
        if hasattr(other, 'bbox'): # should be Rect
            other = other.bbox
        xmin = max(self.bbox[0], other[0])
        ymin = max(self.bbox[1], other[1])
        xmax = min(self.bbox[2], other[2])
        ymax = min(self.bbox[3], other[3])
        if xmin >= xmax or ymin >= ymax:
            return Rect.EMPTY
        self.bbox = (xmin, ymin, xmax, ymax)
        return self

    def is_intersecting(self, other: tuple[float, float, float, float]):
        if hasattr(other, 'bbox'): # should be Rect
            other = other.bbox
        xmin = max(self.bbox[0], other[0])
        ymin = max(self.bbox[1], other[1])
        xmax = min(self.bbox[2], other[2])
        ymax = min(self.bbox[3], other[3])
        return xmin < xmax and ymin < ymax
    
    @property
    def width(self):
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self):
        return self.bbox[3] - self.bbox[1]
    
    @property
    def xmin(self):
        return self.bbox[0]
    
    @property
    def ymin(self):
        return self.bbox[1]
    
    @property
    def xmax(self):
        return self.bbox[2]
    
    @property
    def ymax(self):
        return self.bbox[3]
    
    @property
    def area(self):
        return (self.bbox[2] - self.bbox[0]) * (self.bbox[3] - self.bbox[1])
    
Rect.EMPTY = Rect((0, 0, 0, 0))

