import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, text # Import text for SQLAlchemy 2.0 compatibility
import os
import time
import sys
import datetime
import dash_bootstrap_components as dbc
from dash import dash_table

# --- Database Connection Configuration ---
DB_USER = os.getenv('POSTGRES_USER', 'sd22750')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'your_secure_password')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'sentiment')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Database Engine Initialization with Retry Logic ---
engine = None
max_db_retries = 20
db_retry_delay_seconds = 5

print(f"Attempting to connect to PostgreSQL for Dash app at {DB_HOST}:{DB_PORT}/{DB_NAME}...", flush=True)
for i in range(max_db_retries):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            pass # Simple connection test
        print("Successfully connected to PostgreSQL for Dash app!", flush=True)
        break
    except Exception as e:
        print(f"Attempt {i+1}/{max_db_retries}: PostgreSQL not yet available for Dash app or connection error: {e}. Retrying in {db_retry_delay_seconds} seconds...", flush=True)
        time.sleep(db_retry_delay_seconds)

if engine is None:
    print("Failed to connect to PostgreSQL for Dash app after multiple retries. Exiting.", flush=True)
    sys.exit(1)

# --- Dash App Initialization ---
# Changed external_stylesheets to a milder theme (FLATLY)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], update_title='Updating...',
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# --- Data Fetching Function (now selects all model columns) ---
def fetch_sentiment_data(start_date=None, end_date=None, sentiment_labels=None, limit=1000):
    try:
        query_parts = []
        params = {}

        sql_query = """
        SELECT
            id,
            title,
            description,
            url,
            vader_score,
            vader_label,
            textblob_score,
            textblob_label,
            transformer_score,
            transformer_label,
            created_at
        FROM
            sentiment_results
        """

        if start_date:
            query_parts.append("created_at >= :start_date")
            params['start_date'] = start_date
        if end_date:
            query_parts.append("created_at <= :end_date")
            params['end_date'] = end_date

        if sentiment_labels and len(sentiment_labels) > 0:
            # Note: This filter applies to VADER sentiment by default.
            # For multi-model filtering, you'd need more complex UI/SQL
            sentiment_placeholders = ','.join([f":sentiment_{i}" for i in range(len(sentiment_labels))])
            query_parts.append(f"vader_label IN ({sentiment_placeholders})")
            for i, label in enumerate(sentiment_labels):
                params[f'sentiment_{i}'] = label

        if query_parts:
            sql_query += " WHERE " + " AND ".join(query_parts)

        sql_query += " ORDER BY created_at DESC LIMIT :limit;"
        params['limit'] = limit
        
        df = pd.read_sql(text(sql_query), engine, params=params)
        df['created_at'] = pd.to_datetime(df['created_at'])
        print(f"Fetched {len(df)} records from database with filters.", flush=True)
        return df
    except Exception as e:
        print(f"Error fetching data from database: {e}", flush=True)
        return pd.DataFrame()

# Define milder color palette for sentiment labels
# Green for Positive, Yellow/Orange for Neutral, Red for Negative
MILD_COLOR_MAP = {
    'Positive': "#4BAA73",  # Emerald Green
    'Neutral': "#C4AD54",   # Sunflower Yellow
    'Negative': "#F77566"   # Alizarin Red
}

