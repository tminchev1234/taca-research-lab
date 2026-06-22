# TACA Protocol Lock v2
## Pre-Registration of the CRF Asymmetry-Detection Methodology

**Author:** Teodor Minchev
**Version:** 2.0
**Lock date:** 2026-06-22
**Supersedes:** v1 (DOI 10.5281/zenodo.20800461)
**Status:** LOCKED — pre-registered prior to any case execution.

---

### 0. Meaning of the Lock

This document fixes every methodological degree of freedom *before* a single empirical
case is scored. Once locked, no parameter, definition, threshold, or hypothesis below may
be altered during case work. Any change requires a new version (v3, v4, …), dated and
justified, and applies **only to cases scored after** that new version. Cases already
scored under a given version are never re-scored under a later version. This rule is the
sole protection against hindsight-driven parameter drift.

Parameters below are tagged **[PRINCIPAL]** (confirmed by the author as a research
commitment) or **[DEFAULT]** (set by the methodology at lock time; changeable only by
versioned amendment, like any other locked value).

### 0.1 Amendment Record (v1 → v2)

This amendment is issued **before any case was scored under v1**. Because no scored data
exists, the change cannot retrofit results and is therefore integrity-clean; it merely
strengthens the design before the program begins. Three changes:

1. **Case-selection frame** (Section 11): window changed from 1995–2020 to **2000–2023**
   (better point-in-time fundamental coverage; uses the best-covered recent, fully-resolved
   years). Added a **pre-registered temporal holdout** (development 2000–2015, replication
   2016–2023) and **regime stratification**. Rationale: guards against a metric that works
   in only one era and against quadrant artifacts clustering in single crises.
2. **Measurability floor** (Section 6.6): the flat `n_min = 40` is replaced by a
   **two-part, tail-aware rule** (total ≥ 50 analogues AND ≥ 8 in the combined right-tail
   bins). Rationale: a flat total under-protects the right tail — the bins that actually
   drive CRF and H2.
3. **Non-methodological corrections:** license stated unambiguously (Section L); forbidden-
   practices list re-numbered 1–6.

---

### L. License

**CC BY 4.0** (Creative Commons Attribution 4.0 International). The Zenodo record metadata
must be set to this single license. (If non-commercial protection is preferred, substitute
CC BY-NC-SA 4.0 consistently in both the document and the Zenodo metadata — never both at
once, as occurred in the v1 record.)

---

### 1. Purpose and Scope

This protocol tests one claim of the Theory of Asymmetric Capital Accumulation (TACA):

> Asymmetry emerges when structural reality evolves faster than collective interpretation.

It operationalizes that claim as a **measurable, point-in-time divergence** between what
the market prices and what a locked evidence model implies, and specifies how that
divergence is to be validated against realized outcomes.

**This protocol does NOT claim:**
- to measure a Structural Probability Transition directly (SPTs are latent);
- predictive validity in advance of the empirical test;
- that any single case validates the theory.

It claims only that the methodology can be **executed consistently, auditably, and
point-in-time**, and that its central hypotheses are **falsifiable** on a pre-registered
sample with out-of-sample replication.

---

### 2. Canonical Definitions (Name-Collision Resolution)

Within this protocol and all cases scored under it, **"CRF" has exactly one meaning:**

> **CRF (Cognitive Risk Friction)** = an information-theoretic divergence between a
> market-perceived outcome distribution and an evidence-model outcome distribution,
> computed at a fixed point in time.

The doctrinal "Cognitive Reflexivity Function" (epistemic-legitimacy construct, declared
orthogonal to probability distributions) is **explicitly excluded** as an operational
definition here. It may be cited only as qualitative motivation, never as the measured
quantity. This resolves the corpus-wide collision in which "CRF" carried incompatible
meanings.

- **X** — the locked outcome space (Section 4).
- **Q_t** — the market-perceived distribution over X at time t (Section 5).
- **P_t** — the evidence-model distribution over X at time t (Section 6).
- **R** — the realized outcome, observed only at t+h (Section 8).

---

### 3. The Metric

CRF_t = JSD( Q_t || P_t )

- JSD = Jensen–Shannon divergence, **log base 2**, range **[0, 1]**. **[DEFAULT]**
- Chosen over KL because JSD is symmetric, always finite (even with disjoint support),
  and bounded — hence comparable across cases. **[DEFAULT]**

