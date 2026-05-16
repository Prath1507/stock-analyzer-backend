def detect_breakout(price, pivots, daily_df, indicators):

    r1 = pivots["r1"]
    r2 = pivots["r2"]
    s1 = pivots["s1"]
    pivot = pivots["pivot"]

    volume_ratio = indicators["volume_ratio"]
    close_strength = indicators["close_strength"]
    rsi = indicators["daily_rsi"]

    # =========================
    # BREAKOUT CONDITIONS
    # =========================
    breakout = price > r1
    strong_breakout = price > r1 and volume_ratio > 1.2 and rsi > 60

    # =========================
    # WEAK BREAKOUT (FAKE MOVE)
    # =========================
    weak_breakout = price > r1 and volume_ratio < 1

    # =========================
    # BREAKDOWN CONDITIONS
    # =========================
    breakdown = price < s1

    # =========================
    # SIGNAL LOGIC
    # =========================
    if strong_breakout:
        signal = "STRONG BREAKOUT BUY"

    elif breakout and not strong_breakout:
        signal = "WEAK BREAKOUT - WAIT CONFIRMATION"

    elif breakdown:
        signal = "BREAKDOWN - AVOID / EXIT"

    elif price > pivot:
        signal = "BULLISH ZONE - RANGE TRADE"

    else:
        signal = "NEUTRAL ZONE - NO TRADE"

    return {
        "signal": signal,
        "breakout": breakout,
        "strong_breakout": strong_breakout,
        "weak_breakout": weak_breakout
    }