# Contributing to GitLab Analysis Tool

Thank you for your interest in contributing to the GitLab Analysis Tool! This document provides guidelines and information for contributors.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** following the README setup instructions
4. **Create a feature branch** for your changes

## 📁 Project Structure

Please familiarize yourself with the project structure:

- `scripts/` - Main executable scripts
- `src/` - Shared utilities and common functionality
- `config/` - Configuration files and examples
- `docs/` - Documentation files
- `archive/` - Legacy scripts (do not modify)

## 🔧 Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### File Organization

- Place new utilities in `src/`
- Create new scripts in `scripts/`
- Update the main entry point (`gitlab_analysis.py`) if adding new commands

### Testing

- Test your changes with real GitLab repositories
- Verify all output formats work correctly
- Check that the main entry point properly delegates to your script

## 📝 Pull Request Process

1. **Create a descriptive branch name**: `feature/add-new-export-format`
2. **Make focused commits** with clear commit messages
3. **Update documentation** if needed (README, help text, etc.)
4. **Test thoroughly** with various scenarios
5. **Submit a pull request** with:
   - Clear description of changes
   - Why the change is needed
   - How to test the changes

## 🐛 Bug Reports

When reporting bugs, please include:

- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Environment details (OS, Python version)

## 💡 Feature Requests

For new features:

- Describe the use case
- Explain how it fits with existing functionality
- Consider implementation complexity
- Discuss potential breaking changes

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/gitlab-analysis-script.git
cd gitlab-analysis-script

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp config/.env.example .env
# Edit .env with your settings
```

## 🔍 Code Review

All contributions will be reviewed for:

- Code quality and style
- Functionality and correctness
- Documentation completeness
- Test coverage
- Compatibility with existing features

