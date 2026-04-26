# Architecture — LLM Biodata Training: SPARQL Query Assistant

> This document describes the application architecture, data flow, module boundaries,
> and dependency rules for the chatbot component located in `project/`.

---

## 1. High-Level Overview

The SPARQL Query Assistant is a **RAG (Retrieval-Augmented Generation)** chatbot. Rather than
relying on the LLM's parametric knowledge about SPARQL syntax, the system pre-indexes
official SPARQL examples and data schemas from biological databases, then retrieves the most
relevant context for each user question before generating a query.

This approach allows the LLM to generate syntactically correct, endpoint-specific SPARQL
queries — even for databases it may not have been trained on.

---

## 2. Component Map

```
┌──────────────────────────────────────────────────────────────────┐
│                     Chainlit Web UI                              │
│                 (on_message / set_starters)                      │
└──────────────────────────────────────────────────────────────────┘
                              │
                    User message arrives
                              │
          ┌───────────────────┼──────────────────────┐
          ▼                   ▼                        ▼
┌──────────────────┐ ┌─────────────────┐   ┌──────────────────────┐
│  FastEmbed       │ │  Qdrant (local) │   │  LLM Provider        │
│  BAAI/bge-small  │ │  data/vectordb/ │   │  Mistral AI / Groq   │
│  384-dim vectors │ │                 │   │  (via LangChain)     │
└──────────────────┘ └─────────────────┘   └──────────────────────┘
          │                   │                        │
    embed question     vector search              generate query
          └───────────────────┘                        │
                    retrieved docs                      │
                    (examples + schemas)                │
                              │                         │
                   inject into SYSTEM_PROMPT            │
                              └─────────────────────────┘
                                           │
                                  LLM streams response
                                           │
                          ┌────────────────┴──────────────────┐
                          ▼                                    ▼
               Contains SPARQL block?               No SPARQL block?
                          │                                    │
                          ▼                                    ▼
               extract_sparql_queries()              stream to user
               parse endpoint URL + query
                          │
                          ▼
               query_sparql() → live HTTP call
               to biological endpoint
                          │
               ┌──────────┴────────────┐
               ▼                       ▼
          Results found?         No results?
               │                       │
               ▼                       ▼
       summarise results        inject corrective
       and stream to user       feedback → retry
                                (max 3 attempts)
```

---

## 3. Module Boundaries

The application is currently a **single monolithic file** (`app.py`). It contains five
logically distinct sections, each mapping to a planned module in a future refactoring:

| Section | Functions | Responsibility |
|---------|-----------|----------------|
| **1. LLM Provider** | `load_chat_model()` | Factory for chat model instances |
| **2. Vector DB + Indexing** | `index_endpoints()`, `embedding_model`, `vectordb` | One-time indexing of SPARQL docs |
| **3. Retrieval** | `retrieve_docs()`, `format_doc()`, `SYSTEM_PROMPT` | Per-query document retrieval and context formatting |
| **4. Query Execution** | `execute_query()` | SPARQL extraction and execution |
| **5. Chat UI** | `on_message()`, `set_starters()` | Chainlit handlers and retry loop |

### 3.1 Dependency Direction (Current)

```
Chainlit handlers
    └── retrieve_docs() ──→ Qdrant + FastEmbed
    └── LLM (load_chat_model)
    └── execute_query() ──→ sparql-llm (extract + query)
```

### 3.2 Dependency Rule

- **Section 5** (UI) may call all other sections.
- **Sections 1–4** must not call Chainlit.
- `index_endpoints()` must only be called explicitly — never triggered by a user message.
- No circular dependencies.

---

## 4. Data Formats

### 4.1 Vector Database Documents (Qdrant payload)

Each document stored in the vector DB has a `payload` with at least:

| Field | Type | Example |
|-------|------|---------|
| `doc_type` | `str` | `"SPARQL endpoints query examples"` or `"SPARQL endpoints classes schema"` |
| `question` | `str` | `"How to retrieve all human proteins?"` |
| `answer` | `str` | The SPARQL query string |
| `endpoint_url` | `str` | `"https://sparql.uniprot.org/sparql/"` |

### 4.2 SPARQL Query Format Expected by `execute_query()`

The LLM response must contain a markdown codeblock tagged `sparql` with the endpoint URL
as a comment on the first line:

````
```sparql
#+ endpoint: https://sparql.uniprot.org/sparql/
SELECT ?protein WHERE {
  ...
}
```
````

The `extract_sparql_queries()` function from `sparql-llm` parses this format. If the comment
is missing, `execute_query()` cannot determine the target endpoint and will return `None`.

### 4.3 SPARQL Endpoint Results

`query_sparql()` returns a SPARQL JSON results object:

