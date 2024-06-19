import pandas as pd
from pyvis.network import Network

# Load the classified CSV data
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

# Define topics
topics = ['climate', 'migration', 'economy', 'health', 'education']

# Group by post_id and concatenate keywords
df_grouped = df.groupby('post_id')['keyword'].apply(lambda x: ' '.join(x)).reset_index()

# Process the data to create separate network graphs for each topic
for topic in topics:
    net = Network(height='750px', width='100%', notebook=True)
    
    # Add nodes for each party
    for party in party_synonyms.keys():
        net.add_node(party, label=party, title=f"Party: {party}")
    
    topic_df = df[df['classified_topic'] == topic]
    topic_grouped = topic_df.groupby('post_id')['keyword'].apply(lambda x: ' '.join(x)).reset_index()
    
    # Iterate through all pairs of parties to count co-occurrences
    for party1 in party_synonyms.keys():
        for party2 in party_synonyms.keys():
            if party1 != party2:
                count = 0
                for post in topic_grouped.itertuples():
                    keywords = post.keyword.split()
                    if any(synonym in keywords for synonym in party_synonyms[party1]) and \
                       any(synonym in keywords for synonym in party_synonyms[party2]):
                        count += 1
                if count > 0:
                    net.add_edge(party1, party2, value=count, title=f"Topic: {topic}, Co-occurrence: {count}")

    # Add legend to explain colors and thickness
    legend_html = """
    <div style="position: absolute; right: 10px; top: 10px; background-color: white; padding: 10px; border: 1px solid black;">
        <h3>Legend</h3>
        <p><b>Node:</b> Political Party</p>
        <p><b>Edge Thickness:</b> Frequency of Co-occurrence</p>
        <p>Thicker edges represent more frequent co-occurrences of mentions between the parties in the same posts.</p>
    </div>
    """
    net.html += legend_html

    # Save and show the graph for the current topic
    net.show(f'political_topics_network_{topic}.html')
