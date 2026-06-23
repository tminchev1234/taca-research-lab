# -*- coding: utf-8 -*-
"""
taca_engine.py — TACA CRF engine core.

Implements the protocol-compliant math of TACA Protocol Lock v3:
binning, Dirichlet smoothing, Jensen-Shannon divergence (CRF), KL, the
validation Gap, the measurability rule, and the direction/quadrant logic.

This module contains ONLY the math. It holds no data, prints nothing, and
makes no network calls. Distributions are numpy probability vectors over the
10 locked outcome bins (Section 4). Data adapters (Q_t from option RND, P_t
from a survivorship-free reference class) live elsewhere and feed this core.

Reference: protocol/TACA_Protocol_Lock_v3.md
"""
from __future__ import annotations
import numpy as np
from math import erf, sqrt, log

# --- Section 4: 10 asymmetric outcome bins, given by upper return edges -------
BIN_UPPER = [-0.50, -0.25, -0.10, 0.0, 0.10, 0.25, 0.50, 1.00, 2.00, float("inf")]
N_BINS = len(BIN_UPPER)                 # 10
RIGHT_TAIL_BINS = [7, 8, 9]             # (50%,100%], (100%,200%], (200%,+inf)

# --- Locked constants (v3) ----------------------------------------------------
ALPHA = 0.5                             # Dirichlet (Jeffreys) smoothing, Section 6.5
TAU = 0.10                              # inter-rater tolerance, Section 10
N_MIN_TOTAL = 50                        # Section 6.6 (v2)
N_MIN_TAIL = 8                          # Section 6.6 (v2)


def bin_index(r: float) -> int:
    """Return the outcome-bin index for a forward return r."""
    for i, u in enumerate(BIN_UPPER):
        if r <= u:
            return i
    return N_BINS - 1


def hist_from_returns(returns) -> np.ndarray:
    """Raw counts of forward returns into the 10 bins."""
    counts = np.zeros(N_BINS)
    for r in returns:
        counts[bin_index(r)] += 1
    return counts


def smooth_normalize(counts) -> np.ndarray:
    """Dirichlet add-alpha smoothing -> probability vector (no zeros)."""
    p = np.asarray(counts, dtype=float) + ALPHA
    return p / p.sum()


def kl(p, q) -> float:
    """KL(p || q) in nats. Inputs must be smoothed (no zeros)."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    return float(np.sum(p * np.log(p / q)))


def jsd(p, q) -> float:
    """Jensen-Shannon divergence in bits -> range [0, 1]. This is CRF_t."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    m = 0.5 * (p + q)
    return (0.5 * kl(p, m) + 0.5 * kl(q, m)) / log(2)


def measurable(counts) -> tuple[bool, int, int]:
    """Section 6.6 two-part rule: (ok, total, right_tail_count)."""
    counts = np.asarray(counts)
    total = int(counts.sum())
    tail = int(counts[RIGHT_TAIL_BINS].sum())
    return (total >= N_MIN_TOTAL and tail >= N_MIN_TAIL), total, tail


def median_bin(p) -> int:
    """Index of the median bin of a probability vector."""
    return int(np.searchsorted(np.cumsum(np.asarray(p)), 0.5))


def realized_vector(r: float) -> np.ndarray:
    """R as a smoothed one-hot at the realized bin (for validation)."""
    counts = np.zeros(N_BINS)
    counts[bin_index(r)] = 1
    return smooth_normalize(counts)


def gap(R, Q_t, P_t) -> float:
    """Validation Gap = L_Q - L_P = D(R||Q) - D(R||P). >0 => evidence beat market."""
    return kl(R, Q_t) - kl(R, P_t)


# --- Tail-aware signed direction (proposed v4 alternative to §7 median rule) ---
LEFT_TAIL_BINS = [0, 1]   # returns <= -25%   (mirror of RIGHT_TAIL_BINS, > 50%)


def tail_masses(p) -> tuple[float, float]:
    p = np.asarray(p)
    return float(p[LEFT_TAIL_BINS].sum()), float(p[RIGHT_TAIL_BINS].sum())


def tilt(P, Q) -> float:
    """Signed tail-aware direction. >0: evidence puts more weight on the big-up
    tail (and/or less on the big-down tail) than the market does — i.e. the
    market is underpricing the upside relative to the evidence. <0: the reverse."""
    pL, pR = tail_masses(P)
    qL, qR = tail_masses(Q)
    return (pR - qR) - (pL - qL)


def detect(Q, P, crf_floor=0.05, tilt_floor=0.05) -> dict:
    """Combined detection PROFILE — magnitude (CRF) + signed direction (tilt).

    Returns a LABELLED PROFILE, never a single blended score (that would be the
    AXI-PRO trap, §12.3). The static tilt direction here is the practice-grade
    proxy; the protocol's lead-lag direction (who moved first) needs t-12m
    snapshots and finer time resolution.

    crf_floor / tilt_floor are PROVISIONAL demo thresholds. The locked cutoff is
    sample-relative (high-CRF = top tercile of the scored sample, §9), not a
    fixed number — do not read these as protocol values.
    """
    c = jsd(Q, P)
    tl = tilt(P, Q)
    if c < crf_floor:
        label = "Recognized — no material divergence"
    elif tl > tilt_floor:
        label = "True-positive candidate (evidence sees more upside)"
    elif tl < -tilt_floor:
        label = "Counter-asymmetry candidate (evidence sees more downside)"
    else:
        label = "False-asymmetry zone (divergence in shape, not direction)"
    return {"crf": round(c, 4), "tilt": round(tl, 4), "label": label}


def quadrant(P_now, Q_now, P_prev, Q_prev) -> str:
    """Section 7 direction rule (median-bin form)."""
    mP, mQ = median_bin(P_now), median_bin(Q_now)
    dP = median_bin(P_now) - median_bin(P_prev)   # evidence shift
    dQ = median_bin(Q_now) - median_bin(Q_prev)   # recognition shift
    if abs(mP - mQ) <= 1:
        return "Recognized — no asymmetry"
    if mP > mQ and dP >= dQ:
        return "True positive asymmetry"
    if mQ > mP and dQ > 0 and abs(dP) <= 1:
        return "False asymmetry"
    if mP < mQ:
        return "Counter-asymmetry"
    return "Unclassified"


# --- Q_t helper: lognormal stand-in for an option-implied RND ------------------
# A compliant Q_t comes from Breeden-Litzenberger on the option chain. This
# single-vol lognormal mapping is a placeholder for adapters/feasibility only.
def _normal_cdf(x, mu, sigma) -> float:
    return 0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))))


def Q_from_lognormal(iv_annual: float, horizon_years: float = 2.0, rf: float = 0.03) -> np.ndarray:
    """Map a risk-neutral lognormal return law onto the 10 bins (placeholder)."""
    sigma = iv_annual * sqrt(horizon_years)
    mu = (rf * horizon_years) - 0.5 * sigma**2
    probs = np.zeros(N_BINS)
    lower = log(1e-6)
    edges = [log(1 + u) if u > -1 else lower for u in BIN_UPPER[:-1]]
    prev = lower
    for i, e in enumerate(edges):
        probs[i] = _normal_cdf(e, mu, sigma) - _normal_cdf(prev, mu, sigma)
        prev = e
    probs[-1] = 1.0 - _normal_cdf(prev, mu, sigma)
    probs = np.clip(probs, 1e-9, None)
    return probs / probs.sum()
