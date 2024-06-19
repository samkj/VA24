import pandas as pd
from transformers import pipeline

# Load the CSV data
file_path = r'subreddits_datafiles\processed_datafiles_sentiment\sentiment_all_subreddits_data.csv'
df = pd.read_csv(file_path)

# Load zero-shot classification model
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

# Define topics
topics = ['climate', 'migration', 'economy', 'health', 'education']

# Preprocess and classify posts
def classify_topic(texts, topics):
    try:
        results = classifier(texts, topics)
        return [result['labels'][0] for result in results]
    except Exception as e:
        print(f"Error classifying text: {e}")
        return [None] * len(texts)

# Create a column for classified topics
df['classified_topic'] = None

batch_size = 10
for i in range(0, len(df), batch_size):
    batch_texts = df['cleaned_comment_body'].iloc[i:i+batch_size].tolist()
    classified_topics = classify_topic(batch_texts, topics)
    df.loc[i:i+batch_size-1, 'classified_topic'] = classified_topics
    print(f"Processed {i+batch_size}/{len(df)} posts")

# Save the dataframe with classified topics to a new CSV file
output_file_path = r'subreddits_datafiles\processed_datafiles_sentiment\classified_sentiment_all_subreddits_data.csv'
df.to_csv(output_file_path, index=False)
print(f"Classified topics saved to {output_file_path}")
