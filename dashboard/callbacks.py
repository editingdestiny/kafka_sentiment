# callbacks.py
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from data_handler import fetch_sentiment_data
from constants import MILD_COLOR_MAP, MODEL_COLOR_MAP

# Define dark theme specific Plotly colors
PLOTLY_DARK_BG_COLOR = '#2C3E50' # A dark blue-grey that fits Cyborg
PLOTLY_DARK_FONT_COLOR = '#ECF0F1' # Light text color
PLOTLY_DARK_GRID_COLOR = '#3A4B5C' # Subtle grid color

def register_callbacks(app, engine):
    @app.callback(
        [Output('vader-pie-chart', 'figure'),
         Output('textblob-pie-chart', 'figure'),
         Output('transformer-pie-chart', 'figure'),
         # Removed Output('sentiment-time-series', 'figure'),
         Output('recent-articles-table', 'data'),
         Output('total-articles-card', 'children'),
         Output('avg-vader-card', 'children'),
         Output('avg-textblob-card', 'children'),
         Output('avg-transformer-card', 'children'),
         Output('vader-transformer-scatter', 'figure'),
         Output('textblob-transformer-scatter', 'figure'),
         Output('model-disagreement-bar', 'figure'),
         Output('vader-transformer-confusion', 'figure'),
         Output('textblob-transformer-confusion', 'figure'),
         # METRIC OUTPUTS
         Output('vader-accuracy', 'children'),
         Output('vader-precision', 'children'),
         Output('vader-recall', 'children'),
         Output('vader-f1', 'children'),
         Output('textblob-accuracy', 'children'),
         Output('textblob-precision', 'children'),
         Output('textblob-recall', 'children'),
         Output('textblob-f1', 'children')],
        [Input('interval-component', 'n_intervals'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date')]
    )
    def update_dashboard(n_intervals, start_date, end_date):
        print(f"Updating dashboard at interval {n_intervals} with filters: {start_date}, {end_date}", flush=True)

        df = fetch_sentiment_data(engine, start_date, end_date)

        total_articles_last_retrieval = 0
        avg_vader_last_retrieval_str = "N/A"
        avg_textblob_last_retrieval_str = "N/A"
        avg_transformer_last_retrieval_str = "N/A"

        vader_acc, vader_prec, vader_rec, vader_f1 = "N/A", "N/A", "N/A", "N/A"
        textblob_acc, textblob_prec, textblob_rec, textblob_f1 = "N/A", "N/A", "N/A", "N/A"

        if not df.empty:
            total_articles_last_retrieval = len(df)
            
            avg_vader_last_retrieval = df['vader_score'].mean()
            avg_textblob_last_retrieval = df['textblob_score'].mean()
            avg_transformer_last_retrieval = df['transformer_score'].mean()
            
            avg_vader_last_retrieval_str = f"{avg_vader_last_retrieval:.2f}" if pd.notna(avg_vader_last_retrieval) else "N/A"
            avg_textblob_last_retrieval_str = f"{avg_textblob_last_retrieval:.2f}" if pd.notna(avg_textblob_last_retrieval) else "N/A"
            avg_transformer_last_retrieval_str = f"{avg_transformer_last_retrieval:.2f}" if pd.notna(avg_transformer_last_retrieval) else "N/A"

        vader_pie_chart_fig = {}
        textblob_pie_chart_fig = {}
        transformer_pie_chart_fig = {}
        # time_series_fig = {} # No longer needed as an output
        vader_transformer_scatter_fig = {}
        textblob_transformer_scatter_fig = {}
        disagreement_bar_fig = {}
        vader_transformer_confusion_fig = {}
        textblob_transformer_confusion_fig = {}
        recent_articles_data = []

        if df.empty:
            return (vader_pie_chart_fig, textblob_pie_chart_fig, transformer_pie_chart_fig,
                    recent_articles_data, # Removed time_series_fig
                    total_articles_last_retrieval, 
                    avg_vader_last_retrieval_str, avg_textblob_last_retrieval_str, avg_transformer_last_retrieval_str,
                    vader_transformer_scatter_fig, textblob_transformer_scatter_fig, disagreement_bar_fig,
                    vader_transformer_confusion_fig, textblob_transformer_confusion_fig,
                    vader_acc, vader_prec, vader_rec, vader_f1,
                    textblob_acc, textblob_prec, textblob_rec, textblob_f1)

        # --- Helper for Classification Metrics ---
        def calculate_metrics(y_true, y_pred, labels_order):
            if len(y_true) == 0 or len(y_pred) == 0:
                return "N/A", "N/A", "N/A", "N/A"
            
            common_labels = [label for label in labels_order if label in y_true.unique() or label in y_pred.unique()]
            
            if len(common_labels) < 2:
                try:
                    acc = accuracy_score(y_true, y_pred)
                    return f"{acc:.2f}", "N/A", "N/A", "N/A"
                except Exception:
                    return "N/A", "N/A", "N/A", "N/A"

            try:
                acc = accuracy_score(y_true, y_pred)
                prec = precision_score(y_true, y_pred, labels=common_labels, average='weighted', zero_division=0)
                rec = recall_score(y_true, y_pred, labels=common_labels, average='weighted', zero_division=0)
                f1 = f1_score(y_true, y_pred, labels=common_labels, average='weighted', zero_division=0)
                
                return f"{acc:.2f}", f"{prec:.2f}", f"{rec:.2f}", f"{f1:.2f}"
            except Exception as e:
                print(f"Error calculating metrics: {e}", flush=True)
                return "N/A", "N/A", "N/A", "N/A"

        sentiment_labels_order = ['Positive', 'Neutral', 'Negative']

        vader_acc, vader_prec, vader_rec, vader_f1 = calculate_metrics(
            df['transformer_label'], df['vader_label'], sentiment_labels_order
        )

        textblob_acc, textblob_prec, textblob_rec, textblob_f1 = calculate_metrics(
            df['transformer_label'], df['textblob_label'], sentiment_labels_order
        )

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
                plot_bgcolor=PLOTLY_DARK_BG_COLOR, paper_bgcolor=PLOTLY_DARK_BG_COLOR,
                font_color=PLOTLY_DARK_FONT_COLOR,
                title_font_color=PLOTLY_DARK_FONT_COLOR, legend_font_color=PLOTLY_DARK_FONT_COLOR,
                margin=dict(t=50, b=0, l=0, r=0),
                height=350,
                width=350   
            )
            return fig

        vader_pie_chart_fig = create_pie_chart(df, 'vader_label', 'VADER')
        textblob_pie_chart_fig = create_pie_chart(df, 'textblob_label', 'TextBlob')
        transformer_pie_chart_fig = create_pie_chart(df, 'transformer_label', 'Transformer')

        # Removed all logic for sentiment_time_series chart as per request

        # --- Model Score Comparison Scatter Plot ---
        vader_transformer_scatter_fig = px.scatter(
            df,
            x='vader_score',
            y='transformer_score',
            color='vader_label',
            hover_data=['title', 'description', 'vader_label', 'textblob_label', 'transformer_label'],
            title='VADER Score vs. Transformer Score',
            color_discrete_map=MILD_COLOR_MAP
        )
        vader_transformer_scatter_fig.update_layout(
            plot_bgcolor=PLOTLY_DARK_BG_COLOR, paper_bgcolor=PLOTLY_DARK_BG_COLOR,
            font_color=PLOTLY_DARK_FONT_COLOR,
            title_font_color=PLOTLY_DARK_FONT_COLOR, xaxis_title='VADER Score', yaxis_title='Transformer Score',
            xaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR),
            yaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR)
        )
        vader_transformer_scatter_fig.update_traces(marker=dict(size=8, opacity=0.7))

        # --- Model Score Comparison Scatter Plot ---
        textblob_transformer_scatter_fig = px.scatter(
            df,
            x='textblob_score',
            y='transformer_score',
            color='textblob_label',
            hover_data=['title', 'description', 'vader_label', 'textblob_label', 'transformer_label'],
            title='TextBlob Score vs. Transformer Score',
            color_discrete_map=MILD_COLOR_MAP
        )
        textblob_transformer_scatter_fig.update_layout(
            plot_bgcolor=PLOTLY_DARK_BG_COLOR, paper_bgcolor=PLOTLY_DARK_BG_COLOR,
            font_color=PLOTLY_DARK_FONT_COLOR,
            title_font_color=PLOTLY_DARK_FONT_COLOR, xaxis_title='TextBlob Score', yaxis_title='Transformer Score',
            xaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR),
            yaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR)
        )
        textblob_transformer_scatter_fig.update_traces(marker=dict(size=8, opacity=0.7))


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
            title='Model Agreement/Disagreement (All Three Models)',
            color='Agreement',
            color_discrete_map={'Agree': MILD_COLOR_MAP['Positive'], 'Disagree': MILD_COLOR_MAP['Negative']}
        )
        disagreement_bar_fig.update_layout(
            plot_bgcolor=PLOTLY_DARK_BG_COLOR, paper_bgcolor=PLOTLY_DARK_BG_COLOR,
            font_color=PLOTLY_DARK_FONT_COLOR,
            title_font_color=PLOTLY_DARK_FONT_COLOR, xaxis_title='', yaxis_title='Number of Articles',
            xaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR),
            yaxis=dict(showgrid=True, gridcolor=PLOTLY_DARK_GRID_COLOR)
        )

        # --- Confusion Matrix Generation ---
        def create_confusion_matrix_fig(df_data, predicted_col, actual_col, title):
            labels_order = ['Positive', 'Neutral', 'Negative']
            
            confusion_matrix_df = pd.crosstab(
                df_data[predicted_col],
                df_data[actual_col],
                dropna=False
            ).reindex(index=labels_order, columns=labels_order, fill_value=0)

            fig = go.Figure(data=go.Heatmap(
                z=confusion_matrix_df.values,
                x=confusion_matrix_df.columns,
                y=confusion_matrix_df.index,
                colorscale="Viridis",
                text=confusion_matrix_df.values,
                texttemplate="%{text}",
                textfont={"size": 14, "color": "white"}
            ))

            fig.update_layout(
                title_text=title,
                xaxis=dict(title=f'Actual ({actual_col.replace("_label", "").replace("transformer", "Transformer")})', showgrid=False, zeroline=False, tickfont=dict(color=PLOTLY_DARK_FONT_COLOR)),
                yaxis=dict(title=f'Predicted ({predicted_col.replace("_label", "").replace("vader", "VADER").replace("textblob", "TextBlob")})', showgrid=False, zeroline=False, tickfont=dict(color=PLOTLY_DARK_FONT_COLOR)),
                plot_bgcolor=PLOTLY_DARK_BG_COLOR, paper_bgcolor=PLOTLY_DARK_BG_COLOR,
                font_color=PLOTLY_DARK_FONT_COLOR,
                title_font_color=PLOTLY_DARK_FONT_COLOR
            )
            return fig

        vader_transformer_confusion_fig = create_confusion_matrix_fig(
            df, 'vader_label', 'transformer_label', 'VADER vs. Transformer Sentiment'
        )
        textblob_transformer_confusion_fig = create_confusion_matrix_fig(
            df, 'textblob_label', 'transformer_label', 'TextBlob vs. Transformer Sentiment'
        )

        # --- Recent Articles Table Data ---
        df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'url' in df.columns:
            df['title'] = df.apply(lambda row: f"[{row['title']}]({row['url']})", axis=1)
        recent_articles_data = df.to_dict('records')

        return (vader_pie_chart_fig, textblob_pie_chart_fig, transformer_pie_chart_fig,
                recent_articles_data, # time_series_fig is removed from here
                total_articles_last_retrieval, 
                avg_vader_last_retrieval_str, avg_textblob_last_retrieval_str, avg_transformer_last_retrieval_str,
                vader_transformer_scatter_fig, textblob_transformer_scatter_fig, disagreement_bar_fig,
                vader_transformer_confusion_fig, textblob_transformer_confusion_fig,
                vader_acc, vader_prec, vader_rec, vader_f1,
                textblob_acc, textblob_prec, textblob_rec, textblob_f1)