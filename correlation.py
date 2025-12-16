#!/usr/bin/env python3
"""
correlation.py - Digital Image Correlation

This module provides functionality to compute the digital image correlation
between two single-channel grayscale images using normalized cross-correlation.

Digital Image Correlation (DIC) is a technique used to track and measure changes
between two images. The algorithm finds where a template (smaller image) appears
within a larger input image by computing correlation coefficients at each position.

Main Functions:
    - load_images: Load and convert images to grayscale arrays
    - validate_dimensions: Verify image dimensions are appropriate
    - correlation: Compute normalized cross-correlation
    - normalize_array: Scale array values to [0, 1] range
    - save_correlation: Save correlation result as image
    - main: Orchestrate the complete workflow

Usage:
    Basic usage with automatic output naming:
        python correlation.py input.jpg template.jpg

    Output will be saved as: input_vs_template_correlation.jpg

Requirements:
    - Input image must be larger than template image
    - Both images will be converted to grayscale
    - Images must not exceed MAX_DIMENSION (10000x10000 pixels)

Limitations:
    - Memory usage scales with input image size
    - Processing time increases with image dimensions
    - Large images may require significant computational resources

Author: Brad Montgomery
        http://bradmontgomery.net

License: MIT

"""
import logging
import sys
import timeit
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage.feature import match_template

# Configure module logger
logger = logging.getLogger(__name__)

# Maximum image dimension in pixels (configurable for memory protection)
MAX_DIMENSION = 10000


def normalize_array(array: np.ndarray) -> np.ndarray:
    """
    Normalize array values to the range [0, 1].

    This function performs min-max normalization, scaling all values in the input
    array to fall between 0 and 1. Negative values are shifted to be non-negative
    before scaling.

    Args:
        array: Input numpy array of any numeric type and shape

    Returns:
        Float array of the same shape with values normalized to [0, 1]

    Raises:
        ValueError: If array normalization fails

    Notes:
        - If the array has negative values, they are shifted by adding abs(min)
        - If all values are identical (max == 0 after shifting), returns zeros
        - The input array is not modified; a new array is returned

    Examples:
        >>> arr = np.array([1, 2, 3, 4, 5])
        >>> normalized = normalize_array(arr)
        >>> normalized
        array([0.  , 0.25, 0.5 , 0.75, 1.  ])

        >>> arr_negative = np.array([-2, -1, 0, 1, 2])
        >>> normalized = normalize_array(arr_negative)
        >>> normalized
        array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    """
    try:
        minval = array.min()
        if minval < 0:
            array = array + abs(minval)
        maxval = array.max()
        if maxval == 0:
            logger.warning(
                "Array has zero max value after shifting. Returning zero array."
            )
            return np.zeros(array.shape, dtype=float)
        return array.astype(float) / maxval
    except Exception as e:
        raise ValueError(f"Error normalizing array: {e}") from e


