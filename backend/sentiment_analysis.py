from textblob import TextBlob

def analyze_sentiment(text):
    if not text:
        return {"polarity": 0, "sentiment": "neutral"}
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"polarity": polarity, "sentiment": sentiment} 