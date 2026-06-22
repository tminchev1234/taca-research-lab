# -*- coding: utf-8 -*-
"""
practice_real_data.py — Layer-1 detection on REAL data (PRACTICE, NON-COMPLIANT).

Wires the real Q_t (live option chain) and the practice P_t (real historical
forward-24m returns) into one CRF. De-risking smoke test only: it shows the
machinery runs end-to-end on real market data and yields a sane CRF. It does
NOT score a compliant case (see each adapter's caveats; no validation layer
because the object's own outcome is in the future).

Run:  python feasibility/practice_real_data.py [TICKER]
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data", "adapters"))

from taca_engine import jsd, median_bin            # noqa: E402
from qt_options import qt_from_chain               # noqa: E402
from pt_practice_yf import build_practice_pt        # noqa: E402

LABELS = ["<-50%","-50..-25","-25..-10","-10..0","0..10","10..25","25..50","50..100","100..200",">200%"]


def main():
    obj = sys.argv[1] if len(sys.argv) > 1 else "CRM"
    print("=" * 72)
    print(f"PRACTICE — real-data Layer-1 detection for {obj}  [NON-COMPLIANT]")
    print("=" * 72)

    print("\nBuilding Q_t from live option chain ...")
    Q, qprov = qt_from_chain(obj)
    print("  Q_t:", qprov["method"], "| horizon", qprov["horizon_years"], "y", "|", qprov["horizon_flag"])

    print("Building practice P_t from real historical forward-24m returns ...")
    P, pprov = build_practice_pt()
    print("  P_t:", pprov["n_analogues"], "analogues | measurable:", pprov["measurable"],
          f"(total {pprov['total']}, right-tail {pprov['right_tail']})")

    crf = jsd(Q, P)
    print("\n  P_t median bin =", median_bin(P), " Q_t median bin =", median_bin(Q))
    print(f"  CRF_t = JSD(Q_t || P_t) = {crf:.4f}   (range [0,1])")

    print("\n  bin        Q_t    P_t")
    for lab, q, p in zip(LABELS, Q, P):
        print(f"  {lab:>9}  {q:5.3f}  {p:5.3f}")

    print("\n" + "-" * 72)
    print("CAVEATS:", "; ".join(pprov["caveats"]) + "; Q_t from current chain (not point-in-time).")
    print("Real CRF on real data => machinery works. NOT a compliant case; no validation layer.")
    print("-" * 72)


if __name__ == "__main__":
    main()