def correlation(input_arr: np.ndarray, match_arr: np.ndarray) -> np.ndarray:
    """
    Calculate normalized cross-correlation between pixel arrays.

    Uses scikit-image's match_template to compute the normalized cross-correlation
    coefficient at each position where the template could be placed on the input.
    The result is padded to match the input size for visualization purposes.

    Args:
        input_arr: Input image as 2D numpy array (grayscale)
        match_arr: Template image as 2D numpy array (must be smaller than input)

    Returns:
        Correlation coefficient map as 2D numpy array, same size as input.
        Values range from -1 (anti-correlated) to 1 (perfectly correlated).
        Padded regions (where template extends beyond input) are filled with 0.

    Raises:
        RuntimeError: If correlation computation or padding fails

    Notes:
        - Uses normalized cross-correlation (invariant to brightness/contrast)
        - Output is padded with zeros to match input dimensions
        - Padded regions (right and bottom edges) contain no meaningful correlation data
        - Time complexity: O(n*m*k*l) where input is n×m and template is k×l
        - Higher correlation values indicate better matches

    Implementation Details:
        The padding is added for backward compatibility and consistent output sizing.
        The match_template function naturally returns a smaller array (by template size).
        We pad with zeros on the right and bottom edges to restore original dimensions.
    """
    logger.info("Computing correlation coefficients...")
    start_time = timeit.default_timer()

    try:
        # Use scikit-image's match_template which implements normalized
        # cross-correlation
        correlation_result = match_template(input_arr, match_arr)
    except Exception as e:
        raise RuntimeError(f"Error computing correlation: {e}") from e

    # Pad the result to match the input size
    # The original implementation produced an output of the same size as input.
    # We pad with zeros on the right and bottom to maintain backward compatibility.
    # Note: These padded regions contain no actual correlation data - they represent
    # positions where the template would extend beyond the input image boundaries.
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
    logger.info(f"Correlation computed in {elapsed} seconds")
    logger.debug(
        f"Correlation statistics - Max: {correlation_result.max():.6f}, "
        f"Min: {correlation_result.min():.6f}, "
        f"Mean: {correlation_result.mean():.6f}"
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
        raise ValueError(f"Output directory does not exist: {output_path.parent}")

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


def load_images(input_file: str, match_file: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load and convert images to grayscale numpy arrays.

    Opens the specified image files, converts them to grayscale (single channel),
    and returns them as numpy arrays suitable for correlation computation.

    Args:
        input_file: Path to the input image file (larger image)
        match_file: Path to the match template file (smaller image)

    Returns:
        Tuple of (input_array, match_array) as 2D numpy arrays

    Raises:
        FileNotFoundError: If image file doesn't exist
        UnidentifiedImageError: If image format is invalid or corrupted
        PermissionError: If file access is denied
        ValueError: If image to array conversion fails
        Exception: For other image loading errors

    Notes:
        - Images are automatically converted to grayscale ('L' mode)
        - Supports common formats: JPEG, PNG, BMP, TIFF, etc.
        - Uses context managers to ensure proper resource cleanup
    """
    try:
        with Image.open(input_file) as img1, Image.open(match_file) as img2:
            im1 = img1.convert("L")
            im2 = img2.convert("L")

            # Convert from PIL Image to numpy array
            try:
                input_array = np.asarray(im1)
                match_array = np.asarray(im2)
            except Exception as e:
                raise ValueError(f"Error converting images to arrays: {e}") from e

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
    Normalize correlation array and save as an image file.

    Takes the correlation result, normalizes it to [0, 255] range for
    visualization, and saves it as a grayscale image.

    Args:
        corr: Correlation result array (2D numpy array with float values)
        output_file: Validated output path (Path object)

    Raises:
        ValueError: If normalization or image creation fails
        PermissionError: If file write permission denied
        OSError: If file system error occurs during save

    Notes:
        - Correlation values are normalized to [0, 1] then scaled to [0, 255]
        - Output is saved as 8-bit grayscale image
        - Higher brightness indicates higher correlation at that position
    """
    try:
        normalized = normalize_array(corr)
        output_image = Image.fromarray(np.uint8(normalized * 255))
    except Exception as e:
        raise ValueError(f"Error creating output image: {e}") from e

    try:
        logger.info(f"Saving correlation result to: {output_file}")
        output_image.save(output_file)
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing output file: {e}") from e
    except OSError as e:
        raise OSError(f"Error saving output file: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error saving file: {e}") from e


def main(input_file: str, match_file: str, output_file: Optional[str] = None) -> None:
    """
    Orchestrate the image correlation workflow.

    This is the main entry point that coordinates loading images, validating
    dimensions, computing correlation, and saving results. It handles all error
    conditions and provides user feedback.

    Args:
        input_file: Path to the input image file (larger image)
        match_file: Path to the match template file (smaller image to find)
        output_file: Optional output filename. If None, auto-generates based on
                    input filenames using format: {input}_vs_{match}_correlation.jpg

    Exit Codes:
        0: Success
        1: Error occurred (see error message for details)

    Examples:
        >>> # Basic usage with auto-generated output filename
        >>> main("photo.jpg", "template.jpg")

        >>> # Specify custom output filename
        >>> main("photo.jpg", "template.jpg", "my_result.jpg")
    """
    # Generate output filename if not provided
    if output_file is None:
        output_file = generate_output_filename(input_file, match_file)

    # Validate output path first
    try:
        validated_output = validate_output_path(output_file)
    except ValueError as e:
        logger.error(f"Output path validation failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    # Load and convert images
    try:
        input_array, match_array = load_images(input_file, match_file)
    except FileNotFoundError as e:
        logger.error(f"Image file not found: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except UnidentifiedImageError as e:
        logger.error(f"Invalid image format: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Image loading failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    # Validate dimensions
    try:
        validate_dimensions(input_array, match_array)
    except ValueError as e:
        logger.error(f"Dimension validation failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    # Compute correlation
    try:
        corr = correlation(input_array, match_array)
    except Exception as e:
        logger.error(f"Correlation computation failed: {e}")
        print(f"Error computing correlation: {e}")
        sys.exit(1)

    # Save result
    try:
        save_correlation(corr, validated_output)
    except Exception as e:
        logger.error(f"Failed to save output: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Configure logging for CLI usage
    # Default to INFO level - shows progress but not debug details
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("USAGE: python correlation.py <image file> <match file>")
