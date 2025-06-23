import json
import time
import sys
import os
import requests
import datetime # For handling datetime objects, potentially for fallbacks
from urllib.parse import urlparse # For more robust URL parsing if needed for unique IDs

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# For SerpAPI integration
from serpapi.google_search import GoogleSearch

# --- Kafka Configuration ---
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'raw-news'

# --- API Configurations ---

# NewsAPI Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_QUERY = "Finance or Markets"
NEWS_API_LANGUAGE = "en"
NEWS_API_SORT_BY = "publishedAt"
NEWS_API_PAGE_SIZE = 10 # Keep this low for free tier

# Guardian API Configuration
GUARDIAN_API_KEY = os.getenv('GUARDIAN_API_KEY')
GUARDIAN_API_ENDPOINT = "https://content.guardianapis.com/search"
GUARDIAN_API_QUERY = "finance or markets"
GUARDIAN_API_SHOW_FIELDS = "headline,standfirst,bodyText,webUrl,webPublicationDate"
GUARDIAN_API_PAGE_SIZE = 10 # Keep this low for free tier

# MediaStack API Configuration
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')
MEDIASTACK_API_ENDPOINT = "http://api.mediastack.com/v1/news"
MEDIASTACK_API_QUERY = "finance or markets"
MEDIASTACK_API_LANGUAGES = "en"
MEDIASTACK_API_LIMIT = 10 # Number of articles per API call

# Reddit API Configuration (No API Key needed for basic reads, but a User-Agent is good practice)
REDDIT_USER_AGENT = "KafkaSentimentPipeline/1.0 (by /u/Wide_Emu_7464)" # REPLACE WITH YOUR REDDIT USERNAME
REDDIT_SUBREDDITS = ["finance", "investing","stocks",] # Subreddits to pull from
REDDIT_POST_LIMIT = 10 # Posts per subreddit
REDDIT_BASE_URL = "https://www.reddit.com/r/"

# SerpAPI Configuration - NEW
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
# Note: SerpAPI queries are usually specific. For "finance or markets" news globally,
# we might need to iterate through different regions or just use a general query.
# Let's use categories/countries as in your previous SerpAPI example, but adjust to finance/markets context.
SERPAPI_QUERIES = ['Finance news', 'Markets news', 'Stock market news']
# Add country-specific queries if desired, e.g., 'US finance news', 'UK markets news'
# SERPAPI_COUNTRIES_OR_TOPICS = ['Technology', 'AI', 'India', 'UK', 'US'] # Example from your previous snippet
# For relevance to 'Finance or Markets', let's stick to explicit keywords
SERPAPI_NEWS_LIMIT = 30 # Articles per SerpAPI query

# --- API Key Checks ---
if not NEWS_API_KEY:
    print("WARNING: NEWS_API_KEY environment variable not set. NewsAPI fetching will be skipped.", flush=True)
if not GUARDIAN_API_KEY:
    print("WARNING: GUARDIAN_API_KEY environment variable not set. Guardian API fetching will be skipped.", flush=True)
if not MEDIASTACK_API_KEY:
    print("WARNING: MEDIASTACK_API_KEY environment variable not set. MediaStack API fetching will be skipped.", flush=True)
if not SERPAPI_API_KEY:
    print("WARNING: SERPAPI_API_KEY environment variable not set. SerpAPI fetching will be skipped.", flush=True)

# --- Kafka Producer Connection ---
producer = None
kafka_max_retries = 20
kafka_retry_delay_seconds = 5

print(f"Attempting to connect to Kafka at {KAFKA_BROKER}...", flush=True)

for i in range(kafka_max_retries):
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        print("Successfully connected to Kafka!", flush=True)
        break
    except NoBrokersAvailable:
        print(f"Attempt {i+1}/{kafka_max_retries}: Kafka broker not yet available. Retrying in {kafka_retry_delay_seconds} seconds...", flush=True)
        time.sleep(kafka_retry_delay_seconds)
    except Exception as e:
        print(f"An unexpected error occurred during Kafka connection attempt {i+1}/{kafka_max_retries}: {e}", flush=True)
        time.sleep(kafka_retry_delay_seconds)

if producer is None:
    print("Failed to connect to Kafka after multiple retries. Exiting.", flush=True)
    sys.exit(1)


# --- Fetching Functions for Each API ---

def fetch_newsapi_articles():
    if not NEWS_API_KEY: return []
    params = {
        'q': NEWS_API_QUERY, 'language': NEWS_API_LANGUAGE,
        'sortBy': NEWS_API_SORT_BY, 'pageSize': NEWS_API_PAGE_SIZE,
        'apiKey': NEWS_API_KEY
    }
    try:
        print(f"Fetching NewsAPI articles for '{NEWS_API_QUERY}'...", flush=True)
        response = requests.get(NEWS_API_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        print(f"Successfully fetched {len(articles)} articles from NewsAPI.", flush=True)
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from NewsAPI: {e}", flush=True)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding NewsAPI response: {e}", flush=True)
        return []

