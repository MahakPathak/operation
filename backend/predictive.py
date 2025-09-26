import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from typing import List, Dict

def predictive_model() -> LinearRegression:
    """
    Trains a simple linear regression model on historical mileage vs days_to_failure data.
    Returns:
        LinearRegression: trained model
    """
    # Historical sample data
    hist = pd.DataFrame({
        'mileage': [5000, 100000, 150000, 200000, 250000],
        'days_to_failure': [220, 160, 100, 60, 30]
    })
    model = LinearRegression()
    model.fit(hist[['mileage']], hist['days_to_failure'])
    return model

def apply_predictive(df: pd.DataFrame) -> List[Dict]:
    """
    Applies predictive model to input train DataFrame.
    Args:
        df (pd.DataFrame): Input dataset with 'id', 'route', 'mileage' columns.
    Returns:
        List[Dict]: Prediction results including predicted_days and status label.
    """
    # Clean column names: lowercase, remove spaces
    df = df.rename(columns=lambda x: x.strip().lower())

    df2 = df.copy()
    df2['mileage'] = pd.to_numeric(df2['mileage'], errors='coerce').fillna(0)

    # Train predictive model
    model = predictive_model()
    preds = model.predict(df2[['mileage']])

    # Avoid negative predictions
    preds = np.maximum(preds, 0)
    df2['predicted_days'] = preds

    # Assign status labels
    def status_label(days: float) -> str:
        if days < 30:
            return "Critical"
        elif days < 90:
            return "Warning"
        return "Safe"

    df2['status'] = df2['predicted_days'].apply(status_label)

    # Return relevant columns as JSON-serializable list
    return df2[['id', 'route', 'mileage', 'predicted_days', 'status']].to_dict(orient='records')
