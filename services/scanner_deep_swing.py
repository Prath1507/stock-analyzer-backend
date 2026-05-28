import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")


# ======================================
# RSI CALCULATION
# ======================================
def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


# ======================================
# CLOSE STRENGTH
# ======================================
def close_strength(df):

    return (
        (df['Close'].iloc[-1] - df['Low'].iloc[-1]) /
        (df['High'].iloc[-1] - df['Low'].iloc[-1] + 1e-9)
    )


# ======================================
# GET NSE500 LIST
# ======================================
def get_nse500():

    urls = [
        "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
        "https://www1.nseindia.com/content/indices/ind_nifty500list.csv"
    ]

    for url in urls:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            df = pd.read_csv(url, headers=headers)
            return df['Symbol'].tolist()

        except Exception as e:
            print(f"Failed NSE URL: {url} -> {e}")
            continue

    # SAFE FALLBACK (important for Render stability)
    return [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
        "SBIN", "LT", "ITC", "HINDUNILVR", "AXISBANK"
    ]


# ======================================
# FIXED SAFE DATA EXTRACTOR (IMPORTANT)
# ======================================
def safe_extract(data, symbol):
    try:
        if symbol not in data:
            return None

        df = data[symbol]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if len(df) == 0:
            return None

        return df

    except:
        return None


# ======================================
# FIXED NIFTY CHANGE
# ======================================
def get_nifty_change():

    df = yf.download(
        "^NSEI",
        period="2d",
        interval="5m",
        progress=False
    )

    if df.empty or len(df) < 50:
        return 0.0

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    if 'Datetime' not in df.columns:
        df.rename(columns={'index': 'Datetime'}, inplace=True)

    df['Date'] = pd.to_datetime(df['Datetime']).dt.date

    unique_dates = df['Date'].unique()

    if len(unique_dates) < 2:
        return 0.0

    yesterday = unique_dates[-2]
    today = unique_dates[-1]

    yest_df = df[df['Date'] == yesterday]

    prev_close = yest_df.iloc[-1]['Close']

    today_df = df[df['Date'] == today]

    current = today_df.iloc[-1]['Close']

    return (current - prev_close) / prev_close


# ======================================
# BULK DOWNLOAD
# ======================================
def bulk_download(symbols, period, interval):

    data = yf.download(
        tickers=symbols,
        period=period,
        interval=interval,
        group_by="ticker",
        threads=True,
        progress=False
    )

    return data


# ======================================
# MAIN DEEP SWING SCANNER (FIXED SAFETY ONLY)
# ======================================
def scan_swing_stocks():

    print("\nScanning NSE 500...\n")

    nifty_change = get_nifty_change()

    print(f"Nifty Daily Change: {round(nifty_change * 100, 2)}%\n")

    stocks = get_nse500()

    symbols = [s + ".NS" for s in stocks]

    print("Downloading Daily Data...")

    daily_data = bulk_download(symbols, "6mo", "1d")

    print("Downloading Weekly Data...")

    weekly_data = bulk_download(symbols, "1y", "1wk")

    results = []

    for symbol in symbols:

        try:

            # ================= SAFE FIX =================
            df = safe_extract(daily_data, symbol)
            weekly = safe_extract(weekly_data, symbol)

            if df is None or weekly is None:
                continue

            if len(df) < 60 or len(weekly) < 20:
                continue
            # ============================================

            # RSI
            df['RSI'] = calculate_rsi(df['Close'])
            weekly['RSI'] = calculate_rsi(weekly['Close'])

            rsi = df['RSI'].iloc[-1]
            weekly_rsi = weekly['RSI'].iloc[-1]

            price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]

            stock_change = (price - prev_close) / prev_close
            relative_strength = stock_change - nifty_change
            daily_momentum = stock_change * 100

            dma20 = df['Close'].rolling(20).mean().iloc[-1]
            dma50 = df['Close'].rolling(50).mean().iloc[-1]

            momentum_5d = (price - df['Close'].iloc[-6]) / df['Close'].iloc[-6]
            momentum_5d_percent = momentum_5d * 100

            strength = close_strength(df)

            avg_volume_20 = df['Volume'].rolling(20).mean().iloc[-1]
            today_volume = df['Volume'].iloc[-1]

            volume_ratio = today_volume / (avg_volume_20 + 1e-9)

            # CORE CONDITIONS (UNCHANGED)
            if (
                price > dma20 and
                dma20 > dma50 and
                45 <= rsi <= 65 and
                50 <= weekly_rsi <= 65 and
                strength > 0.70 and
                relative_strength > 0 and
                0 < momentum_5d_percent < 5 and
                0 < daily_momentum < 3
            ):

                score = (
                    relative_strength * 40 +
                    momentum_5d * 30 +
                    (rsi / 100) * 10 +
                    strength * 20
                )

                results.append({
                    "stock": symbol.replace(".NS", ""),
                    "price": round(float(price), 2),
                    "daily_rsi": round(float(rsi), 2),
                    "weekly_rsi": round(float(weekly_rsi), 2),
                    "daily_change_percent": round(float(daily_momentum), 2),
                    "relative_strength_percent": round(float(relative_strength * 100), 2),
                    "momentum_5d_percent": round(float(momentum_5d_percent), 2),
                    "close_strength": round(float(strength), 2),
                    "today_volume": int(today_volume),
                    "avg_volume_20d": int(avg_volume_20),
                    "volume_ratio": round(float(volume_ratio), 2),
                    "swing_score": round(float(score), 2),
                    "setup": "HEALTHY SWING"
                })

        except:
            continue

    result_df = pd.DataFrame(results)

    if result_df.empty:
        return {
            "scanner": "Deep Swing",
            "nifty_change": round(float(nifty_change * 100), 2),
            "total_stocks_found": 0,
            "stocks": []
        }

    result_df = result_df.sort_values("swing_score", ascending=False)

    return {
        "scanner": "Deep Swing",
        "nifty_change": round(float(nifty_change * 100), 2),
        "total_stocks_found": int(len(result_df)),
        "stocks": result_df.head(5).to_dict(orient="records")
    }