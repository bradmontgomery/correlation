# correlation.py

[![CI](https://github.com/bradmontgomery/correlation/actions/workflows/ci.yml/badge.svg)](https://github.com/bradmontgomery/correlation/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A Python tool for computing [digital image correlation](https://en.wikipedia.org/wiki/Digital_image_correlation) between two grayscale images using normalized cross-correlation.

## Features

- ✅ **Efficient correlation** using scikit-image's optimized algorithms
- ✅ **Multiple output formats** (JPG, PNG, TIFF, NPY)
- ✅ **Statistics export** to JSON
- ✅ **Comprehensive CLI** with argparse
- ✅ **Type hints** and full test coverage
- ✅ **Security features** (path validation, size limits)
- ✅ **Performance timing** breakdown

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone https://github.com/bradmontgomery/correlation.git
cd correlation

# Sync dependencies
uv sync
```

## Usage

### Basic Usage

```bash
# Auto-generated output filename
uv run python correlation.py input.jpg template.jpg

# Specify output filename
uv run python correlation.py input.jpg template.jpg -o result.png
```

### Advanced Options

```bash
# Save as PNG with statistics
uv run python correlation.py input.jpg template.jpg --format png --save-stats

# Save as float32 TIFF for scientific analysis
uv run python correlation.py input.jpg template.jpg --format tiff

# Save raw numpy array
uv run python correlation.py input.jpg template.jpg --format npy

# Verbose output with timing details
uv run python correlation.py input.jpg template.jpg -v

# Quiet mode (errors only)
uv run python correlation.py input.jpg template.jpg -q

# Custom max dimension
uv run python correlation.py input.jpg template.jpg --max-dimension 5000
```

### CLI Options

```
positional arguments:
  input_file            Input image file (larger image)
  match_file            Template image file (smaller image)

options:
  -h, --help            Show help message and exit
  -o, --output          Output filename (default: auto-generated)
  --format              Output format: jpg, png, tiff, npy (default: jpg)
  --max-dimension       Maximum image dimension in pixels (default: 10000)
  --save-stats          Save correlation statistics to JSON file
  --allow-absolute-paths Allow output paths outside current directory
  -v, --verbose         Enable verbose output (DEBUG level)
  -q, --quiet           Suppress all output except errors
  --version             Show version number and exit
```

## Examples

The `example_images` directory contains sample images. Try:

```bash
uv run python correlation.py example_images/dandelions.jpg example_images/tip.jpg
```

This will create `dandelions_vs_tip_correlation.jpg` showing where the template appears in the input image.

## Output Formats

- **JPG** (default): 8-bit grayscale, suitable for visualization
- **PNG**: 8-bit grayscale, lossless compression
- **TIFF**: 32-bit float, preserves full correlation precision
- **NPY**: Raw numpy array for further analysis

## Statistics Export

Use `--save-stats` to export correlation statistics to JSON:

```json
{
  "max": 0.999930804558912,
  "min": -0.7516019751334637,
  "mean": 0.010192396331339872,
  "std": 0.18944689670704123,
  "shape": [3744, 5616]
}
```

## Performance

Typical performance on a modern laptop:
- Small images (< 1000x1000): < 1 second
- Medium images (2000x2000): 2-5 seconds
- Large images (4000x4000): 10-30 seconds

Performance breakdown is logged with `-v` flag.

## Requirements

- **Python**: 3.12 or higher
- **Input images**: Must be larger than template
- **Template**: Must be smaller than input image
- **Memory**: Scales with image size (approx. width × height × 8 bytes)
- **Max dimension**: 10000×10000 pixels (configurable)

## Limitations

- Images are automatically converted to grayscale
- Template must be smaller than input image in both dimensions
- Large images may require significant memory and processing time
- Correlation computation is CPU-intensive (no GPU acceleration)

## Development

### Setup

```bash
# Install development dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=correlation --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_correlation.py -v
```

### Code Quality

```bash
# Format code
uv run black correlation.py tests/

# Lint code
uv run flake8 correlation.py tests/

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Running Linters

The project uses:
- **black** for code formatting
- **flake8** for linting
- **pytest** for testing

These run automatically via pre-commit hooks and GitHub Actions.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Troubleshooting

### "Match template must be smaller than input image"
Ensure the template image dimensions are smaller than the input image in both width and height.

### "Image too large"
The default maximum dimension is 10000 pixels. Use `--max-dimension` to adjust, but be aware of memory requirements.

### Out of memory errors
Reduce image size or increase available RAM. Consider downsampling large images before processing.

### Slow performance
- Use smaller images if possible
- Enable verbose mode (`-v`) to see timing breakdown
- Consider using TIFF format only for final high-precision results

## License

This code is distributed under the MIT license. See [LICENSE.txt](LICENSE.txt) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Author

Brad Montgomery
- Website: http://bradmontgomery.net
- GitHub: [@bradmontgomery](https://github.com/bradmontgomery)
