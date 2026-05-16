import yfinance as yf


def get_data(ticker: str):

    daily_df = yf.download(
        ticker,
        period="6mo",
        interval="1d",
        auto_adjust=True
    )

    weekly_df = yf.download(
        ticker,
        period="2y",
        interval="1wk",
        auto_adjust=True
    )

    nifty_df = yf.download(
        "^NSEI",
        period="6mo",
        interval="1d",
        auto_adjust=True
    )

    # =========================
    # FLATTEN COLUMNS SAFELY
    # =========================
    daily_df.columns = daily_df.columns.get_level_values(0) if hasattr(daily_df.columns, "levels") else daily_df.columns
    weekly_df.columns = weekly_df.columns.get_level_values(0) if hasattr(weekly_df.columns, "levels") else weekly_df.columns
    nifty_df.columns = nifty_df.columns.get_level_values(0) if hasattr(nifty_df.columns, "levels") else nifty_df.columns

    return daily_df, weekly_df, nifty_df