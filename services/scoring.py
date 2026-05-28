def calculate_score(indicators, pivots, signal_data, daily_df):

    score = 0

    # ==========================================
    # INDICATORS
    # ==========================================
    rsi = indicators["daily_rsi"]
    weekly_rsi = indicators["weekly_rsi"]
    momentum = indicators["momentum_5d"]
    rs = indicators["relative_strength"]
    vol = indicators["volume_ratio"]
    close_strength = indicators["close_strength"]

    signal = signal_data["signal"]

    latest_close = daily_df["Close"].iloc[-1]

    # ==========================================
    # MOVING AVERAGES
    # ==========================================
    ma20 = daily_df["Close"].rolling(20).mean().iloc[-1]
    ma50 = daily_df["Close"].rolling(50).mean().iloc[-1]
    ma200 = daily_df["Close"].rolling(200).mean().iloc[-1]

    # ==========================================
    # DISTANCE FROM MA20
    # ==========================================
    distance_from_ma20 = (
        (latest_close - ma20) / ma20
    ) * 100

    # ==========================================
    # TREND STRUCTURE SCORE (0–20)
    # ==========================================
    if (
        latest_close > ma20 and
        ma20 > ma50 and
        ma50 > ma200
    ):

        score += 20

    elif (
        latest_close > ma20 and
        ma20 > ma50
    ):

        score += 14

    elif latest_close > ma20:

        score += 8

    else:

        score += 3

    # ==========================================
    # DAILY RSI SCORE (0–15)
    # ==========================================
    if 55 <= rsi <= 68:

        score += 15

    elif 50 <= rsi < 55:

        score += 10

    elif 68 < rsi <= 75:

        score += 7

    elif 75 < rsi <= 80:

        score += 2

    elif rsi > 80:

        score -= 15

    else:

        score += 3

    # ==========================================
    # WEEKLY RSI SCORE (0–15)
    # ==========================================
    if 55 <= weekly_rsi <= 68:

        score += 15

    elif 68 < weekly_rsi <= 75:

        score += 8

    elif weekly_rsi > 75:

        score -= 10

    elif weekly_rsi > 50:

        score += 10

    else:

        score += 5

    # ==========================================
    # MOMENTUM QUALITY SCORE (0–20)
    # ==========================================
    if 2 <= momentum <= 8:

        score += 20

    elif 8 < momentum <= 12:

        score += 10

    elif 12 < momentum <= 15:

        score += 3

    elif 15 < momentum <= 20:

        score -= 12

    elif momentum > 20:

        score -= 25

    elif momentum > 0:

        score += 8

    else:

        score += 2

    # ==========================================
    # RELATIVE STRENGTH SCORE (0–15)
    # ==========================================
    if 1.5 <= rs <= 8:

        score += 15

    elif 8 < rs <= 15:

        score += 8

    elif rs > 15:

        score -= 8

    elif rs > 1:

        score += 12

    elif rs > 0:

        score += 7

    else:

        score += 2

    # ==========================================
    # VOLUME QUALITY SCORE (0–10)
    # ==========================================
    if 1.5 <= vol <= 4:

        score += 10

    elif 4 < vol <= 8:

        score += 6

    elif vol > 8:

        score -= 10

    elif vol > 1:

        score += 5

    else:

        score += 2

    # ==========================================
    # CLOSE STRENGTH SCORE (0–10)
    # ==========================================
    if close_strength > 0.8:

        score += 10

    elif close_strength > 0.7:

        score += 8

    elif close_strength > 0.6:

        score += 5

    elif close_strength > 0.5:

        score += 3

    else:

        score += 1

    # ==========================================
    # BREAKOUT QUALITY BONUS
    # ==========================================
    if "MAJOR 3-YEAR BREAKOUT" in signal:

        score += 15

    elif "52-WEEK HIGH BREAKOUT" in signal:

        score += 12

    elif "STRONG SWING BREAKOUT" in signal:

        score += 10

    elif "MOMENTUM IGNITION" in signal:

        score += 8

    elif "FAILED BREAKOUT" in signal:

        score -= 15

    elif "BREAKDOWN" in signal:

        score -= 20

    # ==========================================
    # EXTENDED STOCK PENALTIES
    # ==========================================
    if distance_from_ma20 > 15:

        score -= 15

    elif distance_from_ma20 > 10:

        score -= 8

    # ==========================================
    # OVERHEATED STOCK DETECTION
    # ==========================================
    overheated = (
        momentum > 15 or
        rsi > 78 or
        weekly_rsi > 75 or
        vol > 8
    )

    parabolic_move = (
        momentum > 20 and
        vol > 10
    )

    if overheated:

        score -= 15

    if parabolic_move:

        score -= 25

    # ==========================================
    # SCORE LIMIT
    # ==========================================
    score = max(min(score, 100), 0)

    # ==========================================
    # FINAL RATING
    # ==========================================
    if parabolic_move:

        rating = "PARABOLIC - AVOID FRESH ENTRY"

    elif overheated:

        rating = "EXTENDED - WAIT FOR PULLBACK"

    elif score >= 85:

        rating = "STRONG BUY"

    elif score >= 70:

        rating = "BUY"

    elif score >= 55:

        rating = "HOLD"

    else:

        rating = "AVOID"

    return {
        "score": round(score, 2),
        "rating": rating,
        "overheated": overheated,
        "parabolic_move": parabolic_move,
        "distance_from_ma20": round(distance_from_ma20, 2)
    }