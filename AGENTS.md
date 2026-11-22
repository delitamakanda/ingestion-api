# `AGENTS.md`

## Development workflow

- This project is typed. Run ``mypy`` to check for type errors after adding new code or modifications.
  - `uv run mypy .`
- Use `ruff` to check for linting errors and formatting issues.
  - `uv run ruff format .`
  - `uv run ruff check .`
- Run the full test suite after modifying code or adding new features.
  - `uv run pytest`
- Add or update tests when changing behavior.
- Before committing, run:
  - `uv run pre-commit run --all-files`
- Prefer small, focused functions.

# Documentation

- Update documentation when public behavior changes.