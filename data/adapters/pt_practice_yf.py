# -*- coding: utf-8 -*-
"""
pt_practice_yf.py — PRACTICE P_t from real forward-24m returns (yfinance).

PURPOSE: a de-risking smoke test — does the pipeline produce a sane CRF on
REAL data, end to end? It is NOT a compliant P_t.

NON-COMPLIANT, on purpose:
  * reference class = a fixed diversified universe's historical 24m outcomes,
    NOT the locked 6-feature Mahalanobis class (§6.1);
  * universe is currently-listed only -> survivorship-biased (§6.4);
  * no point-in-time fundamentals.
What IS real: the forward-24m returns are real market outcomes; the histogram,
binning, smoothing and (paired with qt_options) the JSD are the real engine.
"""
from __future__ import annotations
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from taca_engine import hist_from_returns, smooth_normalize, measurable  # noqa: E402

# A deliberately diversified, currently-listed universe (survivorship-biased).
UNIVERSE = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","CRM","ADBE","ORCL","CSCO",
    "JPM","BAC","XOM","CVX","JNJ","PFE","KO","PEP","WMT","COST",
    "DIS","NKE","MCD","CAT","BA","GE","T","VZ","INTC","AMD",
    "PYPL","SQ","SHOP","UBER","ABNB","SNAP","PINS","ZM","ROKU","PLTR",
]
ENTRY_DATES = ["2017-06-01", "2019-06-01", "2021-06-01"]  # forward-24m all closed


def build_practice_pt(universe=None, entry_dates=None):
    """Return (P_t vector, provenance) from real historical forward-24m returns."""
    import yfinance as yf
    import pandas as pd
    universe = universe or UNIVERSE
    entry_dates = entry_dates or ENTRY_DATES

    px = yf.download(universe, start="2016-06-01", end="2024-01-01",
                     auto_adjust=True, progress=False)["Close"]

    returns = []
    used = 0
    for ent in entry_dates:
        ent_ts = pd.Timestamp(ent)
        exit_ts = ent_ts + pd.DateOffset(months=24)
        for tk in universe:
            try:
                s = px[tk].dropna()
                p0 = s.asof(ent_ts)
                p1 = s.asof(exit_ts)
                if p0 and p1 and p0 > 0 and not (np.isnan(p0) or np.isnan(p1)):
                    returns.append(p1 / p0 - 1.0)
                    used += 1
            except Exception:
                continue

    counts = hist_from_returns(returns)
    ok, total, tail = measurable(counts)
    prov = {
        "source": "yfinance historical prices (PRACTICE, NON-COMPLIANT)",
        "reference_class": "diversified fixed universe (sector/feature-agnostic)",
        "n_analogues": int(used), "entry_dates": entry_dates,
        "measurable": bool(ok), "total": int(total), "right_tail": int(tail),
        "caveats": ["survivorship-biased", "not point-in-time", "crude class (no 6 features)"],
    }
    return smooth_normalize(counts), prov


if __name__ == "__main__":
    import json
    P, prov = build_practice_pt()
    print(json.dumps(prov, indent=2))
    labels = ["<-50%","-50..-25","-25..-10","-10..0","0..10","10..25","25..50","50..100","100..200",">200%"]
    print("\nPractice P_t over the 10 bins (sum=%.3f):" % P.sum())
    for lab, p in zip(labels, P):
        print(f"  {lab:>9}  {p:5.3f}  {'#'*int(round(p*60))}")
