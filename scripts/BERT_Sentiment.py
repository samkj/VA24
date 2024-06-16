from transformers import pipeline
import pandas as pd
from tqdm import tqdm
from pathlib import Path

def analyze_sentiments(input_csv, output_csv, state_output_dir, model_name="ssary/XLM-RoBERTa-German-sentiment", max_token_length=512):
    sentiment_pipeline = pipeline(model=model_name)
    
    Reddit_data = pd.read_csv(input_csv)

    Reddit_data['BERT_class'] = "Neutral"
    Reddit_data['BERT_Compound'] = 0.0
    Reddit_data['BERT_label'] = 0.0

    for i in tqdm(range(len(Reddit_data['comment_body'])), desc="Processing Sentiments"):
        comment = Reddit_data['comment_body'][i][:max_token_length] 
        sentiment_dict = sentiment_pipeline(comment)
        Reddit_data.loc[i, 'BERT_class'] = sentiment_dict[0]['label'].upper()
        Reddit_data.loc[i, 'BERT_Compound'] = sentiment_dict[0]['score']
        
        if Reddit_data.loc[i, 'BERT_class'] == 'POSITIVE':
            Reddit_data.loc[i, 'BERT_label'] = 3.0 - Reddit_data.loc[i, 'BERT_Compound']
        elif Reddit_data.loc[i, 'BERT_class'] == 'NEUTRAL':
            Reddit_data.loc[i, 'BERT_label'] = 2.0 - float(Reddit_data.loc[i, 'BERT_Compound'])
        elif Reddit_data.loc[i, 'BERT_class'] == 'NEGATIVE':
            Reddit_data.loc[i, 'BERT_label'] = 1.0 - float(Reddit_data.loc[i, 'BERT_Compound'])

    Reddit_data = Reddit_data[Reddit_data['BERT_Compound'] != 0.0]
    
    # Save the result to the output CSV file
    Reddit_data.to_csv(output_csv, index=False)

    # Save the result to individual state CSV files
    state_groups = Reddit_data.groupby('state')
    for state, group in state_groups:
        state_output_file = Path(state_output_dir) / f"{state.lower()}_politik_posts_sentiment.csv"
        group.to_csv(state_output_file, index=False)

    data = pd.read_csv(output_csv)

    sentiment_percentage = data["BERT_class"].value_counts(normalize=True) * 100
    print("Sentiment Percentage:")
    print(sentiment_percentage)

    mean_sentiments = data.groupby('BERT_class')['BERT_label'].mean()
    print("Mean Sentiments:")
    print(mean_sentiments)

analyze_sentiments(
    input_csv='subreddits_datafiles/processed_datafiles/cleaned_data1.csv', 
    output_csv='subreddits_datafiles/processed_datafiles_sentiment/sentiment_all_subreddits_data.csv',
    state_output_dir='subreddits_datafiles/processed_datafiles_sentiment'
)
