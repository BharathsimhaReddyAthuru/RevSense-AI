import os
from pathlib import Path

import joblib
import sys
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (accuracy_score, classification_report, mean_absolute_error,
                             mean_squared_error, precision_score, recall_score, roc_auc_score,
                             r2_score)
from sklearn.model_selection import train_test_split
from snowflake import connector
from snowflake.connector.pandas_tools import write_pandas

load_dotenv(dotenv_path=Path(__file__).resolve().parent / '.env')

SNOWFLAKE_CONFIG = {
    'user': os.environ.get('SNOWFLAKE_USER'),
    'password': os.environ.get('SNOWFLAKE_PASSWORD'),
    'account': os.environ.get('SNOWFLAKE_ACCOUNT'),
    'role': os.environ.get('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
    'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE', 'REVSENSE_WH'),
    'database': os.environ.get('SNOWFLAKE_DATABASE', 'REVSENSE_AI'),
    'schema': os.environ.get('SNOWFLAKE_SCHEMA', 'DEV'),
}

MODEL_DIR = Path(__file__).resolve().parent / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def validate_snowflake_config():
    missing = [k for k in ('user', 'password', 'account') if not SNOWFLAKE_CONFIG.get(k)]
    if missing:
        print('Missing Snowflake credentials in environment for:', ', '.join(missing))
        print('Create a `ml/.env` from `ml/.env.example` and populate SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT')
        sys.exit(1)



