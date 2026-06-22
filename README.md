# TACA Research Lab

A research platform to test the **TACA** methodology (Theory of Asymmetric Capital
Accumulation) — specifically, whether a pre-registered metric can detect *structural
probability transitions* point-in-time, auditably, and falsifiably.

> **Structural change detection is not outcome detection.**

This is a **standalone research project**. It deliberately shares **no code** with the
consumer-facing `asymmetry_engine` (AXI / ALEX_SCORE) in the separate `alex-finance-mvp`
product. That engine is a cross-sectional price-factor scanner; this project is a
falsifiable research instrument with opposite epistemic standards. Keeping them apart is
intentional — see `protocol/` §12 (forbidden practices).

## The operational metric

```
CRF_t = JSD( Q_t || P_t )
```

- **Q_t** — market-perceived outcome distribution (option-implied RND; analyst-target fallback).
- **P_t** — evidence-model distribution (smoothed reference-class histogram of forward-24m
  returns of the 75 most similar survivorship-free analogues, point-in-time).
- **CRF_t** — Jensen–Shannon divergence between them, range [0, 1].
- **Validation** — at t+24m: `Gap = D(R||Q) − D(R||P)`; high CRF should predict Gap > 0.

Four quadrants from direction: true-positive / false / counter-asymmetry / recognized.

## Status

| Layer | State |
|-------|-------|
| Locked protocol (pre-registration) | ✅ `protocol/` v3, published on Zenodo |
| Engine core (the math) | ✅ `engine/taca_engine.py` |
| Feasibility pipeline | ✅ `feasibility/` — runs end-to-end on synthetic data |
| Q_t adapter (real data) | 🟡 `data/adapters/qt_options.py` — real option chain → CDF; NON-COMPLIANT source |
| P_t adapter (compliant) | ⛔ stub — needs survivorship-free PIT data (`data/DATA_SPEC.md`) |
| Scored cases | ⛔ none — Amazon 2004 is feasibility-only |

## Layout

```
protocol/    Locked pre-registration (v1→v3, .md + .docx). v3 is canonical.
engine/      taca_engine.py — protocol-compliant math. No data, no I/O.
feasibility/ amazon_feasibility.py — SYNTHETIC demo. Proves mechanics, not the theory.
data/        DATA_SPEC.md — what a compliant run requires. Adapters go here later.
cases/       Scored cases (audit trail, dual-scoring records). Empty for now.
```

## Run the feasibility demo

```bash
python feasibility/amazon_feasibility.py
```

Requires `numpy`. Output is NON-COMPLIANT (synthetic inputs) and proves only that the
pipeline executes, is reproducible, and is dual-scorable.

## Canonical protocol

The methodology is **locked**. Parameters change only by dated, versioned re-issue
applying to cases scored *after* the new version. Current: **Protocol Lock v3**
(`protocol/TACA_Protocol_Lock_v3.md`), Zenodo series concept DOI
`10.5281/zenodo.20800460`.

## What this project does NOT claim

- to measure a Structural Probability Transition directly (SPTs are latent);
- predictive validity in advance of the empirical test;
- that any single case validates the theory.
