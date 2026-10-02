import numpy as np
import pandas as pd


def equity_curve(df: pd.DataFrame, start_balance: float) -> pd.Series:
    return start_balance + df.set_index("close_time")["net"].cumsum()


def max_drawdown(eq: pd.Series) -> tuple:
    peak = eq.cummax()
    dd = eq - peak
    i = dd.idxmin()
    return float(dd.min()), float((dd / peak).min() * 100), i


def summary(df: pd.DataFrame, start_balance: float) -> dict:
    net = df["net"]
    wins, losses = net[net > 0], net[net <= 0]
    eq = equity_curve(df, start_balance)
    dd_abs, dd_pct, _ = max_drawdown(pd.concat([pd.Series([start_balance], index=[eq.index[0] - pd.Timedelta("1s")]), eq]))
    streak = (net <= 0).astype(int)
    longest_loss = int(streak.groupby((streak != streak.shift()).cumsum()).cumsum().max())
    daily = df.groupby(df.close_time.dt.date)["net"].sum()
    return {
        "Trades": len(df),
        "Net profit": round(net.sum(), 2),
        "Return %": round(net.sum() / start_balance * 100, 2),
        "Win rate %": round(len(wins) / len(df) * 100, 1),
        "Profit factor": round(wins.sum() / -losses.sum(), 2) if len(losses) and losses.sum() < 0 else np.inf,
        "Avg win": round(wins.mean(), 2),
        "Avg loss": round(losses.mean(), 2),
        "Expectancy / trade": round(net.mean(), 2),
        "Max drawdown": round(dd_abs, 2),
        "Max drawdown %": round(dd_pct, 2),
        "Longest losing streak": longest_loss,
        "Worst day": round(daily.min(), 2),
        "Costs (commission + swap)": round((df.commission + df.swap).sum(), 2),
    }


def breakdown(df: pd.DataFrame, by: str) -> pd.DataFrame:
    g = df.groupby(by)["net"]
    out = pd.DataFrame({"trades": g.size(), "net": g.sum().round(2), "win %": g.apply(lambda s: (s > 0).mean() * 100).round(1),
                        "avg": g.mean().round(2)})
    return out.sort_values("net", ascending=False)


def monthly_returns(df: pd.DataFrame, start_balance: float) -> pd.DataFrame:
    eq = equity_curve(df, start_balance)
    m = eq.resample("ME").last()
    prev = m.shift(1).fillna(start_balance)
    r = (m / prev - 1) * 100
    t = pd.DataFrame({"year": r.index.year, "month": r.index.month, "ret": r.values})
    return t.pivot(index="year", columns="month", values="ret")


def prop_firm_check(df: pd.DataFrame, start_balance: float, daily_limit_pct: float = 5.0, max_dd_pct: float = 10.0) -> dict:
    """Would this history have breached typical prop-firm limits? (closed-trade basis, static drawdown)"""
    daily = df.groupby(df.close_time.dt.date)["net"].sum()
    eq = equity_curve(df, start_balance)
    return {"Daily loss limit %": daily_limit_pct, "Worst day %": round(daily.min() / start_balance * 100, 2),
            "Daily limit breached": bool((daily < -start_balance * daily_limit_pct / 100).any()),
            "Max DD limit %": max_dd_pct, "Lowest equity vs start %": round((eq.min() / start_balance - 1) * 100, 2),
            "Max DD breached": bool(eq.min() < start_balance * (1 - max_dd_pct / 100))}
