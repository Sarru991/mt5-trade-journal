import os, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from journal.load import load_history
from journal.sample import make_sample_history
from journal.metrics import summary, max_drawdown, prop_firm_check


def test_net_includes_costs():
    df = load_history(make_sample_history(50))
    assert (df.net == df.profit + df.commission + df.swap).all()


def test_max_drawdown_simple():
    eq = pd.Series([100, 120, 90, 130, 110], index=pd.date_range("2025-01-01", periods=5))
    dd_abs, dd_pct, _ = max_drawdown(eq)
    assert dd_abs == -30 and round(dd_pct, 2) == -25.0


def test_summary_and_prop_check():
    df = load_history(make_sample_history(200))
    s = summary(df, 10000)
    assert s["Trades"] == 200 and 0 < s["Win rate %"] < 100
    p = prop_firm_check(df, 10000, daily_limit_pct=0.1)
    assert p["Daily limit breached"] is True
