# CodeMind AI — Intelligent Code Assistant

CodeMind AI is a Streamlit application for asking questions about a local codebase. It searches source files in `data/`, selects relevant code using a hybrid retrieval pipeline, reranks those results, and sends the selected context to a Groq language model to produce an answer.

The application can explain code, investigate possible bugs, suggest optimizations, and generate test ideas. Answers include the source chunks retrieved for the question so you can check the response against the code.

## Features

- Indexes supported source files recursively from `data/`.
- Combines semantic retrieval using Sentence Transformers and FAISS with keyword retrieval using BM25.
- Reranks candidate chunks with FlashRank.
- Generates answers with Groq's `openai/gpt-oss-120b` model.
- Provides Ask, Explain, Debug, Optimize, and Generate Tests modes.
- Displays indexed-file and chunk counts, retrieved source snippets, file paths, and reranking scores.
- Includes sample Python files in `data/` so the app has example content to index.

## How it works

1. `code_loader.py` recursively scans the configured data folder for supported file extensions and reads the files as UTF-8, ignoring undecodable characters.
2. Each file is divided into 1,000-character chunks with 200 characters of overlap. Empty chunks are skipped.
3. `rag_pipeline.py` embeds all chunks using `all-MiniLM-L6-v2`. It normalizes these vectors and adds them to a FAISS inner-product index, which is used for cosine-similarity retrieval.
4. The same chunks are tokenized with lowercase whitespace splitting and indexed with BM25 for keyword search.
5. The pipeline retrieves up to eight candidates from each search path and combines them using the configured 0.6 semantic / 0.4 BM25 weighted score.
6. FlashRank reranks the candidates against the question. Up to four chunks are sent as context to Groq.
7. The model is instructed to ground answers in the supplied code context and to say when the indexed context does not contain the answer.

The embedding model, FAISS index, BM25 index, and loaded documents are held in memory. The Streamlit app caches the `CodeRAG` resource for the running process; restarting the process rebuilds the indexes.

## Requirements

- Python 3.10 or newer is recommended.
- A Groq API key.
- Internet access on first run to download the Sentence Transformers and FlashRank models.
- Disk space for Python packages and model files.

The application dependencies are listed in `requirements.txt`: Streamlit, Groq, python-dotenv, Sentence Transformers, FAISS CPU, rank-bm25, FlashRank, and NumPy.

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/dhilleswar07/Intelligent_Code_Assistant.git
cd Intelligent_Code_Assistant
```

Create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configure the API key

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

The application loads this value through `python-dotenv`. Keep `.env` private and do not commit or share it. The provided `.gitignore` excludes `.env`, but it can still be included when manually creating an archive, so check distributions before sharing them.

## Add code to index

Place the source code you want to query inside the root `data/` directory. Its subdirectories are searched recursively. The archive includes `data/sample.py` and `data/utils.py` as example files.

```text
Intelligent_Code_Assistant/
├── app.py
├── code_loader.py
├── rag_pipeline.py
├── requirements.txt
└── data/
    ├── sample.py
    ├── utils.py
    └── your_project/
        └── main.py
```

The loader indexes only the file types listed below. It does not scan the entire repository; only files beneath `data/` are indexed.

## Start the app

From the project root, run:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. On first startup, the embedding and reranking models may need to download. The app constructs the code indexes when it initializes, so startup time depends on the size of `data/` and whether the models are already cached.

## Use the assistant

1. Select a mode from the sidebar.
2. Enter a question in the chat field, or choose a quick action on the page.
3. Read the answer and expand **Retrieved Sources** to inspect the code that was passed as context.
4. Choose **Clear Conversation** in the sidebar to clear the session's visible chat history.

| Mode | Focus |
| --- | --- |
| Ask | Answer a question about the indexed code. |
| Explain | Describe relevant code step by step in simple technical language. |
| Debug | Look for bugs, exceptions, incorrect logic, and edge cases. |
| Optimize | Suggest performance, efficiency, and maintainability improvements. |
| Generate Tests | Draft practical unit tests for relevant functions. |

Quick actions submit preset prompts for explaining the codebase, finding possible bugs, optimizing the codebase, or generating unit tests.

## Supported file extensions

The loader currently indexes:

`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.h`, `.cs`, `.go`, `.rs`, `.sql`, `.html`, and `.css`.

Extension matching is case-insensitive. Other files such as Markdown, JSON, YAML, notebooks, and configuration files are skipped.

## Current defaults

| Setting | Value |
| --- | --- |
| Data folder | `data/` |
| Chunk size / overlap | 1,000 / 200 characters |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector index | FAISS `IndexFlatIP`, with normalized embeddings |
| Hybrid candidate count | Up to 8 |
| Hybrid score weights | Semantic 0.6, BM25 0.4 |
| Reranker | FlashRank `ms-marco-MiniLM-L-12-v2` |
| Context chunks sent to Groq | Up to 4 |
| Groq model | `openai/gpt-oss-120b` |
| Generation temperature | 0.2 |
| Maximum completion tokens | 1,500 |

These are values set in the Python source, not configurable environment variables.

## Project files

| File or folder | Purpose |
| --- | --- |
| `app.py` | Streamlit page, assistant modes, chat state, quick actions, and source display. |
| `code_loader.py` | Finds supported files and creates overlapping text chunks. |
| `rag_pipeline.py` | Builds indexes, retrieves and reranks code, and calls the Groq API. |
| `requirements.txt` | Python dependencies. |
| `.env` | Local Groq API key; create locally and keep private. |
| `data/` | Code files to index. |
| `cache/` | FlashRank model cache directory configured by the pipeline. |

## Troubleshooting

### No supported code files found

Add at least one non-empty supported source file beneath `data/`. The pipeline raises an error when it finds no chunks to index.

### Groq API key error

Confirm that `.env` is in the project root and contains a `GROQ_API_KEY=...` entry. Restart Streamlit after changing the key. Check that the key is valid and that the Groq account can use the configured model.

### Model download or initialization errors

Check internet access, disk space, and the Python environment. The first run downloads model files; later runs can reuse cached copies.

### App startup is slow

The pipeline reads every supported file under `data/`, chunks all content, and generates embeddings during initialization. Reduce the indexed dataset or exclude unnecessary folders from `data/` if startup takes too long.

### Answers miss relevant code

Make sure the relevant files are under `data/` and use supported extensions. The pipeline sends at most four reranked chunks to the model, and character-based chunking can split functions across boundaries. Try a more specific question that includes a function, class, or filename.

## Privacy and limitations

- Code chunks selected by retrieval are included in requests to the configured Groq API. Do not index credentials, personal data, or source code you are not authorized to send to that service.
- The model can still produce inaccurate or incomplete answers. Review retrieved sources and verify generated code before using it.
- Chunking is based on character positions rather than language syntax, so functions may be split between chunks.
- The BM25 tokenizer uses lowercase whitespace splitting; it does not perform language-aware tokenization.
- Indexes are rebuilt at app initialization and are not saved as a persistent database.
- The pipeline combines raw FAISS and BM25 scores with fixed weights. These score ranges can differ, so the weights do not guarantee balanced contributions for every query.
- The sidebar's pipeline readiness labels are static UI messages, not independent health checks of each service.
- The archive contains a `.env` file. Before sharing the archive, remove that file; if its API key is real or has been exposed, revoke or rotate it.

## License

No license file was present in the supplied project archive. Add the license that applies to this project before redistributing it.
