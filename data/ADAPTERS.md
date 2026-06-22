# Adapter contract

The engine (`engine/taca_engine.py`) consumes **probability vectors over the 10 locked
bins**. Adapters turn real sources into those vectors. Every adapter returns:

```
(prob_vector: np.ndarray shape (10,),  provenance: dict)
```

`provenance` is the audit record — source, dates, method, and (for P_t) the full analogue
list. No adapter may hand-assign probabilities; the vector must derive from data.

## Implemented

| Adapter | Builds | Source | Compliance |
|---------|--------|--------|------------|
| `qt_options.py` | Q_t | live yfinance option chain → Breeden–Litzenberger CDF (ATM-IV lognormal fallback) | **NON-COMPLIANT** — current chain, not point-in-time; free/noisy |
| `pt_reference_class.py` | P_t | — | **stub** — needs survivorship-free PIT fundamentals (raises `CompliantDataRequired`) |

## Why Q_t is partly real but P_t is blocked

Q_t needs one object's option chain — a live chain exercises the math on real prices today
(horizon depends on the longest listed expiry). P_t needs a whole **survivorship-free,
point-in-time** universe of analogues with fundamentals reaching back years — that is the
paid-data gate (`DATA_SPEC.md`). Until it is wired, P_t stays a stub and no case is
compliant.

## Swapping in compliant sources

Replace the source inside each adapter; the engine and the rest of the pipeline are
unchanged. `qt_options.py` → historical OptionMetrics chain at `t`. `pt_reference_class.py`
→ implement `build_pt` against Sharadar/CRSP with the §6.1 feature formulas.
