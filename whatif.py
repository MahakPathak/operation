import pandas as pd
from typing import List, Dict

def _branding_to_num(s: str) -> int:
    """
    Convert branding categories to numeric scores.
    Defaults to 1 (Low) if unrecognized.
    """
    mapping = {"Low": 1, "Medium": 2, "High": 3}
    return mapping.get(str(s).strip(), 1)

def what_if(
    df: pd.DataFrame,
    k: int = 10,
    branding_weight: float = 2000,
    stabling_weight: float = 5
) -> List[Dict]:
    """
    Perform a 'what-if' analysis on train dataset.
    Calculates a score based on mileage, branding, and stabling position.

    Args:
        df (pd.DataFrame): Input dataset containing train details.
        k (int): Number of top trains to select.
        branding_weight (float): Weight factor for branding.
        stabling_weight (float): Weight factor for stabling position.

    Returns:
        List[Dict]: Top-k trains with selected columns and calculated score.
    """
    df2 = df.copy()

    # Ensure numeric columns
    df2['mileage'] = pd.to_numeric(df2['mileage'], errors='coerce').fillna(0)
    df2['stabling_pos'] = pd.to_numeric(df2['stabling_pos'], errors='coerce').fillna(1)

    # Convert branding to numeric
    df2['branding_num'] = df2['branding'].apply(_branding_to_num)

    # Compute score for what-if analysis
    df2['score'] = df2['mileage'] - (branding_weight * df2['branding_num']) + \
                   (stabling_weight * (df2['stabling_pos'] - 1).abs())

    # Select top-k trains
    selected = df2.sort_values('score', ascending=False).head(min(k, len(df2)))

    # Return relevant columns as JSON-serializable list
    return selected[['id', 'fitness', 'job_card_open', 'branding', 'mileage',
                     'cleaning_due', 'stabling_pos', 'score']].to_dict(orient='records')
