"""Unit tests for normalize_array function."""

import numpy as np
import pytest
from correlation import normalize_array


class TestNormalizeArray:
    """Test cases for the normalize_array function."""

    def test_positive_values(self):
        """Test normalization of array with positive values."""
        arr = np.array([1, 2, 3, 4, 5], dtype=float)
        result = normalize_array(arr)

        # With positive values starting at 1, min won't be 0
        assert result.max() == 1.0
        assert result.shape == arr.shape
        # Values are divided by max (5), so: 1/5, 2/5, 3/5, 4/5, 5/5
        np.testing.assert_array_almost_equal(
            result, np.array([0.2, 0.4, 0.6, 0.8, 1.0])
        )

    def test_negative_values(self):
        """Test normalization shifts negative values correctly."""
        arr = np.array([-2, -1, 0, 1, 2], dtype=float)
        result = normalize_array(arr)

        assert result.min() == 0.0
        assert result.max() == 1.0
        assert result.shape == arr.shape
        np.testing.assert_array_almost_equal(
            result, np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        )

    def test_all_zeros(self):
        """Test normalization of array with all zeros."""
        arr = np.zeros((5, 5), dtype=float)
        result = normalize_array(arr)

        assert result.shape == arr.shape
        assert np.all(result == 0.0)

    def test_all_same_value(self):
        """Test normalization when all values are identical."""
        arr = np.ones((3, 3), dtype=float) * 42.0
        result = normalize_array(arr)

        assert result.shape == arr.shape
        # When all values are same and positive, max = that value, so result is all 1.0
        assert np.all(result == 1.0)

    def test_single_element(self):
        """Test normalization of single element array."""
        arr = np.array([5.0])
        result = normalize_array(arr)

        assert result.shape == arr.shape
        # Single positive value normalized by itself equals 1.0
        assert result[0] == 1.0

    def test_2d_array(self):
        """Test normalization of 2D array."""
        arr = np.array([[0, 1, 2], [3, 4, 5]], dtype=float)
        result = normalize_array(arr)

        assert result.shape == arr.shape
        assert result.min() == 0.0
        assert result.max() == 1.0
        assert result[0, 0] == 0.0
        assert result[1, 2] == 1.0

    def test_integer_dtype(self):
        """Test normalization preserves behavior with integer input."""
        arr = np.array([10, 20, 30, 40, 50], dtype=np.int32)
        result = normalize_array(arr)

        assert result.dtype == np.float64
        assert result.max() == 1.0
        # Values divided by max (50): 10/50, 20/50, etc.
        np.testing.assert_array_almost_equal(
            result, np.array([0.2, 0.4, 0.6, 0.8, 1.0])
        )

    def test_uint8_dtype(self):
        """Test normalization with uint8 input (common for images)."""
        arr = np.array([0, 64, 128, 192, 255], dtype=np.uint8)
        result = normalize_array(arr)

        assert result.dtype == np.float64
        assert result.min() == 0.0
        assert result.max() == 1.0
        np.testing.assert_array_almost_equal(
            result, np.array([0.0, 64 / 255, 128 / 255, 192 / 255, 1.0])
        )

    def test_large_array(self):
        """Test normalization performance with large array."""
        arr = np.random.rand(1000, 1000) * 100 - 50  # Random values -50 to 50
        result = normalize_array(arr)

        assert result.shape == arr.shape
        assert 0.0 <= result.min() <= 0.01  # Close to 0
        assert 0.99 <= result.max() <= 1.0  # Close to 1

    def test_negative_only_values(self):
        """Test normalization with only negative values."""
        arr = np.array([-10, -8, -6, -4, -2], dtype=float)
        result = normalize_array(arr)

        assert result.min() == 0.0
        assert result.max() == 1.0
        np.testing.assert_array_almost_equal(
            result, np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        )

    def test_preserves_shape(self):
        """Test that normalization preserves array shape."""
        shapes = [(5,), (5, 5), (2, 3, 4), (10, 20, 30)]
        for shape in shapes:
            arr = np.random.rand(*shape)
            result = normalize_array(arr)
            assert result.shape == shape

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            # This should raise an error (testing error propagation)
            normalize_array(None)
