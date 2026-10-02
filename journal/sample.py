import numpy as np
import pandas as pd


def make_sample_history(n: int = 400, seed: int = 11) -> pd.DataFrame:
    """Synthetic closed-trade history in the same columns as an MT5 'Positions' export.
    Random, made-up trades, used only to demonstrate the report."""
    rng = np.random.default_rng(seed)
    symbols = np.array(["XAUUSD", "EURUSD", "US500", "GBPUSD", "NAS100"])
    t_open = pd.Timestamp("2025-01-06 08:00") + pd.to_timedelta(np.sort(rng.uniform(0, 365 * 24, n)), unit="h")
    t_open = t_open.floor("min")
    hold = pd.to_timedelta(rng.gamma(2.0, 3.0, n), unit="h").floor("min")
    side = rng.choice(["buy", "sell"], n)
    sym = rng.choice(symbols, n, p=[0.35, 0.2, 0.2, 0.15, 0.1])
    risk = 50.0                                                     # risk per trade in account currency
    R = np.where(rng.random(n) < 0.42, rng.normal(1.6, 0.5, n), rng.normal(-0.95, 0.15, n))
    profit = np.round(R * risk, 2)
    commission = -np.round(rng.uniform(0.5, 3.5, n), 2)
    swap = np.round(np.where(hold > pd.Timedelta("20h"), -rng.uniform(0, 4, n), 0.0), 2)
    return pd.DataFrame({"Time": t_open, "Position": np.arange(100000, 100000 + n), "Symbol": sym, "Type": side,
                         "Volume": np.round(rng.uniform(0.05, 1.0, n), 2), "Time.1": t_open + hold,
                         "Commission": commission, "Swap": swap, "Profit": profit})
