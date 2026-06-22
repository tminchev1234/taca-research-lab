# Data Specification — what a compliant TACA run requires

The engine (`engine/taca_engine.py`) is data-agnostic: it consumes probability vectors
over the 10 locked bins. This document specifies the data a **protocol-compliant** run
must supply. The feasibility demo uses synthetic stand-ins for all of it.

## P_t — evidence-model (reference-class) inputs

For every firm-quarter in a **survivorship-free US equity universe** (delisted, bankrupt,
acquired firms **included**), point-in-time / as-first-reported:

| Need | Fields | Notes |
|------|--------|-------|
| Feature 1 Scalability | revenue, COGS (8q) | OLS slope of gross margin |
| Feature 2 Reinvestment | capex, operating cash flow (4q) | |
| Feature 3 Optionality | R&D, revenue (4q); GICS sub-industry revenue (3y) | R&D-intensity × sector CAGR |
| Feature 4 Network/retention | quarterly revenue (12q) | AR(1) of log-revenue |
| Feature 5 Survivability | cash, OCF burn, debt, interest expense | runway + interest coverage |
| Feature 6 Unit-economics | operating income, revenue (8q) | OLS slope OpInc~Revenue |
| Outcome label | forward-24m total return (price + dividends) | per analogue |
| Survivorship | delisting / bankruptcy returns | critical — left-tail integrity |
| Point-in-time | report/publication dates | enforce "available at t" |

**Depth:** analogues for a case at t need their forward-24m window closed *before* t, so
fundamentals must reach back ~4 years before the earliest case (frame starts 2000 →
data from ~1996).

## Q_t — market-perceived inputs

| Need | Fields | Notes |
|------|--------|-------|
| Primary | option chain: strikes, expiries bracketing 24m, prices/IV, open interest | Breeden–Litzenberger → RND |
| Fallback | 24-month analyst price targets (consensus + dispersion) | when options thin |

## Candidate sources (none free; §6.4 forbids survivorship-biased free data)

- **Fundamentals, survivorship-free, point-in-time:** Sharadar/Nasdaq SF1, or CRSP/Compustat
  (academic gold standard). *Note:* EODHD (already used in `alex-finance-mvp`) provides
  fundamentals but is typically restated, not as-first-reported, and needs its full
  delisted universe — a point-in-time gap to close.
- **Options (RND):** OptionMetrics IvyDB (from 1996).
- **Analyst targets (fallback):** I/B/E/S.

## Compliance gaps to close before a real run

1. **Survivorship-free** universe (not a live S&P-500 scrape).
2. **Point-in-time** (as-first-reported) fundamentals, not latest restated.
3. **Option-RND** source for Q_t — not currently wired anywhere.

Until these are met, runs are **feasibility-only** and must be labelled NON-COMPLIANT.
