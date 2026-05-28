 
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
from services.scanner_deep_swing import scan_swing_stocks
from services.scanner_volume import scan_volume_swing_stocks
from services.scanner_breakout import scan_breakout_stocks

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
    # ADVANCED SCORING ENGINE
    # =========================================
    score_data = calculate_score(
        indicators,
        pivots,
        signal_data,
        daily_df
    )

    score = float(score_data["score"])

    rating = score_data["rating"]

    overheated = bool(score_data["overheated"])

    parabolic_move = bool(
        score_data["parabolic_move"]
    )

    distance_from_ma20 = float(
        score_data["distance_from_ma20"]
    )

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

        # =====================================
        # BASIC
        # =====================================
        "stock": stock.upper(),

        "price": round(
            float(indicators["price"]), 2
        ),

        # =====================================
        # RSI
        # =====================================
        "daily_rsi": round(
            float(indicators["daily_rsi"]), 2
        ),

        "weekly_rsi": round(
            float(indicators["weekly_rsi"]), 2
        ),

        # =====================================
        # MOMENTUM
        # =====================================
        "momentum_5d": round(
            float(indicators["momentum_5d"]), 2
        ),

        "relative_strength": round(
            float(indicators["relative_strength"]), 2
        ),

        # =====================================
        # PRICE ACTION
        # =====================================
        "close_strength": round(
            float(indicators["close_strength"]), 2
        ),

        "volume_ratio": round(
            float(indicators["volume_ratio"]), 2
        ),

        # =====================================
        # TREND
        # =====================================
        "trend": trend,

        # =====================================
        # PIVOT LEVELS
        # =====================================
        "pivot_levels": {
            "pivot": round(
                float(pivots["pivot"]), 2
            ),
            "r1": round(
                float(pivots["r1"]), 2
            ),
            "r2": round(
                float(pivots["r2"]), 2
            ),
            "s1": round(
                float(pivots["s1"]), 2
            ),
            "s2": round(
                float(pivots["s2"]), 2
            ),
        },

        # =====================================
        # BREAKOUT SIGNAL
        # =====================================
        "signal": signal_data["signal"],

        # =====================================
        # BREAKOUT LEVELS
        # =====================================
        "breakout_20d": bool(
            signal_data["breakout_20d"]
        ),

        "breakout_3m": bool(
            signal_data["breakout_3m"]
        ),

        "breakout_6m": bool(
            signal_data["breakout_6m"]
        ),

        "breakout_1y": bool(
            signal_data["breakout_1y"]
        ),

        "breakout_3y": bool(
            signal_data["breakout_3y"]
        ),

        # =====================================
        # SETUP ZONES
        # =====================================
        "near_52w": bool(
            signal_data["near_52w"]
        ),

        "near_3y": bool(
            signal_data["near_3y"]
        ),

        # =====================================
        # TREND STRUCTURE
        # =====================================
        "bullish_trend": bool(
            signal_data["bullish_trend"]
        ),

        "strong_uptrend": bool(
            signal_data["strong_uptrend"]
        ),

        # =====================================
        # QUALITY CHECKS
        # =====================================
        "fake_breakout": bool(
            signal_data["fake_breakout"]
        ),

        "extended_move": bool(
            signal_data["extended_move"]
        ),

        "explosive_candle": bool(
            signal_data["explosive_candle"]
        ),

        # =====================================
        # RESISTANCE LEVELS
        # =====================================
        "high_20d": round(
            float(signal_data["high_20d"]), 2
        ),

        "high_3m": round(
            float(signal_data["high_3m"]), 2
        ),

        "high_6m": round(
            float(signal_data["high_6m"]), 2
        ),

        "high_1y": round(
            float(signal_data["high_1y"]), 2
        ),

        "high_3y": round(
            float(signal_data["high_3y"]), 2
        ),

        # =====================================
        # SCORE & RATING
        # =====================================
        "score": round(score, 2),

        "rating": rating,

        # =====================================
        # RISK ANALYSIS
        # =====================================
        "overheated": overheated,

        "parabolic_move": parabolic_move,

        "distance_from_ma20": round(
            distance_from_ma20, 2
        ),
         
        # =====================================
        # ANALYST DATA
        # =====================================
        "analyst": analyst_data,

        # =====================================
        # NEWS
        # =====================================
        "news": news_data,

        # =====================================
        # NEWS SENTIMENT
        # =====================================
        "news_sentiment": sentiment

        
    }

# =========================================
# DEEP SWING SCANNER (ADDED ONLY)
# =========================================
@app.get("/scanner/deep-swing")
def deep_swing_scanner():
    return scan_swing_stocks()


# =========================================
# VOLUME SCANNER (ADDED ONLY)
# =========================================
@app.get("/scanner/volume")
def volume_scanner():
    return scan_volume_swing_stocks()

@app.get("/scanner/breakout")
def breakout_scanner():
    return scan_breakout_stocks()