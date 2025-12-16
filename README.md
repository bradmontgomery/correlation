correlation.py
==============

This module provides a very simplistic method to compute the
[digital image correlation](https://en.wikipedia.org/wiki/Digital_image_correlation)
between two, single-channel, grayscale input images. If you run `correlation.py`
with 3-channel color images (e.g. .jpg files), they'll be converted to grayscale.

The second image must be smaller than the first.

**NOTE**: This script uses `scikit-image` for efficient correlation computation.


Usage
-----

Here's how to use this script with `uv`:

1. Sync dependencies: `uv sync`
2. Run the script: `uv run correlation.py <input-image> <smaller-image-to-match>`


Examples
--------

See the images in `example_images` for an example of this code. Run the
following command to see the results:

    uv run correlation.py example_images/dandilions.jpg example_images/tip.jpg


License
-------

This code may be distributed under the terms of the MIT license. See the
[LICENSE.txt](LICENSE.txt) file for the full license.
