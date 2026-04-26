# Contributing to llm-biodata-training

Thank you for contributing! This guide covers the development workflow, branch strategy,
commit conventions, and code quality standards for this project.

> **Before starting any work, read [`AGENTS.md`](AGENTS.md) first.**
> It contains the project memory, scope guardrails, and rules that prevent duplicate work.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Project Structure](#2-project-structure)
3. [Git Workflow](#3-git-workflow)
4. [Commit Message Format](#4-commit-message-format)
5. [Pull Requests](#5-pull-requests)
6. [Code Quality Standards](#6-code-quality-standards)
7. [Running Tests](#7-running-tests)
8. [Environment Setup](#8-environment-setup)
9. [Reporting Issues](#9-reporting-issues)

---

## 1. Getting Started

### Prerequisites
- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`
- Node.js LTS (for slides development only)
- A Mistral AI or Groq API key (for running the chatbot)

### Chatbot Application Setup

```bash
# Clone the repository
git clone https://github.com/AMVamsi/llm-biodata-training.git
cd llm-biodata-training/project

# Install dependencies using uv
uv sync

# OR using pip in a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env and fill in MISTRAL_API_KEY and/or GROQ_API_KEY
```

### Indexing the Vector Database

Before running the chatbot for the first time, index the SPARQL endpoints:

```python
# Run once — downloads and embeds endpoint metadata into data/vectordb/
from app import index_endpoints
index_endpoints()
```

Or temporarily uncomment the `index_endpoints()` call at the bottom of `app.py` and run once.

### Running the Chatbot

```bash
cd project
chainlit run app.py
```

The chat interface will be available at `http://localhost:8000`.

---

## 2. Project Structure

```text
llm-biodata-training/
├── project/               # Python chatbot application — primary development area
│   ├── app.py             # Application entrypoint (LLM, vector DB, Chainlit UI)
│   ├── pyproject.toml     # Python dependencies and tool config
│   ├── .env.example       # API key template — never commit .env
│   └── data/vectordb/     # Local vector database (runtime, not modified by hand)
├── public/                # Slide assets (Reveal.js)
├── .github/workflows/     # GitHub Actions workflows
├── docs/                  # Technical documentation
├── AGENTS.md              # Contributor and AI agent operating guide
├── CONTRIBUTING.md        # This file
├── CHANGELOG.md           # History of changes
└── README.md              # High-level overview
```

---

## 3. Git Workflow

This project uses a **feature branch workflow**:

- `main` is the stable branch — direct commits are not allowed.
- All changes must go through a **Pull Request** (PR).
- Every PR must reference a GitHub **Issue**.
- `main` is protected: at least one approval is required before merging.

### Branch Naming Convention

```
<type>/<short-description>
```

| Type | When to use |
|------|-------------|
| `feat` | New feature or enhancement |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behaviour change |
| `test` | Adding or updating tests |
| `ci` | CI/CD workflow changes |
| `docs` | Documentation only |
| `chore` | Tooling, dependencies, config |

**Examples:**
```
feat/add-pytest-config
fix/execute-query-none-return
refactor/extract-constants-to-top
ci/add-ruff-workflow
docs/update-project-readme
chore/add-ruff-mypy-dev-deps
```

### Typical Branch Lifecycle

```bash
# 1. Start from latest main
git checkout main
git pull origin main

# 2. Create a feature branch
git checkout -b feat/my-feature

# 3. Make changes and commit regularly
git add <files>
git commit -m "feat(app): short description of change"

# 4. Push and open a PR
git push origin feat/my-feature
# Open PR on GitHub → link to the relevant Issue
```

---

## 4. Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

[optional body — explain WHY, not WHAT]

[optional footer — e.g. Closes #42]
```

### Types

| Type | Use |
|------|-----|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change without behaviour change |
| `test` | Tests added or updated |
| `ci` | CI/CD configuration |
| `docs` | Documentation only |
| `chore` | Tooling, dependency, config update |

### Scopes (use the relevant area)

| Scope | Area |
|-------|------|
| `app` | `project/app.py` — main application |
| `tests` | Test suite |
| `ci` | GitHub Actions workflows |
| `docs` | Documentation files |
| `deps` | Dependency changes |
| `config` | Configuration files (`pyproject.toml`, `.gitignore`) |

### Examples

```
feat(app): add query result caching with functools.lru_cache
fix(app): handle None return from execute_query in retry loop
refactor(app): extract configuration constants to module top
test(app): add unit tests for format_doc and load_chat_model
ci: add ruff linter and pytest workflow
docs: add project README for chatbot setup
chore(deps): add ruff, mypy, pytest as dev dependencies
```

### Rules

- Use the imperative mood: *"add"* not *"added"* or *"adds"*
- Do not end the subject line with a period
- Keep the subject line under 72 characters
- Reference the related Issue in the footer: `Closes #12`

---

## 5. Pull Requests

### Before Opening a PR

- [ ] Branch is up to date with `main`
- [ ] `ruff check project/` passes (once configured)
- [ ] `mypy project/app.py` passes (once configured)
- [ ] `pytest` passes with no failures
- [ ] No unrelated files were changed
- [ ] `docs/FEATURE_STATUS.md` is updated if feature status changed
- [ ] `CHANGELOG.md` has a new entry

### PR Template

When opening a PR, include:

```markdown
## Summary
Brief description of what this PR does.

## Related Issue
Closes #<issue-number>

## Changes
- List of specific changes made

## Testing
- How the change was tested
- New tests added (if any)

## Checklist
- [ ] ruff check passes
- [ ] mypy passes
- [ ] pytest passes
- [ ] No unrelated files changed
- [ ] CHANGELOG.md updated
- [ ] FEATURE_STATUS.md updated (if applicable)
```

### Review Process

- PRs require at least **one review** before merging.
- Address all review comments before requesting re-review.
- Use **Squash and Merge** to keep `main` history clean.

---

## 6. Code Quality Standards

### Formatter and Linter: `ruff`

```bash
# Check for issues
ruff check project/

# Auto-fix safe issues
ruff check --fix project/

# Format code
ruff format project/

# Check formatting without changing files
ruff format --check project/
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Type Checker: `mypy`

```bash
mypy project/app.py
```

- All public functions must have type annotations.
- `execute_query` return type must be `list[dict[str, str]] | None` — not just `list`.

### Code Style Rules

- Line length: **88 characters**
- Python 3.12 only
- Import order: stdlib → third-party → first-party
- Docstrings required on all public functions
- No hardcoded secrets or absolute file paths
- No global mutable state in modules
- No side effects at import time (e.g., no network calls on import)

---

## 7. Running Tests

```bash
cd project

# Run all tests
pytest

# Run with coverage report
pytest --cov=project --cov-report=term-missing

# Run a specific test file
pytest tests/unit/test_app.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in `tests/unit/test_<module>.py`
- Do not make real network calls in unit tests — mock all HTTP and LLM calls
- Use `pytest.monkeypatch` or `unittest.mock.patch` for mocking
- Start with pure functions: `format_doc`, `load_chat_model` (error path)

---

## 8. Environment Setup

### Required Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp project/.env.example project/.env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_API_KEY` | Yes (if using Mistral) | API key from console.mistral.ai |
| `GROQ_API_KEY` | Yes (if using Groq) | API key from console.groq.com |

> **Never commit `.env`** — it is in `.gitignore`. Only `.env.example` is tracked.

### Installing Dev Dependencies

Once the dev dependency group is configured in `pyproject.toml`:

```bash
# Using uv
uv sync --extra dev

# Using pip
pip install -e ".[dev]"
```

Dev dependencies include: `ruff`, `mypy`, `pytest`, `pytest-cov`.

---

## 9. Reporting Issues

Use **GitHub Issues** to report bugs, request features, or raise questions.

### Bug Report

Include:
- Python version and OS
- Exact error message and traceback
- Steps to reproduce
- Expected vs actual behaviour

### Feature Request

Include:
- What problem it solves
- Proposed approach (optional)
- Whether it fits within the current project scope (see `AGENTS.md` Section 5)

### Labels to Use

| Label | Use |
|-------|-----|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Docs-only issue |
| `question` | Help or clarification needed |
| `good first issue` | Suitable for a new contributor |
| `wontfix` | Out of scope |