```json
{
  "results": {
    "bindings": [
      {"gene": {"type": "uri", "value": "http://..."}, ...}
    ]
  }
}
```

`execute_query()` returns `bindings` as `list[dict[str, str]]`, or `None` if no query was found.

---

## 5. Indexing Pipeline (One-Time Setup)

```
index_endpoints()
    │
    ├─ for each endpoint in endpoints[]:
    │       SparqlExamplesLoader(endpoint_url).load()  → example Q&A pairs
    │       SparqlVoidShapesLoader(endpoint_url).load() → data schema shapes
    │
    ├─ SparqlInfoLoader(endpoints).load()  → general endpoint info
    │
    ├─ Delete existing Qdrant collection "sparql-docs"
    ├─ Create new collection (384-dim, cosine distance)
    │
    └─ embedding_model.embed(all docs) → upload vectors + payloads to Qdrant
```

**Key characteristics:**
- Runs once at startup (or manually when endpoints change)
- Makes HTTP requests to live SPARQL endpoints — requires network access
- Overwrites the collection each time (no incremental update)
- Stored in `project/data/vectordb/` (local Qdrant on disk)

---

## 6. Retrieval Pipeline (Per Query)

```
retrieve_docs(question)
    │
    ├─ FastEmbed.embed([question])  → 384-dim question vector (fast, ~50ms)
    │
    ├─ Qdrant.query_points(filter: doc_type == "SPARQL endpoints query examples", limit=3)
    ├─ Qdrant.query_points(filter: doc_type == "SPARQL endpoints classes schema", limit=3)
    │
    └─ returns list of ScoredPoint (up to 6 total)
```

**Key characteristics:**
- Runs on every user message
- Filtered search — ensures both query examples and schema are always included
- Top-3 per type (controlled by `retrieved_docs_count = 3`)

---

## 7. Biological Endpoints

| Endpoint | URL | Data Type |
|----------|-----|-----------|
| UniProt | `https://sparql.uniprot.org/sparql/` | Protein sequences, functions, annotations |
| Bgee | `https://www.bgee.org/sparql/` | Gene expression across tissues and species |
| OMA Browser | `https://sparql.omabrowser.org/sparql/` | Orthologous gene relationships |

Adding a new endpoint requires:
1. Adding an entry to the `endpoints` list in `app.py`
2. Re-running `index_endpoints()`
3. Updating `docs/FEATURE_STATUS.md`
4. Updating the `chainlit.md` welcome screen
5. Adding a test case for the new endpoint coverage

---

## 8. LLM Providers

| Provider | Model Used | When Active |
|----------|-----------|-------------|
| Mistral AI | `mistral-small-latest` | Default (active) |
| Groq | `meta-llama/llama-4-scout-17b-16e-instruct` | Commented out; toggle in code |

To switch provider, change line 36 in `app.py`:
```python
llm = load_chat_model("mistralai/mistral-small-latest")
# llm = load_chat_model("groq/meta-llama/llama-4-scout-17b-16e-instruct")
```

The `load_chat_model()` factory handles provider routing. To add a new provider:
1. Add a new `if provider == "..."` branch in `load_chat_model()`
2. Add the corresponding langchain package to `pyproject.toml`
3. Add the API key to `.env.example`
4. Write a test for the new provider (mock the API)

---

## 9. Key Dependencies

| Package | Version Constraint | Purpose |
|---------|-------------------|---------|
| `sparql-llm` | `>=0.0.8` | SPARQL example/schema loaders, query extraction, query execution |
| `langchain` | `>=0.3.27` | LLM abstraction layer |
| `langchain-mistralai` | `>=0.2.12` | Mistral AI backend |
| `langchain-groq` | `>=0.3.8` | Groq backend |
| `langchain-ollama` | `>=0.3.8` | Ollama backend (declared; not yet wired) |
| `qdrant-client` | `>=1.15.1` | Local vector database |
| `fastembed` | `>=0.7.3` | Local embedding model (no API key needed) |
| `chainlit` | `>=2.8.1` | Chat web UI framework |

---

## 10. Known Design Tradeoffs

| Decision | Rationale | Known Limitation |
|----------|-----------|------------------|
| Single `app.py` file | Training/tutorial context; easy to follow | Hard to test; no isolation between concerns |
| Local Qdrant (on-disk) | No external service needed | Single-user; not shareable across instances |
| `delete + recreate` on index | Simple; always consistent | Slow; not incremental |
| Max 3 retry attempts | Prevents infinite loops | May fail on genuinely ambiguous questions |
| Filtered retrieval (2 doc types) | Ensures both examples and schema are always returned | May miss relevant docs of other types |
| No query caching | Simple | Same question re-runs LLM every time (cost + latency) |
