import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter


party_synonyms = {
        'ÖVP': ['ÖVP', 'OEVP', 'Volkspartei', 'Schwarz', 'Schwarzen'],
        'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche', 'Blau'],
        'Grüne': ['Grüne', 'Gruene', 'Die Grünen'],
        'SPÖ': ['SPÖ', 'SPOE', 'Sozialdemokratische Partei Österreichs', 'Sozialdemokraten', 'Roten', 'Rot'],
        'Neos': ['Neos', 'NEOS', 'Neue Österreich', 'Liberales Forum', 'Pink', 'Pinken']
    }


def load_data(file_path: str) -> pd.DataFrame:
    """
    This function loads the data from a .csv file and returns it as a pandas DataFrame.
    """
    df = pd.read_csv(file_path, parse_dates=['post_date'])  # Ensure post_date is parsed as datetime
    return df


def get_posts_by_state(state, start_date=None, end_date=None):
    # file_path = f'subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv'
    file_path = f'subreddits_datafiles/all data_sentiment/austria_politik_all_posts_sentiment.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame()  

    #if start_date and end_date:
        #df = df[(df['post_date'] >= start_date) & (df['post_date'] <= end_date)]
    return df[df['state'] == state]
    
    # return df


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


def load_sentiment_data(state: str, filter, selected_year) -> pd.DataFrame:
    """
    This function loads the sentiment data for a given state from a .csv file and returns it as a pandas DataFrame.
    """
    # print("Selected Year", selected_year)
    # print("State", state)
    # print("Filter", filter)
    file_path = f'subreddits_datafiles/all data_sentiment/austria_politik_all_posts_sentiment.csv'
    # print("SENTIMENT File Path", file_path)

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Convert the 'post_date' column to datetime
    df['post_date'] = pd.to_datetime(df['post_date'])

    # Filter the data based on the selected year
    df = df[df['post_date'].dt.year <= selected_year]
    # print(df.columns)

    if state:
        print("State is not None")
        if state == 'Niederoesterreich':
            state = 'Niederösterreich'
        elif state == 'Oberoesterreich':
            state = 'Oberösterreich'
        df = get_posts_by_state(state)
        # print(df.head(5))  # Print the DataFrame for debugging
    else:
        # print("State is None")
        df = df

    # Parties can be multiple, so we need to filter the data based on the selected parties
    if filter != ['All']:
        print("Not All Party in sentiment data")
        # filter also for the synonyms of the parties
        filter = [party for party in party_synonyms if party in filter]
        df = df[df['comment_keyword'].isin(filter)]
        # print("HAHAHHAHHAH")
        # print(df.head(5))  # Print the DataFrame for debugging
    else:
        print("All Party in sentiment data")
        df = df

    # print("HAHAHHAHHAH")
    return df


def load_wordcloud_data(city: str, party, selected_year) -> dict:
    """
    This function loads the word cloud data for a given city and party from a .csv file and returns it as a pandas DataFrame.
    """
    print("load_wordcloud_data Year", selected_year)
    print("load_wordcloud_data Party", party)
    print("load_wordcloud_data City", city)
    file_path = f'subreddits_datafiles/all data_sentiment/austria_politik_all_posts_sentiment.csv'
    df = pd.read_csv(file_path)
    # Convert the 'post_date' column to datetime
    df['post_date'] = pd.to_datetime(df['post_date'])

    # Filter the data based on the selected year
    df = df[df['post_date'].dt.year <= selected_year]

    if city:
        print("City is not None")
        # if Niederoesterreich -> Niederösterreich and same for Oberoesterreich
        if city == 'Niederoesterreich':
            city = 'Niederösterreich'
        elif city == 'Oberoesterreich':
            city = 'Oberösterreich'
        df = get_posts_by_state(city)
        print(df.head(5))
    else:
        print("City is None")
        df = df

    # make sure that party is a list
    if not isinstance(party, list):
        party = [party]
    # parties can be multiple, so we need to filter the data based on the selected parties
    if party != ['All']:
        print("Not All Party")
        filter = [parties for parties in party_synonyms if parties in party]
        df = df[df['comment_keyword'].isin(filter)]
        print(df.shape)
    else:
        print("All Party")
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


def query_sentiment_data(sentiment: str, filter) -> pd.DataFrame:
    """
    This function queries the sentiment data for a given sentiment and party from a .csv file and returns it as a pandas DataFrame.
    """
    # print("query_sentiment_data", sentiment)
    # print("query_sentiment_data", filter)
    file_path = f'subreddits_datafiles/all data_sentiment/austria_politik_all_posts_sentiment.csv'
    # Load the sentiment data from a CSV file
    df = pd.read_csv(file_path)

    # Filter the data based on the selected sentiment
    df = df[df['BERT_class'] == sentiment.upper()]

    # As parties can be multiple, we need to filter
    # the data based on the selected parties
    if filter != ['All']:
        filter = [party for party in party_synonyms if party in filter]
        df = df[df['comment_keyword'].isin(filter)]
    else:
        df = df

    print("INSIDE query_sentiment_data--", df.describe())

    return df[['author_name', 'title', 'comment_body']]