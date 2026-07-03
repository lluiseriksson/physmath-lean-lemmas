# Is this a Mathlib contribution?

The user-facing question for this satellite was: *"al ser Tonelli + serie
geométrica, valora incluso si es contribución a mathlib en vez de repo
propio."* This document records the evaluation, made **after** completing
the proof (so the inventory of what Mathlib already provides is empirical,
not guessed).

## What the proof actually consumed

Every step of `ThreeInfinities.lean` is a direct application of existing
Mathlib lemmas, verified against `mathlib v4.31.0`:

| ingredient | Mathlib declaration |
|---|---|
| geometric series in `ℝ≥0∞` | `ENNReal.tsum_geometric` |
| pulling constants out of `tsum` | `ENNReal.tsum_mul_left`, `ENNReal.tsum_mul_right` |
| termwise `tsum` monotonicity (no summability needed) | `ENNReal.tsum_le_tsum` |
| Tonelli over products | `ENNReal.tsum_prod` |
| antitone truncated subtraction / inverse | `tsub_le_tsub_left`, `ENNReal.inv_le_inv`, `tsub_pos_of_lt` |
| finiteness bookkeeping | `ENNReal.mul_ne_top`, `ENNReal.inv_ne_top`, `ne_top_of_le_ne_top` |
| `ℝ≥0∞ → ℝ≥0 → ℝ` bridges | `ENNReal.tsum_coe_ne_top_iff_summable`, `ENNReal.coe_tsum`, `NNReal.coe_tsum`, `NNReal.summable_coe`, `ENNReal.coe_sub/inv/mul/one` |
| normed consumer | `Summable.of_nnnorm`, `norm_tsum_le_tsum_norm` |

No auxiliary lemma had to be *invented*. The only helper introduced,
`tsum_geometric_le_of_le` (`r ≤ q → ∑' rⁿ ≤ (1-q)⁻¹`), is a two-lemma
composition (`ENNReal.tsum_geometric` + inverse antitonicity) — below the
bar Mathlib applies to convenience one-liners without demonstrated
repeated use across the library.

## Verdict: **own repository, not a Mathlib PR** (as stated)

Reasons, in Mathlib's own terms:

1. **No independent mathematical content.** The theorem is a *composition*
   of the ingredients above. Mathlib's review culture asks each lemma to
   be the maximally general unit; compositions whose only glue is a
   specific hypothesis bundle are considered applications, and belong
   downstream.
2. **Programme-shaped hypotheses.** The named budget constants
   (`M, L, K, q, G`, the root/leaf/entropy/profile semantics, the
   `e^{-c₀ t}` prefactor) encode the Appendix-F contract of one research
   programme. A Mathlib-general statement would strip them to "bounded by
   a product of a summable family, a geometric family and a summable
   weight" — at which point it *is* `tsum_le_tsum` + `tsum_mul_*` +
   `tsum_geometric` applied in sequence, i.e. no lemma at all.
3. **The consumer layer is standard.** `summable_of_rootedLeafBudget` is
   the classical "compare with a summable majorant via `ℝ≥0∞`" pattern;
   Mathlib already exposes each step.

## Reversal condition (what would flip this verdict)

Per the tree's falsifier discipline, the verdict carries its own reversal
trigger: **if, during instantiation in the Yang–Mills core, a genuinely
missing reusable Mathlib lemma surfaces** — for example a convenient
`iterated-tsum` Tonelli variant that the elaborator needs in a form not
present, or a monotone-power lemma absent at the required generality —
then *that single lemma* (not this theorem) should be PR'd to Mathlib,
with this repository as the motivating use. During this proof one small
name gap was noticed (`pow_le_pow_right_of_le_one` does not exist at
v4.31.0; `pow_le_one'` + `gcongr` covers the need), which is not a gap in
content, only in naming — not PR-worthy.

## Practical placement

- This satellite hosts the abstract lemmas and their axiom audit.
- `physmath-knowledge-tree` links to it from
  `bridge.three_infinities_rooted_closure` (Lean target discharged:
  abstract form).
- `THE-ERIKSSON-PROGRAMME` vendors the file when instantiating, keeping
  its sorry-free core free of non-Mathlib lake dependencies.
