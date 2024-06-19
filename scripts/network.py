import pandas as pd
from pyvis.network import Network

# Load the classified CSV data
file_path = r'subreddits_datafiles\processed_datafiles_sentiment\classified_sentiment_all_subreddits_data.csv'
df = pd.read_csv(file_path)

# Define the political parties and their synonyms
party_synonyms = {
    'ÖVP': ['ÖVP', 'OEVP'],
    'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche'],
    'Grüne': ['Grüne', 'Gruene'],
    'SPÖ': ['SPÖ', 'SPOE'],
    'Neos': ['Neos']
}

# Define topics
topics = ['climate', 'migration', 'economy', 'health', 'education']

# Process the data to create separate network graphs for each topic
for topic in topics:
    net = Network(height='750px', width='100%', notebook=True)
    
    # Add nodes for each party
    for party in party_synonyms.keys():
        net.add_node(party, label=party)
    
    topic_df = df[df['classified_topic'] == topic]
    for party1 in party_synonyms.keys():
        for party2 in party_synonyms.keys():
            if party1 != party2:
                count1 = topic_df[topic_df['keyword'].isin(party_synonyms[party1])].shape[0]
                count2 = topic_df[topic_df['keyword'].isin(party_synonyms[party2])].shape[0]
                if count1 > 0 and count2 > 0:
                    weight = (count1 + count2) / 2
                    net.add_edge(party1, party2, value=weight, title=f"Topic: {topic}, Weight: {weight}")

    # Save and show the graph for the current topic
    net.show(f'political_topics_network_{topic}.html')
