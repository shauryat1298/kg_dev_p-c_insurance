# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Knowledge Graph (KG) development pipeline for Property & Casualty Insurance documents. The system uses LLM-powered agents coordinated through LangGraph to:
1. Extract structured data from insurance PDFs (policies, claims forms, underwriting guidelines)
2. Build a domain-specific knowledge graph with entities and relationships
3. Store the graph in ChromaDB for retrieval-augmented applications

The architecture is **agent-based**: multiple autonomous LLM agents process documents through a state machine workflow, each handling specific tasks like entity extraction, entity matching, and entity improvement.

## Development Commands

### Environment Setup
```bash
# Install dependencies (recommended: use uv for fast dependency management)
pip install uv
uv sync

# Or use standard pip
uv pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
OPENROUTER_API_KEY=your_openrouter_api_key
```

### Running the Pipeline
```bash
# Run the full end-to-end pipeline
uv python run main.py

# Or with standard Python
python main.py
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run a specific test file
python -m pytest tests/test_section_to_entity_dev.py

# Run a single test
python -m pytest tests/test_section_to_entity_dev.py::SectionToEntityDevTests::test_build_workflow
```

### Frontend (Streamlit)
```bash
# Run the Streamlit web interface
python -m streamlit run frontend/index.py

# Access at http://localhost:8501
```

### Docker Deployment
```bash
# Build and start container
docker-compose up -d

# Access at http://localhost:8501

# Stop container
docker-compose down
```

## Architecture

### Pipeline Stages (main.py)

The pipeline executes in 4 sequential stages:

1. **PDF to Image Conversion** (`src/pdf_to_img.py`)
   - Converts PDFs from `artifacts/forms_pdf/` to PNGs in `artifacts/forms_png/`
   - Uses PyMuPDF with multi-threaded processing

2. **Data Model Generation** (`src/page_data_model_dev.py`)
   - Processes PNG pages to generate Proto3 data models
   - Uses LLM vision capabilities to extract form structure
   - Outputs `.proto` files to `artifacts/forms_proto_dm/`
   - Prompts defined in `prompts/form_page_dm.py`

3. **Embedding Generation** (`src/emedding_dm.py`)
   - Extracts proto message definitions from `.proto` files
   - Generates natural language descriptions of each section
   - Creates embeddings and stores in ChromaDB collection
   - Prompts defined in `prompts/proto_sectional_desc.py`

4. **Knowledge Graph Entity Development** (`src/section_to_entity_dev.py`)
   - Executes LangGraph workflow to build/update master KG entities
   - See "LangGraph Workflow" section below

### LangGraph Workflow (`src/section_to_entity_dev.py`)

The workflow is a **StateGraph** that processes document sections and builds a master knowledge graph of entities. State is defined in `states/cluster_dev_state.py`.

**Flow:**
```
section_entity_matching → [match found?]
  ├─ Yes → entity_improving_bool → [improvement needed?]
  │         ├─ Yes → entity_improving → load_master_db → END
  │         └─ No → END
  └─ No → new_entity_dev → load_master_db → END
```

**Agents (in `agents/`):**

- `section_entity_matching_agent.py`: Queries ChromaDB for similar entities, asks LLM if semantic match exists
- `new_entity_dev_agent.py`: Creates new KG entity from section when no match found
- `entity_improving_bool_agent.py`: Determines if matched entity needs improvement
- `entity_improving_agent.py`: Merges section data into existing entity
- `load_master_db_agent.py`: Persists entity to master ChromaDB collection

**Key Insight:** The workflow **does not** modify the master KG during agent execution. Agents only update workflow state. The final agent (`load_master_db_agent`) is responsible for all database writes.

### State Management

**ClusterDevState** (`states/cluster_dev_state.py`):
- `section`: Current document section being processed (description, embedding, proto_heading, proto_dm)
- `master_kg_entity`: Entity from master KG (heading, description, embedding, proto_dm)
- `section_entity_match_bool`: Whether section matches an existing entity
- `entity_improvement_required_bool`: Whether matched entity needs updating
- `matched_entity_id`: ID of matched entity

### ChromaDB Collections

