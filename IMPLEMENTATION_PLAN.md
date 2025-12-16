# Implementation Plan - Code Review Remediation

**Date**: December 16, 2025  
**Branch**: `code-review-feedback`

This document outlines the work required to address all concerns raised in CODE_REVIEW.md.

---

## **Phase 1: Foundation & Critical Fixes** (Priority: High)

### Task 1.1: PEP 8 Compliance
- [ ] Rename `normalizeArray()` → `normalize_array()`
- [ ] Update all function calls to use new name
- [ ] Run `black` formatter on entire codebase
- [ ] Run `flake8` to verify compliance

**Files**: `correlation.py`  
**Estimated Time**: 15 minutes

### Task 1.2: Add Type Hints
- [ ] Import `typing` module and numpy types
- [ ] Add type hints to `normalize_array(a: np.ndarray) -> np.ndarray`
- [ ] Add type hints to `correlation(input_arr: np.ndarray, match_arr: np.ndarray) -> np.ndarray`
- [ ] Add type hints to `main(input_file: str, match_file: str, output_file: str = ...) -> None`
- [ ] Add type hints to helper functions (if any added)

**Files**: `correlation.py`  
**Estimated Time**: 20 minutes

### Task 1.3: Improve Variable Names
- [ ] `main()`: Rename `f1, f2` → `input_file, match_file`
- [ ] `main()`: Rename `f, w` → `input_array, match_array`
- [ ] `normalize_array()`: Rename `a` → `array`
- [ ] `correlation()`: Rename `c` → `correlation_result` or `corr_map`
- [ ] Update all references throughout code

**Files**: `correlation.py`  
**Estimated Time**: 25 minutes

### Task 1.4: Comprehensive Error Handling
- [ ] Wrap `Image.open().convert()` in try-except for conversion errors
- [ ] Add try-except around `c.save()` for write failures
- [ ] Add try-except around `match_template()` for computation errors
- [ ] Add try-except around numpy operations
- [ ] Create custom exception classes if needed (e.g., `ImageValidationError`)
- [ ] Provide helpful error messages for each failure mode

**Files**: `correlation.py`  
**Estimated Time**: 30 minutes

### Task 1.5: Output Path Validation
- [ ] Import `pathlib.Path`
- [ ] Add function `validate_output_path(path: str) -> Path`
- [ ] Check for path traversal attempts (`..` in path)
- [ ] Check for absolute paths to sensitive directories (`/etc`, `/sys`, etc.)
- [ ] Ensure parent directory exists or is writable
- [ ] Restrict output to current directory or subdirectories by default
- [ ] Add `--allow-absolute-paths` CLI flag for advanced users

**Files**: `correlation.py`  
**Estimated Time**: 40 minutes

**Phase 1 Total**: ~2.5 hours

---

## **Phase 2: Code Architecture & Design** (Priority: High-Medium)

### Task 2.1: Refactor `main()` - Extract Functions
- [ ] Create `load_images(input_file: str, match_file: str) -> tuple[np.ndarray, np.ndarray]`
  - Handle file opening, conversion to grayscale, numpy conversion
  - Raise `ImageLoadError` on failure
- [ ] Create `validate_dimensions(input_arr: np.ndarray, match_arr: np.ndarray) -> None`
  - Check match template is smaller than input
  - Check for minimum sizes (avoid 0 or 1-pixel images)
  - Check for maximum sizes (memory protection)
  - Raise `DimensionError` on failure
- [ ] Create `save_correlation(corr: np.ndarray, output_file: str) -> None`
  - Normalize array
  - Convert to image
  - Save to file
  - Handle errors
- [ ] Update `main()` to orchestrate these functions
- [ ] Make `main()` return success/failure status code

**Files**: `correlation.py`  
**Estimated Time**: 60 minutes

### Task 2.2: Dynamic Output Filename Generation
- [ ] Create `generate_output_filename(input_file: str, match_file: str) -> str`
- [ ] Use `Path(input_file).stem` and `Path(match_file).stem`
- [ ] Format: `{input_stem}_vs_{match_stem}_correlation.jpg`
- [ ] Update default parameter: `output_file: str | None = None`
- [ ] In `main()`, if `output_file is None`, call generator function
- [ ] Add CLI argument for custom output filename

