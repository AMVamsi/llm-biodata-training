# Feature Status — llm-biodata-training

> **Single source of truth for implementation status.**
> Read this file before assuming something is missing or needs to be built.
> Update this file every time a task is completed.

---

## How to Read This Table

| Status | Meaning |
|--------|---------|
| `implemented` | Fully working; do not rebuild |
| `baseline` | First working version; may be refined only if explicitly instructed |
| `planned` | Not started; do not build unless the current task explicitly requests it |
| `todo` | Accepted for near-term work; not yet started |
| `in_progress` | Actively being built — check branch before touching |
| `blocked` | Waiting on an external decision or dependency |
| `deprecated` | Do not use for new work |

---

## Application Core (`project/app.py`)

| Feature | Status | Notes | Implemented In |
|---------|--------|-------|----------------|
| `load_chat_model()` | `implemented` | Provider/model string split; Mistral + Groq backends | `app.py:12` |
| `index_endpoints()` | `implemented` | UniProt, Bgee, OMA; deletes + recreates collection on each call | `app.py:62` |
| `retrieve_docs()` | `implemented` | Filters by `doc_type`: query examples + schema shapes; top-3 each | `app.py:101` |
| `format_doc()` | `implemented` | Pure function; markdown codeblock with `#+ endpoint:` comment | `app.py:133` |
| `execute_query()` | `implemented` | Extracts SPARQL from LLM markdown; calls live SPARQL endpoint | `app.py:174` |
| Retry loop (max 3 attempts) | `implemented` | Appends corrective feedback on no-results; re-calls LLM | `app.py:189` |
| `on_message()` Chainlit handler | `implemented` | Streaming responses; step display for retrieved docs + results | `app.py:343` |
| `set_starters()` | `implemented` | Rat orthologs starter question | `app.py:378` |
| LLM provider: Mistral AI | `implemented` | `mistralai/mistral-small-latest` (active) | `app.py:36` |
| LLM provider: Groq | `implemented` | Commented out by default; toggle by changing `load_chat_model` call | `app.py:37` |
| LLM provider: Ollama | `baseline` | Dependency declared in `pyproject.toml`; not wired in function | `pyproject.toml` |
| Return type fix for `execute_query` | `todo` | Should be `list[dict] \| None`; currently annotated as `list[dict]` only | `app.py:174` |
| Commented-out dead code removal | `todo` | ~4 old `async def main()` implementations still in file | `app.py:150–340` |
| Configuration constants extracted | `todo` | `retrieved_docs_count`, `max_try_count`, etc. scattered mid-file | `app.py` |
| Type annotations completed | `todo` | `index_endpoints()` missing return type; others partially typed | `app.py` |
| Docstrings completed | `todo` | `load_chat_model()` and `index_endpoints()` missing docstrings | `app.py` |

---

## Project Structure

| Feature | Status | Notes |
|---------|--------|-------|
| Demo scripts in `demos/` subfolder | `planned` | Currently 5 scripts mixed with app code in `project/` |
| `project/README.md` for chatbot | `todo` | Current README only covers slides, not chatbot setup |
| `chainlit.md` customised | `todo` | Still shows default Chainlit boilerplate text |
| `tests/` folder created | `todo` | No test suite exists |
| `docs/` folder created | `implemented` | Contains `FEATURE_STATUS.md` and `architecture.md` |

---

## Configuration and Tooling

| Feature | Status | Notes |
|---------|--------|-------|
| `ruff` linter + formatter | `todo` | Not yet in `pyproject.toml`; must be added as dev dependency |
| `mypy` type checker | `todo` | Not yet configured |
| `pytest` + `pytest-cov` | `todo` | Not yet installed or configured |
| Dev dependency group in `pyproject.toml` | `todo` | No `[project.optional-dependencies]` dev section yet |
| `__pycache__/` in `.gitignore` | `todo` | Bytecode already committed; need to untrack + add to `.gitignore` |
| `.mypy_cache/` in `.gitignore` | `todo` | Present locally; should be explicitly ignored |
| `data/vectordb/.lock` in `.gitignore` | `todo` | Runtime lock file currently tracked in git |
| Remove tracked `__pycache__/*.pyc` | `todo` | `git rm --cached` needed |
| Remove tracked `data/vectordb/.lock` | `todo` | `git rm --cached` needed |

---

## CI/CD (GitHub Actions)

| Feature | Status | Notes |
|---------|--------|-------|
| Slides deploy to GitHub Pages | `implemented` | `.github/workflows/deploy.yml`; triggers on push to `main` |
| Python CI workflow (`ci.yml`) | `planned` | Lint + type check + test + coverage — Week 17 task |
| Ruff check in CI | `planned` | Requires `ruff` configured first |
| Mypy check in CI | `planned` | Requires `mypy` configured first |
| `pytest` in CI | `planned` | Requires tests written first |
| Coverage upload to Codecov | `planned` | Requires pytest-cov + Codecov account |
| Branch protection on `main` | `planned` | Requires CI checks to be set up first; configure on GitHub |

---

## Tests (`tests/`)

| Test | Status | Notes |
|------|--------|-------|
| `test_format_doc` | `todo` | Pure function — easiest to write first |
| `test_load_chat_model_error` | `todo` | Test `ValueError` on unknown provider |
| `test_load_chat_model_mistral` | `todo` | Mock `ChatMistralAI`; assert return type |
| `test_load_chat_model_groq` | `todo` | Mock `ChatGroq`; assert return type |
| `test_retrieve_docs` | `todo` | Mock Qdrant client; assert filtering by `doc_type` |
| `test_execute_query_no_block` | `todo` | Input with no SPARQL block → assert `None` |
| `test_execute_query_with_block` | `todo` | Input with valid SPARQL block → assert query + endpoint extracted |
| Integration tests | `planned` | Requires live endpoints; scope for later |

---

## Profiling (Week 16 Task)

| Feature | Status | Notes |
|---------|--------|-------|
| `index_endpoints()` flamegraph | `planned` | Known slow path: network + HTTP + embedding |
| `on_message()` profiling | `planned` | Identify LLM vs embedding vs SPARQL time split |
| Bottleneck documentation | `planned` | To be written in `docs/profiling.md` |
| Query result caching | `planned` | Optional: `lru_cache` keyed on question for repeated queries |
| Incremental re-indexing | `planned` | Optional: skip deleting collection if endpoints unchanged |

---

## Future / Out of Scope

| Feature | Status | Notes |
|---------|--------|-------|
| PubMed literature extraction | `planned` | Via UniProt `rdfs:seeAlso` links or PubMed E-utilities |
| Additional SPARQL endpoints | `planned` | e.g., ChEMBL, Ensembl |
| Multi-user / production deployment | `planned` | Requires shared Qdrant + auth |
| Query result caching (persistent) | `planned` | Redis or disk-based cache |
| Custom endpoint upload via UI | `planned` | User-configurable endpoint list |

---

## Last Updated

| Date | Updated By | Change Summary |
|------|-----------|----------------|
| 2026-04-25 | AMVamsi | Initial FEATURE_STATUS.md created from codebase analysis |
