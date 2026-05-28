import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import requests
from io import StringIO

warnings.filterwarnings("ignore")


# ======================================
# RSI
# ======================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))


# ======================================
# CLOSE STRENGTH
# ======================================
def close_strength(df):
    return (
        (df["Close"].iloc[-1] - df["Low"].iloc[-1]) /
        (df["High"].iloc[-1] - df["Low"].iloc[-1] + 1e-9)
    )


# ======================================
# NSE500
# ======================================
def get_nse500_stocks():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(StringIO(r.text))

        return df["Symbol"].dropna().tolist()

    except Exception as e:
        print("NSE fetch error:", e)
        return []


# ======================================
# DOWNLOAD
# ======================================
def bulk_download(symbols):
    try:
        return yf.download(
            tickers=symbols,
            period="6mo",
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )
    except:
        return pd.DataFrame()


# ======================================
# MAIN SCANNER
# ======================================
def scan_volume_swing_stocks():

    stocks = get_nse500_stocks()
    symbols = [s + ".NS" for s in stocks]

    data = bulk_download(symbols)

    results = []

    for symbol in symbols:
        try:
            if symbol not in data:
                continue

            df = data[symbol].dropna()

            if len(df) < 60:
                continue

            price = df["Close"].iloc[-1]
            prev_close = df["Close"].iloc[-2]
            prev_high = df["High"].iloc[-2]

            # ======================
            # VOLUME
            # ======================
            volume_today = df["Volume"].iloc[-1]
            volume_prev = df["Volume"].iloc[-2]
            avg_volume_20 = df["Volume"].rolling(20).mean().iloc[-1]

            if pd.isna(avg_volume_20):
                continue

            # ======================
            # INDICATORS
            # ======================
            rsi = calculate_rsi(df["Close"]).iloc[-1]

            weekly = df.resample("W").last()
            weekly_rsi = calculate_rsi(weekly["Close"]).iloc[-1]

            dma20 = df["Close"].rolling(20).mean().iloc[-1]
            dma50 = df["Close"].rolling(50).mean().iloc[-1]

            strength = close_strength(df)

            momentum_5d = (price - df["Close"].iloc[-6]) / df["Close"].iloc[-6]
            daily_momentum = (price - prev_close) / prev_close

            stock_change = daily_momentum

            relative_strength = stock_change  # simplified (you can subtract Nifty if needed)

            volume_ratio = volume_today / (avg_volume_20 + 1e-9)

            # ======================================
            # PRICE ACTION FILTER (UNCHANGED)
            # ======================================
            if not (
                price > 100 and
                volume_today > volume_prev and
                price > prev_high and
                avg_volume_20 > 200000
            ):
                continue

            # ======================================
            # FINAL FILTER (UPDATED EXACTLY AS REQUESTED)
            # ======================================
            if not (
                price > dma20 and
                dma20 > dma50 and

                # DAILY RSI
                40 <= rsi <= 65 and

                # WEEKLY RSI
                50 <= weekly_rsi <= 65 and

                # CLOSE STRENGTH
                strength > 0.70 and

                # RELATIVE STRENGTH
                relative_strength > 0 and

                # 5 DAY MOMENTUM
                0 < momentum_5d * 100 < 5 and

                # 1 DAY MOMENTUM
                0 < daily_momentum * 100 < 4
            ):
                continue

            # ======================================
            # SCORE
            # ======================================
            score = (
                volume_ratio * 30 +
                strength * 25 +
                momentum_5d * 100 * 20 +
                (rsi / 100) * 10 +
                stock_change * 100 * 15
            )

            results.append({
                "stock": symbol.replace(".NS", ""),
                "price": round(float(price), 2),

                "daily_rsi": round(float(rsi), 2),
                "weekly_rsi": round(float(weekly_rsi), 2),

                "daily_change_percent": round(float(daily_momentum * 100), 2),

                "close_strength": round(float(strength), 2),

                "momentum_5d_percent": round(float(momentum_5d * 100), 2),

                "today_volume": int(volume_today),
                "avg_volume_20d": int(avg_volume_20),

                "volume_ratio": round(float(volume_ratio), 2),

                "score": round(float(score), 2)
            })

        except:
            continue

    df = pd.DataFrame(results)

    if df.empty:
        return {
            "scanner": "Volume Scanner",
            "stocks": []
        }

    df = df.sort_values("score", ascending=False)

    return {
        "scanner": "Volume Scanner",
        "total_stocks_found": len(df),
        "stocks": df.head(10).to_dict(orient="records")
    }