---

### 4. Outcome Space X (LOCKED)

- **Variable:** forward total return of the object over horizon **h = 24 months**. **[PRINCIPAL]**
- **Binning (return space), 10 bins:** **[DEFAULT]**
  `(-100%,-50%], (-50%,-25%], (-25%,-10%], (-10%,0%], (0%,10%], (10%,25%], (25%,50%], (50%,100%], (100%,200%], (200%,+inf)`
  Bins are deliberately asymmetric to preserve right-tail resolution (the theory lives in
  the tail; symmetric bins would blur it). The **right-tail bins** referenced elsewhere are
  the top three: `(50%,100%], (100%,200%], (200%,+inf)`.
- All three distributions (Q_t, P_t, R-as-point) are expressed over these identical bins.

---

### 5. Q_t — Market-Perceived Distribution (LOCKED)

Q_t is **read from the market**, never constructed by the analyst. Source precedence: **[DEFAULT]**

1. **Option-implied risk-neutral density** (Breeden–Litzenberger), when listed options
   exist with maturities bracketing h and open interest above the locked liquidity floor.
   The RND is mapped onto the Section-4 bins.
2. **Fallback — analyst target distribution:** if options are insufficient, use the
   cross-section of 24-month analyst price targets (consensus + dispersion) fitted to the
   same bins.
3. **If neither exists:** the case is flagged **Q-unmeasurable** and excluded from H1/H2
   (logged, not silently dropped — Section 13).

---

### 6. P_t — Evidence-Model Distribution (LOCKED): Reference-Class Method

P_t is the **smoothed empirical histogram of the forward-h returns of the k historical
analogues most similar to the object**, by a locked structural feature vector. P_t is the
output of a locked computation, **not the analyst's opinion**. Six locked components:

**6.1 Feature set f (declared once, program-wide) — 6 features [PRINCIPAL]:**
| # | Feature | Locked single-source operationalization |
|---|---------|------------------------------------------|
| 1 | Scalability | Gross-margin trend over trailing 8 quarters |
| 2 | Reinvestment runway | Capex / operating cash flow (trailing 4q) |
| 3 | Optionality | R&D intensity (R&D/revenue) × addressable-market growth proxy |
| 4 | Network / retention | Revenue retention or repeat-revenue proxy (trailing) |
| 5 | Survivability | Cash runway (months) + interest coverage |
| 6 | Unit-economics trend | Contribution-/incremental-margin trend (trailing 8q) |

No per-case feature selection. Ambiguity in any feature is a leakage-log item (Section 10).

**6.2 Similarity metric & class size [DEFAULT]:** features z-scored on the pre-t
cross-section; distance = Mahalanobis using the pre-t cross-sectional covariance; take the
**k = 75** nearest analogues. **[PRINCIPAL: k=75]**

**6.3 Strict point-in-time rule [DEFAULT]:** an analogue qualifies only if its own
forward-h (24m) window **closed before t**. The feature→outcome relationship is therefore
entirely historical relative to t. No future information enters P_t.

**6.4 Survivorship-free universe [PRINCIPAL]:** analogues drawn from **US listed equities**
meeting the locked size/data filters, **including delisted, bankrupt, and acquired firms**.
A survivorship-biased universe would poison the left tail of P_t — the very bias the theory
claims to fight.

**6.5 Binning & smoothing [DEFAULT]:** analogue returns binned per Section 4; Dirichlet
(add-α) smoothing with **α = 0.5** (Jeffreys) so empty bins do not destabilize small-sample
estimates.

**6.6 Measurability floor — two-part, tail-aware rule [DEFAULT, amended in v2]:** construct
P_t only if **both**: (a) **total qualifying analogues ≥ 50**, and (b) **≥ 8 analogues fall
in the combined right-tail bins** (top three bins, Section 4). If either fails, the case is
flagged **out-of-measurable-domain**; P_t is **not** constructed and the case is excluded
from H1/H2 (logged, Section 13). The tail condition exists because a sufficient total can
still leave the right tail — which drives CRF and H2 — too sparse to estimate. Novel
structural transitions with no analogue base are declared unmeasurable rather than
fabricated.

