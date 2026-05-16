def calculate_score(indicators, pivots, signal_data):

    score = 0

    rsi = indicators["daily_rsi"]
    weekly_rsi = indicators["weekly_rsi"]
    momentum = indicators["momentum_5d"]
    rs = indicators["relative_strength"]
    vol = indicators["volume_ratio"]
    close_strength = indicators["close_strength"]

    signal = signal_data["signal"]

    # =========================
    # RSI SCORE (0–20)
    # =========================
    if 55 <= rsi <= 70:
        score += 20
    elif 50 <= rsi < 55 or 70 < rsi <= 75:
        score += 12
    elif rsi > 75:
        score += 8
    else:
        score += 5

    # =========================
    # WEEKLY TREND SCORE (0–15)
    # =========================
    if weekly_rsi > 55:
        score += 15
    elif weekly_rsi > 50:
        score += 10
    else:
        score += 5

    # =========================
    # MOMENTUM SCORE (0–20)
    # =========================
    if momentum > 5:
        score += 20
    elif momentum > 2:
        score += 12
    elif momentum > 0:
        score += 8
    else:
        score += 3

    # =========================
    # RELATIVE STRENGTH (0–15)
    # =========================
    if rs > 5:
        score += 15
    elif rs > 0:
        score += 10
    else:
        score += 5

    # =========================
    # VOLUME SCORE (0–15)
    # =========================
    if vol > 1.5:
        score += 15
    elif vol > 1:
        score += 10
    else:
        score += 5

    # =========================
    # CLOSE STRENGTH (0–10)
    # =========================
    if close_strength > 0.7:
        score += 10
    elif close_strength > 0.5:
        score += 7
    else:
        score += 3

    # =========================
    # SIGNAL BONUS (0–5)
    # =========================
    if signal == "STRONG BREAKOUT BUY":
        score += 5
    elif signal == "WEAK BREAKOUT - WAIT CONFIRMATION":
        score += 2
    elif signal == "BREAKDOWN - AVOID / EXIT":
        score -= 10

    return min(max(score, 0), 100)