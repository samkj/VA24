import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    dcc.Tabs(id='topic-tabs', value='climate', children=[
        dcc.Tab(label='Climate', value='climate'),
        dcc.Tab(label='Migration', value='migration'),
        dcc.Tab(label='Economy', value='economy'),
        dcc.Tab(label='Health', value='health'),
        dcc.Tab(label='Education', value='education'),
    ]),
    html.Div(id='tabs-content'),
    html.Iframe(srcDoc=open('topics_parties_network.html', 'r').read(), width='100%', height='750px')
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
        'ÖVP': ['ÖVP', 'OEVP', 'Volkspartei', 'Schwarz', 'Schwarzen'],
        'FPÖ': ['FPÖ', 'FPOE', 'Blaue', 'Blauen', 'Freiheitliche', 'Blau'],
        'Grüne': ['Grüne', 'Gruene', 'Die Grünen'],
        'SPÖ': ['SPÖ', 'SPOE', 'Sozialdemokratische Partei Österreichs', 'Sozialdemokraten', 'Roten', 'Rot'],
        'Neos': ['Neos', 'NEOS', 'Neue Österreich', 'Liberales Forum', 'Pink', 'Pinken']
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
            go.Pie(
                labels=['Negative', 'Neutral', 'Positive'], 
                values=sentiments, 
                name=party,
                marker=dict(colors=['red', 'gray', 'green'])
            ),
            row=1, col=i+1
        )

    fig.update_layout(title_text='Sentiment Distribution for Selected States by Party', showlegend=False)
    return fig

@app.callback(
    Output('tabs-content', 'children'),
    Input('topic-tabs', 'value')
)
def render_content(tab):
    return html.Iframe(srcDoc=open(f'political_topics_network_{tab}.html', 'r').read(), width='100%', height='750px')

if __name__ == '__main__':
    app.run_server(debug=True)
