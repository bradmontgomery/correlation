# Contributing to correlation.py

Thank you for your interest in contributing to correlation.py! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/correlation.git
   cd correlation
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

4. **Verify setup**
   ```bash
   uv run pytest
   ```

## Development Workflow

### 1. Create a Branch

Create a feature branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

Use prefixes like:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `test/` for test improvements

### 2. Make Changes

Follow these guidelines:

#### Code Style

- **Formatting**: Use `black` (runs automatically via pre-commit)
- **Linting**: Follow PEP 8 (enforced by `flake8`)
- **Line length**: 88 characters (black default)
- **Type hints**: Add type annotations to new functions
- **Docstrings**: Use Google-style docstrings

Example function:

```python
def process_image(image: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """
    Process an image with the given threshold.

    Args:
        image: Input image as numpy array
        threshold: Processing threshold (default: 0.5)

    Returns:
        Processed image array

    Raises:
        ValueError: If threshold is out of range
    """
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    return image * threshold
```

#### Testing

- Add tests for new functionality
- Maintain or improve code coverage
- Tests should be fast and isolated
- Use descriptive test names

### 3. Run Quality Checks

Before committing, ensure all checks pass:

```bash
# Format code
uv run black correlation.py tests/

# Lint code
uv run flake8 correlation.py tests/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=correlation --cov-report=term-missing

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### 4. Commit Changes

Write clear, descriptive commit messages:

```
Add feature to export correlation statistics

- Implement save_statistics() function
- Add --save-stats CLI flag
- Export max, min, mean, std to JSON
- Add tests for statistics export
```

Follow the conventional commits format when possible:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference to any related issues
- Screenshots if applicable (for UI changes)

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style (black + flake8)
- [ ] All tests pass (`uv run pytest`)
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Pre-commit hooks pass
- [ ] Commit messages are clear

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests pass
- [ ] Code formatted with black
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
```

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in the changelog

## Testing Guidelines

### Unit Tests

- Located in `tests/`
- Use pytest fixtures from `conftest.py`
- Test one thing per test
- Use descriptive names

Example:

```python
def test_normalize_array_with_negative_values():
    """Test that negative values are correctly shifted."""
    arr = np.array([-2, -1, 0, 1, 2])
    result = normalize_array(arr)
    
    assert result.min() == 0.0
    assert result.max() == 1.0
    np.testing.assert_array_almost_equal(
        result, np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    )
```

### Integration Tests

- Test complete workflows
- Use temporary files (`tmp_path` fixture)
- Clean up after tests

### Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/test_correlation.py

# Run specific test
uv run pytest tests/test_correlation.py::TestCorrelation::test_exact_match

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=correlation
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    One-line summary.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised

    Examples:
        >>> example_function("test", 5)
        True
    """
```

### README Updates

- Keep examples up to date
- Update CLI options if changed
- Add troubleshooting entries for common issues

### Changelog

Update `CHANGELOG.md` for:
- New features
- Bug fixes
- Breaking changes
- Deprecations

## Questions or Problems?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- `CHANGELOG.md` for their contributions
- GitHub contributors page
- Release notes

Thank you for contributing! 🎉
