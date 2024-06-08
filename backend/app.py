# app.py
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from services.data_service import get_posts_per_day

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

print(states)
# print(geometries)

state_colors = {state: color for state, color in zip(states, px.colors.qualitative.Plotly)}
print(state_colors)
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
    html.H1("Reddit Austrain Politics Analysis"),
    dcc.Graph(id='map', figure=fig),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 1, 31)
    ),
    dcc.Graph(id='streak-map', figure=go.Figure()),
    dcc.Slider(
        id='date-slider',
        min=0,
        max=12,
        value=0,
        marks={i: f'Month {i + 1}' for i in range(12)}
    ),
])


def get_colour(value):
    print("Inside get_colour")
    if value > 5:
        return colors[3]
    elif value > 3:
        return colors[2]
    elif value > 1:
        return colors[1]
    else:
        return colors[0]
    pass


@app.callback(
    Output('streak-map', 'figure'),
    Input('map', 'clickData'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('date-slider', 'value')
)
def update_streak_map(clickData, start_date, end_date, slider_value):
    print("Streak update")
    if not clickData:
        return go.Figure()
    state = clickData['points'][0]['location']
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # start_date += pd.DateOffset(weeks=week)
    # end_date += pd.DateOffset(weeks=week)
    df = get_posts_per_day(state, start_date, end_date)
    if df.empty:
        return "No data available for this state"
    heatmap = create_count_streak(df)
    weeks = df['date'].dt.strftime('%U').unique()
    week_index = min(slider_value, len(weeks) - 1)

    # Create a figure for the heatmap
    fig = px.imshow(
        heatmap,
        labels=dict(x="Week", y="Day of Week", color="Post Count"),
        x=weeks,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        color_continuous_scale='Viridis'
    )
    fig.update_layout(title=f'Streak Map for {state}')

    return fig


def create_count_streak(df):
    df['day_of_week'] = df['date'].dt.dayofweek
    df['week'] = df['date'].dt.strftime('%U')

    weeks = df['week'].unique()
    days = df['day_of_week'].unique()
    heatmap = np.zeros((len(days), len(weeks)))

    for i, week in enumerate(weeks):
        for j, day in enumerate(days):
            count = df[(df['week'] == week) & (df['day_of_week'] == day)]['post_count'].sum()
            heatmap[j, i] = count

    return heatmap


colors = ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b']


if __name__ == '__main__':
    app.run_server(debug=True)