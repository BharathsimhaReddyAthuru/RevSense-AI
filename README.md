# RevSense-AI

End-to-end revenue intelligence and ML pipeline built around the Brazilian Olist ecommerce dataset.

## What this project is

RevSense-AI is a reproducible portfolio project that demonstrates how to build an analytics + ML stack with production-oriented patterns:

- dbt-based ELT and data modeling (staging, features, marts) in `revsense_dbt/`
- Python training pipelines and model artifacts in `ml/` (`ml/train_revenue_models.py`, `ml/models/`)
- A retrieval-augmented chatbot implementation for exploring docs and model outputs in `ml/chatbot/`
- Documentation, KPIs and data inventory in `docs/` and sample raw data in `data/raw/`

This repository is intended as a well-documented starting point for experimentation or for hardening to a production deployment.

## What we implemented and how

- Data modeling: a dbt project (`revsense_dbt/`) with staging, intermediate, feature and mart models to produce analytics-ready tables.
- Machine learning: example training scripts for churn, customer lifetime value (LTV), and monthly revenue forecasting (`ml/train_revenue_models.py`). Trained models are saved to `ml/models/`.
- Retrieval-augmented chatbot: an industry-grade RAG implementation using LangChain + HuggingFace embeddings + Chroma/FAISS and optional local `transformers` generation. Key points:
	- The chatbot code lives in `ml/chatbot/` and is driven by `ml/chatbot/app_industry.py`.
	- The implementation uses delayed/guarded imports so the repository can be inspected without immediately requiring heavy binary packages.
	- A Dockerfile and `requirements-chatbot.txt` are provided to build a reproducible runtime (Python 3.11) and to install CPU PyTorch wheels prior to other packages to avoid wheel resolution issues on newer host Python versions.
	- If local generation via `transformers` is unavailable in your environment, the system will fall back to returning retrieved document content instead of failing.

Notes on the chatbot: there is no separate lightweight TF-IDF chatbot in this repository — the provided implementation targets an industry-style LangChain/HuggingFace stack and expects heavy ML packages when running in industry mode.

## Contents

- `revsense_dbt/` — dbt models and manifest
- `ml/` — training scripts, model artifacts, and `ml/chatbot/`
- `ml/chatbot/` — industry-grade chatbot, Dockerfile, and requirements
- `data/` — raw and processed datasets
- `docs/` — business questions, KPIs, and data inventory
- `notebooks/` — exploratory analysis

## Quick start

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install core Python dependencies for data & ML work

```bash
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

3. (Optional) Configure environment for ML workflows

```bash
cp ml/.env.example ml/.env
# edit ml/.env for Snowflake or other credentials if needed
```

4. Run dbt (if you have a warehouse configured)

```bash
cd revsense_dbt
dbt run
cd ..
```

5. Train example models

```bash
python ml/train_revenue_models.py
```

## Chatbot (industry-grade)

This repository ships an industry-style RAG chatbot. Because the chatbot depends on binary packages (CPU PyTorch, FAISS/chromadb), use the provided Dockerfile for a reproducible environment.

Build and run in Docker (from repo root):

```bash
# build the image
docker build -t revsense-chatbot -f ml/chatbot/Dockerfile .

# build the index inside the container (mount repo so container can access files)
docker run --rm -v "$PWD":/app revsense-chatbot python ml/chatbot/app_industry.py --build-index

# query the bot
docker run --rm -v "$PWD":/app revsense-chatbot python ml/chatbot/app_industry.py --query "What is customer lifetime value?"
```

Notes:
- If you mount the repository into the container (`-v "$PWD":/app`), the container uses the host files; rebuild the image after code changes if you need the image to include updates.
- The Dockerfile installs a CPU PyTorch wheel first to satisfy `sentence-transformers` and avoid wheel resolution failures on some host Python versions.

## Tests

Unit tests for the chatbot are under `ml/chatbot/tests/`. Run a quick syntax check:

```bash
python -m py_compile ml/chatbot/*.py ml/chatbot/tests/*.py
```

## What you can improve next

- Add CI to run tests and linting
- Add a reproducible environment for local development (conda/pyenv) to match Docker
- Add integration tests for the chatbot index build and query

## License

See the `LICENSE` file at the repository root.


