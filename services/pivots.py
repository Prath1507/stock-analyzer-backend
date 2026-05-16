def calculate_pivots(daily_df):

    prev = daily_df.iloc[-2]  # previous completed candle

    high = float(prev["High"])
    low = float(prev["Low"])
    close = float(prev["Close"])

    # =========================
    # CLASSIC PIVOT FORMULA
    # =========================
    pivot = (high + low + close) / 3

    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)

    return {
        "pivot": round(pivot, 2),
        "r1": round(r1, 2),
        "r2": round(r2, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2)
    }