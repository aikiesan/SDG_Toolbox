# Contributing to the SDG Assessment Toolkit

**Version:** 1.0.0  
**Last Updated:** 2025-04-25

Thank you for your interest in contributing! We welcome input from architects, developers, sustainability experts, and the broader community.

## How to Contribute
- **Bug Reports:** Open an issue describing the problem and steps to reproduce it.
- **Feature Requests:** Suggest new features or improvements via issues.
- **Pull Requests:**
  1. Fork the repository on GitHub.
  2. Clone your fork locally.
  3. Create a new branch for your feature or fix:
     ```bash
     git checkout -b feature/your-feature-name
     ```
  4. Make your changes and commit them with clear, descriptive messages.
  5. Push your branch to your fork:
     ```bash
     git push origin feature/your-feature-name
     ```
  6. Open a pull request against the `main` branch with a detailed description.
- **Translations:** Help us localize the toolkit by contributing translations.

## Prerequisites
- Python 3.9 or higher
- Git
- Familiarity with GitHub workflow (fork, branch, pull request)

## Project Setup
1. **Clone the repository** and create a virtual environment:
   ```bash
   git clone https://github.com/aikiesan/sdg-assessment.git
   cd sdg-assessment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Set up the database:**
   ```bash
   python create_db.py
   python create_tables.py
   python seed_sdg_questions.py
   ```
   Or use the provided migration scripts as needed.
3. **Set environment variables:**
   - See [ENVIRONMENT.md](./ENVIRONMENT.md) for required variables and example `.env` file.
4. **Run the development server:**
   ```bash
   python run.py
   ```
   The app will be available at http://localhost:5001

## Environment
- Python 3.9+
- All dependencies are listed in `requirements.txt`.
- Set environment variables as described in [ENVIRONMENT.md](./ENVIRONMENT.md).

## Testing
- Automated tests are in the `tests/` directory.
- To run all tests:
   ```bash
   pytest
   ```
- For coverage reports:
   ```bash
   pytest --cov=app
   ```
- Please ensure all new features and bug fixes include appropriate tests.
- If you add new dependencies for tests, update `requirements.txt` accordingly.

## Code Style
- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use clear, descriptive commit messages (e.g., `fix: correct SDG score calculation`).
- Write or update tests for any new features or bug fixes.
- (If you use specific tools like black, flake8, pre-commit, please let me know so I can add them here.)

## Getting Help
For questions or support, contact Lucas Nakamura at [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com), or open a discussion issue.

---
**Maintained by Lucas Nakamura**