def fetch_sql(sql: str) -> pd.DataFrame:
    with connector.connect(**SNOWFLAKE_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [col[0] for col in cur.description]
            data = cur.fetchall()
    df = pd.DataFrame(data, columns=columns)
    # normalize column names to lowercase for consistent access in code
    df.columns = [c.lower() for c in df.columns]
    return df


def verify_table(table_name: str) -> None:
    print(f'\n=== Verifying {table_name} ===')
    try:
        df = fetch_sql(f'SELECT * FROM {table_name} LIMIT 5')
    except Exception as exc:
        print('Error querying table:', exc)
        return
    print('Sample rows:')
    print(df.head())
    try:
        row_count = fetch_sql(f'SELECT COUNT(*) AS count FROM {table_name}')
        print('Row count:', int(row_count['count'][0]))
    except Exception:
        pass


def verify_data() -> None:
    tables = [
        'MARTS.customer_ltv',
        'MARTS.churn_prediction_dataset',
        'MARTS.monthly_revenue_forecast',
        'MARTS.order_volume_forecast',
        'MARTS.revenue_by_category',
        'MARTS.revenue_by_state',
        'MARTS.revenue_by_seller',
        'MARTS.product_review_metrics',
    ]
    for table in tables:
        verify_table(table)


def build_churn_features() -> pd.DataFrame:
    sql = '''
    SELECT
        cd.customer_id,
        cd.days_since_last_order,
        cd.churn_label,
        COALESCE(cl.total_orders, 0) AS total_orders,
        COALESCE(cl.total_revenue, 0) AS total_revenue,
        COALESCE(cl.avg_order_value, 0) AS avg_order_value,
        COALESCE(cl.customer_age_days, 0) AS customer_age_days,
        COALESCE(cl.is_repeat_customer, FALSE) AS is_repeat_customer
    FROM MARTS.churn_prediction_dataset cd
    LEFT JOIN MARTS.customer_ltv cl ON cd.customer_id = cl.customer_id
    WHERE cd.churn_label IS NOT NULL
    '''
    df = fetch_sql(sql)
    if df.empty:
        return df
    df['revenue_per_order'] = df['total_revenue'] / df['total_orders'].replace(0, np.nan)
    df['revenue_per_order'] = df['revenue_per_order'].fillna(0)
    df['orders_per_day'] = df['total_orders'] / df['customer_age_days'].replace(0, np.nan)
    df['orders_per_day'] = df['orders_per_day'].fillna(0)
    df['recency_ratio'] = df['days_since_last_order'] / df['customer_age_days'].replace(0, 1)
    return df


def build_ltv_features() -> pd.DataFrame:
    sql = '''
    SELECT
        customer_id,
        total_orders,
        total_revenue,
        avg_order_value,
        customer_age_days,
        is_repeat_customer
    FROM MARTS.customer_ltv
    WHERE total_revenue IS NOT NULL
    '''
    df = fetch_sql(sql)
    if df.empty:
        return df
    df['revenue_per_order'] = df['total_revenue'] / df['total_orders'].replace(0, np.nan)
    df['revenue_per_order'] = df['revenue_per_order'].fillna(0)
    df['orders_per_day'] = df['total_orders'] / df['customer_age_days'].replace(0, np.nan)
    df['orders_per_day'] = df['orders_per_day'].fillna(0)
    return df


def build_forecast_features() -> pd.DataFrame:
    sql = '''
    SELECT
        order_month,
        revenue,
        prior_month_revenue,
        next_month_revenue
    FROM MARTS.monthly_revenue_forecast
    WHERE order_month IS NOT NULL
    ORDER BY order_month
    '''
    df = fetch_sql(sql)
    if df.empty:
        return df
    df['order_month'] = pd.to_datetime(df['order_month'])
    df['month_index'] = np.arange(len(df))
    df['month_of_year'] = df['order_month'].dt.month
    df['prior_diff'] = df['revenue'] - df['prior_month_revenue'].fillna(0)
    df['lag2_revenue'] = df['revenue'].shift(2).fillna(0)
    return df.dropna(subset=['revenue'])


def evaluate_regression(y_true: pd.Series, y_pred: np.ndarray, name: str) -> None:
    print(f'\n--- {name} regression evaluation ---')
    print('MAE:', mean_absolute_error(y_true, y_pred))
    print('RMSE:', np.sqrt(mean_squared_error(y_true, y_pred)))
    print('R2:', r2_score(y_true, y_pred))


def evaluate_classifier(y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray, name: str) -> None:
    print(f'\n--- {name} classification evaluation ---')
    print('Accuracy:', accuracy_score(y_true, y_pred))
    print('Precision:', precision_score(y_true, y_pred, zero_division=0))
    print('Recall:', recall_score(y_true, y_pred, zero_division=0))
    try:
        print('ROC AUC:', roc_auc_score(y_true, y_prob))
    except Exception:
        pass
    print(classification_report(y_true, y_pred))


def train_model(X: pd.DataFrame, y: pd.Series, model_type: str, model_name: str):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == 'classifier':
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    if model_type == 'classifier':
        proba = model.predict_proba(X_test)
        if proba.shape[1] == 1:
            # only one class present in training; set probability column to the single-class probability
            y_prob = proba[:, 0]
        else:
            # try to pick the '1' class if available, otherwise use second column
            classes = list(model.classes_)
            if 1 in classes:
                idx = classes.index(1)
            else:
                idx = 1
            y_prob = proba[:, idx]
        evaluate_classifier(y_test, y_pred, y_prob, model_name)
    else:
        evaluate_regression(y_test, y_pred, model_name)

    joblib.dump(model, MODEL_DIR / f'{model_name}.pkl')
    print(f'Saved model: {MODEL_DIR / f"{model_name}.pkl"}')
    return model, X_test, y_test


def train_churn_model() -> None:
    df = build_churn_features()
    if df.empty:
        print('No churn training data found')
        return
    df['is_new_customer'] = (df['days_since_last_order'] > 180).astype(int)
    feature_cols = ['days_since_last_order', 'is_new_customer', 'total_orders', 'avg_order_value',
                    'customer_age_days', 'is_repeat_customer', 'revenue_per_order', 'orders_per_day', 'recency_ratio']
    X = df[feature_cols].fillna(0)
    y = df['churn_label']
    train_model(X, y, 'classifier', 'customer_churn_classifier')


def train_ltv_model() -> None:
    df = build_ltv_features()
    if df.empty:
        print('No LTV training data found')
        return
    feature_cols = ['total_orders', 'avg_order_value', 'customer_age_days', 'is_repeat_customer',
                    'revenue_per_order', 'orders_per_day']
    X = df[feature_cols].fillna(0)
    y = df['total_revenue']
    train_model(X, y, 'regressor', 'customer_ltv_regressor')


def train_revenue_forecast_model() -> None:
    df = build_forecast_features()
    if df.empty:
        print('No forecast training data found')
        return
    feature_cols = ['month_index', 'month_of_year', 'prior_month_revenue', 'lag2_revenue']
    X = df[feature_cols].fillna(0)
    y = df['revenue']
    train_model(X, y, 'regressor', 'revenue_forecast_regressor')


def write_predictions(table_name: str, df: pd.DataFrame) -> None:
    if df.empty:
        print(f'No rows to write for {table_name}')
        return
    # create or replace target table with simple type inference to ensure it exists
    def snowflake_type(dtype) -> str:
        if pd.api.types.is_integer_dtype(dtype):
            return 'NUMBER'
        if pd.api.types.is_float_dtype(dtype):
            return 'FLOAT'
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return 'TIMESTAMP_NTZ'
        return 'VARCHAR'

    db = SNOWFLAKE_CONFIG['database']
    schema = table_name.split('.')[-2]
    tbl = table_name.split('.')[-1]
    cols_sql = ', '.join([f'"{c}" {snowflake_type(dt)}' for c, dt in zip(df.columns, df.dtypes)])
    # quote the table name to match how write_pandas references it (preserves lowercase)
    create_sql = f'CREATE OR REPLACE TABLE {db}.{schema}."{tbl}" ({cols_sql})'
    with connector.connect(**SNOWFLAKE_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
        success, nchunks, nrows, _ = write_pandas(conn, df, tbl, database=db, schema=schema)
    print(f'Wrote {nrows} rows to {table_name}')


def score_models() -> None:
    # load if available
    churn_path = MODEL_DIR / 'customer_churn_classifier.pkl'
    ltv_path = MODEL_DIR / 'customer_ltv_regressor.pkl'
    forecast_path = MODEL_DIR / 'revenue_forecast_regressor.pkl'

    if not churn_path.exists() or not ltv_path.exists() or not forecast_path.exists():
        print('Model artifacts not all present, skipping scoring')
        return

    churn_model = joblib.load(churn_path)
    ltv_model = joblib.load(ltv_path)
    forecast_model = joblib.load(forecast_path)

    churn_df = build_churn_features()
    if not churn_df.empty:
        # ensure derived feature `is_new_customer` exists (same logic as training)
        if 'is_new_customer' not in churn_df.columns:
            churn_df['is_new_customer'] = (churn_df['days_since_last_order'] > 180).astype(int)
        churn_features = churn_df[['days_since_last_order', 'is_new_customer', 'total_orders', 'avg_order_value',
                                    'customer_age_days', 'is_repeat_customer', 'revenue_per_order', 'orders_per_day', 'recency_ratio']].fillna(0)
        proba = churn_model.predict_proba(churn_features)
        if proba.shape[1] == 1:
            churn_df['churn_probability'] = proba[:, 0]
        else:
            classes = list(churn_model.classes_)
            idx = classes.index(1) if 1 in classes else 1
            churn_df['churn_probability'] = proba[:, idx]
        churn_df['churn_prediction'] = churn_model.predict(churn_features)
        write_predictions('REVSENSE_AI.MARTS.customer_churn_score', churn_df[['customer_id', 'churn_probability', 'churn_prediction']])

    ltv_df = build_ltv_features()
    if not ltv_df.empty:
        ltv_features = ltv_df[['total_orders', 'avg_order_value', 'customer_age_days', 'is_repeat_customer',
                                'revenue_per_order', 'orders_per_day']].fillna(0)
        ltv_df['predicted_ltv'] = ltv_model.predict(ltv_features)
        write_predictions('REVSENSE_AI.MARTS.customer_ltv_prediction', ltv_df[['customer_id', 'predicted_ltv']])

    forecast_df = build_forecast_features()
    if not forecast_df.empty:
        forecast_features = forecast_df[['month_index', 'month_of_year', 'prior_month_revenue', 'lag2_revenue']].fillna(0)
        forecast_df['predicted_revenue'] = forecast_model.predict(forecast_features)
        write_predictions('REVSENSE_AI.MARTS.revenue_forecast_prediction', forecast_df[['order_month', 'predicted_revenue']])


if __name__ == '__main__':
    validate_snowflake_config()
    print('Verifying feature tables...')
    verify_data()
    print('\nTraining churn model...')
    train_churn_model()
    print('\nTraining LTV model...')
    train_ltv_model()
    print('\nTraining revenue forecast model...')
    train_revenue_forecast_model()
    print('\nScoring models and writing predictions back to Snowflake...')
    score_models()
