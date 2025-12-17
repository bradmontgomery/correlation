# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-16

### Added

#### Enhanced Features (Phase 6)
- **Professional CLI with argparse**: Replaced basic sys.argv parsing with comprehensive argument parser
  - Added `-o, --output` for custom output filenames
  - Added `--format` to select output format (jpg, png, tiff, npy)
  - Added `--max-dimension` to configure maximum image size
  - Added `--save-stats` to export correlation statistics to JSON
  - Added `--allow-absolute-paths` for security override
  - Added `-v, --verbose` for DEBUG level logging
  - Added `-q, --quiet` for ERROR level logging only
  - Added `--version` to show version number
- **Multiple output formats**: Support for JPG, PNG, TIFF (float32), and NPY (numpy array)
- **Statistics export**: JSON export with max, min, mean, std, and shape
- **Performance timing**: Detailed breakdown of load, compute, and save times
- **Version information**: Added `__version__ = "0.2.0"`

#### CI/CD & Automation (Phase 5)
- **GitHub Actions workflow**: Automated CI pipeline
  - Code formatting checks with black
  - Linting with flake8
  - Test suite with coverage reporting
  - Codecov integration ready
  - Artifact preservation
- **Pre-commit hooks**: 11 hooks for code quality
  - black for formatting
  - flake8 for linting
  - File cleanup (trailing whitespace, EOF, etc.)
  - YAML/TOML validation
  - Large file detection
  - Merge conflict detection
- **`.gitignore`**: Comprehensive Python gitignore

#### Testing Infrastructure (Phase 4)
- **pytest framework**: Comprehensive test suite
  - 42 unit and integration tests
  - 68% code coverage
  - Test fixtures in conftest.py
  - Coverage configuration (.coveragerc)
- **Test organization**:
  - `tests/test_normalize_array.py`: 12 tests
  - `tests/test_correlation.py`: 10 tests
  - `tests/test_integration.py`: 20 integration tests

#### Documentation & Best Practices (Phase 3)
- **Enhanced docstrings**: Google/NumPy format for all functions
  - Complete Args/Returns/Raises/Notes sections
  - Usage examples in docstrings
  - Module-level documentation
- **Logging framework**: Replaced print() with structured logging
  - INFO level for progress messages
  - DEBUG level for detailed statistics
  - WARNING level for non-fatal issues
  - ERROR level for failures
- **Context managers**: Resource-safe image loading
- **Detailed padding documentation**: Explained backward compatibility

#### Code Architecture (Phase 2)
- **Refactored main()**: Extracted into smaller, testable functions
  - `load_images()`: Image loading and conversion
  - `validate_dimensions()`: Comprehensive dimension checks
  - `save_correlation()`: Image saving with format support
  - `generate_output_filename()`: Dynamic filename generation
- **Memory protection**: Maximum dimension validation
- **Better separation of concerns**: Single Responsibility Principle

#### Foundation & Security (Phase 1)
- **Type hints**: Full type annotations on all functions
- **PEP 8 compliance**: Proper naming conventions
- **Path validation**: Security against path traversal attacks
- **Error handling**: Comprehensive exception handling with 7 specific exception types
- **Input validation**: Dimension checks, size limits, format validation

### Changed

- **Function names**: `normalizeArray()` → `normalize_array()` (PEP 8)
- **Variable names**: Improved from cryptic (f1, f2) to descriptive (input_file, match_file)
- **Timing**: Changed from `timeit.default_timer()` to `time.perf_counter()` for better accuracy
- **Output filename**: Now auto-generated as `{input}_vs_{match}_correlation.{ext}`
- **save_correlation()**: Now accepts `output_format` parameter

### Fixed

- **Usage string**: Added .py extension to examples
- **Resource leaks**: Images now use context managers
- **Error messages**: More descriptive and user-friendly
- **Code formatting**: Applied black formatting throughout

### Security

- **Path validation**: Prevents path traversal attacks (../ sequences)
- **Output restrictions**: Default restriction to current directory
- **Size limits**: Configurable maximum dimensions (default: 10000px)
- **Permission handling**: Graceful permission error handling

### Performance

- **Optimized timing**: Sub-millisecond accuracy with perf_counter
- **Detailed profiling**: Load/compute/save time breakdown
- **Efficient logging**: Configurable verbosity levels

### Documentation

- **README.md**: Complete rewrite with:
  - Badges (CI, License, Python version)
  - Feature list
  - Comprehensive usage examples
  - CLI reference
  - Performance notes
  - Troubleshooting section
- **CONTRIBUTING.md**: Contribution guidelines added
- **CHANGELOG.md**: This file
- **Code comments**: Detailed inline documentation

### Development

- **uv**: Migrated to uv for dependency management
- **pyproject.toml**: Centralized configuration
- **pytest.ini**: Test configuration
- **.coveragerc**: Coverage configuration
- **.pre-commit-config.yaml**: Pre-commit hooks
- **.github/workflows/ci.yml**: CI/CD pipeline

## [0.1.0] - 2020-XX-XX

### Initial Release

- Basic correlation computation using custom implementation
- JPEG output only
- Simple command-line interface
- Basic error handling

[0.2.0]: https://github.com/bradmontgomery/correlation/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bradmontgomery/correlation/releases/tag/v0.1.0
