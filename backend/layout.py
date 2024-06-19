import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash import html
from dash import dash_table
import plotly.express as px
import pandas as pd
import json

from services.data_service import data_dropdown_Party


def create_layout() -> object:
    # Read GeoJSON data
    with open('backend/data/map_data/oesterreich.json') as f:
        map_data = json.load(f)

    # Extract features
    features = map_data['features']

    # Extract state names
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
    # create a dropdown menu
    dropdown_menu = dcc.Dropdown(
        id='navbar-dropdown',
        options=[{'label': option['label'], 'value': option['value']} for option in data_dropdown_Party()],
        value='All'  # default value
    )
    # create a navbarand add the dropdown menu
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
        columns=[{'name': i, 'id': i} for i in ['author_name', 'title', 'comment_body', 'BERT_label', 'BERT_Compound']],
        data=[
            # {'author_name': '-', 'title': '-', 'comment_body': '-', 'BERT_label': '-', 'BERT_Compound': '-'},
            # {'author_name': '-', 'title': '-', 'comment_body': '-', 'BERT_label': '-', 'BERT_Compound': '-'}
        ],  # Add more sample rows if needed
        style_table={'overflowX': 'auto'},  # Hide the table by default
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            # 'padding': '15px',
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
    store = dcc.Store(id='store')

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
            store,
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
            html.Iframe(srcDoc=open('topics_parties_network.html', 'r').read(), width='100%', height='750px')
        ], style={'max-width': '1200px', 'margin': '0 auto'}),  # Center the layout
    ])
    return layout
