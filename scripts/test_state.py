from typing import List, Tuple
import pandas as pd

# parse the 'subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv' and load the data into a pandas DataFrame
#     and put all the state and subreddit data into a set to see the unique values
#     file_path = 'subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv'

def load_data(file_path: str) -> pd.DataFrame:
    """
    This function loads the data from a .csv file and returns it as a pandas DataFrame.
    """
    df = pd.read_csv(file_path, parse_dates=['post_date'])  # Ensure post_date is parsed as datetime
    return df


def check_unique_values(file_path: str):
    df = pd.read_csv(file_path)
    state_set = set(df['state'])
    subreddit_set = set(df['subreddit'])
    return state_set, subreddit_set

if __name__ == '__main__':
    file_path = f'subreddits_datafiles/all data_sentiment/austria_politik_all_posts_sentiment.csv'
    state_set, subreddit_set = check_unique_values(file_path)
    print(state_set)
    print(subreddit_set)