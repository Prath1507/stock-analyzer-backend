from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.data_loader import get_data
from services.indicators import compute_indicators
from services.trend import get_trend
from services.pivots import calculate_pivots
from services.breakout import detect_breakout
from services.scoring import calculate_score
from services.analyst import get_analyst_data
from services.news import get_stock_news
from services.news_sentiment import analyze_sentiment

app = FastAPI()

# =========================================
# CORS
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# HOME
# =========================================
@app.get("/")
def home():
    return {
        "message": "Stock Analyzer Running"
    }


# =========================================
# ANALYZE STOCK
# =========================================
@app.get("/analyze/{stock}")
def analyze_stock(stock: str):

    ticker = stock.upper() + ".NS"

    # =========================================
    # LOAD DATA
    # =========================================
    daily_df, weekly_df, nifty_df = get_data(ticker)

    if daily_df.empty or weekly_df.empty:
        return {
            "error": "Stock not found"
        }

    # =========================================
    # INDICATORS
    # =========================================
    indicators = compute_indicators(
        daily_df,
        weekly_df,
        nifty_df
    )

    # =========================================
    # PIVOT LEVELS
    # =========================================
    pivots = calculate_pivots(daily_df)

    # =========================================
    # BREAKOUT ENGINE
    # =========================================
    signal_data = detect_breakout(
        indicators["price"],
        pivots,
        daily_df,
        indicators
    )

    # =========================================
    # SWING SCORE
    # =========================================
    score = calculate_score(
        indicators,
        pivots,
        signal_data
    )

    # =========================================
    # RATING ENGINE
    # =========================================
    if score >= 80:
        rating = "STRONG BUY"

    elif score >= 65:
        rating = "BUY"

    elif score >= 50:
        rating = "HOLD"

    else:
        rating = "AVOID"

    # =========================================
    # TREND ENGINE
    # =========================================
    trend = get_trend(
        indicators["daily_rsi"],
        indicators["weekly_rsi"]
    )

    # =========================================
    # ANALYST DATA
    # =========================================
    analyst_data = get_analyst_data(ticker)

    # =========================================
    # NEWS
    # =========================================
    news_data = get_stock_news(stock)

    # =========================================
    # NEWS SENTIMENT
    # =========================================
    sentiment = analyze_sentiment(news_data)

    # =========================================
    # FINAL RESPONSE
    # =========================================
    return {

        # BASIC
        "stock": stock.upper(),
        "price": indicators["price"],

        # RSI
        "daily_rsi": indicators["daily_rsi"],
        "weekly_rsi": indicators["weekly_rsi"],

        # MOMENTUM
        "momentum_5d": indicators["momentum_5d"],
        "relative_strength": indicators["relative_strength"],

        # PRICE ACTION
        "close_strength": indicators["close_strength"],
        "volume_ratio": indicators["volume_ratio"],

        # TREND
        "trend": trend,

        # PIVOTS
        "pivot_levels": pivots,

        # BREAKOUT
        "signal": signal_data["signal"],
        "breakout": signal_data["breakout"],
        "strong_breakout": signal_data["strong_breakout"],
        "weak_breakout": signal_data["weak_breakout"],

        # SCORE
        "score": score,
        "rating": rating,

        # ANALYST
        "analyst": analyst_data,

        # NEWS
        "news": news_data,

        # SENTIMENT
        "news_sentiment": sentiment
    }