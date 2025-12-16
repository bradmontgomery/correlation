"""Pytest configuration and shared fixtures."""
import numpy as np
import pytest
from pathlib import Path
from PIL import Image


@pytest.fixture
def simple_input_array():
    """Create a simple 10x10 input array with a pattern."""
    arr = np.zeros((10, 10), dtype=np.uint8)
    arr[3:6, 3:6] = 255  # White square in the middle
    return arr


@pytest.fixture
def simple_match_array():
    """Create a simple 3x3 match template."""
    arr = np.ones((3, 3), dtype=np.uint8) * 255
    return arr


@pytest.fixture
def test_image_path(tmp_path):
    """Create a temporary test image file."""
    img = Image.new('L', (100, 100), color=128)
    img_path = tmp_path / "test_image.jpg"
    img.save(img_path)
    return img_path


@pytest.fixture
def test_template_path(tmp_path):
    """Create a temporary template image file."""
    img = Image.new('L', (20, 20), color=200)
    img_path = tmp_path / "test_template.jpg"
    img.save(img_path)
    return img_path


@pytest.fixture
def output_path(tmp_path):
    """Create a temporary output path."""
    return tmp_path / "output.jpg"
