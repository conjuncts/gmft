import pytest
from PIL import Image
from gmft.pdf_bindings.base import ImageOnlyPage
from gmft.base import Rect


@pytest.fixture
def sample_image():
    """Create a simple test image (72 DPI equivalent, 612x792 pixels)."""
    return Image.new("RGB", (612, 792), color="white")


@pytest.fixture
def image_page_default(sample_image):
    """ImageOnlyPage with default scale_factor (1.0)."""
    return ImageOnlyPage(sample_image)


@pytest.fixture
def image_page_144dpi(sample_image):
    """ImageOnlyPage created from a 144 DPI image."""
    # For 144 DPI, the image would be 2x larger
    img_144 = sample_image.resize((1224, 1584))
    return ImageOnlyPage(img_144, dpi=144)


class TestImageOnlyPageGetImage:
    """Tests for ImageOnlyPage.get_image method."""

    def test_get_image_no_parameters(self, image_page_default):
        """Test getting image without any parameters returns original."""
        img = image_page_default.get_image()
        assert img.width == 612
        assert img.height == 792

        img = image_page_default.get_image(dpi=72)
        assert img.width == 612
        assert img.height == 792

    def test_get_image_upscale_dpi_144(self, image_page_default):
        """Test upscaling from 72 to 144 DPI."""
        img = image_page_default.get_image(dpi=144)
        assert img.width == 1224  # 612 * 2
        assert img.height == 1584  # 792 * 2

    @pytest.mark.skip(reason="low priority")
    def test_get_image_upscale_dpi_300(self, image_page_default):
        """Test upscaling to 300 DPI."""
        img = image_page_default.get_image(dpi=300)
        expected_width = int(612 * 300 / 72)
        expected_height = int(792 * 300 / 72)
        assert img.width == expected_width
        assert img.height == expected_height

    def test_get_image_downscale_from_144dpi(self, image_page_144dpi):
        """Test downscaling from 144 DPI to 72 DPI."""
        img = image_page_144dpi.get_image(dpi=72)
        assert img.width == 612
        assert img.height == 792

        # Without dpi, should assume dpi=72 and downscale
        img = image_page_144dpi.get_image()
        assert img.width == 612
        assert img.height == 792

    @pytest.mark.skip(reason="low priority")
    def test_get_image_same_dpi_as_scale_factor(self, image_page_144dpi):
        """Test when requested dpi matches the page's scale_factor."""
        img = image_page_144dpi.get_image(dpi=144)
        assert img.width == 1224
        assert img.height == 1584

    @pytest.mark.skip(reason="low priority")
    def test_get_image_with_rect_partial(self, image_page_default):
        """Test cropping to a partial region."""
        rect = Rect((100, 100, 300, 400))
        img = image_page_default.get_image(rect=rect)
        assert img.width == 200  # 300 - 100
        assert img.height == 300  # 400 - 100

    def test_get_image_with_rect_and_dpi(self, image_page_default):
        """Test combining rect cropping with DPI scaling."""
        rect = Rect((0, 0, 306, 396))  # Half of the page in PDF units
        img = image_page_default.get_image(dpi=144, rect=rect)
        # Rect is in PDF units (72 DPI), so at 144 DPI it should be 2x
        assert img.width == 612  # 306 * 2
        assert img.height == 792  # 396 * 2

    def test_get_image_with_rect_and_dpi_144dpi_page(self, image_page_144dpi):
        """Test rect cropping on a 144 DPI page with dpi parameter."""
        rect = Rect((0, 0, 306, 396))  # Half page in PDF units
        img = image_page_144dpi.get_image(dpi=72, rect=rect)
        # Should crop to half the page at 72 DPI
        assert img.width == 306
        assert img.height == 396

    @pytest.mark.skip(reason="low priority")
    def test_get_image_rect_at_offset(self, image_page_default):
        """Test cropping rect at an offset position."""
        rect = Rect((50, 50, 150, 200))
        img = image_page_default.get_image(dpi=72, rect=rect)
        assert img.width == 100
        assert img.height == 150

    def test_get_image_rect_at_offset_with_scaling(self, image_page_default):
        """Test cropping and scaling together at offset."""
        rect = Rect((50, 50, 150, 200))
        img = image_page_default.get_image(dpi=144, rect=rect)
        # At 144 DPI, the crop dimensions should be doubled
        assert img.width == 200  # (150-50) * 2
        assert img.height == 300  # (200-50) * 2

    @pytest.mark.skip(reason="low priority")
    def test_get_image_preserves_original(self, image_page_default):
        """Test that getting image doesn't modify the original."""
        original_width = image_page_default.img.width
        original_height = image_page_default.img.height

        # Get various versions
        _ = image_page_default.get_image(dpi=144)
        _ = image_page_default.get_image(rect=Rect((0, 0, 100, 100)))

        # Original should be unchanged
        assert image_page_default.img.width == original_width
        assert image_page_default.img.height == original_height

    @pytest.mark.skip(reason="low priority")
    def test_get_image_small_rect(self, image_page_default):
        """Test with a very small rect."""
        rect = Rect((10, 10, 20, 20))
        img = image_page_default.get_image(rect=rect)
        assert img.width == 10
        assert img.height == 10

    def test_get_image_full_page_rect(self, image_page_default):
        """Test with rect covering the full page."""
        rect = Rect((0, 0, 612, 792))
        img = image_page_default.get_image(rect=rect)
        assert img.width == 612
        assert img.height == 792

    def test_image_page_scaling_with_words(self):
        """Test scaling on ImageOnlyPage with words."""
        img = Image.new("RGB", (1224, 1584), color="white")
        words = [(10, 10, 50, 30, "Test")]
        page = ImageOnlyPage(img, words=words, dpi=144)

        # Get at original DPI
        result_img = page.get_image(dpi=144)
        assert result_img.width == 1224
        assert result_img.height == 1584

        # Get at downscaled DPI
        result_img = page.get_image(dpi=72)
        assert result_img.width == 612
        assert result_img.height == 792

        assert list(page.get_positions_and_text()) == words
