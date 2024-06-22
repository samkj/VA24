import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import json
from wordcloud import WordCloud
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from services.data_service import load_sentiment_data, load_wordcloud_data, query_sentiment_data, get_posts_by_state
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from services.data_service import data_dropdown_Party


def update_sentiment_piecharts(selected_states, start_date=None, end_date=None):
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
        specs=[[{'type': 'pie'} for _ in party_synonyms]]  
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
        sentiment_data = load_sentiment_data(state, filter1)
        print("Sentiment Data", sentiment_data.shape)
        positive = sentiment_data[sentiment_data['BERT_class'] == 'POSITIVE'].shape[0] / sentiment_data.shape[0] * 100
        negative = sentiment_data[sentiment_data['BERT_class'] == 'NEGATIVE'].shape[0] / sentiment_data.shape[0] * 100
        neutral = sentiment_data[sentiment_data['BERT_class'] == 'NEUTRAL'].shape[0] / sentiment_data.shape[0] * 100

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
                    marks={i: f'{i}' for i in range(2019, 2024)}
                )
            ])
        ])

        return [card_content]

    # @app.callback(
    #     Output('url', 'pathname'),
    #     [Input('map', 'clickData'), Input('navbar-dropdown', 'value'), Input('url', 'pathname')]
    # )
    # def update_url(click_data, navbar_filter, pathname):
    #     parsed_url = urlparse(pathname)
    #     query_params = parse_qs(parsed_url.query)
    #     print("query_params", query_params)
    #     print("parsed_url", parsed_url)
    #     print("pathname", pathname)
    #     print("NAVBAR FILTER", navbar_filter)
    #
    #     # Update the party filter in the query string
    #     if pathname == '/':
    #         query_params['party'] = ["All"]
    #     else:
    #         # if a party is selected, add it to the list of selected parties
    #         if navbar_filter != 'All':
    #             if 'party' in query_params:
    #                 current_parties = set(query_params['party'])
    #                 current_parties.add(navbar_filter)
    #                 if 'All' in current_parties:
    #                     current_parties.remove('All')
    #                 print("Current Parties", current_parties, list(current_parties))
    #                 query_params['party'] = list(current_parties)
    #                 print("Query Params", query_params)
    #                 if navbar_filter not in current_parties:
    #                     current_parties.add(navbar_filter)
    #             else:
    #                 query_params['party'] = [navbar_filter]
    #         elif navbar_filter == 'All':
    #             # remove the party filter if 'All' is selected
    #             if 'party' in query_params:
    #                 query_params.pop('party')
    #
    #     # Construct the new query string
    #     new_query = urlencode(query_params, doseq=True)
    #     if click_data:
    #         state = click_data['points'][0]['location']
    #         new_path = '/' + state
    #     else:
    #         new_path = '/'
    #
    #     # Construct the new URL
    #     new_url = urlunparse(parsed_url._replace(path=new_path, query=new_query))
    #     return new_url

    @app.callback(
        Output('navbar-dropdown', 'value'),
        [Input('navbar-dropdown', 'value')]
    )
    def update_dropdown(selected_values):
        print("Selected Values", selected_values)
        # make sure that the selected values are always a list
        if not isinstance(selected_values, list):
            selected_values = [selected_values]
        options = [{'label': option['label'], 'value': option['value']} for option in data_dropdown_Party()]
        print("Options", options)

        # if other options are selected, and 'All' is selected, remove all other options
        if len(selected_values) > 1:
            print("More than one selected")
            if 'All' in selected_values and selected_values[0] == 'All':
                # if 'All' is at the beginning, remove 'All'
                selected_values = selected_values[1:]
            elif 'All' in selected_values and selected_values[-1] == 'All':
                selected_values = ['All']
            else:
                # if 'All' is not at the beginning, remove all other options
                selected_values = selected_values
        print("Selected Values", selected_values)
        return selected_values

    @app.callback(
        Output('wordcloud-graph', component_property='figure'),
        [Input('map', 'clickData'), Input('navbar-dropdown', 'value')]
    )
    def update_wordcloud_graph(click_data, filter1):
        # If a city is clicked, extract the clicked city
        city = click_data['points'][0]['location'] if click_data else None

        # Load the word cloud data for the clicked city and the selected party
        wordcloud_data = load_wordcloud_data(city, filter1)

        # Create a word cloud with the word cloud data
        wc = WordCloud(background_color='white').generate_from_frequencies(wordcloud_data)

        # Convert the word cloud to a Plotly figure, and remove the co, ordinates
        fig = px.imshow(wc, binary_string=True)
        fig.update_xaxes(visible=False).update_yaxes(visible=False)
        return fig

    @app.callback(
        [Output('sentiment-table', 'data'), Output('sentiment-table-container', 'style'), Output('store', 'data')],
        [Input('sentiment-polar-chart', 'clickData')],
        [State('store', 'data')]
    )
    def update_table(clickData, store_data):
        if clickData is None:
            return [], {'display': 'none'}, None

        # Extract the sentiment from the clicked data point
        sentiment = clickData['points'][0]['theta']

        if store_data and store_data['points'][0]['theta'] == sentiment:
            return [], {'display': 'none'}, None

        # Query your data source to get the list of data corresponding to the clicked sentiment
        data = query_sentiment_data(sentiment).head(15)
        data = data.to_dict('records')

        return data, {'display': 'block'}, clickData

    @app.callback(
        Output('tabs-content', 'children'),
        Input('topic-tabs', 'value')
    )
    def render_content(tab):
        return html.Iframe(srcDoc=open(f'political_topics_network_{tab}.html', 'r').read(), width='100%',
                           height='750px')

    @app.callback(
        Output('sentiment-piecharts', 'figure'),
        [Input('state-checklist', 'value'),
         Input('date-slider', 'value')]
    )
    def update_piecharts(selected_states, selected_year):
        # Convert the selected year to start and end dates
        start_date = f"{selected_year}-01-01"
        end_date = f"{selected_year}-12-31"
        return update_sentiment_piecharts(selected_states, start_date, end_date)
