import yfinance as yf
import pandas as pd
import numpy as np
import warnings

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
# NSE 500 LIST
# ======================================
def get_nse500_stocks():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    df = pd.read_csv(url)
    symbols = df["Symbol"].dropna().tolist()
    return [s.strip() for s in symbols]


# ======================================
# BULK DOWNLOAD
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
# NIFTY CHANGE
# ======================================
def get_nifty_change():
    try:
        df = yf.download("^NSEI", period="5d", interval="1d", progress=False)

        if df.empty or len(df) < 2:
            return 0.0

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]

    except:
        return 0.0


# ======================================
# MAIN BREAKOUT SCANNER
# ======================================
def scan_breakout_stocks():

    stocks = get_nse500_stocks()
    symbols = [s + ".NS" for s in stocks]

    data = bulk_download(symbols)

    nifty_change = get_nifty_change()

    results = []

    for symbol in symbols:
        try:

            if symbol not in data:
                continue

            df = data[symbol].dropna()

            if len(df) < 60:
                continue

            # ======================
            # INDICATORS (UNCHANGED)
            # ======================
            df["20_DMA"] = df["Close"].rolling(20).mean()
            df["50_DMA"] = df["Close"].rolling(50).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            df = df.dropna()

            if len(df) < 30:
                continue

            latest = df.iloc[-1]
            last_20 = df.tail(20)

            close = float(latest["Close"])
            dma20 = float(latest["20_DMA"])
            dma50 = float(latest["50_DMA"])
            rsi = float(latest["RSI"])

            high_20 = float(last_20["High"].max())
            low_20 = float(last_20["Low"].min())

            # ======================
            # ORIGINAL CONDITIONS (UNCHANGED)
            # ======================
            uptrend = close > dma20 and dma20 > dma50
            tight_range = (high_20 - low_20) / close < 0.10
            near_breakout = close >= high_20 * 0.97
            rsi_ok = 45 < rsi < 70

            if not (uptrend and tight_range and near_breakout and rsi_ok):
                continue

            # ======================
            # EXTRA METRICS (NEW)
            # ======================
            strength = close_strength(df)

            weekly = df.resample("W").last()
            weekly_rsi = calculate_rsi(weekly["Close"]).iloc[-1]

            momentum_5d = (close - df["Close"].iloc[-6]) / df["Close"].iloc[-6]
            daily_momentum = (close - df["Close"].iloc[-2]) / df["Close"].iloc[-2]

            relative_strength = (daily_momentum - nifty_change)

            # ======================
            # FINAL FILTER (YOUR REQUIREMENT)
            # ======================
            if not (
                close > dma20 and
                dma20 > dma50 and

                40 <= rsi <= 65 and
                40 <= weekly_rsi <= 65 and

                strength > 0.70 and

                relative_strength > 0 and

                0 < momentum_5d * 100 < 5 and
                0 < daily_momentum * 100 < 3
            ):
                continue

            # ======================
            # SCORE (UNCHANGED LOGIC)
            # ======================
            compression = (high_20 - low_20) / close
            breakout_power = (close - dma20) / dma20

            score = (
                (1 - compression) * 2 +
                breakout_power * 5 +
                (rsi / 100)
            )

            results.append({
                "stock": symbol.replace(".NS", ""),
                "price": round(close, 2),
                "rsi": round(rsi, 2),
                "weekly_rsi": round(weekly_rsi, 2),
                "range_percent": round(compression * 100, 2),
                "strength": round(strength, 2),
                "relative_strength": round(relative_strength * 100, 2),
                "momentum_5d_percent": round(momentum_5d * 100, 2),
                "daily_momentum_percent": round(daily_momentum * 100, 2),
                "score": round(score, 3)
            })

        except:
            continue

    df = pd.DataFrame(results)

    if df.empty:
        return {
            "scanner": "Breakout Scanner",
            "total_stocks_found": 0,
            "stocks": []
        }

    df = df.sort_values("score", ascending=False)

    return {
        "scanner": "Breakout Scanner",
        "total_stocks_found": int(len(df)),
        "stocks": df.head(10).to_dict(orient="records")
    }