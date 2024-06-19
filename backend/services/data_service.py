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


def data_dropdown_Party() -> list:
    # hardcode the party ["ÖVP", "SPÖ", "FPÖ", "Grüne", "Neos"]
    return [
        {'label': 'All', 'value': 'All'},
        {'label': 'ÖVP', 'value': 'ÖVP'},
        {'label': 'SPÖ', 'value': 'SPÖ'},
        {'label': 'FPÖ', 'value': 'FPÖ'},
        {'label': 'Grüne', 'value': 'Grüne'},
        {'label': 'Neos', 'value': 'Neos'}
    ]

def load_sentiment_data(state: str, filter) -> pd.DataFrame:
    """
    This function loads the sentiment data for a given state from a .csv file and returns it as a pandas DataFrame.
    """
    print("State", state)
    print("Filter", filter)
    # Define the column names
    column_names = ["author_name","post_id","title","body","post_date","keyword","comment_author_name""",
                    "comment_id","comment_parent_id","comment_body","comment_score","comment_created_utc",
                    "comment_replies_count","comment_keyword","subreddit,state","cleaned_body",
                    "cleaned_comment_body","BERT_class","BERT_Compound","BERT_label"]
    state_prefix = 'austria_'
    if state == 'Steiermark':
        state_prefix = 'Stmk_'
    elif state == 'Niederoesterreich':
        state_prefix = 'Noesterreich_'
    elif state == 'Oberoesterreich':
        state_prefix = 'Linz_'
    elif state == 'Salzburg':
        state_prefix = 'Salzburg_'
    elif state == 'Tirol':
        state_prefix = 'Tirol_'
    elif state == 'Wien':
        state_prefix = 'wien_'

    # Construct the file path based on the state
    # file_path = f'subreddits_datafiles/processed_datafiles_sentiment/{state_prefix}politik_posts_sentiment.csv'
    temp_file_path = f'subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv'
    # print("File Path", file_path)

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(temp_file_path, names=column_names, header=None, skiprows=1)
    print(df.describe())
    # print(df.head(5))  # Print the DataFrame for debugging
    # if start_date and end_date:
    #     df = df[(df['post_date'] >= start_date) & (df['post_date'] <= end_date)]

    return df


def load_wordcloud_data(city: str, party: str) -> dict:
    """
    This function loads the word cloud data for a given city and party from a .csv file and returns it as a pandas DataFrame.
    """
    print("load_wordcloud_data Party", party)
    state_prefix = 'austria_'
    if city == 'Steiermark':
        state_prefix = 'Stmk_'
    elif city == 'Niederoesterreich':
        state_prefix = 'Noesterreich_'
    elif city == 'Oberoesterreich':
        state_prefix = 'Linz_'
    elif city == 'Salzburg':
        state_prefix = 'Salzburg_'
    elif city == 'Tirol':
        state_prefix = 'Tirol_'
    elif city == 'Wien':
        state_prefix = 'wien_'
    file_path = f'subreddits_datafiles/processed_datafiles_sentiment/{state_prefix}politik_posts_sentiment.csv'
    print("File Path", file_path)
    df = pd.read_csv(file_path)

    # Filter the data based on the selected party
    if party != 'All':
        df = df[df['comment_keyword'] == party]
    else:
        df = df

    # combine the title and body columns
    df['text'] = df['title'] + ' ' + df['comment_body']
    # Lowercase the text
    df['text'] = df['text'].str.lower()

    # Remove punctuation
    df['text'] = df['text'].str.translate(str.maketrans('', '', string.punctuation))

    # Remove stopwords
    stop_words = set(stopwords.words('german'))
    df['text'] = df['text'].apply(lambda x: ' '.join(word for word in x.split() if word not in stop_words))

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    df['text'] = df['text'].apply(lambda x: ' '.join(lemmatizer.lemmatize(word) for word in word_tokenize(x)))

    word_freq = Counter(' '.join(df['text']).split())
    return dict(word_freq)

def query_sentiment_data(sentiment: str) -> pd.DataFrame:
    """
    This function queries the sentiment data for a given sentiment and party from a .csv file and returns it as a pandas DataFrame.
    """
    # Load the sentiment data from a CSV file
    df = pd.read_csv('subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv')

    # Filter the data based on the selected sentiment
    # df = df[df['BERT_label'] == sentiment]
    # print(df.head(5))  # Print the DataFrame for debugging

    # Filter the data based on the selected party
    # if party != 'All':
    #     df = df[df['comment_keyword'] == party]

    return df[['author_name', 'title', 'comment_body', 'BERT_label', 'BERT_Compound']]