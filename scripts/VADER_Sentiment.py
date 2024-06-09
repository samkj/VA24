from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from tqdm import tqdm

def perform_sentiment_analysis(input_csv, output_csv):
    data = pd.read_csv(input_csv)
    data = data.dropna(subset=['comment_body'])
    data['comment_body'] = data['comment_body'].astype(str)
    vader = SentimentIntensityAnalyzer()

    data["VADER_compound"] = 0.0
    for i in tqdm(range(len(data['comment_body'])), desc="Analyzing Sentiments"):
        sentiment_dict = vader.polarity_scores(data['comment_body'][i])
        data["VADER_compound"][i] = float(sentiment_dict['compound'])

    data["VADER_class"] = ""
    for i in range(len(data['VADER_compound'])):
        compound_score = data['VADER_compound'][i]
        if compound_score > 0.5:
            data["VADER_class"][i] = "Positive"
        elif compound_score < -0.5:
            data["VADER_class"][i] = "Negative"
        else:
            data["VADER_class"][i] = "Neutral"

    sentiment_percentage = data["VADER_class"].value_counts(normalize=True) * 100
    print("Sentiment Percentage:")
    print(sentiment_percentage)

    mean_sentiments = data.groupby('VADER_class')['VADER_compound'].mean()
    print("Mean Sentiments:")
    print(mean_sentiments)

    data = data[data['VADER_compound'] != 0]
    data.to_csv(output_csv, index=False)

perform_sentiment_analysis(input_csv=r"C:\Stefan\Uni Graz\Master\VU Visual Analytics\Group Project\subreddits_datafiles\austria_politik_posts.csv", output_csv=r"C:\Stefan\Uni Graz\Master\VU Visual Analytics\Group Project\processed_datafiles_sentiment\austria_politik_posts_sentiment - Kopie.csv")
