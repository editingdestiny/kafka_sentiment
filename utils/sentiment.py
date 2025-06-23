import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon if not already downloaded
# This is typically done once, perhaps in a Dockerfile's RUN command or at first run.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    print("Downloading vader_lexicon...", flush=True)
    nltk.download('vader_lexicon', quiet=True)
    print("vader_lexicon downloaded.", flush=True)

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using VADER.
    Returns a dictionary with 'sentiment_score' and 'sentiment_label'.
    """
    if not isinstance(text, str):
        text = str(text) # Ensure text is string for analysis
    
    vs = analyzer.polarity_scores(text)
    
    # VADER returns a compound score typically between -1 (most negative) and +1 (most positive)
    compound_score = vs['compound']
    
    if compound_score >= 0.05:
        label = "Positive"
    elif compound_score <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        "sentiment_score": compound_score,
        "sentiment_label": label
    }

if __name__ == '__main__':
    # Simple test cases
    print(analyze_sentiment("This is a fantastic movie!"))
    print(analyze_sentiment("I really hate this product, it's terrible."))
    print(analyze_sentiment("The weather is okay today."))
    print(analyze_sentiment("That was good, but not great."))