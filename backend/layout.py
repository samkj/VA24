import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
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

    layout = html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div([
            html.H1("Map of Austria"),
            html.Div(id='map-wrapper', children=[
                dcc.Graph(id='map', figure=fig)
            ]),
            html.Div(id='sentiment-card'),
            dcc.Graph(id='wordcloud-graph'),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            )
        ], style={'max-width': '1200px', 'margin': '0 auto'})  # Center the layout
    ])

    return layout
