import pandas as pd
import matplotlib.pyplot as plt

# Absolute path to the CSV file
file_path = 'C:/Users/Niklas/OneDrive/Desktop/Master/VA24/out/sentiment_all_subreddits_data.csv'

def load_data(file_path):
    return pd.read_csv(file_path)

# Create a pie chart for sentiment percentages
def plot_sentiment_pie(sentiment_percentage):
    plt.figure(figsize=(8, 8))
    sentiment_percentage.plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('Sentiment Percentage')
    plt.ylabel('')  # Hide the y-label
    plt.savefig('sentiment_percentage_pie_chart.png')
    plt.show()

# Create a bar chart for mean sentiments
def plot_mean_sentiments(mean_sentiments):
    plt.figure(figsize=(10, 6))
    mean_sentiments.plot(kind='bar', color=['red', 'green'])
    plt.title('Mean Sentiments')
    plt.xlabel('Sentiment Class')
    plt.ylabel('Mean Sentiment Score')
    plt.xticks(rotation=0)
    plt.savefig('mean_sentiments_bar_chart.png')
    plt.show()

if __name__ == "__main__":
    data = load_data(file_path)
    # Calculate percentage for each sentiment class
    sentiment_percentage = data["BERT_class"].value_counts(normalize=True) * 100

    # Calculate mean for each sentiment class
    mean_sentiments = data.groupby('BERT_class')['BERT_label'].mean()

    # Plot the charts
    plot_sentiment_pie(sentiment_percentage)
    plot_mean_sentiments(mean_sentiments)
