"""Integration tests for complete correlation workflow."""

import numpy as np
import pytest
from pathlib import Path
from PIL import Image
from correlation import (
    load_images,
    validate_dimensions,
    validate_output_path,
    correlation,
    save_correlation,
    main,
)


class TestLoadImages:
    """Test cases for load_images function."""

    def test_load_valid_images(self, test_image_path, test_template_path):
        """Test loading valid image files."""
        input_arr, match_arr = load_images(
            str(test_image_path), str(test_template_path)
        )

        assert isinstance(input_arr, np.ndarray)
        assert isinstance(match_arr, np.ndarray)
        assert input_arr.shape == (100, 100)
        assert match_arr.shape == (20, 20)

    def test_load_nonexistent_file(self, test_image_path):
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            load_images(str(test_image_path), "nonexistent.jpg")

    def test_load_invalid_format(self, tmp_path):
        """Test error handling for invalid image format."""
        bad_file = tmp_path / "bad.jpg"
        bad_file.write_text("not an image")

        with pytest.raises(Exception):  # UnidentifiedImageError
            load_images(str(bad_file), str(bad_file))

    def test_converts_to_grayscale(self, tmp_path):
        """Test that color images are converted to grayscale."""
        # Create RGB image
        color_img = Image.new("RGB", (50, 50), color=(255, 0, 0))
        color_path = tmp_path / "color.jpg"
        color_img.save(color_path)

        gray_img = Image.new("L", (10, 10), color=128)
        gray_path = tmp_path / "gray.jpg"
        gray_img.save(gray_path)

        input_arr, match_arr = load_images(str(color_path), str(gray_path))

        # Should be 2D arrays (grayscale)
        assert input_arr.ndim == 2
        assert match_arr.ndim == 2


class TestValidateDimensions:
    """Test cases for validate_dimensions function."""

    def test_valid_dimensions(self):
        """Test validation passes for valid dimensions."""
        input_arr = np.zeros((100, 100))
        match_arr = np.zeros((20, 20))

        # Should not raise any exception
        validate_dimensions(input_arr, match_arr)

    def test_template_too_large(self):
        """Test error when template is larger than input."""
        input_arr = np.zeros((50, 50))
        match_arr = np.zeros((100, 100))

        with pytest.raises(ValueError, match="must be smaller"):
            validate_dimensions(input_arr, match_arr)

    def test_template_equal_size(self):
        """Test error when template equals input size."""
        input_arr = np.zeros((50, 50))
        match_arr = np.zeros((50, 50))

        with pytest.raises(ValueError, match="must be smaller"):
            validate_dimensions(input_arr, match_arr)

    def test_empty_array(self):
        """Test error for empty arrays."""
        input_arr = np.zeros((0, 0))
        match_arr = np.zeros((5, 5))

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_dimensions(input_arr, match_arr)

    def test_too_small_input(self):
        """Test error for input smaller than 2x2."""
        input_arr = np.zeros((1, 1))
        match_arr = np.zeros((1, 1))

        with pytest.raises(ValueError, match="too small"):
            validate_dimensions(input_arr, match_arr)

    def test_max_dimension_exceeded(self):
        """Test error when image exceeds maximum dimension."""
        # Create large mock array (don't actually allocate)
        input_arr = np.zeros((10, 10))
        match_arr = np.zeros((5, 5))

        # Test with custom max_dimension
        with pytest.raises(ValueError, match="too large"):
            validate_dimensions(input_arr, match_arr, max_dimension=5)


class TestValidateOutputPath:
    """Test cases for validate_output_path function."""

    def test_valid_path_current_directory(self, tmp_path):
        """Test validation of path in current directory."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = validate_output_path("output.jpg")
            assert result.name == "output.jpg"
        finally:
            os.chdir(original_cwd)

    def test_path_traversal_blocked(self):
        """Test that path traversal is blocked."""
        with pytest.raises(ValueError, match="must be within current directory"):
            validate_output_path("../../etc/passwd")

    def test_absolute_path_outside_cwd(self, tmp_path):
        """Test that absolute paths outside cwd are blocked."""
        with pytest.raises(ValueError, match="must be within current directory"):
            validate_output_path("/tmp/output.jpg")

    def test_subdirectory_allowed(self, tmp_path):
        """Test that subdirectories are allowed."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            result = validate_output_path("subdir/output.jpg")
            assert result.parent.name == "subdir"
        finally:
            os.chdir(original_cwd)


class TestSaveCorrelation:
    """Test cases for save_correlation function."""

    def test_save_creates_file(self, tmp_path):
        """Test that save_correlation creates output file."""
        corr = np.random.rand(50, 50)
        output_path = tmp_path / "test_output.jpg"

        save_correlation(corr, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_saved_image_is_valid(self, tmp_path):
        """Test that saved image can be opened."""
        corr = np.random.rand(30, 30)
        output_path = tmp_path / "test_output.jpg"

        save_correlation(corr, output_path)

        # Should be able to open as image
        img = Image.open(output_path)
        assert img.size == (30, 30)
        assert img.mode == "L"  # Grayscale

    def test_save_permission_error(self, tmp_path):
        """Test error handling for permission denied."""
        corr = np.random.rand(10, 10)

        # Try to save to non-writable location
        import os

        if os.name != "nt":  # Skip on Windows
            with pytest.raises(PermissionError):
                save_correlation(corr, Path("/root/forbidden.jpg"))


class TestCompleteWorkflow:
    """Integration tests for complete workflow."""

    def test_end_to_end_workflow(self, tmp_path):
        """Test complete workflow from images to output."""
        # Create test images
        input_img = Image.new("L", (100, 100), color=128)
        input_img.paste(255, (30, 30, 50, 50))  # White square
        input_path = tmp_path / "input.jpg"
        input_img.save(input_path)

        template_img = Image.new("L", (20, 20), color=255)
        template_path = tmp_path / "template.jpg"
        template_img.save(template_path)

        output_path = tmp_path / "output.jpg"

        # Change to tmp_path to allow output
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Run complete workflow
            main(str(input_path), str(template_path), "output.jpg")

            # Verify output exists
            assert output_path.exists()

            # Verify output is valid image
            result_img = Image.open(output_path)
            assert result_img.size == (100, 100)

        finally:
            os.chdir(original_cwd)

    def test_workflow_with_example_images(self):
        """Test workflow with actual example images if they exist."""
        example_dir = Path("example_images")
        if not example_dir.exists():
            pytest.skip("Example images directory not found")

        dandelions = example_dir / "dandelions.jpg"
        tip = example_dir / "tip.jpg"

        if not (dandelions.exists() and tip.exists()):
            pytest.skip("Example images not found")

        # Just test loading and correlation, don't save
        input_arr, match_arr = load_images(str(dandelions), str(tip))
        validate_dimensions(input_arr, match_arr)
        result = correlation(input_arr, match_arr)

        assert result.shape == input_arr.shape
        assert -1 <= result.min() <= result.max() <= 1

    def test_error_workflow_wrong_size(self, tmp_path):
        """Test that workflow correctly handles wrong-sized images."""
        # Create images where template is larger
        small_img = Image.new("L", (50, 50), color=128)
        small_path = tmp_path / "small.jpg"
        small_img.save(small_path)

        large_img = Image.new("L", (100, 100), color=200)
        large_path = tmp_path / "large.jpg"
        large_img.save(large_path)

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Should exit with error code 1
            with pytest.raises(SystemExit) as exc_info:
                main(str(small_path), str(large_path))

            assert exc_info.value.code == 1

        finally:
            os.chdir(original_cwd)