def fetch_guardian_articles():
    if not GUARDIAN_API_KEY: return []
    params = {
        'q': GUARDIAN_API_QUERY, 'api-key': GUARDIAN_API_KEY,
        'show-fields': GUARDIAN_API_SHOW_FIELDS, 'page-size': GUARDIAN_API_PAGE_SIZE
    }
    try:
        print(f"Fetching Guardian articles for '{GUARDIAN_API_QUERY}'...", flush=True)
        response = requests.get(GUARDIAN_API_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get('response', {}).get('results', [])
        print(f"Successfully fetched {len(articles)} articles from The Guardian.", flush=True)
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from The Guardian API: {e}", flush=True)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding Guardian API response: {e}", flush=True)
        return []

def fetch_mediastack_articles():
    if not MEDIASTACK_API_KEY: return []
    params = {
        'access_key': MEDIASTACK_API_KEY,
        'keywords': MEDIASTACK_API_QUERY,
        'languages': MEDIASTACK_API_LANGUAGES,
        'limit': MEDIASTACK_API_LIMIT
    }
    try:
        print(f"Fetching MediaStack articles for '{MEDIASTACK_API_QUERY}'...", flush=True)
        response = requests.get(MEDIASTACK_API_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get('data', [])
        print(f"Successfully fetched {len(articles)} articles from MediaStack.", flush=True)
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from MediaStack API: {e}", flush=True)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding MediaStack response: {e}", flush=True)
        return []

