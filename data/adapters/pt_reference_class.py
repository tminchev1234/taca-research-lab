# -*- coding: utf-8 -*-
"""
pt_reference_class.py — P_t adapter (reference-class evidence model).

STATUS: interface stub. A compliant P_t adapter CANNOT be built on free data —
it requires a survivorship-free, point-in-time fundamentals universe (see
../DATA_SPEC.md). This file defines the contract so a compliant implementation
slots straight into the engine once such data is available.

Contract
--------
build_pt(object_ref, t, universe) -> (np.ndarray shape (10,), provenance: dict)

  1. Compute the locked 6-feature vector f for `object_ref` using only data
     available at `t` (protocol §6.1, formulas pinned in v3).
  2. z-score f against the pre-t cross-section; Mahalanobis-rank all eligible
     analogues (forward-24m window closed before t; §6.3); take k = 75 nearest.
  3. Measurability gate (§6.6): require total >= 50 AND >= 8 in right-tail bins,
     else raise OutOfMeasurableDomain.
  4. Histogram the analogues' forward-24m returns into the 10 bins; Dirichlet
     smooth (alpha = 0.5). Return that vector + a provenance dict listing every
     analogue ticker, its f, and its realized return (the audit trail).
"""
from __future__ import annotations


class OutOfMeasurableDomain(Exception):
    """Raised when the reference class fails the §6.6 measurability gate."""


class CompliantDataRequired(NotImplementedError):
    """Raised because no survivorship-free point-in-time source is wired."""


def build_pt(object_ref, t, universe=None):
    raise CompliantDataRequired(
        "P_t requires a survivorship-free, point-in-time fundamentals universe "
        "(Sharadar/CRSP-Compustat) including delisted firms. See data/DATA_SPEC.md. "
        "Free sources (yfinance/EODHD-restated) violate protocol §6.3/§6.4 and must "
        "not be used to score a compliant case."
    )