**6.7 Robustness cross-check [DEFAULT]:** an alternative P_t′ from a locked quantile
regression on the same f and same pre-t data is computed; **JSD(P_t || P_t′)** is reported
as a model-dependence diagnostic. Large disagreement flags low confidence for that case.

---

### 7. Direction / Quadrant Rule (LOCKED) [DEFAULT]

JSD is unsigned. Direction is assigned by comparing P_t and Q_t and their shift over the
trailing window **[t−12m, t]**:

| Configuration | Quadrant |
|---------------|----------|
| P implies higher than Q; P moved before Q | **True positive asymmetry** |
| Q higher than P; Q moved, P flat | **False asymmetry** |
| P implies lower than Q; P deteriorating, Q lagging | **Counter-asymmetry** |
| P ≈ Q | Recognized — no asymmetry |

"Higher/lower" = comparison of distribution central tendency (median bin). "Moved" = shift
in central tendency over the trailing window beyond one bin.

---

### 8. Three-Layer Evaluation (LOCKED)

- **Layer 1 — Detection (at t, observable):** CRF_t = JSD(Q_t||P_t); quadrant per Section 7.
- **Layer 2 — Validation (at t+h):** realized R observed. Compute
  **L_Q = D(R||Q_t)**, **L_P = D(R||P_t)**, and **Gap = L_Q − L_P** (D = KL; R as the
  realized-bin indicator with the same α-smoothing).
- **Layer 3 — Payoff link (at t+h):** record whether realized R landed in the right-tail
  bins (top 2 bins) in the direction the quadrant predicted.

---

### 9. Pre-Registered Hypotheses & Decision Rules (LOCKED) [DEFAULT thresholds]

Define **high-CRF** = CRF_t in the **top tercile** of the scored sample. Define
**positive-direction** = True-positive-asymmetry quadrant.

- **H1 (cognitive-lag claim):** Among high-CRF positive-direction cases, the share with
  **Gap > 0** exceeds 0.5 (one-sided binomial test, **α = 0.05**).
  *Refutation:* if high CRF does not predict that the evidence model beat the market, the
  cognitive-lag thesis fails.
- **H2 (asymmetric-payoff claim):** High-CRF positive-direction cases realize right-tail
  outcomes (Layer 3) at a higher rate than a matched low-CRF control (two-proportion test,
  **α = 0.05**).
- **H0 (null):** CRF_t has no relationship to Gap or to realized asymmetry.

**Two-period design (amended in v2):**
- **Primary test — development period 2000–2015:** H1 and H2 evaluated as above, with a
  minimum **N ≥ 60** scored cases spanning all four quadrants.
- **Confirmatory replication — holdout 2016–2023:** the identical tests are re-run on
  cases the development analysis never touched. A hypothesis is reported **SUPPORTED only
  if it holds in development AND directionally replicates in the holdout**. Holdout results
  are reported regardless of outcome (no silent caps, Section 12).

---

### 10. Controls (LOCKED)

- **Independent dual scoring:** every case scored by **≥ 2 independent evaluators** who do
  not deliberate. Agreement metric = **JSD(P_t^A || P_t^B)**. Tolerance **τ = 0.10**.
  **Disagreement beyond τ = protocol failure for that case** (the case is flagged, not
  reconciled by discussion — reconciliation would contaminate independence on later cases).
  **[PRINCIPAL: dual scoring; DEFAULT: τ=0.10]**
- **Author exclusion:** the theory's author may not be a sole scorer of any case; if
  participating, that score is flagged.
- **Leakage Control Log (per major score):** (a) Could this be influenced by future
  knowledge? (b) Would it survive if the object had later failed? (c) What contemporaneous
  evidence alone supports it? Logged into the audit record.
- **Blinding (preferred where feasible):** present the contemporaneous evidence dossier
  de-identified (name redacted, dates shifted) so the scorer does not know the object. Where
  the object is too famous to blind, this is recorded as a known contamination risk and is
  an argument for preferring obscure cases (Section 11).

---

### 11. Case-Selection Frame (LOCKED) [DEFAULT, amended in v2]

Cases are **sampled from a pre-registered frame**, never cherry-picked by known outcome.

- **Frame window:** firm-quarters from the Section-6.4 universe over **2000–2023** (so that
  the t+24m window has fully resolved and predates the lock date, and point-in-time
  fundamental coverage is reliable).
