import re


positive_words = [
    "rise", "surge", "jump", "strong", "growth", "profit", "record",
    "beats", "upgrade", "positive", "gain", "outperform"
]

negative_words = [
    "fall", "drop", "decline", "loss", "weak", "miss", "downgrade",
    "pressure", "concern", "slump"
]


def analyze_sentiment(news_list):

    score = 0
    total = 0

    for news in news_list:

        title = news.get("title", "")
        text = title.lower()

        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)

        score += (pos - neg)
        total += 1

    if total == 0:
        return {
            "sentiment_score": 0,
            "sentiment": "NEUTRAL"
        }

    final_score = score / total

    if final_score > 0.5:
        sentiment = "BULLISH"
    elif final_score < -0.5:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"

    return {
        "sentiment_score": round(final_score, 2),
        "sentiment": sentiment
    }