# layout.py
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
from constants import MILD_COLOR_MAP, MODEL_COLOR_MAP # No leading dot

# NOTE: Make sure you are using create_layout() in your app.py:
# app.layout = create_layout()
# Remove any legacy 'layout' assignment in app.py.

def create_layout():
    card_style_summary = {
        'background': 'linear-gradient(135deg, #232526 0%, #6dd5ed 100%)',
        'boxShadow': '0 4px 24px 0 rgba(0,0,0,0.25)',
        'borderRadius': '18px',
        'padding': '18px 8px',
        'border': '1px solid #343A40',
        'transition': 'transform 0.15s, box-shadow 0.15s',
    }
    card_style_vader = {
        'background': 'linear-gradient(135deg, #232526 0%, #ff512f 100%)',
        'boxShadow': '0 4px 24px 0 rgba(0,0,0,0.25)',
        'borderRadius': '18px',
        'padding': '18px 8px',
        'border': '1px solid #343A40',
        'transition': 'transform 0.15s, box-shadow 0.15s',
    }
    card_style_textblob = {
        'background': 'linear-gradient(135deg, #232526 0%, #36d1c4 100%)',
        'boxShadow': '0 4px 24px 0 rgba(0,0,0,0.25)',
        'borderRadius': '18px',
        'padding': '18px 8px',
        'border': '1px solid #343A40',
        'transition': 'transform 0.15s, box-shadow 0.15s',
    }
    card_style_transformer = {
        'background': 'linear-gradient(135deg, #232526 0%, #8e54e9 100%)',
        'boxShadow': '0 4px 24px 0 rgba(0,0,0,0.25)',
        'borderRadius': '18px',
        'padding': '18px 8px',
        'border': '1px solid #343A40',
        'transition': 'transform 0.15s, box-shadow 0.15s',
    }
    card_body_style = {
        'padding': '0',
    }
    return dbc.Container(
        fluid=True,
        style={'backgroundColor': '#212529', 'color': '#ECF0F1', 'fontFamily': 'Inter, sans-serif'},
        children=[
            # Header and Model Selector
            dbc.Row([
                dbc.Col(html.H1('Real-time Sentiment Analysis Dashboard (Multi-Model)', className='text-center my-4', style={'color': '#ECF0F1'}), md=6),
                dbc.Col(
                    dcc.Dropdown(
                        id='model-selector',
                        options=[
                            {'label': 'All Models', 'value': 'all'},
                            {'label': 'VADER', 'value': 'VADER'},
                            {'label': 'TextBlob', 'value': 'TextBlob'},
                            {'label': 'Transformer', 'value': 'Transformer'}
                        ],
                        value='all',
                        clearable=False,
                        style={'color': '#212529'}
                    ),
                    md=2
                ),
                dbc.Col(
                    dcc.Input(
                        id='keyword-input',
                        type='text',
                        placeholder='Keyword filter...',
                        style={'width': '100%'}
                    ),
                    md=2
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='sentiment-filter',
                        options=[
                            {'label': 'All Sentiments', 'value': 'all'},
                            {'label': 'Positive', 'value': 'Positive'},
                            {'label': 'Negative', 'value': 'Negative'},
                            {'label': 'Neutral', 'value': 'Neutral'}
                        ],
                        value='all',
                        clearable=False,
                        style={'color': '#212529'}
                    ),
                    md=2
                ),
                dbc.Col(
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date',
                        style={'width': '100%'}
                    ),
                    md=2
                ),
            ], className='mb-4'),
            # Cards Row
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Total Articles (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='total-articles-card', className="text-center")
                        ], style=card_body_style),
                        style=card_style_summary,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Avg. VADER Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-vader-card', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ], style=card_body_style),
                        style=card_style_vader,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Avg. TextBlob Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-textblob-card', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ], style=card_body_style),
                        style=card_style_textblob,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Avg. Transformer Score (Last Retrieval)", className="card-title text-center"),
                            html.H2(id='avg-transformer-card', className="text-center", style={'color': MODEL_COLOR_MAP['Transformer']})
                        ], style=card_body_style),
                        style=card_style_transformer,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
            ]),
            # Classification Metrics
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("VADER Accuracy", className="card-title text-center"),
                            html.H2(id='vader-accuracy', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ], style=card_body_style),
                        style=card_style_vader,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("VADER Precision", className="card-title text-center"),
                            html.H2(id='vader-precision', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ], style=card_body_style),
                        style=card_style_vader,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("VADER Recall", className="card-title text-center"),
                            html.H2(id='vader-recall', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ], style=card_body_style),
                        style=card_style_vader,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("VADER F1-Score", className="card-title text-center"),
                            html.H2(id='vader-f1', className="text-center", style={'color': MODEL_COLOR_MAP['VADER']})
                        ], style=card_body_style),
                        style=card_style_vader,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
            ], className='mb-4'),
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("TextBlob Accuracy", className="card-title text-center"),
                            html.H2(id='textblob-accuracy', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ], style=card_body_style),
                        style=card_style_textblob,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("TextBlob Precision", className="card-title text-center"),
                            html.H2(id='textblob-precision', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ], style=card_body_style),
                        style=card_style_textblob,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("TextBlob Recall", className="card-title text-center"),
                            html.H2(id='textblob-recall', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ], style=card_body_style),
                        style=card_style_textblob,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("TextBlob F1-Score", className="card-title text-center"),
                            html.H2(id='textblob-f1', className="text-center", style={'color': MODEL_COLOR_MAP['TextBlob']})
                        ], style=card_body_style),
                        style=card_style_textblob,
                        className="dashboard-card",
                        color="dark", outline=True),
                    md=3
                ),
            ], className='mb-4'),
            # Pie charts and tabs
            dcc.Tabs([
                dcc.Tab(label='Overview', children=[
                    dbc.Row(
                        className='mb-4',
                        children=[
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('VADER Sentiment Distribution', className="card-title text-center"),
                                    dcc.Graph(id='vader-pie-chart')
                                ]), color="dark", outline=True),
                                lg=4
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('TextBlob Sentiment Distribution', className="card-title text-center"),
                                    dcc.Graph(id='textblob-pie-chart')
                                ]), color="dark", outline=True),
                                lg=4
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('Transformer Sentiment Distribution', className="card-title text-center"),
                                    dcc.Graph(id='transformer-pie-chart')
                                ]), color="dark", outline=True),
                                lg=4
                            )
                        ]
                    )
                ]),
                dcc.Tab(label='Visualizations', children=[
                    dbc.Row(
                        className='mb-4',
                        children=[
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('VADER vs. Transformer Scores', className="card-title text-center"),
                                    dcc.Graph(id='vader-transformer-scatter')
                                ]), color="dark", outline=True),
                                lg=6
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('TextBlob vs. Transformer Scores', className="card-title text-center"),
                                    dcc.Graph(id='textblob-transformer-scatter')
                                ]), color="dark", outline=True),
                                lg=6
                            )
                        ]
                    ),
                    dbc.Row(
                        className='mb-4',
                        children=[
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('Model Disagreement Overview', className="card-title text-center"),
                                    dcc.Graph(id='model-disagreement-bar')
                                ]), color="dark", outline=True),
                                lg=12
                            )
                        ]
                    ),
                    dbc.Row(
                        className='mb-4',
                        children=[
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('VADER vs. Transformer (Confusion Matrix)', className="card-title text-center"),
                                    dcc.Graph(id='vader-transformer-confusion')
                                ]), color="dark", outline=True),
                                lg=6
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H4('TextBlob vs. Transformer (Confusion Matrix)', className="card-title text-center"),
                                    dcc.Graph(id='textblob-transformer-confusion')
                                ]), color="dark", outline=True),
                                lg=6
                            )
                        ]
                    )
                ]),
                dcc.Tab(label='Data Table', children=[
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
                                        style_header={'backgroundColor': '#343A40', 'color': '#ECF0F1', 'fontWeight': 'bold'},
                                        style_data={'backgroundColor': '#2B3E50', 'color': '#ECF0F1', 'border': '1px solid #3F5060'},
                                        style_cell={'padding': '8px', 'fontFamily': 'Inter, sans-serif', 'fontSize': '14px', 'textAlign': 'left'},
                                        style_cell_conditional=[
                                            {'if': {'column_id': 'created_at'}, 'width': '130px', 'minWidth': '130px', 'maxWidth': '130px'},
                                            {'if': {'column_id': 'vader_label'}, 'width': '90px', 'minWidth': '90px', 'maxWidth': '90px'},
                                            {'if': {'column_id': 'vader_score'}, 'width': '90px', 'minWidth': '90px', 'maxWidth': '90px'},
                                            {'if': {'column_id': 'textblob_label'}, 'width': '100px', 'minWidth': '100px', 'maxWidth': '100px'},
                                            {'if': {'column_id': 'textblob_score'}, 'width': '100px', 'minWidth': '100px', 'maxWidth': '100px'},
                                            {'if': {'column_id': 'transformer_label'}, 'width': '110px', 'minWidth': '110px', 'maxWidth': '110px'},
                                            {'if': {'column_id': 'transformer_score'}, 'width': '110px', 'minWidth': '110px', 'maxWidth': '110px'},
                                            {'if': {'column_id': 'title'}, 'width': 'auto', 'minWidth': '150px', 'textOverflow': 'ellipsis', 'overflow': 'hidden', 'whiteSpace': 'nowrap'},
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
                                ]), color="dark", outline=True)
                            )
                        ]
                    )
                ])
            ],
            colors={
                "border": "#888",
                "primary": "#ECF0F1",
                "background": "#212529"
            },
            parent_className="custom-tabs-container"
            ),
            html.Div(id='filtered-data-store', style={'display': 'none'}),
            dcc.Interval(
                id='interval-component',
                interval=15*1000,
                n_intervals=0
            )
        ]
    )

# Remove any callback code from layout.py! All callbacks should be in callbacks.py.
