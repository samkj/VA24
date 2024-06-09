from germansentiment import SentimentModel
#https://github.com/oliverguhr/german-sentiment-lib?tab=readme-ov-file
#https://huggingface.co/oliverguhr/german-sentiment-bert/tree/main
import pandas as pd
from tqdm import tqdm

def analyze_sentiments(input_csv, output_csv, max_token_length=512):
    sentiment_model = SentimentModel()
    
    Reddit_data = pd.read_csv(input_csv)

    Reddit_data['BERT_class'] = "Neutral"
    Reddit_data['BERT_Compound'] = 0.0
    Reddit_data['BERT_label'] = 0.0
    Reddit_data['Positive_Prob'] = 0.0
    Reddit_data['Neutral_Prob'] = 0.0
    Reddit_data['Negative_Prob'] = 0.0
    Reddit_data['Max_Prob_Class'] = "Neutral"

    for i in tqdm(range(len(Reddit_data['comment_body'])), desc="Processing Sentiments"):
        comment = Reddit_data['comment_body'][i][:max_token_length]
        classes, probabilities = sentiment_model.predict_sentiment([comment], output_probabilities=True)
        sentiment = classes[0]
        probs = probabilities[0]
        
        if sentiment == 'positive':
            Reddit_data['BERT_class'][i] = 'POSITIVE'
            Reddit_data['BERT_Compound'][i] = 1.0
        elif sentiment == 'neutral':
            Reddit_data['BERT_class'][i] = 'NEUTRAL'
            Reddit_data['BERT_Compound'][i] = 0.5
        elif sentiment == 'negative':
            Reddit_data['BERT_class'][i] = 'NEGATIVE'
            Reddit_data['BERT_Compound'][i] = 0.0
        
        Reddit_data['Positive_Prob'][i] = probs[0]
        Reddit_data['Neutral_Prob'][i] = probs[1]
        Reddit_data['Negative_Prob'][i] = probs[2]
        
        max_prob_index = probs.index(max(probs))
        max_prob_class = classes[max_prob_index]
        Reddit_data['Max_Prob_Class'][i] = max_prob_class

        if Reddit_data['BERT_class'][i] == 'POSITIVE':
            Reddit_data['BERT_label'][i] = 3.0 - Reddit_data['BERT_Compound'][i]
        elif Reddit_data['BERT_class'][i] == 'NEUTRAL':
            Reddit_data['BERT_label'][i] = 2.0 - Reddit_data['BERT_Compound'][i]
        elif Reddit_data['BERT_class'][i] == 'NEGATIVE':
            Reddit_data['BERT_label'][i] = 1.0 - Reddit_data['BERT_Compound'][i]

    Reddit_data = Reddit_data[Reddit_data['BERT_Compound'] != 0.0]
    
    Reddit_data.to_csv(output_csv, index=False)

    data = pd.read_csv(output_csv)

    sentiment_percentage = data["BERT_class"].value_counts(normalize=True) * 100
    print("Sentiment Percentage:")
    print(sentiment_percentage)

    mean_sentiments = data.groupby('BERT_class')['BERT_label'].mean()
    print("Mean Sentiments:")
    print(mean_sentiments)

analyze_sentiments(input_csv=r"C:\Stefan\Uni Graz\Master\VU Visual Analytics\Group Project\subreddits_datafiles\wien_politik_posts.csv", 
                   output_csv=r"C:\Stefan\Uni Graz\Master\VU Visual Analytics\Group Project\processed_datafiles_sentiment\wien_politik_posts_sentiment.csv")



# from germansentiment import SentimentModel
# import pandas as pd

# model = SentimentModel()

# data = pd.read_csv(r"C:\Stefan\Uni Graz\Master\VU Visual Analytics\Group Project\subreddits_datafiles\Salzburg_politik_posts.csv")
# data = data['comment_body']
# # result = model.predict_sentiment(data)
# # print(result)

# classes, probabilities = model.predict_sentiment(data, output_probabilities = True) 
# print(classes, probabilities)
