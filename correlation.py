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

    With options:
        python correlation.py input.jpg template.jpg -o output.png --format png

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
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage.feature import match_template

__version__ = "0.2.0"

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
    start_time = time.perf_counter()

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

    elapsed = time.perf_counter() - start_time
    logger.info(f"Correlation computed in {elapsed:.2f} seconds")
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


def save_correlation(
    corr: np.ndarray, output_file: Path, output_format: str = "jpg"
) -> None:
    """
    Normalize correlation array and save in specified format.

    Takes the correlation result, normalizes it appropriately for the format,
    and saves it as an image or numpy array.

    Args:
        corr: Correlation result array (2D numpy array with float values)
        output_file: Validated output path (Path object)
        output_format: Output format - 'jpg', 'png', 'tiff', or 'npy'

    Raises:
        ValueError: If normalization or image creation fails
        PermissionError: If file write permission denied
        OSError: If file system error occurs during save

    Notes:
        - For jpg/png: Values normalized to [0, 1] then scaled to [0, 255]
        - For tiff: Saved as float32 preserving full precision
        - For npy: Raw correlation array saved with numpy
        - Higher brightness indicates higher correlation at that position
    """
    output_format = output_format.lower()

    try:
        if output_format == "npy":
            # Save raw correlation array
            logger.info(f"Saving correlation array to: {output_file}")
            np.save(output_file, corr)
        elif output_format == "tiff":
            # Save as float32 TIFF to preserve precision
            logger.info(f"Saving correlation result (float32) to: {output_file}")
            # Convert to float32 and save
            output_image = Image.fromarray(corr.astype(np.float32), mode="F")
            output_image.save(output_file)
        else:
            # Save as 8-bit image (jpg, png)
            normalized = normalize_array(corr)
            output_image = Image.fromarray(np.uint8(normalized * 255))
            logger.info(f"Saving correlation result to: {output_file}")
            output_image.save(output_file)
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing output file: {e}") from e
    except OSError as e:
        raise OSError(f"Error saving output file: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error saving file: {e}") from e


def save_statistics(corr: np.ndarray, output_file: str) -> None:
    """
    Save correlation statistics to JSON file.

    Args:
        corr: Correlation result array
        output_file: Path to JSON output file

    Raises:
        OSError: If file write fails
    """
    stats = {
        "max": float(corr.max()),
        "min": float(corr.min()),
        "mean": float(corr.mean()),
        "std": float(corr.std()),
        "shape": corr.shape,
    }

    try:
        logger.info(f"Saving statistics to: {output_file}")
        with open(output_file, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        raise OSError(f"Error saving statistics: {e}") from e


def main(
    input_file: str,
    match_file: str,
    output_file: Optional[str] = None,
    output_format: str = "jpg",
    max_dimension: int = MAX_DIMENSION,
    save_stats: bool = False,
    allow_absolute_paths: bool = False,
) -> None:
    """
    Orchestrate the image correlation workflow.

    This is the main entry point that coordinates loading images, validating
    dimensions, computing correlation, and saving results. It handles all error
    conditions and provides user feedback.

    Args:
        input_file: Path to the input image file (larger image)
        match_file: Path to the match template file (smaller image to find)
        output_file: Optional output filename. If None, auto-generates based on
                    input filenames using format: {input}_vs_{match}_correlation.{ext}
        output_format: Output format - 'jpg', 'png', 'tiff', or 'npy'
        max_dimension: Maximum image dimension in pixels
        save_stats: Whether to save statistics to JSON
        allow_absolute_paths: Allow output paths outside current directory

    Exit Codes:
        0: Success
        1: Error occurred (see error message for details)

    Examples:
        >>> # Basic usage with auto-generated output filename
        >>> main("photo.jpg", "template.jpg")

        >>> # Specify custom output filename
        >>> main("photo.jpg", "template.jpg", "my_result.jpg")

        >>> # Save as TIFF with statistics
        >>> main("photo.jpg", "template.jpg", format="tiff", save_stats=True)
    """
    start_total = time.perf_counter()

    # Generate output filename if not provided
    if output_file is None:
        base_name = generate_output_filename(input_file, match_file)
        # Replace extension with chosen format
        output_file = str(Path(base_name).with_suffix(f".{output_format}"))

    # Validate output path first (unless absolute paths allowed)
    if not allow_absolute_paths:
        try:
            validated_output = validate_output_path(output_file)
        except ValueError as e:
            logger.error(f"Output path validation failed: {e}")
            print(f"Error: {e}")
            sys.exit(1)
    else:
        validated_output = Path(output_file)

    # Load and convert images
    load_start = time.perf_counter()
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
    load_time = time.perf_counter() - load_start
    logger.debug(f"Images loaded in {load_time:.2f} seconds")

    # Validate dimensions
    try:
        validate_dimensions(input_array, match_array, max_dimension=max_dimension)
    except ValueError as e:
        logger.error(f"Dimension validation failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    # Compute correlation
    compute_start = time.perf_counter()
    try:
        corr = correlation(input_array, match_array)
    except Exception as e:
        logger.error(f"Correlation computation failed: {e}")
        print(f"Error computing correlation: {e}")
        sys.exit(1)
    compute_time = time.perf_counter() - compute_start

    # Save result
    save_start = time.perf_counter()
    try:
        save_correlation(corr, validated_output, output_format)
    except Exception as e:
        logger.error(f"Failed to save output: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    save_time = time.perf_counter() - save_start
    logger.debug(f"Result saved in {save_time:.2f} seconds")

    # Save statistics if requested
    if save_stats:
        stats_file = validated_output.with_suffix(".json")
        try:
            save_statistics(corr, str(stats_file))
        except Exception as e:
            logger.warning(f"Failed to save statistics: {e}")

    total_time = time.perf_counter() - start_total
    logger.info(
        f"Total time: {total_time:.2f}s "
        f"(load: {load_time:.2f}s, compute: {compute_time:.2f}s, "
        f"save: {save_time:.2f}s)"
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compute digital image correlation between two grayscale images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with auto-generated output
  python correlation.py input.jpg template.jpg

  # Specify output filename
  python correlation.py input.jpg template.jpg -o result.png

  # Save as TIFF with statistics
  python correlation.py input.jpg template.jpg --format tiff --save-stats

  # Verbose output
  python correlation.py input.jpg template.jpg -v
        """,
    )

    parser.add_argument("input_file", help="Input image file (larger image)")
    parser.add_argument("match_file", help="Template image file (smaller image)")

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Output filename (default: auto-generated)",
    )

    parser.add_argument(
        "--format",
        choices=["jpg", "png", "tiff", "npy"],
        default="jpg",
        help="Output format (default: jpg)",
    )

    parser.add_argument(
        "--max-dimension",
        type=int,
        default=MAX_DIMENSION,
        help=f"Maximum image dimension in pixels (default: {MAX_DIMENSION})",
    )

    parser.add_argument(
        "--save-stats",
        action="store_true",
        help="Save correlation statistics to JSON file",
    )

    parser.add_argument(
        "--allow-absolute-paths",
        action="store_true",
        help="Allow output paths outside current directory (use with caution)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output (DEBUG level)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress all output except errors"
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Configure logging based on verbosity flags
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Call main with parsed arguments
    main(
        input_file=args.input_file,
        match_file=args.match_file,
        output_file=args.output_file,
        output_format=args.format,
        max_dimension=args.max_dimension,
        save_stats=args.save_stats,
        allow_absolute_paths=args.allow_absolute_paths,
    )
