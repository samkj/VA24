import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """
    This function loads the data from a .csv file and returns it as a pandas DataFrame.
    """
    df = pd.read_csv(file_path, parse_dates=['post_date'])  # Ensure post_date is parsed as datetime
    return df

def get_posts_by_state(state, start_date=None, end_date=None):
    file_path = f'subreddits_datafiles/processed_datafiles_sentiment/{state}_politik_posts_sentiment.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File not found for state: {state}")
        return pd.DataFrame()  # Return an empty DataFrame if the file is not found

    if start_date and end_date:
        df = df[(df['post_date'] >= start_date) & (df['post_date'] <= end_date)]
    
    return df
