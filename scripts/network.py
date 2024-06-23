import pandas as pd
from pyvis.network import Network

# Load 
file_path = r'subreddits_datafiles/processed_datafiles_sentiment/classified_sentiment_all_subreddits_data.csv'
df = pd.read_csv(file_path)

# Define the political parties and their synonyms
party_synonyms = {
    'ÖVP': ['ÖVP', 'OEVP', 'Volkspartei', 'Schwarz', 'Schwarzen'],
    'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche', 'Blau'],
    'Grüne': ['Grüne', 'Gruene', 'Die Grünen'],
    'SPÖ': ['SPÖ', 'SPOE', 'Sozialdemokratische Partei Österreichs', 'Sozialdemokraten', 'Roten', 'Rot'],
    'Neos': ['Neos', 'NEOS', 'Neue Österreich', 'Liberales Forum', 'Pink', 'Pinken']
}

# Define topics and their corresponding colors
topics = {
    'climate': 'gray',
    'migration': 'gray',
    'economy': 'gray',
    'health': 'gray',
    'education': 'gray'
}

# Define colors for parties
party_colors = {
    'ÖVP': 'black',
    'FPÖ': 'blue',
    'Grüne': 'green',
    'SPÖ': 'red',
    'Neos': 'pink'
}

# Create the network graph
net = Network(height='750px', width='100%', notebook=True)

# Add nodes for each topic with increased margin
topic_x = -200
topic_y = 0
for topic, color in topics.items():
    net.add_node(topic, label=topic, color=color, title=f"Topic: {topic}", x=topic_x, y=topic_y, fixed=True)
    topic_x += 100  
# Add nodes for each party with increased margin
party_x = -200
party_y = -200
for party, color in party_colors.items():
    net.add_node(party, label=party, color=color, title=f"Party: {party}", x=party_x, y=party_y, fixed=True)
    party_x += 100  # Increase the margin between nodes

# Iterate through each topic and party to create edges based on co-occurrence
for topic in topics.keys():
    topic_df = df[df['classified_topic'] == topic]
    for party, synonyms in party_synonyms.items():
        count = topic_df[topic_df['keyword'].isin(synonyms)].shape[0]
        if count > 0:
            net.add_edge(topic, party, value=count, title=f"Topic: {topic}, Party: {party}, Co-occurrence: {count}", color=party_colors[party])


net.show('topics_parties_network.html')
