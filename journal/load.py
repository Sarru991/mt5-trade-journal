import pandas as pd

COLMAP = {"Time": "open_time", "Time.1": "close_time", "Position": "ticket", "Symbol": "symbol",
          "Type": "side", "Volume": "volume", "Commission": "commission", "Swap": "swap", "Profit": "profit"}


def load_history(path_or_df) -> pd.DataFrame:
    """Load MT5 'Positions' history (exported from the History tab as CSV/Excel) or a DataFrame.

    Returns one row per closed position with net P/L (profit + commission + swap)."""
    if isinstance(path_or_df, pd.DataFrame):
        df = path_or_df.copy()
    elif str(path_or_df).lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path_or_df)
    else:
        df = pd.read_csv(path_or_df)
    df = df.rename(columns={k: v for k, v in COLMAP.items() if k in df.columns})
    for c in ("open_time", "close_time"):
        df[c] = pd.to_datetime(df[c])
    for c in ("commission", "swap"):
        if c not in df:
            df[c] = 0.0
    df["net"] = df["profit"] + df["commission"] + df["swap"]
    df["side"] = df["side"].str.lower()
    return df.sort_values("close_time").reset_index(drop=True)
