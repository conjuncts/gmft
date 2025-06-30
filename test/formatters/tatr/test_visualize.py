import numpy as np
from PIL import Image
import pytest
from gmft.formatters.tatr import TATRFormattedTable
from gmft.detectors.base import CroppedTable
from gmft.impl.tatr.config import TATRFormatConfig


# def test_tatr_formatted_table_visualize_minimal():
#     # Create a minimal synthetic CroppedTable
#     class DummyCroppedTable(CroppedTable):
#         def __init__(self):
#             self._img_dpi = 72
#             self._img_padding = (0, 0)
#             self._img_margin = (0, 0, 0, 0)
#             self.angle = 0
#             self._df = None
#             self.predictions = {}
#             self.image_shape = (100, 100, 3)

#         def image(self, dpi=None, padding=None, margin=None):
#             # Return a blank white image
#             arr = np.ones(self.image_shape, dtype=np.uint8) * 255
#             return Image.fromarray(arr)

#     cropped_table = DummyCroppedTable()
#     # Minimal fctn_results with one box
#     fctn_results = {
#         "boxes": [[10, 10, 50, 50]],
#         "scores": [0.99],
#         "labels": [0],
#     }
#     config = TATRFormatConfig()
#     tft = TATRFormattedTable(cropped_table, fctn_results, config=config)
#     # Should return a PIL Image
#     img = tft.visualize(return_img=True)
#     assert isinstance(img, Image.Image)
#     # Should not raise for effective=True
#     img2 = tft.visualize(effective=True, return_img=True)
#     assert isinstance(img2, Image.Image)


def images_distance(img1: Image.Image, img2: Image.Image) -> float:
    """
    Compares two PIL images for visual similarity; returns a distance.
    A lower value means more similar.

    Args:
        img1 (Image.Image): First image.
        img2 (Image.Image): Second image.

    Returns:
        float: The mean pixelwise difference between the images. Between 0 and 255.
    """
    # Convert both images to RGB
    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")

    # Check size
    if img1.size != img2.size:
        return float("inf")

    # Convert to NumPy arrays
    arr1 = np.array(img1).astype(np.int16)
    arr2 = np.array(img2).astype(np.int16)

    # Compute absolute difference
    diff = np.abs(arr1 - arr2)

    # Compute mean difference
    return np.mean(diff)


def test_visualize_content(pdf2_tables):
    """
    Tests that the output of visualize() is consistent with a reference image.
    """
    ft = pdf2_tables[2]

    # Generate the image from the table
    generated_img = ft.visualize(effective=True, show_labels=False, return_img=True)

    # Load reference image
    reference_path = "data/test/references/img/pdf2_t2.png"
    try:
        reference_img = Image.open(reference_path)
    except FileNotFoundError:
        pytest.skip(f"Reference image not found at {reference_path}")

    # Compare images
    distance = images_distance(generated_img, reference_img)

    # Allow for minor rendering differences.
    # A value of 1.0 means on average each channel of each pixel is off by 1.
    # print("Distance", distance)
    assert distance < 1.0  # 0.0
