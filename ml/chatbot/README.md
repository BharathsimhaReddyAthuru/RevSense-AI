# RevSense-AI Chatbot

A retrieval-augmented chatbot built with open-source models, local vector search, and domain knowledge from the repository.

## Features

- Document ingestion from `docs`, `sql`, and dbt model directories
- Local TF-IDF vector search using `scikit-learn`
- Optional open-source generation with `transformers`
- Input safety filtering
- Logging of queries and sources
- Unit tests for ingestion, retrieval, generation, and safety

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

3. Build the vector index:

```bash
python ml/chatbot/app.py --build-index
```

4. Ask a query:

```bash
python ml/chatbot/app.py --query "What is customer lifetime value?"
```

## Notes

- The chatbot works in a lightweight, offline retrieval mode without `transformers`.
- Install `transformers` and a compatible model only if you want richer generative answers.
- The index persists to `ml/chatbot/index/`.

## Tests

Run tests with:

```bash
python -m pytest ml/chatbot/tests
```
