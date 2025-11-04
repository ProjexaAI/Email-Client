# Contributing to Simple Email Client

Thank you for your interest in contributing to Simple Email Client! This document provides guidelines and instructions for contributing to this project.

## Part of Projexa.ai Open Source Initiative

This project is part of the [Projexa.ai](https://projexa.ai) open source initiative, dedicated to building useful, well-maintained tools for the community.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title**: Describe the issue concisely
- **Steps to reproduce**: List exact steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, Docker version, etc.
- **Screenshots**: If applicable
- **Logs**: Relevant log output

### Suggesting Features

Feature suggestions are welcome! Please include:

- **Clear description**: What feature you'd like to see
- **Use case**: Why this feature would be useful
- **Proposed solution**: How you envision it working
- **Alternatives**: Other approaches you've considered

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/simple-email-client.git
   cd simple-email-client
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments where necessary
   - Update documentation if needed

4. **Test your changes**
   - Ensure the application runs without errors
   - Test new features thoroughly
   - Check for edge cases

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with details

## Development Setup

### Prerequisites

- Python 3.9+
- MongoDB
- Docker (optional)

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/simple-email-client.git
   cd simple-email-client
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access at** `http://localhost:8000`

## Code Style Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

Example:
```python
def create_user(username: str, password: str, email: str, is_admin: bool = False) -> tuple:
    """
    Create a new user in the database.

    Args:
        username: Unique username for the user
        password: Plain text password (will be hashed)
        email: User's email address
        is_admin: Whether user should have admin privileges

    Returns:
        Tuple of (user_doc, error_message)
    """
    # Implementation
```

### HTML/CSS Style

- Use semantic HTML
- Keep CSS simple and maintainable
- Follow existing design patterns
- Mobile-responsive where applicable

### Database

- Use descriptive collection and field names
- Index fields that are frequently queried
- Validate data before inserting
- Handle errors gracefully

## Testing

Currently, the project doesn't have automated tests. We welcome contributions to add:

- Unit tests for core functions
- Integration tests for API endpoints
- End-to-end tests for critical workflows

## Documentation

Good documentation is crucial. When contributing:

- Update README.md if you add features
- Update DEPLOYMENT.md for deployment-related changes
- Add inline comments for complex logic
- Update API endpoint documentation

## Areas We Need Help With

- **Testing**: Adding test coverage
- **Documentation**: Improving guides and examples
- **Features**: Implementing roadmap items
- **UI/UX**: Improving the user interface
- **Performance**: Optimization and efficiency
- **Security**: Security audits and improvements
- **Mobile**: Mobile responsiveness improvements

## Questions?

Feel free to:
- Open an issue for discussion
- Ask questions in existing issues
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Simple Email Client!

---

**Part of [Projexa.ai](https://projexa.ai) Open Source Initiative**
