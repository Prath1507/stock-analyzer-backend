import yfinance as yf


def get_analyst_data(ticker):

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("regularMarketPrice")

        target_mean = info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        target_low = info.get("targetLowPrice")

        upside = None
        if current_price and target_mean:
            upside = ((target_mean - current_price) / current_price) * 100

        return {
            "target_mean": target_mean,
            "target_high": target_high,
            "target_low": target_low,
            "upside_percent": round(upside, 2) if upside else None
        }

    except:
        return {
            "target_mean": None,
            "target_high": None,
            "target_low": None,
            "upside_percent": None
        }