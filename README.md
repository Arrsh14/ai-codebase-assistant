# 🧠 AI Codebase Assistant

A Retrieval-Augmented Generation (RAG) tool that lets you ask natural-language questions about any codebase and get accurate, grounded answers with source citations — instead of manually digging through files.

## What it does to the project?

Point it at any code repository and ask things like:
- "Where is authentication implemented?"
- "How does the login flow work, from form to session handling?"
- "What does this function do?"

The assistant retrieves the most relevant pieces of code using semantic search, then uses an LLM (Gemini) to generate a clear answer — grounded strictly in the actual code, not guesses.

## How it works

1. **Chunking** — Walks the codebase and splits files into meaningful pieces. Python files are parsed using the `ast` module so each chunk is a *complete function or class*, not an arbitrary slice of text. JavaScript is chunked using pattern matching + brace counting. Other files (HTML, CSS, etc.) use clean line-boundary chunking.
2. **Embedding + storage** — Each chunk is embedded and stored in a local ChromaDB vector database for fast semantic search.
3. **Retrieval** — When you ask a question, the most relevant chunks are retrieved based on meaning, not just keyword matching.
4. **Generation** — Retrieved chunks are passed to Gemini, which generates an answer grounded only in that context — if the answer isn't in the code, it says so instead of guessing.
5. **UI** — A simple Streamlit interface to ask questions in the browser.

## Tech stack

- Python
- ChromaDB (vector database)
- Google Gemini API (`gemini-2.5-flash`)
- Streamlit (UI)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or install chromadb, google-genai, streamlit individually
export GEMINI_API_KEY="your-key-here"
```

## Usage

**Index a codebase:**
```bash
python3 store.py
```

**Ask questions via terminal:**
```bash
python3 generate.py
```

**Ask questions via browser UI:**
```bash
streamlit run app_ui.py
```

## Project status

Built as a learning project to understand RAG systems end-to-end — chunking, embeddings, vector search, and LLM grounding. Tested on multiple real repositories, including a 70+ file production Flask application.

## Possible next steps

- Support for more languages in smart chunking (currently Python + JS)
- Multi-turn conversation memory
- Support for additional LLM providers

Made By->Arrsh Tripathi
23BCI0191
