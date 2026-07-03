# ML Pipeline for RevSense-AI

This folder contains the core machine learning pipeline for training models from dbt feature tables.

## Setup

1. Copy `.env.example` to `.env` and fill in your Snowflake credentials.
2. Install dependencies in the project virtualenv:

```bash
pip install -r requirements.txt
pip install scikit-learn joblib python-dotenv snowflake-connector-python
```

## Training

Run the script to train all models:

```bash
python ml/train_revenue_models.py
```

## Output

Trained model artifacts are saved in `ml/models/`:

- `customer_ltv.pkl`
- `churn_classifier.pkl`
- `revenue_forecast.pkl`