# --- Dashboard Layout ---
app.layout = dbc.Container(
    fluid=True,
    # Changed background and font colors to milder tones
    style={'backgroundColor': '#F8F9FA', 'color': '#343A40', 'fontFamily': 'Inter, sans-serif'},
    children=[
        dbc.Row(dbc.Col(html.H1('Real-time Sentiment Analysis Dashboard (Multi-Model)',
                                className='text-center my-4', style={'color': '#495057'}), width=12)),
        
        # Filters and Key Metrics Row
        dbc.Row(
            className='mb-4',
            children=[
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Time Range", className="card-title"),
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        display_format='YYYY-MM-DD',
                        style={'width': '100%'}
                    )
                ]), color="light", outline=True), md=4), # Changed card color to light
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Filter by VADER Sentiment", className="card-title"), # Now explicitly VADER
                    dcc.Dropdown(
                        id='sentiment-label-dropdown',
                        options=[
                            {'label': 'Positive', 'value': 'Positive'},
                            {'label': 'Neutral', 'value': 'Neutral'},
                            {'label': 'Negative', 'value': 'Negative'}
                        ],
                        value=['Positive', 'Neutral', 'Negative'],
                        multi=True,
                        placeholder="Select sentiment labels...",
                        # Milder dropdown styling
                        style={'backgroundColor': '#FFFFFF', 'color': '#343A40'}
                    )
                ]), color="light", outline=True), md=4), # Changed card color to light
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Total Articles (Past Hour)", className="card-title"),
                    html.H2(id='total-articles-card', className="text-center", style={'color': '#28a745'}) # Green for positive numbers
                ]), color="light", outline=True), md=2), # Changed card color to light
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg. VADER Score (Past Hour)", className="card-title"), # Explicitly VADER
                    html.H2(id='avg-sentiment-card', className="text-center", style={'color': '#007BFF'}) # Primary blue
                ]), color="light", outline=True), md=2), # Changed card color to light
            ]
        ),

        # Three Pie Charts for all models (instead of dropdown)
        dbc.Row(
            className='mb-4',
            children=[
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('VADER Sentiment Distribution', className="card-title text-center"),
                    dcc.Graph(id='vader-pie-chart')
                ]), color="light", outline=True), lg=4), # Changed card color to light, adjusted column size
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('TextBlob Sentiment Distribution', className="card-title text-center"),
                    dcc.Graph(id='textblob-pie-chart')
                ]), color="light", outline=True), lg=4), # Changed card color to light, adjusted column size
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Transformer Sentiment Distribution', className="card-title text-center"),
                    dcc.Graph(id='transformer-pie-chart')
                ]), color="light", outline=True), lg=4) # Changed card color to light, adjusted column size
            ]
        ),

        # Sentiment Over Time Chart (now showing all models)
        dbc.Row(
            className='mb-4',
            children=[
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Multi-Model Sentiment Over Time', className="card-title text-center"), # Title updated
                    dcc.Graph(id='sentiment-time-series')
                ]), color="light", outline=True), lg=12) # Changed card color to light
            ]
        ),

        # Model Comparison Charts Row
        dbc.Row(
            className='mb-4',
            children=[
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Model Score Comparison (VADER vs Transformer)', className="card-title text-center"),
                    dcc.Graph(id='model-score-comparison-scatter')
                ]), color="light", outline=True), lg=6), # Changed card color to light
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4('Model Disagreement Overview', className="card-title text-center"),
                    dcc.Graph(id='model-disagreement-bar')
                ]), color="light", outline=True), lg=6) # Changed card color to light
            ]
        ),

        # Recent Articles Table Row
        dbc.Row(
            children=[
                dbc.Col(dbc.Card(dbc.CardBody([
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
                        ],
                        # Milder table styling
                        style_header={'backgroundColor': '#E9ECEF', 'color': '#495057', 'fontWeight': 'bold'},
                        style_data={'backgroundColor': '#FFFFFF', 'color': '#343A40', 'border': '1px solid #CED4DA'},
                        style_cell={'padding': '8px', 'fontFamily': 'Inter, sans-serif', 'fontSize': '14px', 'textAlign': 'left'},
                        # Define fixed widths for specific columns and allow title to expand
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
                                # Title column takes remaining space
                                'width': 'auto', 'minWidth': '150px', # Ensure it has a minimum size
                                'textOverflow': 'ellipsis',
                                'overflow': 'hidden',
                                'whiteSpace': 'nowrap'
                            },
                        ],
                        # All color-based conditional styling now ONLY in style_data_conditional
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
                ]), color="light", outline=True)), # Changed card color to light
                # Hidden Div to store filtered data for other callbacks if needed
                html.Div(id='filtered-data-store', style={'display': 'none'})
            ]
        ),
        # Interval for automatic updates
        dcc.Interval(
            id='interval-component',
            interval=15*1000, # Update every 15 seconds
            n_intervals=0
        )
    ]
)