**Files**: `correlation.py`  
**Estimated Time**: 25 minutes

### Task 2.3: Add Maximum Image Size Validation
- [ ] Define constant `MAX_DIMENSION = 10000` (configurable)
- [ ] In `validate_dimensions()`, check both width and height
- [ ] Raise `ImageTooLargeError` with helpful message
- [ ] Add CLI argument `--max-dimension` to override default
- [ ] Document memory implications in help text

**Files**: `correlation.py`  
**Estimated Time**: 20 minutes

**Phase 2 Total**: ~1.75 hours

---

## **Phase 3: Documentation & Best Practices** (Priority: Medium)

### Task 3.1: Enhanced Docstrings
- [ ] Update `normalize_array()` docstring with Google/NumPy format
  - Add Args section
  - Add Returns section
  - Add Notes section (explain zero-max behavior)
  - Add Examples section with sample usage
- [ ] Update `correlation()` docstring
  - Document parameters and return value
  - Explain padding behavior or remove padding
  - Add time complexity note
- [ ] Add comprehensive module-level docstring
  - Explain what digital image correlation is
  - List main functions
  - Provide usage examples
  - Document limitations
- [ ] Update `main()` docstring with all parameters

**Files**: `correlation.py`  
**Estimated Time**: 45 minutes

### Task 3.2: Replace Print with Logging
- [ ] Import `logging` module
- [ ] Create logger: `logger = logging.getLogger(__name__)`
- [ ] Replace all `print()` statements with appropriate log levels:
  - Info: "Computing Correlation Coefficients...", timing info
  - Debug: Statistics (max, min, mean)
  - Info: "Saving as: {output_file}"
  - Error: Error messages
- [ ] Add `--verbose` / `--quiet` CLI flags
- [ ] Configure logging in `if __name__ == "__main__"` block
- [ ] Default to INFO level

**Files**: `correlation.py`  
**Estimated Time**: 30 minutes

### Task 3.3: Review Padding Logic
- [ ] Analyze whether padding is necessary for use case
- [ ] **Option A**: Remove padding if not needed
  - Update docstring to note output size differs from input
- [ ] **Option B**: Keep padding but document thoroughly
  - Add detailed comment explaining why
  - Note that padded regions contain no correlation data
  - Consider using `np.nan` instead of 0 for padded regions
- [ ] Add test to verify padding behavior

**Files**: `correlation.py`  
**Estimated Time**: 30 minutes

### Task 3.4: Use Context Managers
- [ ] Refactor image loading to use context managers:
  ```python
  with Image.open(f1) as img1, Image.open(f2) as img2:
      im1 = img1.convert("L")
      im2 = img2.convert("L")
      # Convert to numpy arrays
  ```
- [ ] Verify no resource leaks

**Files**: `correlation.py`  
**Estimated Time**: 15 minutes

### Task 3.5: Fix Usage Strings
- [ ] Update docstring: `python correlation.py` (add .py)
- [ ] Update help message: `python correlation.py` (add .py)
- [ ] Ensure consistency with README

**Files**: `correlation.py`  
**Estimated Time**: 5 minutes

**Phase 3 Total**: ~2 hours

---

## **Phase 4: Testing Infrastructure** (Priority: Medium)

