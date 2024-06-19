import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import json
from wordcloud import WordCloud
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from services.data_service import load_sentiment_data, load_wordcloud_data, query_sentiment_data


def register_callbacks(app):
    with open('backend/data/map_data/oesterreich.json') as f:
        map_data = json.load(f)

    features = map_data['features']

    @app.callback(
        Output('map', 'figure'),
        [Input('map', 'clickData'),
         Input('navbar-dropdown', 'value')]
    )
    def update_map(click_data, filter1):
        fig = px.choropleth_mapbox(
            pd.DataFrame({'state': [feature['properties']['name'] for feature in features]}),
            geojson=map_data,
            locations='state',
            color='state',
            featureidkey="properties.name",
            color_discrete_map={state: color for state, color in
                                zip([feature['properties']['name'] for feature in features],
                                    px.colors.qualitative.Plotly)},
            mapbox_style="carto-positron",
            center={"lat": 47.5162, "lon": 14.5501},
            zoom=6,
            labels={'color': 'state'},
        )
        fig.update_layout(
            margin={"r": 10, "t": 10, "l": 10, "b": 10}
        )
        # Default center
        center = [47.5162, 14.5501]

        if click_data:
            state = click_data['points'][0]['location']
            for feature in features:
                if feature['properties']['name'] == state:
                    # Check if the selected region is a multipolygon
                    if feature['geometry']['type'] == 'MultiPolygon':
                        co_ordinates = [c for c in feature['geometry']['coordinates'][0][0]]
                    else:
                        co_ordinates = feature['geometry']['coordinates'][0]
                    # print("co_ordinates", co_ordinates)
                    center = [sum([c[0] for c in co_ordinates]) / len(co_ordinates),
                              sum([c[1] for c in co_ordinates]) / len(co_ordinates)]
                    break

            # fade out the unselected states
            color_discrete_map = {state: 'rgba(0,0,0,0.1)' for state in
                                  [feature['properties']['name'] for feature in features]}
            color_discrete_map[state] = px.colors.qualitative.Plotly[0]

            fig = px.choropleth_mapbox(
                pd.DataFrame({'state': [feature['properties']['name'] for feature in features]}),
                geojson=map_data,
                locations='state',
                color='state',
                featureidkey="properties.name",
                color_discrete_map=color_discrete_map,
                mapbox_style="carto-positron",
                center={"lat": center[1], "lon": center[0]},
                zoom=6,
                labels={'color': 'state'},
            )

            fig.update_layout(
                margin={"r": 10, "t": 10, "l": 10, "b": 10}
            )
        return fig

    @app.callback(
        [Output('sentiment-card', 'children')],
        [Input('map', 'clickData'), Input('navbar-dropdown', 'value')]
    )
    def update_sentiment_graph(click_data, filter1):
        # if a state is selected, filter the data based on the selected state
        state = click_data['points'][0]['location'] if click_data else None
        print("Filter1---state", filter1, state)
        sentiment_data = load_sentiment_data(state, filter1)
        print(sentiment_data.head(5))
        # count the number of positive, negative and neutral sentiments and divide by the total number of sentiments
        positive = sentiment_data[sentiment_data['BERT_class'] == 'POSITIVE'].shape[0] / sentiment_data.shape[0] * 100
        negative = sentiment_data[sentiment_data['BERT_class'] == 'NEGATIVE'].shape[0] / sentiment_data.shape[0] * 100
        neutral = sentiment_data[sentiment_data['BERT_class'] == 'NEUTRAL'].shape[0] / sentiment_data.shape[0] * 100
        print("Positive", positive, "Negative", negative, "Neutral", neutral)
        print("SUM", positive + negative + neutral)

        fig = go.Figure(
            go.Barpolar(
                r=[positive, negative, neutral],
                theta=['Positive', 'Negative', 'Neutral'],
                marker_color=["#E4FF87", '#FFAA70', '#B6FFB4'],
                marker_line_color="black",
                marker_line_width=2,
                opacity=0.8
            )
        )

        fig.update_layout(
            template=None,
            polar=dict(
                radialaxis=dict(range=[0, 100], showticklabels=False, ticks=''),
                angularaxis=dict(showticklabels=True, ticks='', tickvals=['Positive', 'Negative', 'Neutral'], )
            )
        )
        card_content = dbc.Card([
            dbc.CardHeader(html.B("Sentiment Analysis")),
            dbc.CardBody([
                dcc.Graph(figure=fig, id='sentiment-polar-chart'),
                html.Hr(),
                html.H5("Select Date Range"),
                dcc.Slider(
                    id='date-slider',
                    min=2019,
                    max=2023,
                    step=1,
                    value=2020,
                    marks={i: f'{i}%' for i in range(2019, 2024)}
                )
            ])
        ])

        return [card_content]

    @app.callback(
        Output('url', 'pathname'),
        [Input('map', 'clickData'), Input('navbar-dropdown', 'value')]
    )
    def update_url(click_data, navbar_filter):
        print("In update_url", click_data, navbar_filter)
        if click_data:
            state = click_data['points'][0]['location']
            if navbar_filter:
                return '/' + state + '?party=' + navbar_filter
            return '/' + state
        if navbar_filter:
            return '/?party=' + navbar_filter
        return '/'

    @app.callback(
        Output('wordcloud-graph', component_property='figure'),
        [Input('map', 'clickData'), Input('navbar-dropdown', 'value')]
    )
    def update_wordcloud_graph(click_data, filter1):
        # If a city is clicked, extract the clicked city
        city = click_data['points'][0]['location'] if click_data else None
        print("In Word Cloud", city, filter1)

        # Load the word cloud data for the clicked city and the selected party
        # This is a placeholder. Replace with your actual code to load the word cloud data.
        wordcloud_data = load_wordcloud_data(city, filter1)

        # Create a word cloud with the word cloud data
        wc = WordCloud(background_color='white').generate_from_frequencies(wordcloud_data)

        # Convert the word cloud to a Plotly figure, and remove the co, ordinates
        fig = px.imshow(wc, binary_string=True)
        fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
        return fig

    @app.callback(
        [Output('sentiment-table', 'data'), Output('sentiment-table-container', 'style'), Output('store', 'data')],
        [Input('sentiment-polar-chart', 'clickData')],
        [State('store', 'data')]
    )
    def update_table(clickData, store_data):
        # print("In update_table", clickData)
        if clickData is None:
            return [], {'display': 'none'}, None
        print("Store Data", store_data)

        # Extract the sentiment from the clicked data point
        sentiment = clickData['points'][0][
            'theta']  # replace 'label' with the key that holds the sentiment in your data
        # print("Sentiment", sentiment)

        if store_data and store_data['points'][0]['theta'] == sentiment:
            return [], {'display': 'none'}, None

        # Query your data source to get the list of data corresponding to the clicked sentiment
        # This is a placeholder, replace with your actual query
        data = query_sentiment_data(sentiment).head(15)

        data = data.to_dict('records')
        # print("Data", data)

        return data, {'display': 'block'}, clickData

    @app.callback(
        Output('tabs-content', 'children'),
        Input('topic-tabs', 'value')
    )
    def render_content(tab):
        return html.Iframe(srcDoc=open(f'political_topics_network_{tab}.html', 'r').read(), width='100%',
                           height='750px')

