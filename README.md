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

    python correlation.py <input-image> <smaller-image-to-match>


Examples
--------

See the images in `example_images` for an example of this code. Run
`python correlation example_images/dandilions.jp example_images/tip.jp` to
see the results.


License
-------

This code may be distributed under the terms of the MIT lices. See `LICENSE.txt`.
