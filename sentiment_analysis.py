from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import plotly.express as px
import random
import os

# Set NLTK data path to a writable directory
nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Download required NLTK data with error handling
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('brown', quiet=True)
except Exception as e:
    print(f"Warning: NLTK data download failed - {str(e)}")

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    score = analyzer.polarity_scores(text)
    sentiment = 'Neutral'
    if score['compound'] >= 0.05:
        sentiment = 'Positive'
    elif score['compound'] <= -0.05:
        sentiment = 'Negative'
    return sentiment, score['compound']

def analyze_sentiment_textblob(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    sentiment = 'Neutral'
    if polarity > 0:
        sentiment = 'Positive'
    elif polarity < 0:
        sentiment = 'Negative'
    return sentiment, polarity

def get_keywords(text):
    try:
        blob = TextBlob(text)
        return blob.noun_phrases
    except:
        # Fallback to simple keyword extraction
        words = [word.lower() for word in text.split() if len(word) > 3]
        return list(set(words))[:5]  # Return first 5 unique words