- **Temporal holdout:** **development 2000–2015**, **replication 2016–2023**. Development
  and holdout cases are disjoint; the holdout is not inspected until development scoring is
  complete.
- **Regime stratification:** the sample must include cases drawn from expansion,
  contraction, and high-dispersion market regimes, so that no quadrant is an artifact of a
  single crisis.
- **Sampling:** stratified random draw designed to populate all four quadrants; selection
  uses only point-in-time data available at each candidate's t.
- Outcome valence (winner/loser/false) must not enter selection. Famous cases are
  permitted but flagged for contamination risk; obscure cases are preferred for clean
  process tests.

---

### 12. Forbidden Practices (LOCKED)

1. **No hindsight numbers.** P_t comes from a locked model on pre-t data — never assigned
   by recollection of the outcome (forbids the historical-CRF-table practice).
2. **No hand-assigned probabilities or price targets** as drivers of the metric. Q from
   market, P from model (forbids the ARE 50/50 example practice).
3. **No hidden aggregation.** CRF is one defined operator (JSD); no multiplicative index of
   unitless quantities (forbids the AXI-PRO practice).
4. **One CRF definition** (Section 2). The doctrinal/orthogonal definition is barred as the
   operational quantity.
5. **No silent caps.** Every excluded case (Q-unmeasurable, out-of-domain, τ-failure) is
   logged with reason; coverage is reported as "M of N candidate cases," and holdout
   results are reported regardless of outcome.
6. **No mid-study parameter change.** Section 0 governs amendment.

---

### 13. Measurable-Domain Boundary (Honest Limitation)

The most transformative asymmetries (genuinely novel structural transitions) are precisely
where **both** Q_t (no liquid options) **and** P_t (no analogue base) are hardest to build.
The methodology is therefore most reliable on **moderate, recurring** asymmetries and is
**silent** outside its measurable domain. Results pertain only to cases with sufficient
Q-liquidity and a reference class meeting Section 6.6. This boundary is reported, not
hidden. CRF measures divergence from the **evidence model**, not from truth; all
conclusions are conditional on the model being a reasonable, inspectable evidence
aggregator.

---

### 14. Role of Amazon 2004–2005

Amazon is a **Protocol Execution / Feasibility Case**, not a validation case and not a
calibration (parameter-fitting) case. Its sole purpose: demonstrate that the protocol can
be executed, that the evidence trail reconstructs, that two evaluators follow the same
process. A clean Amazon run validates the **process**, never the theory. Because Amazon is
outcome-loaded and hard to blind, it carries a flagged contamination risk and cannot enter
H1/H2 inference.

---

### 15. Locked Parameter Appendix

| Parameter | Value | Tag |
|-----------|-------|-----|
| Horizon h | 24 months | PRINCIPAL |
| Outcome bins | 10 asymmetric (Section 4) | DEFAULT |
| Right-tail bins | top 3: (50%,100%], (100%,200%], (200%,+inf) | DEFAULT |
| Divergence | Jensen–Shannon, log2, [0,1] | DEFAULT |
| Nearest analogues k | 75 | PRINCIPAL |
| Measurability floor | total ≥ 50 AND ≥ 8 in right-tail bins | DEFAULT (v2) |
| Distance | Mahalanobis on z-scored f | DEFAULT |
| Smoothing | Dirichlet α = 0.5 | DEFAULT |
| Feature set | 6 features (Section 6.1) | PRINCIPAL |
| Universe | US listed, survivorship-free | PRINCIPAL |
| Direction window | trailing 12 months | DEFAULT |
| Inter-rater tolerance τ | 0.10 (JSD) | DEFAULT |
| High-CRF cutoff | top tercile | DEFAULT |
| Significance α | 0.05 | DEFAULT |
| Minimum sample N (development) | 60 | DEFAULT |
| Case frame window | 2000–2023 | DEFAULT (v2) |
| Temporal holdout | dev 2000–2015 / replication 2016–2023 | DEFAULT (v2) |
| Regime stratification | required | DEFAULT (v2) |
| License | CC BY 4.0 | — |

---

*End of TACA Protocol Lock v2. Locked 2026-06-22. Supersedes v1 (DOI
10.5281/zenodo.20800461). Amendments only by dated, versioned re-issue applying to cases
scored after re-issue.*
