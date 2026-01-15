# Contributing to ScopeSignal

Thank you for your interest in contributing to ScopeSignal! This document provides guidelines for contributing to the project.

## Project Philosophy

ScopeSignal is built on **restraint over features**. Before proposing changes, please understand:

- This is a **portfolio/demonstration project** focused on conservative classification
- New features should add **clear value** without compromising the core philosophy
- **False negatives are preferred** over false positives
- The classification logic should **not be tuned** to improve metrics retroactively

## Ways to Contribute

### 1. Bug Reports

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)
- Relevant logs or error messages

### 2. Feature Requests

Before requesting a feature, check if it aligns with the project philosophy:

**Appropriate requests:**
- Performance improvements (caching, optimization)
- Additional export formats
- Better error handling
- Documentation improvements
- Testing infrastructure
- Integration helpers

**Inappropriate requests:**
- Real-time alerting systems
- Multi-agency scraping
- User authentication
- Mobile apps
- Automatic prompt tuning

### 3. Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve error messages
- Enhance API documentation

### 4. Code Contributions

#### Before You Start

1. Open an issue to discuss your proposed changes
2. Wait for maintainer feedback before investing significant time
3. Fork the repository
4. Create a feature branch from `main`

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ScopeSignal.git
cd ScopeSignal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Set up pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

#### Code Standards

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Use Google-style docstrings
- **Testing**: Add tests for new features
- **Commits**: Write clear, descriptive commit messages

#### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agent.py -v

# Run with coverage
python -m pytest tests/ --cov=classifier --cov=evaluation
```

#### Code Formatting

```bash
# Format code with black
black classifier/ evaluation/ tests/

# Check with flake8
flake8 classifier/ evaluation/ tests/ --max-line-length=100

# Type checking
mypy classifier/ evaluation/
```

#### Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Add tests** that verify your changes
3. **Run the full test suite** and ensure it passes
4. **Update CHANGELOG.md** with your changes
5. **Keep commits focused** - one logical change per commit
6. **Write clear PR descriptions** explaining what and why

#### PR Title Format

Use conventional commits format:
```
feat: add CSV export with custom columns
fix: correct cache TTL calculation
docs: improve batch processing examples
test: add tests for export functionality
refactor: simplify metrics calculation
```

#### What to Include in Your PR

- Clear description of the problem and solution
- Links to related issues
- Screenshots for UI changes
- Performance impact (if applicable)
- Breaking changes (clearly marked)

### 5. Testing Real Data

If you test ScopeSignal with real NYC construction data:
- Share aggregate performance metrics (don't share sensitive data)
- Report classification accuracy insights
- Suggest improvements based on real-world usage

## Review Process

1. Maintainers will review your PR within 1-2 weeks
2. Address any requested changes
3. Once approved, maintainers will merge your PR
4. Your contribution will be credited in CHANGELOG.md

## Code of Conduct

### Our Standards

- **Be respectful** and constructive
- **Welcome diverse perspectives**
- **Focus on what's best** for the project
- **Show empathy** towards other contributors

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

### Enforcement

Unacceptable behavior should be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Questions?

- Check the [README](README.md) for basic information
- Review [QUICKSTART.md](QUICKSTART.md) for setup instructions
- Open an issue for questions about contribution

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping improve ScopeSignal!** 🏗️