# --- Callbacks to Update Graphs & Cards ---
@app.callback(
    [Output('vader-pie-chart', 'figure'),
     Output('textblob-pie-chart', 'figure'),
     Output('transformer-pie-chart', 'figure'),
     Output('sentiment-time-series', 'figure'),
     Output('recent-articles-table', 'data'),
     Output('total-articles-card', 'children'),
     Output('avg-sentiment-card', 'children'),
     Output('model-score-comparison-scatter', 'figure'),
     Output('model-disagreement-bar', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('sentiment-label-dropdown', 'value')]
)
def update_dashboard(n_intervals, start_date, end_date, vader_sentiment_labels):
    print(f"Updating dashboard at interval {n_intervals} with filters: {start_date}, {end_date}, VADER labels={vader_sentiment_labels}", flush=True)

    df = fetch_sentiment_data(start_date, end_date, vader_sentiment_labels)

    # Calculate metrics for cards
    if not df.empty:
        total_articles_past_hour = df[df['created_at'] >= (datetime.datetime.now() - datetime.timedelta(hours=1))].shape[0]
        avg_sentiment_past_hour = df[df['created_at'] >= (datetime.datetime.now() - datetime.timedelta(hours=1))]['vader_score'].mean()
        
        if pd.isna(avg_sentiment_past_hour):
            avg_sentiment_past_hour_str = "N/A"
        else:
            avg_sentiment_past_hour_str = f"{avg_sentiment_past_hour:.2f}"
    else:
        total_articles_past_hour = 0
        avg_sentiment_past_hour_str = "N/A"

    # Default empty figures/table
    vader_pie_chart_fig = {}
    textblob_pie_chart_fig = {}
    transformer_pie_chart_fig = {}
    time_series_fig = {}
    scatter_comparison_fig = {}
    disagreement_bar_fig = {}
    recent_articles_data = []

    if df.empty:
        return (vader_pie_chart_fig, textblob_pie_chart_fig, transformer_pie_chart_fig,
                time_series_fig, recent_articles_data, total_articles_past_hour, 
                avg_sentiment_past_hour_str, scatter_comparison_fig, disagreement_bar_fig)

    # --- Generate Pie Charts for Each Model ---
    def create_pie_chart(dataframe, label_col, title_prefix):
        sentiment_counts = dataframe[label_col].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.pie(
            sentiment_counts,
            values='Count', names='Sentiment', title=f'{title_prefix} Sentiment Distribution',
            color='Sentiment', color_discrete_map=MILD_COLOR_MAP
        )
        fig.update_layout(
            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font_color='#343A40',
            title_font_color='#495057', legend_font_color='#343A40', margin=dict(t=50, b=0, l=0, r=0)
        )
        return fig

    vader_pie_chart_fig = create_pie_chart(df, 'vader_label', 'VADER')
    textblob_pie_chart_fig = create_pie_chart(df, 'textblob_label', 'TextBlob')
    transformer_pie_chart_fig = create_pie_chart(df, 'transformer_label', 'Transformer')

    # --- Time Series (now includes all three models) ---
    df_time = df.set_index('created_at').resample('1h').agg(
        vader_positive=('vader_label', lambda x: (x == 'Positive').sum()),
        vader_negative=('vader_label', lambda x: (x == 'Negative').sum()),
        vader_neutral=('vader_label', lambda x: (x == 'Neutral').sum()),
        vader_avg_score=('vader_score', 'mean'),
        textblob_positive=('textblob_label', lambda x: (x == 'Positive').sum()),
        textblob_negative=('textblob_label', lambda x: (x == 'Negative').sum()),
        textblob_neutral=('textblob_label', lambda x: (x == 'Neutral').sum()),
        textblob_avg_score=('textblob_score', 'mean'),
        transformer_positive=('transformer_label', lambda x: (x == 'Positive').sum()),
        transformer_negative=('transformer_label', lambda x: (x == 'Negative').sum()),
        transformer_neutral=('transformer_label', lambda x: (x == 'Neutral').sum()),
        transformer_avg_score=('transformer_score', 'mean')
    ).fillna(0).reset_index()

    time_series_fig = go.Figure()

    # VADER Traces
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['vader_positive'], mode='lines', name='VADER Positive', line=dict(color=MILD_COLOR_MAP['Positive'])))
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['vader_negative'], mode='lines', name='VADER Negative', line=dict(color=MILD_COLOR_MAP['Negative'])))
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['vader_neutral'], mode='lines', name='VADER Neutral', line=dict(color=MILD_COLOR_MAP['Neutral'])))
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['vader_avg_score'], mode='lines', name='VADER Avg Score', yaxis='y2', line=dict(color='#007BFF', dash='dot'))) # Primary blue

    # TextBlob Traces (slightly different line styles/colors for distinction)
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['textblob_positive'], mode='lines', name='TextBlob Positive', line=dict(color='#7DCEA0', dash='dash'))) # Lighter Green
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['textblob_negative'], mode='lines', name='TextBlob Negative', line=dict(color='#EC7063', dash='dash'))) # Lighter Red
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['textblob_neutral'], mode='lines', name='TextBlob Neutral', line=dict(color='#F7DC6F', dash='dash'))) # Lighter Yellow
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['textblob_avg_score'], mode='lines', name='TextBlob Avg Score', yaxis='y2', line=dict(color='#5DADE2', dash='dot'))) # Lighter Blue

    # Transformer Traces (even different line styles/colors for distinction)
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['transformer_positive'], mode='lines', name='Transformer Positive', line=dict(color='#1ABC9C', dash='dot'))) # Turquoise
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['transformer_negative'], mode='lines', name='Transformer Negative', line=dict(color='#C0392B', dash='dot'))) # Darker Red
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['transformer_neutral'], mode='lines', name='Transformer Neutral', line=dict(color='#F1C40F', dash='dot'))) # Darker Yellow
    time_series_fig.add_trace(go.Scatter(x=df_time['created_at'], y=df_time['transformer_avg_score'], mode='lines', name='Transformer Avg Score', yaxis='y2', line=dict(color='#2E86C1', dash='dot'))) # Darker Blue


    time_series_fig.update_layout(
        title_text='Multi-Model Sentiment Counts & Average Scores Over Time (Hourly)',
        xaxis_title='Time', yaxis_title='Count',
        yaxis2=dict(title='Avg Score', overlaying='y', side='right', range=[-1, 1], showgrid=False),
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font_color='#343A40',
        title_font_color='#495057', xaxis_tickformat='%H:%M',
        hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        # Add grid lines
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0'), # Light grey grid lines
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0')  # Light grey grid lines
    )

    # --- Model Score Comparison Scatter Plot (VADER vs Transformer) ---
    scatter_comparison_fig = px.scatter(
        df,
        x='vader_score',
        y='transformer_score',
        color='vader_label', # Color by VADER label
        hover_data=['title', 'description', 'vader_label', 'textblob_label', 'transformer_label'],
        title='VADER Score vs. Transformer Score',
        color_discrete_map=MILD_COLOR_MAP
    )
    scatter_comparison_fig.update_layout(
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font_color='#343A40',
        title_font_color='#495057', xaxis_title='VADER Score', yaxis_title='Transformer Score',
        # Add grid lines
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0')
    )
    scatter_comparison_fig.update_traces(marker=dict(size=8, opacity=0.7))


    # --- Model Disagreement Bar Chart ---
    df_disagreement = df.copy()
    df_disagreement['agrees'] = (
        (df_disagreement['vader_label'] == df_disagreement['textblob_label']) &
        (df_disagreement['textblob_label'] == df_disagreement['transformer_label'])
    )
    
    disagreement_counts = df_disagreement['agrees'].value_counts().reset_index()
    disagreement_counts.columns = ['Agreement', 'Count']
    disagreement_counts['Agreement'] = disagreement_counts['Agreement'].map({True: 'Agree', False: 'Disagree'})

    disagreement_bar_fig = px.bar(
        disagreement_counts,
        x='Agreement',
        y='Count',
        title='Model Agreement/Disagreement',
        color='Agreement',
        color_discrete_map={'Agree': MILD_COLOR_MAP['Positive'], 'Disagree': MILD_COLOR_MAP['Negative']}
    )
    disagreement_bar_fig.update_layout(
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font_color='#343A40',
        title_font_color='#495057', xaxis_title='', yaxis_title='Number of Articles',
        # Add grid lines
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0')
    )

    # --- Recent Articles Table Data ---
    df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    recent_articles_data = df.to_dict('records')
    if 'url' in df.columns:
        df['title'] = df.apply(lambda row: f"[{row['title']}]({row['url']})", axis=1)
        recent_articles_data = df.to_dict('records')

    return (vader_pie_chart_fig, textblob_pie_chart_fig, transformer_pie_chart_fig,
            time_series_fig, recent_articles_data, 
            total_articles_past_hour, avg_sentiment_past_hour_str,
            scatter_comparison_fig, disagreement_bar_fig)

# --- Run the Dash App ---
if __name__ == '__main__':
    print("Starting Dash app...", flush=True)
    app.run(debug=True, host='0.0.0.0', port=8050)