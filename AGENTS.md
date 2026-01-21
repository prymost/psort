# AI Agent Instructions for 'Media Sync'

This file provides context and rules for AI agents working on this repository.

## 1. Project Context
**Goal:** A personal CLI tool to organize photos and videos by date.
**Origin:** A Python migration of a legacy PowerShell script.
**Philosophy:** Simple, functional, and reliable. This is a personal utility, not a commercial product.

## 2. Technical Stack
- **Language:** Python 3.10+
- **Dependency Manager:** Poetry
- **Testing:** `pytest` (with `pytest-cov`)
- **Linting/Formatting:** `flake8` and `black`
- **Key Libraries:** `Pillow` (Images), `hachoir` (Videos)

## 3. Architecture & Design Patterns
**Strictly adhere to these patterns:**

*   **Functional Style:** Avoid stateful classes for logic. Use `dataclasses` for configuration (e.g., `SyncConfig`) and pass them explicitly to pure functions.
*   **Pathlib First:** Use `pathlib.Path` for all file system operations. Avoid `os.path`.
*   **Safe Processing:** All file I/O must be wrapped in `try/except` blocks. One bad file should not crash the process.
*   **Immutability:** Use `frozen=True` for configuration dataclasses.
*   **Internal Helpers:** Use a single leading underscore (`_func_name`) for internal helper functions.
*   **No Asserts:** Do not use `assert` for logic control in production code; use exceptions or conditionals.

## 4. Coding Standards
*   **Type Hints:** Mandatory for all function signatures.
*   **Formatting:** Run `poetry run black .` before committing.
*   **Linting:** Run `poetry run flake8`. Ensure 0 errors.
*   **CI:** All pushes and PRs must pass the GitHub Actions CI workflow (linting + tests).
*   **Line Length:** 88 characters (Black standard).

## 5. Testing Strategy
**Requirement: Maintain 100% Test Coverage.**

*   **Unit Tests:** Use `unittest.mock` to mock external dependencies (filesystem, EXIF data, hashing).
*   **E2E Tests:** located in `tests/test_main.py`. Must use real file generation (via Pillow) and `tmp_path` to verify the full stack.
*   **Fixtures:** Use `tmp_path` for files and `capsys` for CLI output verification.

## 6. Directory Structure
*   `src/`: Application source code.
    *   `main.py`: CLI entry point only.
    *   `processor.py`: Core logic (functional style).
    *   `metadata.py`: Extraction logic (returns `datetime` or `None`).
    *   `utils.py`: Hashing, logging, filename generation.
*   `tests/`: Parallel structure to `src/`.

## 7. Common Tasks

**Running Tests:**
```bash
poetry run pytest tests
```

**Running the Tool (Dev):**
```bash
poetry run python src/main.py --source ./in --destination ./out --dry-run
```

**Building the Binary:**
```bash
./scripts/build.sh
```

**Releases:**
*   Binaries for Linux, Windows, and macOS are automatically built and attached to GitHub Releases via `release.yml`.
