import pandas as pd
import matplotlib.pyplot as plt

# Corrected path to the CSV file
file_path = 'C:/Users/Niklas/OneDrive/Desktop/Master/VA24/out/sentiment_all_subreddits_data.csv'

def load_data(file_path):
    return pd.read_csv(file_path)

def filter_data_by_party(data, party_keywords):
    return data[data['cleaned_comment_body'].str.contains('|'.join(party_keywords), case=False, na=False)]

# Create subplots for sentiment percentages and mean sentiments
def plot_sentiments(party_sentiments, party_means, sentiment_counts):
    fig, axes = plt.subplots(nrows=2, ncols=len(party_sentiments), figsize=(20, 12))
    fig.suptitle('Sentiment Analysis', fontsize=16)

    sentiment_colors = {
        'POSITIVE': 'green',
        'NEGATIVE': 'red',
        'NEUTRAL': 'gray'
    }

    max_y = max([mean.max() for mean in party_means.values()])  # Find the maximum y-value for scaling

    for i, (party, sentiment_percentage) in enumerate(party_sentiments.items()):
        counts = sentiment_counts[party]
        labels = [f"{sentiment} ({counts.get(sentiment, 0)})" for sentiment in sentiment_percentage.index]
        colors = [sentiment_colors.get(sentiment, 'gray') for sentiment in sentiment_percentage.index]
        sentiment_percentage.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=colors, ax=axes[0, i], labels=labels)
        axes[0, i].set_title(f'{party}')
        axes[0, i].set_ylabel('')

    for i, (party, mean_sentiments) in enumerate(party_means.items()):
        colors = [sentiment_colors.get(sentiment, 'gray') for sentiment in mean_sentiments.index]
        mean_sentiments.plot(kind='bar', ax=axes[1, i], color=colors)
        axes[1, i].set_title(f'{party}')
        axes[1, i].set_xlabel('Class')
        axes[1, i].set_ylabel('Mean Score')
        axes[1, i].set_xticklabels(mean_sentiments.index, rotation=0)
        axes[1, i].set_ylim(0, max_y)  # Set the y-axis limit to the maximum value found

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('party_sentiments.png')
    plt.show()

if __name__ == "__main__":
    data = load_data(file_path)
    
    # Define party keywords with more variations
    party_keywords = {
        'OVP': ['ÖVP', 'OVP', 'Volkspartei', 'Oesterreichische Volkspartei'],
        'FPO': ['FPÖ', 'FPO', 'Freiheitlichen', 'Freiheitliche Partei Österreichs'],
        'Grune': ['Grüne', 'Grune', 'Grünen', 'Die Grünen', 'Gruenen'],
        'SPO': ['SPÖ', 'SPO', 'Sozialdemokratische Partei Österreichs', 'Sozialdemokraten'],
        'Neos': ['Neos', 'NEOS']
    }

    party_sentiments = {}
    party_means = {}
    sentiment_counts = {}

    for party, keywords in party_keywords.items():
        party_data = filter_data_by_party(data, keywords)
        
        # Calculate percentage for each sentiment class
        sentiment_percentage = party_data["BERT_class"].value_counts(normalize=True) * 100
        party_sentiments[party] = sentiment_percentage
        
        # Calculate mean for each sentiment class
        mean_sentiments = party_data.groupby('BERT_class')['BERT_label'].mean()
        party_means[party] = mean_sentiments
        
        # Count sentiments
        counts = party_data["BERT_class"].value_counts()
        sentiment_counts[party] = counts

    # Plot the combined charts
    plot_sentiments(party_sentiments, party_means, sentiment_counts)
