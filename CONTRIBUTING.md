# Contributing to ECG Signal Biometric Encryption System

## 🤝 Welcome Contributors!

Thank you for your interest in contributing to our ECG Signal Biometric Encryption System research project! This document provides guidelines and information for contributors.

## 🎯 How Can You Contribute?

### 🔬 Research Contributions
- **Algorithm Improvements**: Enhance encryption algorithms or security measures
- **Performance Optimization**: Improve processing speed or memory efficiency
- **New Features**: Add novel functionality or analysis tools
- **Documentation**: Improve technical documentation or user guides

### 🐛 Bug Reports and Issues
- **Bug Reports**: Report bugs or unexpected behavior
- **Feature Requests**: Suggest new features or improvements
- **Documentation Issues**: Report unclear or missing documentation
- **Performance Issues**: Report performance problems or bottlenecks

### 📚 Code Contributions
- **Bug Fixes**: Fix identified bugs or issues
- **Code Improvements**: Refactor code for better readability or performance
- **Test Coverage**: Add or improve test cases
- **Code Quality**: Improve code style and adherence to standards

## 🚀 Getting Started

### 1. Fork the Repository
1. Go to the main repository page
2. Click the "Fork" button in the top right
3. Clone your forked repository locally

### 2. Set Up Development Environment
```bash
# Clone your fork
git clone https://github.com/yourusername/ecg-biometric-encryption.git
cd ecg-biometric-encryption

# Create virtual environment
python -m venv ecg_env
source ecg_env/bin/activate  # Linux/macOS
ecg_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

### 3. Create a Feature Branch
```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style
We follow PEP 8 Python style guidelines:

```bash
# Format code with black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/
```

### Code Quality Standards
- **Documentation**: All functions and classes must have docstrings
- **Type Hints**: Use type hints for function parameters and return values
- **Error Handling**: Implement proper exception handling
- **Testing**: Write tests for new functionality

### Example Code Structure
```python
def encrypt_signal(signal: np.ndarray, r: float, x0: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Encrypt ECG signal using chaotic encryption.
    
    Args:
        signal: Input ECG signal array
        r: Chaotic parameter for logistic map
        x0: Initial condition for chaotic iteration
        
    Returns:
        tuple: (encrypted_signal, permutation_indices)
        
    Raises:
        ValueError: If parameters are invalid
    """
    try:
        # Validate inputs
        if not isinstance(signal, np.ndarray):
            raise ValueError("Signal must be a numpy array")
        
        # Implementation here
        encrypted, indices = _chaotic_encrypt(signal, r, x0)
        
        return encrypted, indices
        
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_encryption.py

# Run tests in parallel
pytest -n auto
```

### Writing Tests
- **Test Coverage**: Aim for >90% code coverage
- **Test Cases**: Include edge cases and error conditions
- **Mocking**: Use mocks for external dependencies
- **Assertions**: Use descriptive assertion messages

### Example Test Structure
```python
import pytest
import numpy as np
from src.encryption import encrypt_signal

class TestEncryption:
    """Test encryption functionality."""
    
    def test_encrypt_signal_valid_input(self):
        """Test encryption with valid input."""
        # Arrange
        signal = np.random.random(100)
        r = 3.847
        x0 = 0.623
        
        # Act
        encrypted, indices = encrypt_signal(signal, r, x0)
        
        # Assert
        assert encrypted.shape == signal.shape
        assert indices.shape == signal.shape
        assert not np.array_equal(encrypted, signal)
    
    def test_encrypt_signal_invalid_parameters(self):
        """Test encryption with invalid parameters."""
        # Arrange
        signal = np.random.random(100)
        invalid_r = 0.5  # Invalid for logistic map
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid parameter"):
            encrypt_signal(signal, invalid_r, 0.623)
```

## 📋 Pull Request Process

### 1. Prepare Your Changes
- Ensure all tests pass
- Update documentation if needed
- Follow code style guidelines
- Add appropriate commit messages

### 2. Commit Messages
Use conventional commit format:
```
feat: add new encryption algorithm
fix: resolve memory leak in signal processing
docs: update installation instructions
test: add tests for security analysis
refactor: improve code organization
```

### 3. Create Pull Request
1. Push your branch to your fork
2. Create a Pull Request to the main repository
3. Fill out the PR template
4. Request review from maintainers

### 4. PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

## 🔍 Review Process

### Code Review Guidelines
- **Constructive Feedback**: Provide helpful, specific feedback
- **Respect**: Be respectful and professional
- **Learning Opportunity**: Use reviews as learning experiences
- **Timely Response**: Respond to review comments promptly

### Review Criteria
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code readable and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Are there performance implications?

## 📚 Documentation Contributions

### Documentation Types
- **Code Documentation**: Docstrings and inline comments
- **User Guides**: Installation and usage instructions
- **API Reference**: Function and class documentation
- **Research Documentation**: Algorithm descriptions and methodology

### Documentation Standards
- **Clarity**: Write clear, concise explanations
- **Examples**: Include practical examples
- **Accuracy**: Ensure technical accuracy
- **Completeness**: Cover all necessary information

## 🐛 Reporting Issues

### Issue Templates
Use appropriate issue templates:
- **Bug Report**: For software bugs or errors
- **Feature Request**: For new functionality
- **Documentation**: For documentation issues
- **Performance**: For performance problems

### Bug Report Guidelines
- **Reproducible**: Provide steps to reproduce
- **Specific**: Include specific error messages
- **Environment**: Specify OS, Python version, dependencies
- **Expected vs Actual**: Describe expected and actual behavior

## 🏷️ Labels and Milestones

### Issue Labels
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `research`: Research-related tasks

### Milestones
- **v1.0.0**: Initial release
- **v1.1.0**: Feature additions
- **v1.2.0**: Performance improvements
- **v2.0.0**: Major version update

## 🤝 Community Guidelines

### Code of Conduct
- **Respect**: Treat all contributors with respect
- **Inclusion**: Welcome contributors from all backgrounds
- **Collaboration**: Work together constructively
- **Learning**: Support learning and growth

### Communication
- **GitHub Issues**: Use for technical discussions
- **Discussions**: Use for general questions and ideas
- **Email**: For sensitive or private matters
- **Meetings**: For complex discussions (if needed)

## 📞 Getting Help

### Resources
- **Documentation**: Check the docs/ directory
- **Issues**: Search existing issues for solutions
- **Discussions**: Ask questions in GitHub Discussions
- **Maintainers**: Contact maintainers directly

### Support Channels
- **GitHub Issues**: Technical problems and bugs
- **GitHub Discussions**: Questions and ideas
- **Email**: [your.email@institution.edu]
- **Research Lab**: [Lab Website]

## 🎉 Recognition

### Contributor Recognition
- **Contributors List**: All contributors listed in README
- **Commit History**: Preserved in git history
- **Release Notes**: Acknowledged in release notes
- **Research Papers**: Co-authorship for significant contributions

### Contribution Levels
- **Contributor**: Any contribution to the project
- **Maintainer**: Regular contributor with review privileges
- **Core Developer**: Key contributor with merge privileges
- **Research Lead**: Principal investigator and project lead

---

## 🚀 Ready to Contribute?

1. **Fork the repository**
2. **Set up your development environment**
3. **Pick an issue or create a new one**
4. **Make your changes**
5. **Submit a pull request**

We're excited to work with you on advancing ECG signal biometric encryption research!

---

*For questions about contributing, please open an issue or contact the maintainers.*
