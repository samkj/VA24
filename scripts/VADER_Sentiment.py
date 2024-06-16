from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from tqdm import tqdm
from pathlib import Path

def perform_sentiment_analysis(input_csv, output_csv):
    data = pd.read_csv(input_csv)
    data = data.dropna(subset=['comment_body'])
    data['comment_body'] = data['comment_body'].astype(str)
    vader = SentimentIntensityAnalyzer()

    data["VADER_compound"] = 0.0
    for i in tqdm(range(len(data['comment_body'])), desc="Analyzing Sentiments"):
        sentiment_dict = vader.polarity_scores(data['comment_body'][i])
        data.loc[i, "VADER_compound"] = float(sentiment_dict['compound'])

    data["VADER_class"] = ""
    for i in range(len(data['VADER_compound'])):
        compound_score = data['VADER_compound'][i]
        if compound_score > 0.5:
            data.loc[i, "VADER_class"] = "Positive"
        elif compound_score < -0.5:
            data.loc[i, "VADER_class"] = "Negative"
        else:
            data.loc[i, "VADER_class"] = "Neutral"

    sentiment_percentage = data["VADER_class"].value_counts(normalize=True) * 100
    print("Sentiment Percentage:")
    print(sentiment_percentage)

    mean_sentiments = data.groupby('VADER_class')['VADER_compound'].mean()
    print("Mean Sentiments:")
    print(mean_sentiments)

    data = data[data['VADER_compound'] != 0]
    data.to_csv(output_csv, index=False)

def analyze_sentiments_for_all_states():
    files_states = {
        "burgenland_politik_posts.csv": "burgenland_politik_posts_sentiment.csv",
        "kaernten_politik_posts.csv": "kaernten_politik_posts_sentiment.csv",
        "linz_politik_posts.csv": "Linz_politik_posts_sentiment.csv",
        "niederoesterreich_politik_posts.csv": "Noesterreich_politik_posts_sentiment.csv",
        "salzburg_politik_posts.csv": "Salzburg_politik_posts_sentiment.csv",
        "steiermark_politik_posts.csv": "Stmk_politik_posts_sentiment.csv",
        "tirol_politik_posts.csv": "Tirol_politik_posts_sentiment.csv",
        "vorarlberg_politik_posts.csv": "Vorarlberg_politik_posts_sentiment.csv",
        "wien_politik_posts.csv": "wien_politik_posts_sentiment.csv",
        "austria_politik_posts.csv": "austria_politik_posts_sentiment.csv",
        "europe_politik_posts.csv": "europe_politik_posts_sentiment.csv"
    }

    for input_file, output_file in files_states.items():
        input_csv = Path.cwd() / "subreddits_datafiles/processed_datafiles" / input_file
        output_csv = Path.cwd() / "subreddits_datafiles/processed_datafiles_sentiment" / output_file

        if input_csv.exists():
            print(f"Processing {input_file}")
            perform_sentiment_analysis(input_csv, output_csv)
        else:
            print(f"File {input_csv} does not exist")

if __name__ == "__main__":
    analyze_sentiments_for_all_states()
