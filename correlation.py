#!/usr/bin/env python3
"""
correlation.py

Compute the correlation between two, single-channel, grayscale input images.
The second image must be smaller than the first.

Author: Brad Montgomery
        http://bradmontgomery.net

License: MIT

USAGE: python correlation <image file> <match file>

"""
import sys
import timeit
import numpy as np
from PIL import Image
from skimage.feature import match_template


def normalizeArray(a):
    """
    Normalize the given array to values between 0 and 1.
    Return a numpy array of floats (of the same shape as given)
    """
    minval = a.min()
    if minval < 0:
        a = a + abs(minval)
    maxval = a.max()
    if maxval == 0:
        return np.zeros(a.shape, dtype=float)
    return a.astype(float) / maxval


def correlation(input_arr, match_arr):
    """
    Calculate the correlation coefficients between the given pixel arrays.
    """
    print("Computing Correlation Coefficients...")
    start_time = timeit.default_timer()

    # Use scikit-image's match_template which implements normalized
    # cross-correlation
    c = match_template(input_arr, match_arr)

    # Pad the result to match the input size
    # The original implementation produced an output of the same size as input
    # We pad with zeros on the right and bottom
    pad_h = input_arr.shape[0] - c.shape[0]
    pad_w = input_arr.shape[1] - c.shape[1]

    if pad_h > 0 or pad_w > 0:
        c = np.pad(
            c, ((0, pad_h), (0, pad_w)), mode="constant", constant_values=0
        )

    elapsed = round(timeit.default_timer() - start_time, 2)
    print(f"=> Correlation computed in: {elapsed} seconds")
    print(f"\tMax: {c.max()}\n\tMin: {c.min()}\n\tMean: {c.mean()}")
    return c


def main(f1, f2, output_file="CORRELATION.jpg"):
    """Open the image files, and compute their correlation"""
    try:
        im1 = Image.open(f1).convert("L")
        im2 = Image.open(f2).convert("L")
    except IOError as e:
        print(f"Error opening images: {e}")
        sys.exit(1)

    # Convert from Image to Numpy array conversion
    f = np.asarray(im1)
    w = np.asarray(im2)

    # Check dimensions
    if w.shape[0] >= f.shape[0] or w.shape[1] >= f.shape[1]:
        print("Match Template must be Smaller than the input")
        sys.exit(1)

    corr = correlation(f, w)

    # Normalize and save
    c = Image.fromarray(np.uint8(normalizeArray(corr) * 255))

    print(f"Saving as: {output_file}")
    c.save(output_file)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("USAGE: python correlation <image file> <match file>")
