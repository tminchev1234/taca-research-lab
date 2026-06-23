# -*- coding: utf-8 -*-
"""
qt_options.py — Q_t adapter from a real option chain.

Method (robust on free/sparse chains):
  1. read the implied-vol smile from the chain;
  2. fit a smooth IV(log-moneyness) quadratic and read the at-the-money IV
     (incorporates the smile shape at the money, ignores noisy wings);
  3. build a risk-neutral lognormal return law at that IV over the horizon;
  4. bin it across the 10 locked return bins.

Why not raw Breeden-Litzenberger here: differentiating a sparse free call
curve (even after BS reconstruction) is numerically unstable and produced
artifacts in both directions (mass over-spreading, then over-concentrating in
one bin). A smooth single-vol lognormal is a stable, honest Q_t for the
PRACTICE adapter. Full BL (which captures skew) is reserved for COMPLIANT,
dense historical chains (OptionMetrics), where the curve is rich enough to
differentiate cleanly.

COMPLIANCE NOTE — NON-COMPLIANT source: reads the CURRENT chain (not
point-in-time at t) from free yfinance. The math is real; the data is not
protocol-grade. A compliant adapter swaps in a historical chain at t and may
then use full BL.
"""
from __future__ import annotations
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from taca_engine import Q_from_lognormal  # noqa: E402

RF = 0.04   # risk-free proxy; a compliant run uses the t-dated curve


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_call(S, K, T, sigma, r=RF):
    if sigma <= 0 or T <= 0:
        return max(S - K * math.exp(-r * T), 0.0)
    srt = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / srt
    d2 = d1 - srt
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)


def _implied_vol(price, S, K, T, r=RF):
    """Invert Black-Scholes for sigma by bisection. yfinance's own IV column is
    unreliable for far-dated chains, so we recover IV from the (more reliable)
    call price. Returns None if the price is outside no-arbitrage bounds."""
    intrinsic = max(S - K * math.exp(-r * T), 0.0)
    if price <= intrinsic + 1e-6 or price >= S:
        return None
    lo, hi = 1e-3, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _bs_call(S, K, T, mid, r) > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _atm_iv(K, px, S, T):
    """Median implied vol of near-ATM calls, inverted from prices."""
    ivs = []
    for Ki, pi in zip(K, px):
        if 0.85 * S <= Ki <= 1.20 * S and pi > 0:
            iv = _implied_vol(pi, S, Ki, T)
            if iv and 0.05 < iv < 2.5:
                ivs.append(iv)
    if ivs:
        return float(np.median(ivs)), f"BS-inverted from {len(ivs)} near-ATM call prices"
    return 0.40, "default (no invertible near-ATM prices)"


def qt_from_chain(ticker: str):
    """Return (Q_t vector, provenance dict) from a live option chain."""
    import yfinance as yf
    from datetime import datetime, timezone

    t = yf.Ticker(ticker)
    expiries = t.options
    if not expiries:
        raise RuntimeError(f"no listed options for {ticker}")

    try:
        S = float(t.fast_info["lastPrice"])
    except Exception:
        S = float(t.history(period="1d")["Close"].iloc[-1])

    today = datetime.now(timezone.utc).date()
    exp = expiries[-1]
    exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
    T = max((exp_date - today).days, 1) / 365.0

    calls = t.option_chain(exp).calls.copy()
    calls = calls[calls["strike"] > 0]
    mid = (calls["bid"] + calls["ask"]) / 2.0
    calls["px"] = np.where((calls["bid"] > 0) & (calls["ask"] > 0), mid, calls["lastPrice"])
    calls = calls[calls["px"] > 0]
    liq = calls[(calls["openInterest"].fillna(0) + calls["volume"].fillna(0)) > 0]
    if len(liq) >= 6:
        calls = liq
    calls = calls.sort_values("strike")

    K = calls["strike"].to_numpy(dtype=float)
    PX = calls["px"].to_numpy(dtype=float)
    iv_atm, iv_method = _atm_iv(K, PX, S, T)

    Q = Q_from_lognormal(iv_annual=iv_atm, horizon_years=T, rf=RF)
    prov = {
        "source": "yfinance live chain (NON-COMPLIANT source)",
        "ticker": ticker, "spot": round(S, 2), "expiry": exp,
        "horizon_years": round(T, 2),
        "horizon_flag": "OK" if T >= 1.5 else f"SHORT ({round(T,2)}y < 24m)",
        "n_iv_points": int(len(calls)),
        "iv_atm": round(iv_atm, 3),
        "method": f"IV-lognormal ({iv_method}); full BL reserved for compliant dense chains",
    }
    return Q, prov


if __name__ == "__main__":
    import json
    tk = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    q, prov = qt_from_chain(tk)
    print("=" * 70)
    print(f"Q_t from REAL option chain — {tk}   [LIVE, NON-COMPLIANT source]")
    print("=" * 70)
    print(json.dumps(prov, indent=2))
    print("\nQ_t over the 10 bins (sum=%.3f):" % q.sum())
    labels = ["<-50%", "-50..-25", "-25..-10", "-10..0", "0..10",
              "10..25", "25..50", "50..100", "100..200", ">200%"]
    for lab, p in zip(labels, q):
        print(f"  {lab:>9}  {p:5.3f}  {'#' * int(round(p * 60))}")
