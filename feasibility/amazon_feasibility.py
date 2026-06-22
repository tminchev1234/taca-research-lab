# -*- coding: utf-8 -*-
"""
amazon_feasibility.py — NON-COMPLIANT feasibility demo (Protocol §6.4).

SYNTHETIC / ILLUSTRATIVE inputs. Demonstrates that the three-layer pipeline
EXECUTES and is REPRODUCIBLE, and that dual-scoring is computable. It proves
nothing about Amazon or the theory. The engine math it calls is real; only the
data is placeholder.

Run:  python feasibility/amazon_feasibility.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))

import numpy as np
from taca_engine import (
    hist_from_returns, smooth_normalize, jsd, measurable, median_bin,
    realized_vector, gap, quadrant, Q_from_lognormal, bin_index,
    RIGHT_TAIL_BINS, TAU,
)

rng = np.random.default_rng(20040601)   # seeded => demo is reproducible


def synthetic_analogues(n, mix):
    """ILLUSTRATIVE forward-24m returns for a reference class of high-optionality
    firms (heavy right tail + real left-tail failures). NOT real data."""
    out = []
    for frac, (kind, a, b) in mix:
        k = int(round(n * frac))
        if kind in ("fail", "flat", "win"):
            out += list(rng.uniform(a, b, k))
        elif kind == "moonshot":
            out += list(rng.lognormal(a, b, k))
    return out


def main():
    print("=" * 74)
    print("TACA CRF FEASIBILITY DEMO - NON-COMPLIANT (sec 6.4). SYNTHETIC INPUTS.")
    print("Demonstrates pipeline mechanics + reproducibility ONLY. Proves nothing.")
    print("=" * 74)

    # P_t : reference-class evidence distribution (synthetic analogues)
    analogues_t = synthetic_analogues(80, [
        (0.30, ("fail", -0.90, -0.40)),
        (0.40, ("flat", -0.20, 0.30)),
        (0.20, ("win", 0.50, 1.80)),
        (0.10, ("moonshot", 1.2, 0.6)),
    ])
    counts_t = hist_from_returns(analogues_t)
    P_t = smooth_normalize(counts_t)
    ok, total, tail = measurable(counts_t)

    # Q_t : market-implied (illustrative lognormal, AMZN ~2004 IV ~ 45%)
    Q_t = Q_from_lognormal(iv_annual=0.45)

    # trailing t-12m snapshots (illustrative) for direction
    analogues_prev = synthetic_analogues(80, [
        (0.35, ("fail", -0.90, -0.40)),
        (0.45, ("flat", -0.20, 0.30)),
        (0.15, ("win", 0.50, 1.80)),
        (0.05, ("moonshot", 1.1, 0.6)),
    ])
    P_prev = smooth_normalize(hist_from_returns(analogues_prev))
    Q_prev = Q_from_lognormal(iv_annual=0.40)

    # Layer 1 — detection
    crf = jsd(Q_t, P_t)
    quad = quadrant(P_t, Q_t, P_prev, Q_prev)
    print("\n[Layer 1 - Detection @ t]")
    print(f"  Measurable (sec 6.6): {ok}   (total={total} >=50, right-tail={tail} >=8)")
    print(f"  P_t median bin = {median_bin(P_t)}   Q_t median bin = {median_bin(Q_t)}")
    print(f"  CRF_t = JSD(Q_t || P_t) = {crf:.4f}   (range [0,1])")
    print(f"  Quadrant = {quad}")

    # Layer 2 — validation (Amazon realized 24m return — ILLUSTRATIVE)
    R_realized = 0.02
    R = realized_vector(R_realized)
    g = gap(R, Q_t, P_t)
    print("\n[Layer 2 - Validation @ t+24m]  (R is ILLUSTRATIVE)")
    print(f"  Realized 24m return ~ {R_realized:+.0%}  -> bin {bin_index(R_realized)}")
    print(f"  Gap = L_Q - L_P = {g:+.4f}   (>0 => evidence model beat the market)")

    # Layer 3 — payoff link
    hit = bin_index(R_realized) in RIGHT_TAIL_BINS
    print("\n[Layer 3 - Payoff link]")
    print(f"  Right-tail outcome realized? {hit}")

    # Reproducibility
    crf_again = jsd(Q_from_lognormal(0.45), smooth_normalize(hist_from_returns(analogues_t)))
    print("\n[Reproducibility]  same inputs -> identical CRF:",
          bool(np.isclose(crf, crf_again)), f"({crf:.6f})")

    # Inter-rater (§10): scorer B's reference class differs by ~12%
    analogues_B = list(analogues_t)
    nswap = int(0.12 * len(analogues_B))
    idx = rng.choice(len(analogues_B), nswap, replace=False)
    extra = synthetic_analogues(nswap, [(1.0, ("flat", -0.25, 0.35))])
    for j, e in zip(idx, extra):
        analogues_B[j] = e
    irr = jsd(P_t, smooth_normalize(hist_from_returns(analogues_B)))
    print("\n[Inter-rater agreement sec 10]")
    print(f"  JSD(P_A || P_B) = {irr:.4f}   tolerance tau = {TAU}")
    print(f"  Verdict: {'PASS (within tau)' if irr <= TAU else 'PROTOCOL FAILURE (>tau)'}")

    print("\n" + "=" * 74)
    print("CAVEAT: synthetic analogues + lognormal Q + placeholder R. A compliant run")
    print("needs survivorship-free PIT fundamentals, option-RND for Q, and real R.")
    print("=" * 74)


if __name__ == "__main__":
    main()
