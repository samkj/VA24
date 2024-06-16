import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from services.data_service import get_posts_by_state  # Assuming data_service.py is in the same directory

app = dash.Dash(__name__)

# Read GeoJSON data
with open('backend/map_data/oesterreich.json') as f:
    map_data = json.load(f)

# Extract features
features = map_data['features']

# Extract state names and geometries
states = []
geometries = []
for feature in features:
    states.append(feature['properties']['name'])
    geometries.append(feature['geometry'])

state_colors = {state: color for state, color in zip(states, px.colors.qualitative.Plotly)}

# Create a DataFrame
map_df = pd.DataFrame({'state': states, 'geometry': geometries, 'color': [state_colors[state] for state in states]})

fig = px.choropleth_mapbox(
    map_df,
    geojson=map_data,
    locations='state',
    color='state',
    featureidkey="properties.name",
    color_discrete_map=state_colors,
    mapbox_style="carto-positron",
    center={"lat": 47.5162, "lon": 14.5501},
    zoom=6,
    labels={'color': 'state'}
)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

app.layout = html.Div([
    html.H1("Reddit Austrian Politics Analysis"),
    dcc.Graph(id='map', figure=fig),
    dcc.Checklist(
        id='state-checklist',
        options=[{'label': state, 'value': state} for state in states],
        value=[],
        inline=True
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=datetime(2018, 1, 1),
        end_date=datetime(2025, 12, 31),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='sentiment-piecharts', figure=go.Figure()),
    dcc.Slider(
        id='date-slider',
        min=0,
        max=12,
        value=0,
        marks={i: f'Month {i + 1}' for i in range(12)}
    ),
    dcc.Graph(id='network-graph', figure=go.Figure())
])

@app.callback(
    Output('sentiment-piecharts', 'figure'),
    Input('state-checklist', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_sentiment_piecharts(selected_states, start_date, end_date):
    if not selected_states:
        return go.Figure()

    party_synonyms = {
        'ÖVP': ['ÖVP', 'OEVP'],
        'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche'],
        'Grüne': ['Grüne', 'Gruene'],
        'SPÖ': ['SPÖ', 'SPOE'],
        'Neos': ['Neos']
    }
    fig = make_subplots(
        rows=1, 
        cols=len(party_synonyms), 
        subplot_titles=list(party_synonyms.keys()),
        specs=[[{'type': 'pie'} for _ in party_synonyms]]  # Specify that each subplot should be a pie chart
    )

    combined_df = pd.concat([get_posts_by_state(state, start_date, end_date) for state in selected_states])
    if combined_df.empty:
        return go.Figure()

    for i, (party, synonyms) in enumerate(party_synonyms.items()):
        party_df = combined_df[combined_df['keyword'].isin(synonyms)]
        sentiments = party_df['BERT_class'].value_counts(normalize=True) * 100
        sentiments = [sentiments.get('NEGATIVE', 0), sentiments.get('NEUTRAL', 0), sentiments.get('POSITIVE', 0)]

        fig.add_trace(
            go.Pie(labels=['Negative', 'Neutral', 'Positive'], values=sentiments, name=party),
            row=1, col=i+1
        )

    fig.update_layout(title_text='Sentiment Distribution for Selected States by Party', showlegend=False)
    return fig

@app.callback(
    Output('network-graph', 'figure'),
    Input('state-checklist', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_network_graph(selected_states, start_date, end_date):
    if not selected_states:
        return go.Figure()

    topics = ['climate', 'migration', 'economy', 'health', 'education']
    party_synonyms = {
        'ÖVP': ['ÖVP', 'OEVP'],
        'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche'],
        'Grüne': ['Grüne', 'Gruene'],
        'SPÖ': ['SPÖ', 'SPOE'],
        'Neos': ['Neos']
    }

    combined_df = pd.concat([get_posts_by_state(state, start_date, end_date) for state in selected_states])
    if combined_df.empty:
        return go.Figure()

    G = nx.Graph()
    for party, synonyms in party_synonyms.items():
        G.add_node(party)

    for topic in topics:
        topic_df = combined_df[combined_df['keyword'].str.contains(topic, case=False, na=False)]
        for party1 in party_synonyms.keys():
            for party2 in party_synonyms.keys():
                if party1 != party2:
                    count1 = topic_df[topic_df['keyword'].isin(party_synonyms[party1])].shape[0]
                    count2 = topic_df[topic_df['keyword'].isin(party_synonyms[party2])].shape[0]
                    if count1 > 0 and count2 > 0:
                        sentiment1 = topic_df[topic_df['keyword'].isin(party_synonyms[party1])]['BERT_class'].value_counts(normalize=True)
                        sentiment2 = topic_df[topic_df['keyword'].isin(party_synonyms[party2])]['BERT_class'].value_counts(normalize=True)
                        G.add_edge(party1, party2, weight=(count1 + count2) / 2,
                                   sentiment1=sentiment1, sentiment2=sentiment2)

    pos = nx.spring_layout(G, k=0.5)
    edge_trace = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2]['weight']
        sentiment1 = edge[2]['sentiment1']
        sentiment2 = edge[2]['sentiment2']
        edge_trace.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=weight, color='gray'),
            hoverinfo='text',
            mode='lines',
            text=f"Sentiment {edge[0]}: {sentiment1}\nSentiment {edge[1]}: {sentiment2}"
        ))

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

    fig = go.Figure(data=edge_trace + [node_trace],
                    layout=go.Layout(
                        title='Network Graph of Political Topics with Sentiment',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
