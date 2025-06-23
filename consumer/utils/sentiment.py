import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob # Import TextBlob
from transformers import pipeline # Import Hugging Face pipeline
import datetime # Ensure datetime is imported for consistent timestamps

# --- NLTK VADER Setup ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading vader_lexicon...", flush=True)
    nltk.download('vader_lexicon', quiet=True)
    print("vader_lexicon downloaded.", flush=True)
except Exception as e:
    print(f"An unexpected error occurred during NLTK VADER setup: {e}", flush=True)
vader_analyzer = SentimentIntensityAnalyzer()

# --- Hugging Face Transformers Setup ---
# Load a pre-trained sentiment analysis model
# This will download the model the first time it runs.
# 'distilbert-base-uncased-finetuned-sst-2-english' is a common, relatively small sentiment model.
try:
    hf_sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    print("Hugging Face sentiment model loaded.", flush=True)
except Exception as e:
    print(f"Error loading Hugging Face model: {e}. Ensure transformers and torch are installed correctly.", flush=True)
    hf_sentiment_pipeline = None # Set to None if loading fails to prevent further errors


def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using VADER, TextBlob, and Hugging Face Transformers.
    Returns a dictionary with sentiment scores and labels for each model.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # --- VADER Analysis ---
    vader_vs = vader_analyzer.polarity_scores(text)
    vader_compound_score = vader_vs['compound']
    if vader_compound_score >= 0.05:
        vader_label = "Positive"
    elif vader_compound_score <= -0.05:
        vader_label = "Negative"
    else:
        vader_label = "Neutral"
    
    # --- TextBlob Analysis ---
    # TextBlob returns polarity (-1 to 1) and subjectivity (0 to 1)
    textblob_polarity = TextBlob(text).sentiment.polarity
    if textblob_polarity > 0:
        textblob_label = "Positive"
    elif textblob_polarity < 0:
        textblob_label = "Negative"
    else:
        textblob_label = "Neutral"

    # --- Hugging Face Transformers Analysis ---
    hf_score = None
    hf_label = "Neutral" # Default to Neutral if pipeline not loaded or error
    if hf_sentiment_pipeline:
        try:
            hf_result = hf_sentiment_pipeline(text[:512]) # Limit text length for HF, models often have max input
            if hf_result:
                hf_score = hf_result[0]['score']
                hf_label = hf_result[0]['label']
                # HF 'POSITIVE'/'NEGATIVE' labels might need mapping
                if hf_label == 'POSITIVE':
                    hf_label = 'Positive'
                elif hf_label == 'NEGATIVE':
                    hf_label = 'Negative'
        except Exception as e:
            print(f"Error during Hugging Face sentiment analysis for text: '{text[:50]}...': {e}", flush=True)
            # Fallback to Neutral if analysis fails
            hf_score = 0.0 
            hf_label = "Neutral"


    return {
        "vader_score": vader_compound_score,
        "vader_label": vader_label,
        "textblob_score": textblob_polarity,
        "textblob_label": textblob_label,
        "transformer_score": hf_score,
        "transformer_label": hf_label
    }

if __name__ == '__main__':
    print("Testing analyze_sentiment function with multiple models:", flush=True)
    test_texts = [
        "This is an absolutely fantastic movie! I loved every moment.",
        "I am extremely disappointed with the service. It was terrible and frustrating.",
        "The weather is okay today, neither good nor bad.",
        "That was good, but not great, just average.",
        "The project faced unexpected challenges, but the team overcame them brilliantly.",
        "Cat sat on the mat."
    ]
    for text in test_texts:
        print(f"\nText: '{text}'", flush=True)
        results = analyze_sentiment(text)
        print(f"  VADER: Score={results['vader_score']:.2f}, Label={results['vader_label']}", flush=True)
        print(f"  TextBlob: Score={results['textblob_score']:.2f}, Label={results['textblob_label']}", flush=True)
        print(f"  Transformer: Score={results['transformer_score']:.2f}, Label={results['transformer_label']}", flush=True)