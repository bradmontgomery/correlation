correlation.py
==============

This module provides a very simplistic method to compute the
[digital image correlation](https://en.wikipedia.org/wiki/Digital_image_correlation)
between two, single-channel, grayscale input images. If you run `correlation.py`
with 3-channel color images (e.g. .jpg files), they'll be converted to grayscale.

The second image must be smaller than the first.

**NOTE**: This is a very simple, slow, inneficient way to compute correlation.


Usage
-----

Here's one way to use this script:

1. Create a virtual environment with `python3 -m venv env`
2. Activate it: `source env/bin/activate`
3. Install the required libraries: `pip install -r requirements.txt`
4. Run the script: `python correlation.py <input-image> <smaller-image-to-match>`


Examples
--------

See the images in `example_images` for an example of this code. Run the
following command to see the results:

    python correlation example_images/dandilions.jpg example_images/tip.jpg


License
-------

This code may be distributed under the terms of the MIT license. See the
[LICENSE.txt](LICENSE.txt) file for the full license.
