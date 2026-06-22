# -*- coding: utf-8 -*-
"""
qt_options.py — Q_t adapter from a real option chain (Breeden-Litzenberger).

Builds the market-perceived distribution Q_t over the 10 locked outcome bins
from a listed option chain, via the risk-neutral CDF identity:

    P(S_T <= K)  =  1 + e^{rT} * dC/dK

where C(K) is the call price as a function of strike. Binning the CDF across
the protocol's return bins yields Q_t.

COMPLIANCE NOTE
---------------
This adapter is protocol-shaped but its DATA source (free yfinance, live chain)
is NOT compliant for a real case:
  * it reads the CURRENT chain, not a point-in-time historical chain at some t;
  * the longest free expiry is usually < 24 months, so the horizon is shorter
    than the locked h = 24m (flagged in provenance);
  * free chains are sparse/noisy, so BL is regularised and may fall back to an
    ATM-IV lognormal.
Use it to exercise the Q_t half on REAL data, not to score a compliant case.

A compliant adapter swaps the source for historical OptionMetrics chains at t.
"""
from __future__ import annotations
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from taca_engine import BIN_UPPER, N_BINS, smooth_normalize, Q_from_lognormal  # noqa: E402

RF = 0.04  # risk-free proxy; a compliant run uses the t-dated curve


def _bin_edges_return():
    """Return (lower, upper) return edges for each of the 10 bins."""
    edges = []
    for i, up in enumerate(BIN_UPPER):
        lo = -1.0 if i == 0 else BIN_UPPER[i - 1]
        edges.append((lo, up))
    return edges


def _cdf_to_bins(cdf_at_edge):
    """cdf_at_edge: array of CDF values at each bin's UPPER return edge
    (last = 1.0). Returns a smoothed probability vector over the 10 bins."""
    probs = np.zeros(N_BINS)
    prev = 0.0
    for i, c in enumerate(cdf_at_edge):
        probs[i] = max(c - prev, 0.0)
        prev = c
    counts = probs * 1000.0  # scale so Dirichlet smoothing is gentle
    return smooth_normalize(counts)


def qt_from_chain(ticker: str):
    """Return (Q_t vector, provenance dict) from a live option chain."""
    import yfinance as yf
    from datetime import datetime, timezone

    t = yf.Ticker(ticker)
    expiries = t.options
    if not expiries:
        raise RuntimeError(f"no listed options for {ticker}")

    # spot
    try:
        S = float(t.fast_info["lastPrice"])
    except Exception:
        S = float(t.history(period="1d")["Close"].iloc[-1])

    # pick the longest-dated expiry (closest to h=24m we can get for free)
    today = datetime.now(timezone.utc).date()
    exp = expiries[-1]
    exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
    T = max((exp_date - today).days, 1) / 365.0

    calls = t.option_chain(exp).calls.copy()
    calls = calls[(calls["strike"] > 0)]
    # prefer mid price; fall back to lastPrice
    mid = (calls["bid"] + calls["ask"]) / 2.0
    calls["px"] = np.where((calls["bid"] > 0) & (calls["ask"] > 0), mid, calls["lastPrice"])
    calls = calls[(calls["px"] > 0)].sort_values("strike")
    # keep strikes with some liquidity
    liq = calls[(calls["openInterest"].fillna(0) + calls["volume"].fillna(0)) > 0]
    if len(liq) >= 8:
        calls = liq

    prov = {
        "source": "yfinance live chain (NON-COMPLIANT)",
        "ticker": ticker, "spot": round(S, 2),
        "expiry": exp, "horizon_years": round(T, 2),
        "n_strikes": int(len(calls)),
        "horizon_flag": "OK" if T >= 1.5 else f"SHORT ({round(T,2)}y < 24m target)",
        "method": None,
    }

    K = calls["strike"].to_numpy(dtype=float)
    C = calls["px"].to_numpy(dtype=float)

    # need enough distinct strikes for a stable derivative
    if len(K) >= 8 and np.ptp(K) > 0:
        dC = np.gradient(C, K)                       # dC/dK in [-1, 0]
        cdf = 1.0 + math.exp(RF * T) * dC
        cdf = np.clip(cdf, 0.0, 1.0)
        cdf = np.maximum.accumulate(cdf)             # enforce monotone
        edges = _bin_edges_return()
        cdf_at_edge = []
        for i, (lo, up) in enumerate(edges):
            if math.isinf(up):
                cdf_at_edge.append(1.0)
            else:
                K_up = S * (1.0 + up)
                cdf_at_edge.append(float(np.interp(K_up, K, cdf, left=0.0, right=1.0)))
        # sanity: must be roughly monotone and span [0,1]
        if cdf_at_edge[-2] - cdf_at_edge[0] > 0.05:
            prov["method"] = "Breeden-Litzenberger (CDF from dC/dK)"
            return _cdf_to_bins(np.array(cdf_at_edge)), prov

    # fallback: ATM implied-vol lognormal
    atm = calls.iloc[(calls["strike"] - S).abs().argsort()].iloc[0]
    iv = float(atm.get("impliedVolatility") or 0.4)
    prov["method"] = f"fallback ATM-IV lognormal (IV={round(iv,3)})"
    return Q_from_lognormal(iv_annual=iv, horizon_years=T, rf=RF), prov


if __name__ == "__main__":
    import json
    tk = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    q, prov = qt_from_chain(tk)
    print("=" * 70)
    print(f"Q_t from REAL option chain — {tk}   [LIVE, NON-COMPLIANT]")
    print("=" * 70)
    print(json.dumps(prov, indent=2))
    print("\nQ_t over the 10 bins (sum=%.3f):" % q.sum())
    labels = ["<-50%", "-50..-25", "-25..-10", "-10..0", "0..10",
              "10..25", "25..50", "50..100", "100..200", ">200%"]
    for lab, p in zip(labels, q):
        bar = "#" * int(round(p * 60))
        print(f"  {lab:>9}  {p:5.3f}  {bar}")
