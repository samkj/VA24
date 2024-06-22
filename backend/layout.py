import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import pandas as pd
import json
from dash import dcc, html
import plotly.graph_objects as go
from services.data_service import data_dropdown_Party

# Load map data
with open('backend/data/map_data/oesterreich.json') as f:
    map_data = json.load(f)

features = map_data['features']
states = [feature['properties']['name'] for feature in features]
state_colors = {state: color for state, color in zip(states, px.colors.qualitative.Plotly)}

# Create a DataFrame
map_df = pd.DataFrame({'state': states})

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

# Create dropdown menu
dropdown_menu = dcc.Dropdown(
    id='navbar-dropdown',
    options=[{'label': option['label'], 'value': option['value']} for option in data_dropdown_Party()],
    value='All',  # default value
    style={'width': '300px'},
    multi=True
)

# Create navbar and add the dropdown menu
navbar = dbc.Navbar(
    dbc.Container(
        dbc.Nav(
            [dropdown_menu],
            className="ml-auto",
            navbar=True,
        )
    ),
    color="dark",
    dark=True,
)

# Add a DataTable to the layout
datatable = dash_table.DataTable(
    id='sentiment-table',
    columns=[{'name': i, 'id': i} for i in ['author_name', 'title', 'comment_body']],
    data=[],
    style_table={'overflowX': 'auto'},  # Hide the table by default
    style_header={
        'backgroundColor': 'rgba(0, 116, 217, 0.3)',
        'border': '1px solid rgb(0, 116, 217)'
    },
    style_cell={
        'textAlign': 'left',
        'maxHeight': '500px',
        'whiteSpace': 'no-wrap',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    },
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
)


def create_layout():
    # Layout structure
    layout = html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div([
            html.H1("Reddit Austrian Politics Analysis"),
            html.Div(id='map-wrapper', children=[
                dcc.Graph(id='map', figure=fig)
            ]),
            html.Div(id='sentiment-card'),  # sentiment polar chart placeholder
            html.Div(id='sentiment-table-container', children=[
                datatable
            ]),
            dcc.Graph(id='wordcloud-graph'),
            dcc.Store(id='store'),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            ),
            dcc.Tabs(id='topic-tabs', value='climate', children=[
                dcc.Tab(label='Climate', value='climate'),
                dcc.Tab(label='Migration', value='migration'),
                dcc.Tab(label='Economy', value='economy'),
                dcc.Tab(label='Health', value='health'),
                dcc.Tab(label='Education', value='education'),
            ]),
            html.Div(id='tabs-content'),
            html.Iframe(srcDoc=open('topics_parties_network.html', 'r').read(), width='100%', height='750px'),
            dcc.Checklist(
                id='state-checklist',
                options=[{'label': state, 'value': state} for state in states],
                value=[state for state in states],  # All states selected by default
                inline=True
            ),
            dcc.Slider(
                id='date-slider',
                min=2019,
                max=2023,
                step=1,
                value=2020,
                marks={i: f'{i}' for i in range(2019, 2024)}
            ),
            dcc.Graph(id='sentiment-piecharts', figure=go.Figure())
        ], style={'max-width': '1200px', 'margin': '0 auto'})  # Center the layout
    ])
    return layout
