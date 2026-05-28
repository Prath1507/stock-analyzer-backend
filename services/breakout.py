import pandas as pd
import numpy as np


def detect_breakout(price, pivots, daily_df, indicators):

    # ==========================================
    # PIVOTS
    # ==========================================
    r1 = pivots["r1"]
    s1 = pivots["s1"]
    pivot = pivots["pivot"]

    # ==========================================
    # INDICATORS
    # ==========================================
    volume_ratio = indicators["volume_ratio"]
    close_strength = indicators["close_strength"]
    rsi = indicators["daily_rsi"]
    weekly_rsi = indicators.get("weekly_rsi", 0)
    momentum = indicators.get("momentum_5d", 0)
    rel_strength = indicators.get("relative_strength", 0)

    # ==========================================
    # LATEST CANDLE
    # ==========================================
    latest = daily_df.iloc[-1]

    open_price = latest["Open"]
    high = latest["High"]
    low = latest["Low"]
    close = latest["Close"]

    # ==========================================
    # CANDLE STRUCTURE
    # ==========================================
    body = abs(close - open_price)
    candle_range = high - low

    upper_wick = high - max(open_price, close)
    lower_wick = min(open_price, close) - low

    # Avoid divide error
    if candle_range == 0:
        candle_range = 0.01

    body_ratio = body / candle_range

    # ==========================================
    # MOVING AVERAGES
    # ==========================================
    daily_df["20DMA"] = daily_df["Close"].rolling(20).mean()
    daily_df["50DMA"] = daily_df["Close"].rolling(50).mean()
    daily_df["200DMA"] = daily_df["Close"].rolling(200).mean()

    ma20 = daily_df["20DMA"].iloc[-1]
    ma50 = daily_df["50DMA"].iloc[-1]
    ma200 = daily_df["200DMA"].iloc[-1]

    # ==========================================
    # TREND ANALYSIS
    # ==========================================
    bullish_trend = (
        close > ma20 and
        ma20 > ma50 and
        ma50 > ma200
    )

    strong_uptrend = (
        bullish_trend and
        close > ma20 * 1.02
    )

    # ==========================================
    # MULTI-YEAR RESISTANCE
    # Excluding current candle
    # ==========================================
    highs = daily_df["High"].iloc[:-1]

    high_20d = highs.tail(20).max()
    high_3m = highs.tail(63).max()
    high_6m = highs.tail(126).max()
    high_1y = highs.tail(252).max()
    high_3y = highs.tail(756).max()

    # ==========================================
    # BREAKOUT BUFFERS
    # ==========================================
    breakout_buffer = 1.005

    breakout_20d = close > high_20d * breakout_buffer
    breakout_3m = close > high_3m * breakout_buffer
    breakout_6m = close > high_6m * breakout_buffer
    breakout_1y = close > high_1y * breakout_buffer
    breakout_3y = close > high_3y * breakout_buffer

    # ==========================================
    # NEAR BREAKOUT SETUPS
    # ==========================================
    near_52w = (
        abs(close - high_1y) / high_1y < 0.02
    )

    near_3y = (
        abs(close - high_3y) / high_3y < 0.03
    )

    # ==========================================
    # VOLUME ANALYSIS
    # ==========================================
    weak_volume = volume_ratio < 1
    good_volume = volume_ratio > 1.3
    strong_volume = volume_ratio > 1.8
    explosive_volume = volume_ratio > 2.5

    # ==========================================
    # RSI ANALYSIS
    # ==========================================
    healthy_rsi = 55 <= rsi <= 75
    strong_rsi = rsi > 60
    overbought = rsi > 80

    # ==========================================
    # MOMENTUM ANALYSIS
    # ==========================================
    strong_momentum = momentum > 3
    strong_rs = rel_strength > 1.2

    # ==========================================
    # CLOSE QUALITY
    # ==========================================
    strong_close = close_strength > 0.7
    decent_close = close_strength > 0.6
    weak_close = close_strength < 0.5

    # ==========================================
    # FAKE BREAKOUT DETECTION
    # ==========================================
    large_upper_wick = upper_wick > body

    fake_breakout = (
        (
            breakout_20d or
            breakout_3m or
            breakout_1y
        )
        and
        (
            weak_close or
            weak_volume or
            large_upper_wick
        )
    )

    # ==========================================
    # EXTENDED MOVE
    # ==========================================
    extended_move = (
        close > ma20 * 1.12 or
        rsi > 82
    )

    # ==========================================
    # RANGE EXPANSION
    # ==========================================
    daily_df["Range"] = daily_df["High"] - daily_df["Low"]

    avg_range_5d = daily_df["Range"].tail(5).mean()

    explosive_candle = candle_range > avg_range_5d * 1.5

    # ==========================================
    # SIGNAL CLASSIFICATION
    # ==========================================
    signal = "NEUTRAL"

    # ==========================================
    # ELITE BREAKOUTS
    # ==========================================
    if (
        breakout_3y and
        explosive_volume and
        strong_close and
        healthy_rsi and
        strong_momentum and
        strong_rs and
        bullish_trend
    ):

        signal = "MAJOR 3-YEAR BREAKOUT"

    elif (
        breakout_1y and
        strong_volume and
        strong_close and
        bullish_trend and
        healthy_rsi
    ):

        signal = "52-WEEK HIGH BREAKOUT"

    elif (
        breakout_6m and
        strong_volume and
        strong_close and
        bullish_trend
    ):

        signal = "STRONG SWING BREAKOUT"

    # ==========================================
    # MOMENTUM IGNITION
    # ==========================================
    elif (
        breakout_3m and
        explosive_candle and
        explosive_volume and
        strong_close and
        strong_rsi
    ):

        signal = "MOMENTUM IGNITION"

    # ==========================================
    # EARLY SETUPS
    # ==========================================
    elif (
        near_52w and
        bullish_trend and
        decent_close and
        good_volume
    ):

        signal = "EARLY 52W BREAKOUT SETUP"

    elif (
        near_3y and
        bullish_trend and
        strong_rs
    ):

        signal = "EARLY MULTI-YEAR BREAKOUT"

    # ==========================================
    # FAILED BREAKOUTS
    # ==========================================
    elif fake_breakout:

        signal = "FAILED BREAKOUT"

    # ==========================================
    # WEAK BREAKOUTS
    # ==========================================
    elif breakout_20d:

        signal = "WEAK BREAKOUT - WAIT"

    # ==========================================
    # BREAKDOWNS
    # ==========================================
    elif close < s1:

        signal = "BREAKDOWN - AVOID"

    # ==========================================
    # BULLISH ZONE
    # ==========================================
    elif (
        close > pivot and
        bullish_trend
    ):

        signal = "BULLISH TREND"

    # ==========================================
    # EXTENDED WARNING
    # ==========================================
    if extended_move:
        signal += " | EXTENDED"

    # ==========================================
    # RETURN DATA
    # ==========================================
    return {

        "signal": signal,

        # Breakouts
        "breakout_20d": breakout_20d,
        "breakout_3m": breakout_3m,
        "breakout_6m": breakout_6m,
        "breakout_1y": breakout_1y,
        "breakout_3y": breakout_3y,

        # Setup Zones
        "near_52w": near_52w,
        "near_3y": near_3y,

        # Trend
        "bullish_trend": bullish_trend,
        "strong_uptrend": strong_uptrend,

        # Quality
        "fake_breakout": fake_breakout,
        "extended_move": extended_move,
        "explosive_candle": explosive_candle,

        # Levels
        "high_20d": round(high_20d, 2),
        "high_3m": round(high_3m, 2),
        "high_6m": round(high_6m, 2),
        "high_1y": round(high_1y, 2),
        "high_3y": round(high_3y, 2),

        # Extra
        "volume_ratio": round(volume_ratio, 2),
        "close_strength": round(close_strength, 2),
        "daily_rsi": round(rsi, 2),
        "weekly_rsi": round(weekly_rsi, 2),
        "relative_strength": round(rel_strength, 2),
    }