### Task 4.1: Add pytest Framework
- [ ] Add `pytest>=8.0.0` to `[dependency-groups] dev` in `pyproject.toml`
- [ ] Add `pytest-cov` for coverage reporting
- [ ] Run `uv sync` to install
- [ ] Create `tests/` directory
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/conftest.py` with fixtures

**Files**: `pyproject.toml`, `tests/conftest.py`  
**Estimated Time**: 20 minutes

### Task 4.2: Unit Tests for `normalize_array()`
- [ ] Create `tests/test_normalize_array.py`
- [ ] Test normal case: array with positive values
- [ ] Test negative values: ensure shift works correctly
- [ ] Test all zeros: verify returns zero array
- [ ] Test all same value: verify returns zero array
- [ ] Test single element array
- [ ] Test large array performance
- [ ] Test different dtypes (int, float, uint8)

**Files**: `tests/test_normalize_array.py`  
**Estimated Time**: 45 minutes

### Task 4.3: Unit Tests for `correlation()`
- [ ] Create `tests/test_correlation.py`
- [ ] Create small test images as numpy arrays
- [ ] Test exact match: template found in image
- [ ] Test no match: template not in image
- [ ] Test multiple matches: template appears multiple times
- [ ] Test edge cases: template at image boundary
- [ ] Verify output shape matches input shape (if padding kept)
- [ ] Verify correlation values are in expected range

**Files**: `tests/test_correlation.py`  
**Estimated Time**: 60 minutes

### Task 4.4: Integration Tests
- [ ] Create `tests/test_integration.py`
- [ ] Create small test images in `tests/fixtures/`
- [ ] Test complete workflow: load → correlate → save
- [ ] Test with example images from `example_images/`
- [ ] Test error cases:
  - Invalid file paths
  - Match larger than input
  - Corrupt image files
  - Invalid output paths
- [ ] Verify output file is created and valid

**Files**: `tests/test_integration.py`, `tests/fixtures/`  
**Estimated Time**: 75 minutes

### Task 4.5: Test Configuration
- [ ] Create `pytest.ini` or add to `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py"]
  addopts = "-v --cov=correlation --cov-report=term-missing"
  ```
- [ ] Create `.coveragerc` for coverage configuration
- [ ] Add test running instructions to README

**Files**: `pyproject.toml`, `.coveragerc`  
**Estimated Time**: 15 minutes

**Phase 4 Total**: ~3.5 hours

---

## **Phase 5: CI/CD & Automation** (Priority: Medium)

### Task 5.1: GitHub Actions Workflow
- [ ] Create `.github/workflows/ci.yml`
- [ ] Configure Python 3.12 matrix
- [ ] Add steps:
  - Checkout code
  - Setup Python with uv
  - Install dependencies (`uv sync`)
  - Run black check (`uv run black --check .`)
  - Run flake8 (`uv run flake8`)
  - Run pytest with coverage (`uv run pytest`)
  - Upload coverage to codecov (optional)
- [ ] Configure to run on push and pull requests
- [ ] Add branch protection rules (optional)

**Files**: `.github/workflows/ci.yml`  
**Estimated Time**: 40 minutes

### Task 5.2: Pre-commit Hooks
- [ ] Add `pre-commit>=4.0.0` to dev dependencies
- [ ] Create `.pre-commit-config.yaml`
- [ ] Configure hooks:
  - `black` for formatting
  - `flake8` for linting
  - `trailing-whitespace`, `end-of-file-fixer`
  - `check-yaml`, `check-toml`
- [ ] Run `pre-commit install`
- [ ] Document in README

**Files**: `.pre-commit-config.yaml`, `pyproject.toml`  
**Estimated Time**: 25 minutes

**Phase 5 Total**: ~1 hour

---

## **Phase 6: Enhanced Features** (Priority: Low)

### Task 6.1: Improved CLI with argparse
- [ ] Replace `sys.argv` parsing with `argparse`
- [ ] Add arguments:
  - `input_file` (positional)
  - `match_file` (positional)
  - `-o, --output` (optional output filename)
  - `--max-dimension` (max image size)
  - `-v, --verbose` (logging level)
  - `-q, --quiet` (suppress output)
  - `--allow-absolute-paths` (security override)
  - `--version` (show version)
- [ ] Add help text for each argument
- [ ] Generate better error messages

**Files**: `correlation.py`  
**Estimated Time**: 45 minutes

### Task 6.2: Progress Indication
- [ ] Add `tqdm>=4.66.0` to dependencies
- [ ] Wrap `match_template` computation with progress bar
- [ ] Show estimated time remaining
- [ ] Disable if `--quiet` flag is set
- [ ] Test with large images

**Files**: `correlation.py`, `pyproject.toml`  
**Estimated Time**: 30 minutes

### Task 6.3: Alternative Output Formats
- [ ] Add `--format` CLI argument (choices: jpg, png, tiff, npy)
- [ ] For TIFF: save as float32 (preserve precision)
- [ ] For NPY: save raw correlation array with `np.save()`
- [ ] Add `--save-stats` flag to save statistics to JSON
- [ ] Create `save_statistics(corr: np.ndarray, output_file: str) -> None`

**Files**: `correlation.py`  
**Estimated Time**: 40 minutes

### Task 6.4: Performance Optimization
- [ ] Replace `timeit.default_timer()` with `time.perf_counter()`
- [ ] Profile code to find bottlenecks
- [ ] Consider using `@functools.lru_cache` where applicable
- [ ] Add timing breakdown (load time, compute time, save time)

**Files**: `correlation.py`  
**Estimated Time**: 30 minutes

**Phase 6 Total**: ~2.5 hours

---

## **Phase 7: Documentation & Polish** (Priority: Low)

### Task 7.1: README Improvements
- [ ] Fix typo: `dandilions.jpg` → `dandelions.jpg`
- [ ] Add badges (CI status, coverage, license)
- [ ] Expand usage examples with all CLI options
- [ ] Add "Development" section with instructions:
  - Running tests
  - Running linters
  - Contributing guidelines
- [ ] Add performance notes and limitations
- [ ] Add troubleshooting section

**Files**: `README.md`  
**Estimated Time**: 30 minutes

### Task 7.2: Add CONTRIBUTING.md
- [ ] Create contribution guidelines
- [ ] Explain how to set up development environment
- [ ] Code style requirements
- [ ] How to run tests
- [ ] Pull request process

**Files**: `CONTRIBUTING.md`  
**Estimated Time**: 20 minutes

### Task 7.3: Add CHANGELOG.md
- [ ] Create changelog following Keep a Changelog format
- [ ] Document all changes from code review
- [ ] Version as 0.2.0 (breaking changes from API refactor)

**Files**: `CHANGELOG.md`  
**Estimated Time**: 15 minutes

### Task 7.4: Update License Year
- [ ] Check if LICENSE.txt year needs updating (2020 → 2025)
- [ ] Update copyright in source file if needed

**Files**: `LICENSE.txt`, `correlation.py`  
**Estimated Time**: 5 minutes

**Phase 7 Total**: ~1 hour

---

## **Timeline Summary**

| Phase | Priority | Estimated Time | Cumulative |
|-------|----------|----------------|------------|
| Phase 1: Foundation & Critical Fixes | High | 2.5 hours | 2.5 hours |
| Phase 2: Code Architecture & Design | High-Medium | 1.75 hours | 4.25 hours |
| Phase 3: Documentation & Best Practices | Medium | 2 hours | 6.25 hours |
| Phase 4: Testing Infrastructure | Medium | 3.5 hours | 9.75 hours |
| Phase 5: CI/CD & Automation | Medium | 1 hour | 10.75 hours |
| Phase 6: Enhanced Features | Low | 2.5 hours | 13.25 hours |
| Phase 7: Documentation & Polish | Low | 1 hour | 14.25 hours |

**Total Estimated Time**: ~14.25 hours (~2 working days)

---

## **Recommended Execution Order**

### Sprint 1 (High Priority - ~4.25 hours)
1. Phase 1: Foundation & Critical Fixes
2. Phase 2: Code Architecture & Design

### Sprint 2 (Medium Priority - ~6.5 hours)
3. Phase 3: Documentation & Best Practices
4. Phase 4: Testing Infrastructure
5. Phase 5: CI/CD & Automation

### Sprint 3 (Low Priority - ~3.5 hours)
6. Phase 6: Enhanced Features
7. Phase 7: Documentation & Polish

---

## **Success Criteria**

- [ ] All code passes `black` formatting
- [ ] All code passes `flake8` linting
- [ ] Test coverage ≥ 80%
- [ ] All tests passing in CI
- [ ] No security vulnerabilities (path traversal, memory exhaustion)
- [ ] Type hints on all public functions
- [ ] Comprehensive documentation
- [ ] README examples all work correctly

---

## **Dependencies & Tools Needed**

- Python 3.12+
- uv (already installed)
- Additional Python packages (to be added):
  - pytest
  - pytest-cov
  - pre-commit
  - tqdm (optional, Phase 6)

---

## **Notes**

- Each task should be committed separately with descriptive commit messages
- Create feature branches for each phase if desired
- Run tests after each phase to ensure nothing breaks
- Update this document with actual time spent for future estimation improvement
