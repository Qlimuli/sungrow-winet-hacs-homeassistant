# Contributing to Sungrow WINET-S Integration

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/sungrow-winet-s.git
   cd sungrow-winet-s
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest (testing)
- black (code formatting)
- isort (import sorting)
- mypy (type checking)

### Code Style

We follow Home Assistant's code style:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **Type hints** for all functions
- **Docstrings** for all public functions

Format your code before committing:
```bash
black custom_components/sungrow_winet_s
isort custom_components/sungrow_winet_s
```

### Type Checking

Run mypy to check types:
```bash
mypy custom_components/sungrow_winet_s
```

## Testing

### Run Tests

```bash
pytest tests/
```

### Add Tests

When adding new features:
1. Add unit tests in `tests/`
2. Test both success and failure cases
3. Mock external dependencies

## What to Contribute

### Bug Fixes

1. Check if issue already exists
2. If not, create an issue describing the bug
3. Reference the issue in your PR

### New Features

1. Open an issue to discuss the feature first
2. Get feedback from maintainers
3. Implement with tests and documentation

### Documentation

- Fix typos
- Improve clarity
- Add examples
- Translate to other languages

### Good First Issues

Look for issues tagged `good-first-issue` or `help-wanted`.

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Run all tests** and ensure they pass
4. **Format code** with black and isort
5. **Update CHANGELOG.md** with your changes
6. **Create PR** with clear description:
   - What does it change?
   - Why is it needed?
   - How has it been tested?

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Code Review

- Be respectful and constructive
- Respond to feedback promptly
- Be open to suggestions
- Focus on code quality and maintainability

## Reporting Bugs

Use the issue template and include:

1. **Home Assistant version**
2. **Integration version**
3. **Inverter model**
4. **Connection type** (Modbus/HTTP/Cloud)
5. **Steps to reproduce**
6. **Expected behavior**
7. **Actual behavior**
8. **Relevant logs** (with debug enabled)

## Feature Requests

1. Check if already requested
2. Describe the feature clearly
3. Explain the use case
4. Provide examples if possible

## Questions

For questions:
- Check README and documentation first
- Search existing issues
- Ask on Home Assistant Community Forum
- Open a GitHub Discussion

## Recognition

All contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Contact

For private inquiries:
- Email: [your-email@example.com]
- GitHub: [@yourusername]

---

Thank you for contributing! 🎉
