#!/usr/bin/env python3
"""
correlation.py

Compute the correlation between two, single-channel, grayscale input images.
The second image must be smaller than the first.

Author: Brad Montgomery
        http://bradmontgomery.net

License: MIT

USAGE: python correlation.py <image file> <match file>

"""
import sys
import timeit
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage.feature import match_template


def normalize_array(array: np.ndarray) -> np.ndarray:
    """
    Normalize the given array to values between 0 and 1.
    Return a numpy array of floats (of the same shape as given)
    """
    try:
        minval = array.min()
        if minval < 0:
            array = array + abs(minval)
        maxval = array.max()
        if maxval == 0:
            return np.zeros(array.shape, dtype=float)
        return array.astype(float) / maxval
    except Exception as e:
        raise ValueError(f"Error normalizing array: {e}") from e


def correlation(input_arr: np.ndarray, match_arr: np.ndarray) -> np.ndarray:
    """
    Calculate the correlation coefficients between the given pixel arrays.
    """
    print("Computing Correlation Coefficients...")
    start_time = timeit.default_timer()

    try:
        # Use scikit-image's match_template which implements normalized
        # cross-correlation
        correlation_result = match_template(input_arr, match_arr)
    except Exception as e:
        raise RuntimeError(f"Error computing correlation: {e}") from e

    # Pad the result to match the input size
    # The original implementation produced an output of the same size as input
    # We pad with zeros on the right and bottom
    pad_h = input_arr.shape[0] - correlation_result.shape[0]
    pad_w = input_arr.shape[1] - correlation_result.shape[1]

    if pad_h > 0 or pad_w > 0:
        try:
            correlation_result = np.pad(
                correlation_result,
                ((0, pad_h), (0, pad_w)),
                mode="constant",
                constant_values=0,
            )
        except Exception as e:
            raise RuntimeError(f"Error padding correlation result: {e}") from e

    elapsed = round(timeit.default_timer() - start_time, 2)
    print(f"=> Correlation computed in: {elapsed} seconds")
    print(
        f"\tMax: {correlation_result.max()}\n\tMin: {correlation_result.min()}\n\tMean: {correlation_result.mean()}"
    )
    return correlation_result


def validate_output_path(output_file: str) -> Path:
    """
    Validate and sanitize the output file path.

    Prevents path traversal attacks and restricts writes to safe locations.

    Args:
        output_file: The requested output file path

    Returns:
        Validated Path object

    Raises:
        ValueError: If path is invalid or potentially unsafe
    """
    output_path = Path(output_file)

    # Check for path traversal attempts
    try:
        # Resolve to absolute path and check if it's trying to escape cwd
        resolved = output_path.resolve()
        cwd = Path.cwd().resolve()

        # Allow files in current directory or subdirectories
        # This prevents writes to sensitive system directories
        if not str(resolved).startswith(str(cwd)):
            raise ValueError(
                f"Output path must be within current directory. "
                f"Got: {resolved}, Expected prefix: {cwd}"
            )

    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid output path '{output_file}': {e}") from e

    # Check if parent directory exists
    if not output_path.parent.exists():
        raise ValueError(
            f"Output directory does not exist: {output_path.parent}"
        )

    return output_path


def main(
    input_file: str, match_file: str, output_file: str = "CORRELATION.jpg"
) -> None:
    """Open the image files, and compute their correlation"""
    # Validate output path first
    try:
        validated_output = validate_output_path(output_file)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load and convert images
    try:
        im1 = Image.open(input_file).convert("L")
        im2 = Image.open(match_file).convert("L")
    except FileNotFoundError as e:
        print(f"Error: Image file not found: {e}")
        sys.exit(1)
    except UnidentifiedImageError as e:
        print(f"Error: Cannot identify image file (invalid format): {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied reading image file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening or converting images: {e}")
        sys.exit(1)

    # Convert from Image to Numpy array
    try:
        input_array = np.asarray(im1)
        match_array = np.asarray(im2)
    except Exception as e:
        print(f"Error converting images to arrays: {e}")
        sys.exit(1)

    # Check dimensions
    if (
        match_array.shape[0] >= input_array.shape[0]
        or match_array.shape[1] >= input_array.shape[1]
    ):
        print("Error: Match template must be smaller than the input image")
        sys.exit(1)

    # Compute correlation
    try:
        corr = correlation(input_array, match_array)
    except Exception as e:
        print(f"Error computing correlation: {e}")
        sys.exit(1)

    # Normalize and save
    try:
        normalized = normalize_array(corr)
        output_image = Image.fromarray(np.uint8(normalized * 255))
    except Exception as e:
        print(f"Error creating output image: {e}")
        sys.exit(1)

    try:
        print(f"Saving as: {validated_output}")
        output_image.save(validated_output)
    except PermissionError as e:
        print(f"Error: Permission denied writing output file: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error saving file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("USAGE: python correlation.py <image file> <match file>")
