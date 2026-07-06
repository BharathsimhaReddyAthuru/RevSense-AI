# ML Pipeline for RevSense-AI

This folder contains the machine learning training workflow built on dbt feature tables.

## Setup

1. Copy `ml/.env.example` to `ml/.env` and fill in your Snowflake credentials.
2. Install dependencies in the project virtualenv:

```bash
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

## Training

Run the training script to train all models and generate prediction artifacts:

```bash
python ml/train_revenue_models.py
```
## Chatbot prototype

A retrieval-augmented chatbot is available in `ml/chatbot/` for answering domain questions from repository documentation and models.

Build the vector index first:

```bash
python ml/chatbot/app.py --build-index
```

Ask a question:

```bash
python ml/chatbot/app.py --query "What is customer lifetime value?"
```

## Chatbot notes

- The chatbot uses a lightweight TF-IDF retrieval engine by default.
- Generative model responses are optional and require installing `transformers` and a compatible model.
- No OpenAI credits are required for retrieval-based operation.
## Output

Trained model artifacts are saved in `ml/models/`:

- `customer_churn_classifier.pkl`
- `customer_ltv_regressor.pkl`
- `revenue_forecast_regressor.pkl`

## Notes

- `ml/train_revenue_models.py` validates Snowflake configuration, verifies feature tables, trains the models, and writes scored predictions back to Snowflake.
- The repository currently does not include a working `ml/qa_system.py`; that feature is planned but not implemented here.
- `OPENAI_API_KEY` is optional and only needed if you add an OpenAI-based QA extension later.
