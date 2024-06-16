import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import spacy
from transformers import pipeline

# Load the CSV data
file_path = r'subreddits_datafiles\processed_datafiles_sentiment\sentiment_all_subreddits_data.csv'
df = pd.read_csv(file_path)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Load topic classification model with increased timeout
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli', device=0, timeout=600)

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

# Initialize the graph
G = nx.Graph()

# Add nodes for each party
for party in party_synonyms.keys():
    G.add_node(party)

# Preprocess and classify posts
def classify_topic(text, topics):
    try:
        result = classifier(text, topics)
        return result['labels'][0]
    except Exception as e:
        print(f"Error classifying text: {e}")
        return None

# Create a column for classified topics
df['classified_topic'] = None

# Classify topics with progress indication
for i, text in enumerate(df['cleaned_comment_body']):
    if pd.notnull(text):
        df.at[i, 'classified_topic'] = classify_topic(text, topics)
    if i % 100 == 0:
        print(f"Processed {i+1}/{len(df)} posts")

# Debug: Print some classified topics
print(df[['cleaned_comment_body', 'classified_topic']].head())

# Process the data to add edges based on classified topic connections
for topic in topics:
    topic_df = df[df['classified_topic'] == topic]
    for party1 in party_synonyms.keys():
        for party2 in party_synonyms.keys():
            if party1 != party2:
                count1 = topic_df[topic_df['keyword'].isin(party_synonyms[party1])].shape[0]
                count2 = topic_df[topic_df['keyword'].isin(party_synonyms[party2])].shape[0]
                if count1 > 0 and count2 > 0:
                    weight = (count1 + count2) / 2
                    G.add_edge(party1, party2, weight=weight, topic=topic)

# Create positions for the nodes in the graph
pos = nx.spring_layout(G, k=0.5)

# Create edge traces
edge_trace = []
for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    weight = edge[2]['weight']
    topic = edge[2]['topic']
    edge_trace.append(go.Scatter(
        x=[x0, x1, None],
        y=[y0, y1, None],
        line=dict(width=weight, color='gray'),
        hoverinfo='text',
        mode='lines',
        text=f"Topic: {topic}, Weight: {weight}"
    ))

# Create node traces
node_trace = go.Scatter(
    x=[pos[node][0] for node in G.nodes()],
    y=[pos[node][1] for node in G.nodes()],
    text=[node for node in G.nodes()],
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        color='lightblue',
        size=10,
        line_width=2
    )
)

# Create the figure
fig = go.Figure(data=edge_trace + [node_trace],
                layout=go.Layout(
                    title='Network Graph of Political Topics with Sentiment',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, zeroline=False)
                ))

# Display the figure
fig.show()
