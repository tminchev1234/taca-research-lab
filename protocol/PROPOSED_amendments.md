# Proposed amendments (candidates — NOT locked)

This file holds methodology changes that are **designed but not yet locked**. They
are deliberately kept OUT of the canonical protocol (`TACA_Protocol_Lock_v3.md`)
until they pass their validation gate. Documenting a candidate here is not the same
as adopting it. The canonical protocol is unchanged.

---

## PA-1 — Tail-aware signed direction (`tilt`) as the §7 direction rule

**Status:** candidate for a future v4. **NOT locked. Do not use to score cases.**

### Proposal
Replace the §7 median-bin direction rule with a tail-aware signed measure:

```
left  = P[returns <= -25%]  −  Q[returns <= -25%]
right = P[returns >  +50%]  −  Q[returns >  +50%]
tilt  = right − left
```

`tilt > 0`: evidence weights the big-up tail more (and/or the big-down tail less)
than the market — market underpricing the upside. `tilt < 0`: the reverse.
Output is a labelled profile `{crf, tilt, label}` — never a blended score (§12.3).

### Rationale
TACA lives in the tails; the median-bin rule ignores exactly the tails that matter.
`tilt` reads direction from the tail mass directly.

### Why it is NOT locked yet (the validation gate)
Running `tilt` on the practice data (survivorship-biased P_t) classified CRM, KO and
NVDA **all** as "true-positive candidate". Cause: a survivor-only reference class has
a permanently inflated right tail and a thinned left tail (observed L/R ≈ 0.12/0.32),
so the evidence looks more upside-tilted than *any* market Q → tilt is positive for
everything → useless.

This is informative, not a bug: the direction layer makes survivorship bias
**systematic and visible** (not just noise). It also means `tilt` cannot be validated
on biased data — by construction it can only discriminate once P_t is survivorship-free.

**Lock condition:** adopt PA-1 as v4 only after a survivorship-free P_t run shows
`tilt` discriminating across objects (some +, some −, some ≈0) on a held-out set —
i.e. that it is not pinned positive by data bias. Until then it stays here.

### Known limitation carried forward
`tilt` is a STATIC direction (P vs Q at one t). The protocol's lead-lag intent
("evidence moved before the market") needs t-12m snapshots and finer time resolution,
which free data cannot supply (no historical option chains). PA-1, if locked, would
lock only the static form; lead-lag remains a separate, later question.

---

*Amendments graduate from this file into a versioned protocol lock only after their
stated gate is met. No case is ever scored using a candidate from this file.*
