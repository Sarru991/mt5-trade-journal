"""Usage:
    python examples/make_report.py                       # demo with synthetic sample trades
    python examples/make_report.py my_history.csv 10000  # your MT5 export + starting balance
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from journal.load import load_history
from journal.sample import make_sample_history
from journal.report import html_report

base = os.path.join(os.path.dirname(__file__), "..")
if len(sys.argv) > 1:
    df, bal = load_history(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 10000.0
else:
    df, bal = load_history(make_sample_history()), 10000.0
html = html_report(df, bal, save_dir=os.path.join(base, "docs"))
out = os.path.join(base, "report.html")
open(out, "w", encoding="utf-8").write(html)
print("Report written to", os.path.abspath(out))
