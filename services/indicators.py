from ta.momentum import RSIIndicator


def compute_indicators(daily_df, weekly_df, nifty_df):

    # =========================
    # SAFE SERIES (FIXED)
    # =========================
    daily_close = daily_df["Close"].astype(float).squeeze()
    weekly_close = weekly_df["Close"].astype(float).squeeze()
    nifty_close = nifty_df["Close"].astype(float).squeeze()

    # =========================
    # RSI
    # =========================
    daily_rsi = RSIIndicator(daily_close, window=14).rsi().iloc[-1]
    weekly_rsi = RSIIndicator(weekly_close, window=14).rsi().iloc[-1]

    # =========================
    # MOMENTUM
    # =========================
    stock_5d = (
        (daily_close.iloc[-1] - daily_close.iloc[-6]) /
        daily_close.iloc[-6]
    ) * 100

    nifty_5d = (
        (nifty_close.iloc[-1] - nifty_close.iloc[-6]) /
        nifty_close.iloc[-6]
    ) * 100

    relative_strength = stock_5d - nifty_5d

    # =========================
    # SAFE CANDLE VALUES (FIXED)
    # =========================
    high = float(daily_df["High"].iloc[-1])
    low = float(daily_df["Low"].iloc[-1])
    close = float(daily_df["Close"].iloc[-1])
    volume = float(daily_df["Volume"].iloc[-1])

    # =========================
    # CLOSE STRENGTH
    # =========================
    rng = high - low
    close_strength = (close - low) / rng if rng != 0 else 0

    # =========================
    # VOLUME RATIO
    # =========================
    avg_volume = float(daily_df["Volume"].tail(20).mean())
    volume_ratio = volume / avg_volume if avg_volume != 0 else 0

    return {
        "daily_rsi": round(float(daily_rsi), 2),
        "weekly_rsi": round(float(weekly_rsi), 2),
        "momentum_5d": round(float(stock_5d), 2),
        "relative_strength": round(float(relative_strength), 2),
        "close_strength": round(float(close_strength), 2),
        "volume_ratio": round(float(volume_ratio), 2),
        "price": round(float(close), 2)
    }