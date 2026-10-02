import base64, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .metrics import summary, breakdown, monthly_returns, equity_curve, prop_firm_check

BLUE, ORANGE, RED, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#e34948", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})


def _png(fig) -> str:
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=110, bbox_inches="tight"); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)


def charts(df, start_balance, save_dir=None):
    eq = equity_curve(df, start_balance)
    out = {}
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(eq.index, eq.values, color=BLUE, lw=1.8); a1.set_ylabel("Equity"); a1.set_title("Equity curve and drawdown", loc="left")
    dd = (eq / eq.cummax() - 1) * 100
    a2.fill_between(dd.index, dd.values, 0, color=RED, alpha=0.35, lw=0); a2.set_ylabel("DD %")
    _style(a1); _style(a2); out["equity"] = fig
    m = monthly_returns(df, start_balance)
    fig, ax = plt.subplots(figsize=(9, 1.2 + 0.5 * len(m)))
    v = np.nanmax(np.abs(m.values)) or 1
    ax.imshow(m.values, cmap="RdBu", vmin=-v, vmax=v, aspect="auto")
    ax.set_xticks(range(12), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][:m.shape[1]] if m.shape[1] == 12 else [str(c) for c in m.columns])
    ax.set_yticks(range(len(m)), m.index)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if not np.isnan(m.values[i, j]):
                ax.text(j, i, f"{m.values[i, j]:+.1f}%", ha="center", va="center", fontsize=9, color="white" if abs(m.values[i, j]) > 0.6 * v else INK)
    ax.set_title("Monthly returns", loc="left"); out["monthly"] = fig
    h = df.groupby(df.open_time.dt.hour)["net"].sum()
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.bar(h.index, h.values, color=[BLUE if x >= 0 else ORANGE for x in h.values], width=0.7)
    ax.axhline(0, color=MUTED, lw=1); ax.set_xlabel("Entry hour"); ax.set_ylabel("Net P/L"); ax.set_title("P/L by entry hour", loc="left")
    _style(ax); out["hours"] = fig
    if save_dir:
        for k, f in out.items():
            f.savefig(f"{save_dir}/{k}.png", dpi=110, bbox_inches="tight")
    return out


def html_report(df, start_balance: float, title: str = "Trading performance report", save_dir=None) -> str:
    s = summary(df, start_balance); p = prop_firm_check(df, start_balance)
    imgs = {k: _png(f) for k, f in charts(df, start_balance, save_dir).items()}
    row = lambda d: "".join(f"<tr><td>{k}</td><td><b>{v}</b></td></tr>" for k, v in d.items())
    css = ("body{font-family:Segoe UI,Arial,sans-serif;max-width:980px;margin:24px auto;color:#0b0b0b;padding:0 16px}"
           "table{border-collapse:collapse;margin:8px 0 20px}td,th{border-bottom:1px solid #e4e3df;padding:5px 12px;text-align:left}"
           "h1{margin-bottom:4px}h2{margin-top:28px}.g{display:grid;grid-template-columns:1fr 1fr;gap:24px}img{max-width:100%}")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>
<h1>{title}</h1><p>{df.close_time.min():%d %b %Y} to {df.close_time.max():%d %b %Y} · starting balance {start_balance:,.0f}</p>
<div class="g"><div><h2>Summary</h2><table>{row(s)}</table></div><div><h2>Prop-firm rule check</h2><table>{row(p)}</table></div></div>
<img src="data:image/png;base64,{imgs['equity']}"><h2>By symbol</h2>{breakdown(df, 'symbol').to_html()}
<h2>By side</h2>{breakdown(df, 'side').to_html()}<img src="data:image/png;base64,{imgs['monthly']}">
<img src="data:image/png;base64,{imgs['hours']}"></body></html>"""
