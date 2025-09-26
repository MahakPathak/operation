import pandas as pd
from typing import Any

def apply_rules(row: pd.Series) -> pd.Series:
    """
    Determine the status and alerts for a single train row.

    Status:
        - "Eligible" if no alerts
        - "Blocked" if any alerts exist

    Alerts:
        - Semi-colon separated string describing issues

    Args:
        row (pd.Series): Input row from train dataset

    Returns:
        pd.Series: [status, alerts]
    """
    alerts = []

    # Check fitness
    try:
        if int(row.get('fitness', 1)) == 0:
            alerts.append("Fitness Expired")
    except (ValueError, TypeError):
        pass

    # Check job card
    try:
        if int(row.get('job_card_open', 0)) == 1:
            alerts.append("Open Job Card")
    except (ValueError, TypeError):
        pass

    # Check cleaning
    try:
        if int(row.get('cleaning_due', 0)) == 1:
            alerts.append("Cleaning Due")
    except (ValueError, TypeError):
        pass

    status = "Eligible" if not alerts else "Blocked"

    return pd.Series([status, "; ".join(alerts)], index=['status', 'alerts'])
