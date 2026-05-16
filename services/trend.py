def get_trend(daily_rsi, weekly_rsi):

    if daily_rsi > 60 and weekly_rsi > 60:
        return "Strong Bullish"

    elif daily_rsi > 50 and weekly_rsi > 50:
        return "Bullish"

    elif daily_rsi < 40 and weekly_rsi < 40:
        return "Weak Bearish"

    else:
        return "Neutral"