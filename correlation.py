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
from typing import Optional, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage.feature import match_template

# Maximum image dimension in pixels (configurable for memory protection)
MAX_DIMENSION = 10000


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


def generate_output_filename(input_file: str, match_file: str) -> str:
    """
    Generate a descriptive output filename based on input filenames.

    Args:
        input_file: Path to the input image file
        match_file: Path to the match template file

    Returns:
        Generated filename in format: {input}_vs_{match}_correlation.jpg
    """
    input_stem = Path(input_file).stem
    match_stem = Path(match_file).stem
    return f"{input_stem}_vs_{match_stem}_correlation.jpg"


def load_images(
    input_file: str, match_file: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load and convert images to grayscale numpy arrays.

    Args:
        input_file: Path to the input image file
        match_file: Path to the match template file

    Returns:
        Tuple of (input_array, match_array) as numpy arrays

    Raises:
        FileNotFoundError: If image file doesn't exist
        UnidentifiedImageError: If image format is invalid
        PermissionError: If file access is denied
        Exception: For other image loading errors
    """
    try:
        im1 = Image.open(input_file).convert("L")
        im2 = Image.open(match_file).convert("L")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Image file not found: {e}") from e
    except UnidentifiedImageError as e:
        raise UnidentifiedImageError(
            f"Cannot identify image file (invalid format): {e}"
        ) from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading image file: {e}") from e
    except Exception as e:
        raise Exception(f"Error opening or converting images: {e}") from e

    # Convert from Image to Numpy array
    try:
        input_array = np.asarray(im1)
        match_array = np.asarray(im2)
    except Exception as e:
        raise ValueError(f"Error converting images to arrays: {e}") from e

    return input_array, match_array


def validate_dimensions(
    input_arr: np.ndarray, match_arr: np.ndarray, max_dimension: int = MAX_DIMENSION
) -> None:
    """
    Validate that image dimensions are appropriate for correlation.

    Args:
        input_arr: Input image array
        match_arr: Match template array
        max_dimension: Maximum allowed dimension in pixels (default: 10000)

    Raises:
        ValueError: If dimensions are invalid
    """
    # Check for zero or very small dimensions
    if input_arr.size == 0 or match_arr.size == 0:
        raise ValueError("Images cannot be empty (0 pixels)")

    if input_arr.shape[0] < 2 or input_arr.shape[1] < 2:
        raise ValueError(
            f"Input image too small: {input_arr.shape}. Minimum size is 2x2 pixels"
        )

    if match_arr.shape[0] < 1 or match_arr.shape[1] < 1:
        raise ValueError(
            f"Match template too small: {match_arr.shape}. Minimum size is 1x1 pixel"
        )

    # Check maximum dimensions (memory protection)
    if input_arr.shape[0] > max_dimension or input_arr.shape[1] > max_dimension:
        raise ValueError(
            f"Input image too large: {input_arr.shape}. "
            f"Maximum dimension is {max_dimension} pixels"
        )

    if match_arr.shape[0] > max_dimension or match_arr.shape[1] > max_dimension:
        raise ValueError(
            f"Match template too large: {match_arr.shape}. "
            f"Maximum dimension is {max_dimension} pixels"
        )

    # Check that match template is smaller than input
    if (
        match_arr.shape[0] >= input_arr.shape[0]
        or match_arr.shape[1] >= input_arr.shape[1]
    ):
        raise ValueError(
            f"Match template {match_arr.shape} must be smaller than "
            f"input image {input_arr.shape}"
        )


def save_correlation(corr: np.ndarray, output_file: Path) -> None:
    """
    Normalize correlation array and save as image.

    Args:
        corr: Correlation result array
        output_file: Validated output path

    Raises:
        ValueError: If normalization fails
        PermissionError: If file write permission denied
        OSError: If file system error occurs
    """
    try:
        normalized = normalize_array(corr)
        output_image = Image.fromarray(np.uint8(normalized * 255))
    except Exception as e:
        raise ValueError(f"Error creating output image: {e}") from e

    try:
        print(f"Saving as: {output_file}")
        output_image.save(output_file)
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing output file: {e}") from e
    except OSError as e:
        raise OSError(f"Error saving output file: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error saving file: {e}") from e


def main(
    input_file: str, match_file: str, output_file: Optional[str] = None
) -> None:
    """
    Orchestrate the image correlation workflow.

    Args:
        input_file: Path to the input image file
        match_file: Path to the match template file
        output_file: Optional output filename. If None, generates from inputs.
    """
    # Generate output filename if not provided
    if output_file is None:
        output_file = generate_output_filename(input_file, match_file)

    # Validate output path first
    try:
        validated_output = validate_output_path(output_file)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load and convert images
    try:
        input_array, match_array = load_images(input_file, match_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except UnidentifiedImageError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Validate dimensions
    try:
        validate_dimensions(input_array, match_array)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Compute correlation
    try:
        corr = correlation(input_array, match_array)
    except Exception as e:
        print(f"Error computing correlation: {e}")
        sys.exit(1)

    # Save result
    try:
        save_correlation(corr, validated_output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("USAGE: python correlation.py <image file> <match file>")
