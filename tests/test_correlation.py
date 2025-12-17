"""Unit tests for correlation function."""

import numpy as np
import pytest
from correlation import correlation


class TestCorrelation:
    """Test cases for the correlation function."""

    def test_exact_match_center(self):
        """Test correlation when template exactly matches a region."""
        # Create input with varying values and a distinct pattern
        input_arr = np.random.rand(20, 20).astype(np.float32) * 0.3  # Background noise
        input_arr[8:12, 8:12] = [
            [0.1, 0.5, 0.9, 0.5],
            [0.3, 0.7, 1.0, 0.7],
            [0.5, 0.9, 0.8, 0.6],
            [0.2, 0.4, 0.6, 0.4],
        ]  # Distinct pattern

        # Template matches the distinct pattern
        match_arr = input_arr[8:12, 8:12].copy()

        result = correlation(input_arr, match_arr)

        # Result should have same shape as input (due to padding)
        assert result.shape == input_arr.shape

        # Maximum correlation should be close to 1 (perfect match)
        assert result.max() > 0.95

        # Find the position of max correlation - should be near (8, 8)
        max_pos = np.unravel_index(result.argmax(), result.shape)
        assert 7 <= max_pos[0] <= 9
        assert 7 <= max_pos[1] <= 9

    def test_no_match(self):
        """Test correlation when template doesn't match input."""
        input_arr = np.zeros((20, 20), dtype=np.uint8)
        match_arr = np.ones((5, 5), dtype=np.uint8) * 255

        result = correlation(input_arr, match_arr)

        # With completely different patterns, correlation should be low/negative
        assert result.max() < 0.5

    def test_output_shape_with_padding(self):
        """Test that output shape matches input shape due to padding."""
        input_arr = np.random.rand(50, 60)
        match_arr = np.random.rand(10, 15)

        result = correlation(input_arr, match_arr)

        # Due to padding, output should match input dimensions
        assert result.shape == input_arr.shape

    def test_correlation_range(self):
        """Test that correlation values are in valid range [-1, 1]."""
        input_arr = np.random.rand(30, 30)
        match_arr = np.random.rand(5, 5)

        result = correlation(input_arr, match_arr)

        # Correlation coefficients should be in range [-1, 1]
        assert result.min() >= -1.0
        assert result.max() <= 1.0

    def test_template_at_corner(self):
        """Test correlation when template is at image corner."""
        # Create input with varying pattern at corner
        input_arr = np.random.rand(20, 20).astype(np.float32) * 0.2
        # Add distinct pattern at top-left corner
        input_arr[0:5, 0:5] = [
            [0.8, 0.9, 1.0, 0.9, 0.8],
            [0.7, 0.8, 0.9, 0.8, 0.7],
            [0.6, 0.7, 0.8, 0.7, 0.6],
            [0.5, 0.6, 0.7, 0.6, 0.5],
            [0.4, 0.5, 0.6, 0.5, 0.4],
        ]

        # Template matches the corner pattern
        match_arr = input_arr[0:5, 0:5].copy()

        result = correlation(input_arr, match_arr)

        # Should find high correlation at top-left
        assert result[0, 0] > 0.95

    def test_identical_images(self):
        """Test correlation of image with itself (as template)."""
        input_arr = np.random.rand(15, 15)
        # Template is slightly smaller
        match_arr = input_arr[2:10, 2:10].copy()

        result = correlation(input_arr, match_arr)

        # Should find perfect match where template was extracted
        max_corr = result.max()
        assert max_corr > 0.99  # Near perfect correlation

    def test_padded_regions_are_zero(self):
        """Test that padded regions contain zeros."""
        input_arr = np.random.rand(20, 20)
        match_arr = np.random.rand(5, 5)

        result = correlation(input_arr, match_arr)

        # Check bottom-right corner (padded region)
        # Last few rows and columns should be 0
        assert result[-1, -1] == 0.0
        assert result[-2, -1] == 0.0
        assert result[-1, -2] == 0.0

    def test_different_sizes(self):
        """Test correlation with various size combinations."""
        sizes = [
            ((50, 50), (10, 10)),
            ((100, 80), (20, 15)),
            ((30, 40), (5, 8)),
        ]

        for input_size, match_size in sizes:
            input_arr = np.random.rand(*input_size)
            match_arr = np.random.rand(*match_size)

            result = correlation(input_arr, match_arr)

            assert result.shape == input_size
            assert -1.0 <= result.min() <= result.max() <= 1.0

    def test_binary_pattern_matching(self):
        """Test correlation with binary patterns (0s and 1s)."""
        # Create checkerboard pattern
        input_arr = np.zeros((20, 20), dtype=np.uint8)
        input_arr[::2, ::2] = 255
        input_arr[1::2, 1::2] = 255

        # Template is a small checkerboard
        match_arr = np.zeros((4, 4), dtype=np.uint8)
        match_arr[::2, ::2] = 255
        match_arr[1::2, 1::2] = 255

        result = correlation(input_arr, match_arr)

        # Should find good matches throughout (repeating pattern)
        assert result.max() > 0.9

    def test_floating_point_arrays(self):
        """Test correlation works with floating point arrays."""
        input_arr = np.random.rand(25, 25).astype(np.float32)
        match_arr = np.random.rand(7, 7).astype(np.float32)

        result = correlation(input_arr, match_arr)

        assert result.shape == input_arr.shape
        assert result.dtype in [np.float32, np.float64]