**Persistent client** configured in `config.py`:
- Location: `artifacts/chroma_db_client/`
- `collection_name`: Stores sectional embeddings from documents (e.g., "construction_lob")
- `master_collection_name`: Stores master KG entities (e.g., "kg_entity_construction")

### LLM Configuration

**API**: OpenRouter (OpenAI-compatible API for multiple models)
- API key: Set via `.env` or Streamlit sidebar
- Models configured in `config.py`:
  - `COMPLEX_MODEL_NAME`: For complex reasoning tasks (e.g., "anthropic/claude-sonnet-4.5")
  - `SIMPLE_MODEL_NAME`: For simple classification tasks (e.g., "openai/gpt-5-nano")
  - `OPENROUTER_EMBEDDING_MODEL_NAME`: For embeddings (e.g., "sentence-transformers/all-minilm-l12-v2")

**Utilities** (`src/utils.py`):
- `call_openrouter_llm()`: Synchronous LLM calls
- `call_openrouter_llm_async()`: Async LLM calls with retry logic
- `call_openrouter_embeddings()`: Embedding generation
- `get_api_key()`: Retrieves API key from parameter > thread-local > Streamlit session state > environment
- `extract_json_from_llm()`: Parses JSON from LLM responses
- `extract_proto_code_for_llm_response()`: Extracts Proto3 code from markdown blocks

### Prompts

All prompts in `prompts/` directory:
- `form_page_dm.py`: Extract Proto3 data models from form images
- `proto_sectional_desc.py`: Generate natural language descriptions of proto sections
- `section_entity_matching_prompt.py`: Determine semantic match between section and entity
- `new_entity_dev_prompt.py`: Create new entity from section
- `entity_improving_bool_prompt.py`: Decide if entity needs improvement
- `entity_improving_prompt.py`: Merge section data into entity

### Frontend

**Streamlit app** (`frontend/index.py`):
- Single-file application with tabs for document processing and KG visualization
- Users can enter OpenRouter API key directly in sidebar (stored in session state)
- Visualizes knowledge graph using Plotly/NetworkX

## Configuration

**config.py**: Central configuration
- `BASE_PATH`: Project root directory (overridable via env var)
- `ARTIFACTS_PATH`: Storage for generated artifacts
- Path configuration for PDFs, PNGs, proto files, ChromaDB
- Collection names
- Model names and parameters

## Key Design Patterns

1. **Async/Await for I/O**: All LLM calls and file operations in stages 2-3 use asyncio for parallelism
2. **Thread Pool for CPU**: PDF-to-image conversion uses ThreadPoolExecutor
3. **State Machine Workflow**: LangGraph manages agent coordination and conditional routing
4. **Prompt Engineering**: Domain-specific prompts in separate files for maintainability
5. **Vector Similarity Search**: ChromaDB enables semantic matching between sections and entities
6. **Proto3 as Intermediate Format**: Structured representation of form fields for downstream processing

## Testing

Tests located in `tests/` directory:
- `test_pdf_to_img.py`: PDF conversion tests
- `test_page_data_model_dev.py`: Data model generation tests
- `test_emedding_dm.py`: Embedding generation tests
- `test_section_to_entity_dev.py`: LangGraph workflow tests

Tests use `unittest.mock` to avoid external dependencies (LLM APIs, databases).

## Artifacts Directory Structure

```
artifacts/
├── forms_pdf/           # Input: PDF files
├── forms_png/           # Generated: PNG images (one directory per PDF)
├── forms_proto_dm/      # Generated: Proto3 data models (one directory per PDF)
└── chroma_db_client/    # Generated: ChromaDB persistent storage
```

Place PDFs in `artifacts/forms_pdf/` before running the pipeline.

## Important Notes

- **API Keys**: Required for LLM operations. Set in `.env` or enter in Streamlit sidebar.
- **Async Context**: When calling LLM utilities from async code, use the `_async` variants and optionally set API key via `set_api_key()` for thread-local storage.
- **ChromaDB Persistence**: All collections are persistent. Rerunning the pipeline will add to existing data (not overwrite).
- **Agent Idempotency**: Agents are **not** idempotent. Running the same section twice may create duplicate entities or update existing ones.
- **Error Handling**: Async functions have retry logic with exponential backoff for rate limits.
