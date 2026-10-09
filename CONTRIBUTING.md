# Contributing to Austin Events Aggregator

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized development)
- Git

### Local Development

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/austin-events.git
   cd austin-events
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install flake8 pytest pytest-cov  # Dev dependencies
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Maximum line length: 127 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Linting

Run linting before committing:

```bash
flake8 . --max-line-length=127
```

### JavaScript

- Use `const` and `let` instead of `var`
- Use template literals for string interpolation
- Follow consistent naming conventions (camelCase)

## Testing

### Running Tests

```bash
pytest --cov=. --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(sources): add Resident Advisor scraper`
- `fix(map): correct marker clustering behavior`
- `docs(readme): update deployment instructions`

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Update documentation if needed
5. Submit a pull request
6. Wait for review and address feedback

## Adding New Data Sources

To add a new event source:

1. Create a new file in `sources/` directory
2. Implement the scraper/API client with caching
3. Return events in the standard format:
   ```python
   {
       'id': 'unique_id',
       'title': 'Event Title',
       'description': 'Event description',
       'date': '2026-01-01T20:00:00',
       'venue': 'Venue Name',
       'address': 'Full Address',
       'lat': 30.2672,
       'lng': -97.7431,
       'url': 'https://event-url.com',
       'category': 'Music',  # Music, Art, Food, Markets, Nightlife, Other
       'source': 'Source Name',
   }
   ```
4. Add the source to `app.py` aggregation
5. Update the template with source links
6. Add tests for the new source

## Questions?

Open an issue for questions or discussions.
