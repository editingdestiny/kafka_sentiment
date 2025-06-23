# layout.py
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
from constants import MILD_COLOR_MAP, MODEL_COLOR_MAP # No leading dot

def create_layout():
    return dbc.Container(
        fluid=True,
        # Main container style for dark theme
        style={'backgroundColor': '#212529', 'color': '#ECF0F1', 'fontFamily': 'Inter, sans-serif'},
        children=[
            dbc.Row(dbc.Col(html.H1('Real-time Sentiment Analysis Dashboard (Multi-Model)',
                                     className='text-center my-4', style={'color': '#ECF0F1'}), width=12)), # Light title color
            
            # Time Range Filter (Moved here, only one instance)
            dbc.Row(
                className='mb-4',
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H5("Time Range", className="card-title"),
                            dcc.DatePickerRange(
                                id='date-range-picker',
                                start_date_placeholder_text="Start Date",
                                end_date_placeholder_text="End Date",
                                display_format='YYYY-MM-DD',
                                style={'width': '100%'}
                            )
                        ]), color="dark", outline=True), # Card style for dark theme
                        md=4 # Takes 4 out of 12 columns
                    ),
                    dbc.Col(html.Div(), md=8) # Empty column to fill space
                ]
            ),

            # Grouped Metrics Section (Average Scores + Performance Metrics)
            # Row for 4 Average Score boxes
            dbc.Row(
                className='mb-3 mt-4', # Margin top for separation
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H5("Total Articles (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='total-articles-card', className="text-center", style={'color': '#28a745'}) # Green for positive number
                        ]), color="dark", outline=True), # Card style for dark theme
                        md=3 # Each takes 3 out of 12 columns
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H5("Avg. VADER Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-vader-card', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ]), color="dark", outline=True), # Card style for dark theme
                        md=3
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H5("Avg. TextBlob Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-textblob-card', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ]), color="dark", outline=True), # Card style for dark theme
                        md=3
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H5("Avg. Transformer Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-transformer-card', className="text-center", style={'color': MODEL_COLOR_MAP['Transformer']})
                        ]), color="dark", outline=True), # Card style for dark theme
                        md=3
                    ),
                ]
            ),
            # Row for 2 Performance Metrics boxes (directly below Average Scores)
            dbc.Row(
                className='mb-4', # Margin bottom for separation from next section
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('VADER Performance vs. Transformer', className="card-title text-center"),
                            html.P("Accuracy: ", className="card-text d-inline") , html.Span(id='vader-accuracy', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("Precision (weighted): ", className="card-text d-inline"), html.Span(id='vader-precision', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("Recall (weighted): ", className="card-text d-inline"), html.Span(id='vader-recall', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("F1-Score (weighted): ", className="card-text d-inline"), html.Span(id='vader-f1', className="card-text", style={'fontWeight': 'bold'})
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6 # Each takes 6 out of 12 columns (half width)
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('TextBlob Performance vs. Transformer', className="card-title text-center"),
                            html.P("Accuracy: ", className="card-text d-inline"), html.Span(id='textblob-accuracy', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("Precision (weighted): ", className="card-text d-inline"), html.Span(id='textblob-precision', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("Recall (weighted): ", className="card-text d-inline"), html.Span(id='textblob-recall', className="card-text", style={'fontWeight': 'bold'}), html.Br(),
                            html.P("F1-Score (weighted): ", className="card-text d-inline"), html.Span(id='textblob-f1', className="card-text", style={'fontWeight': 'bold'})
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6
                    )
                ]
            ),


            # Three Pie Charts for all models
            dbc.Row(
                className='mb-4',
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('VADER Sentiment Distribution', className="card-title text-center"),
                            dcc.Graph(id='vader-pie-chart')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=4 # Takes 4 out of 12 columns
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('TextBlob Sentiment Distribution', className="card-title text-center"),
                            dcc.Graph(id='textblob-pie-chart')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=4
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('Transformer Sentiment Distribution', className="card-title text-center"),
                            dcc.Graph(id='transformer-pie-chart')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=4
                    )
                ]
            ),

            # Model Comparison Charts Row
            dbc.Row(
                className='mb-4',
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('VADER vs. Transformer Scores', className="card-title text-center"),
                            dcc.Graph(id='vader-transformer-scatter')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('TextBlob vs. Transformer Scores', className="card-title text-center"),
                            dcc.Graph(id='textblob-transformer-scatter')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6
                    )
                ]
            ),

            # Model Disagreement Overview
            dbc.Row(
                className='mb-4',
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('Model Disagreement Overview', className="card-title text-center"),
                            dcc.Graph(id='model-disagreement-bar')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=12
                    )
                ]
            ),

            # Confusion Matrices Row
            dbc.Row(
                className='mb-4',
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('VADER vs. Transformer (Confusion Matrix)', className="card-title text-center"),
                            dcc.Graph(id='vader-transformer-confusion')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6 # Takes 6 out of 12 columns
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('TextBlob vs. Transformer (Confusion Matrix)', className="card-title text-center"),
                            dcc.Graph(id='textblob-transformer-confusion')
                        ]), color="dark", outline=True), # Card style for dark theme
                        lg=6
                    )
                ]
            ),

            # Recent Articles Table Row
            dbc.Row(
                children=[
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.H4('Recent Articles with Multi-Model Sentiment', className="card-title text-center"),
                            dash_table.DataTable(
                                id='recent-articles-table',
                                columns=[
                                    {"name": "Created At", "id": "created_at"},
                                    {"name": "VADER Label", "id": "vader_label"},
                                    {"name": "VADER Score", "id": "vader_score", "type": "numeric", "format": dash_table.Format.Format(precision=3, scheme=dash_table.Format.Scheme.fixed)},
                                    {"name": "TextBlob Label", "id": "textblob_label"},
                                    {"name": "TextBlob Score", "id": "textblob_score", "type": "numeric", "format": dash_table.Format.Format(precision=3, scheme=dash_table.Format.Scheme.fixed)},
                                    {"name": "Transformer Label", "id": "transformer_label"},
                                    {"name": "Transformer Score", "id": "transformer_score", "type": "numeric", "format": dash_table.Format.Format(precision=3, scheme=dash_table.Format.Scheme.fixed)},
                                    {"name": "Headline", "id": "title","presentation": "markdown"},
                                    {"name": "Description", "id": "description"}
                                ],
                                # DataTable styling for dark theme
                                style_header={'backgroundColor': '#343A40', 'color': '#ECF0F1', 'fontWeight': 'bold'}, # Dark header, light text
                                style_data={'backgroundColor': '#2B3E50', 'color': '#ECF0F1', 'border': '1px solid #3F5060'}, # Dark data rows, light text, subtle border
                                style_cell={'padding': '8px', 'fontFamily': 'Inter, sans-serif', 'fontSize': '14px', 'textAlign': 'left'},
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'created_at'},
                                        'width': '130px', 'minWidth': '130px', 'maxWidth': '130px',
                                    },
                                    {
                                        'if': {'column_id': 'vader_label'},
                                        'width': '90px', 'minWidth': '90px', 'maxWidth': '90px',
                                    },
                                    {
                                        'if': {'column_id': 'vader_score'},
                                        'width': '90px', 'minWidth': '90px', 'maxWidth': '90px',
                                    },
                                    {
                                        'if': {'column_id': 'textblob_label'},
                                        'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
                                    },
                                    {
                                        'if': {'column_id': 'textblob_score'},
                                        'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
                                    },
                                    {
                                        'if': {'column_id': 'transformer_label'},
                                        'width': '110px', 'minWidth': '110px', 'maxWidth': '110px',
                                    },
                                    {
                                        'if': {'column_id': 'transformer_score'},
                                        'width': '110px', 'minWidth': '110px', 'maxWidth': '110px',
                                    },
                                    {
                                        'if': {'column_id': 'title'},
                                        'width': 'auto', 'minWidth': '150px',
                                        'textOverflow': 'ellipsis',
                                        'overflow': 'hidden',
                                        'whiteSpace': 'nowrap'
                                    },
                                ],
                                style_data_conditional=[
                                    {'if': {'column_id': 'vader_label', 'filter_query': '{vader_label} eq "Positive"'}, 'color': MILD_COLOR_MAP['Positive']},
                                    {'if': {'column_id': 'vader_label', 'filter_query': '{vader_label} eq "Negative"'}, 'color': MILD_COLOR_MAP['Negative']},
                                    {'if': {'column_id': 'vader_label', 'filter_query': '{vader_label} eq "Neutral"'}, 'color': MILD_COLOR_MAP['Neutral']},
                                    
                                    {'if': {'column_id': 'textblob_label', 'filter_query': '{textblob_label} eq "Positive"'}, 'color': MILD_COLOR_MAP['Positive']},
                                    {'if': {'column_id': 'textblob_label', 'filter_query': '{textblob_label} eq "Negative"'}, 'color': MILD_COLOR_MAP['Negative']},
                                    {'if': {'column_id': 'textblob_label', 'filter_query': '{textblob_label} eq "Neutral"'}, 'color': MILD_COLOR_MAP['Neutral']},
                                    
                                    {'if': {'column_id': 'transformer_label', 'filter_query': '{transformer_label} eq "Positive"'}, 'color': MILD_COLOR_MAP['Positive']},
                                    {'if': {'column_id': 'transformer_label', 'filter_query': '{transformer_label} eq "Negative"'}, 'color': MILD_COLOR_MAP['Negative']},
                                    {'if': {'column_id': 'transformer_label', 'filter_query': '{transformer_label} eq "Neutral"'}, 'color': MILD_COLOR_MAP['Neutral']},
                                ],
                                page_size=10,
                                row_selectable="single",
                                selected_rows=[],
                                sort_action="native",
                                filter_action="native"
                            )
                ]), color="dark", outline=True) # Card style for dark theme
                    )
                ]
            ),
            html.Div(id='filtered-data-store', style={'display': 'none'}), # Keep this hidden div
            dcc.Interval(
                id='interval-component',
                interval=15*1000, # Update every 15 seconds
                n_intervals=0
            )
        ]
    )