def fetch_reddit_articles():
    all_reddit_posts = []
    headers = {'User-Agent': REDDIT_USER_AGENT}
    for subreddit in REDDIT_SUBREDDITS:
        url = f"{REDDIT_BASE_URL}{subreddit}/top.json?limit={REDDIT_POST_LIMIT}"
        try:
            print(f"Fetching Reddit posts from r/{subreddit}...", flush=True)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            posts = response.json().get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                if post_data:
                    all_reddit_posts.append(post_data)
            print(f"Successfully fetched {len(posts)} posts from r/{subreddit}.", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Reddit API (r/{subreddit}): {e}", flush=True)
        except json.JSONDecodeError as e:
            print(f"Error decoding Reddit response (r/{subreddit}): {e}", flush=True)
        time.sleep(1) # Small delay between subreddits to be polite
    return all_reddit_posts

def fetch_serpapi_articles():
    if not SERPAPI_API_KEY: return []
    all_serpapi_news = []
    
    for query in SERPAPI_QUERIES:
        params = {
            "engine": "google",
            "q": query,
            "tbm": "nws",  # news search
            "api_key": SERPAPI_API_KEY,
            "num": SERPAPI_NEWS_LIMIT # Limit number of results
        }
        try:
            print(f"Fetching SerpAPI articles for '{query}'...", flush=True)
            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            
            for article in news_results:
                all_serpapi_news.append(article)
            print(f"Successfully fetched {len(news_results)} articles from SerpAPI for '{query}'.", flush=True)
        except Exception as e: # Catching general exception as SerpAPI client might raise various errors
            print(f"Error fetching from SerpAPI for '{query}': {e}", flush=True)
        
        time.sleep(0.5) # Polite API usage between queries
    return all_serpapi_news


# --- Main Loop to Fetch from All APIs and Send to Kafka ---

if __name__ == "__main__":
    while True:
        all_articles_to_send = []

        # 1. Fetch from NewsAPI.org
        newsapi_articles = fetch_newsapi_articles()
        for article in newsapi_articles:
            processed_article = {
                "title": article.get('title', 'No Title'),
                "description": article.get('description') or article.get('content', 'No Description'),
                "url": article.get('url', ''),
                "publishedAt": article.get('publishedAt', datetime.datetime.utcnow().isoformat() + 'Z')
            }
            all_articles_to_send.append(processed_article)
            
        # 2. Fetch from The Guardian API
        guardian_articles = fetch_guardian_articles()
        for article in guardian_articles:
            title = article.get('webTitle', 'No Title')
            description = article.get('fields', {}).get('bodyText')
            if not description:
                description = article.get('fields', {}).get('standfirst')
            if not description:
                description = title # Fallback to title if no description/standfirst

            processed_article = {
                "title": title,
                "description": description,
                "url": article.get('webUrl', ''),
                "publishedAt": article.get('webPublicationDate', datetime.datetime.utcnow().isoformat() + 'Z')
            }
            all_articles_to_send.append(processed_article)

        # 3. Fetch from MediaStack API
        mediastack_articles = fetch_mediastack_articles()
        for article in mediastack_articles:
            processed_article = {
                "title": article.get('title', 'No Title'),
                "description": article.get('description', 'No Description'),
                "url": article.get('url', ''),
                "publishedAt": article.get('published_at', datetime.datetime.utcnow().isoformat() + 'Z')
            }
            all_articles_to_send.append(processed_article)

        # 4. Fetch from Reddit API
        reddit_posts = fetch_reddit_articles()
        for post_data in reddit_posts:
            title = post_data.get('title', 'No Title')
            # Reddit posts have 'selftext' (the body) or just a 'url' for link posts
            description = post_data.get('selftext', post_data.get('url', 'No Description'))
            
            # Ensure the description is text, sometimes it's empty string for link posts
            if not description:
                description = title # Fallback
            
            # Reddit's 'created_utc' is a Unix timestamp; convert to ISO format
            published_at_utc = post_data.get('created_utc')
            if published_at_utc:
                dt_object = datetime.datetime.fromtimestamp(published_at_utc, tz=datetime.timezone.utc)
                published_at_iso = dt_object.isoformat().replace('+00:00', 'Z')
            else:
                published_at_iso = datetime.datetime.utcnow().isoformat() + 'Z'

            processed_article = {
                "title": title,
                "description": description,
                "url": post_data.get('url', ''),
                "publishedAt": published_at_iso
            }
            all_articles_to_send.append(processed_article)

        # 5. Fetch from SerpAPI - NEW INTEGRATION
        serpapi_articles = fetch_serpapi_articles()
        for article in serpapi_articles:
            # SerpAPI news_results format: title, snippet, link, date, source, etc.
            # Convert 'date' to 'publishedAt' if available, otherwise use current time
            published_at_str = article.get('date', '')
            try:
                # Attempt to parse common date formats from SerpAPI
                # This might need adjustment based on the exact date format in SerpAPI responses
                published_at = pd.to_datetime(published_at_str, errors='coerce', utc=True)
                if pd.isna(published_at):
                    published_at_iso = datetime.datetime.utcnow().isoformat() + 'Z'
                else:
                    published_at_iso = published_at.isoformat().replace('+00:00', 'Z')
            except Exception:
                published_at_iso = datetime.datetime.utcnow().isoformat() + 'Z' # Fallback

            processed_article = {
                "title": article.get("title", "No Title"),
                "description": article.get("snippet", "No Description"),
                "url": article.get("link", ""),
                "publishedAt": published_at_iso
            }
            all_articles_to_send.append(processed_article)


        print(f"Total articles collected from all sources: {len(all_articles_to_send)}", flush=True)

        if not all_articles_to_send:
            print("No articles from any source. Waiting before retrying all fetches...", flush=True)
            time.sleep(300) # Wait 5 minutes if nothing found
            continue

        # Send all collected articles to Kafka
        articles_sent_count = 0
        for article_to_send in all_articles_to_send:
            # Basic validation before sending to Kafka
            if article_to_send.get('title') and article_to_send.get('description') and article_to_send.get('url'):
                try:
                    producer.send(KAFKA_TOPIC, article_to_send)
                    producer.flush()
                    articles_sent_count += 1
                    # Log only first few chars of description for brevity
                    print(f"Sent: '{article_to_send['title'][:50]}...' (Source URL: '{article_to_send['url']}')", flush=True)
                except Exception as e:
                    print(f"Failed to send article to Kafka: {e}", flush=True)
            else:
                # This should ideally not happen if mapping is robust, but good for debugging
                print(f"Skipping article due to missing title/description/url after mapping: Title: '{article_to_send.get('title')}', URL: '{article_to_send.get('url')}'", flush=True)
        
        print(f"Successfully sent {articles_sent_count} articles to Kafka.", flush=True)

        # --- IMPORTANT: Manage API Rate Limits for All Sources ---
        # With 5 APIs, especially free tiers, you need very conservative delays.
        # NewsAPI: 100 requests/day
        # MediaStack: 250 requests/day
        # SerpAPI: Free plan usually 100 searches/month, may vary. Each query is a search.
        # Guardian: Generous for non-commercial
        # Reddit: Fairly generous, but be polite (User-Agent helps)
        # Fetching 10-20 articles from each source will quickly eat into daily/monthly limits.
        # A 6-hour delay should allow you to make 4 fetches per day per API,
        # which will exhaust NewsAPI (40 reqs) and MediaStack (40 reqs) limits over time.
        # SerpAPI's 100/month means ~3 queries/day. If you have multiple SerpAPI_QUERIES,
        # you'll hit limits fast. Adjust SERPAPI_NEWS_LIMIT and overall sleep time accordingly.
        
        # Consider a longer sleep or conditional fetching based on API usage
        print("Waiting 6 hours before next combined fetch to respect API limits...", flush=True)
        time.sleep(24 * 3600) # Wait 6 hours (21600 seconds)