import pandas as pd

def _branding_to_num(s):
    """
    Convert branding categories to numeric scores.
    Defaults to 1 (Low) if unrecognized.
    """
    mapping = {"Low": 1, "Medium": 2, "High": 3}
    return mapping.get(str(s).strip(), 1)

def optimize_trains(df: pd.DataFrame, k: int = 10):
    """
    Optimizer that prefers High branding strongly.
    Score = (100000 * branding_num) + mileage - penalty for stabling position.
    
    Args:
        df (pd.DataFrame): Input train dataset containing 'branding', 'mileage', 'stabling_pos'.
        k (int): Number of top trains to select.

    Returns:
        List[Dict]: Top-k trains with selected columns: id, branding, mileage, score.
    """
    df2 = df.copy()

    # Ensure numeric columns are valid
    df2['mileage'] = pd.to_numeric(df2['mileage'], errors='coerce').fillna(0)
    df2['stabling_pos'] = pd.to_numeric(df2['stabling_pos'], errors='coerce').fillna(1)

    # Convert branding to numeric
    df2['branding_num'] = df2['branding'].apply(_branding_to_num)

    # Compute score with strong preference for branding
    df2['score'] = (100000 * df2['branding_num']) + df2['mileage'] - (5 * (df2['stabling_pos'] - 1).abs())

    # Select top-k trains
    selected = df2.sort_values('score', ascending=False).head(min(k, len(df2)))

    # Return as JSON-serializable list of dicts
    return selected[['id', 'branding', 'mileage', 'score']].to_dict(orient='records')
