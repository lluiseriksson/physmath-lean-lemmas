# physmath-lean-lemmas

General-purpose Lean 4 + Mathlib lemmas extracted from the physmath
programme, machine-checked with **zero `sorry`** and audited axioms
(`propext`, `Classical.choice`, `Quot.sound` only — enforced by
`scripts/check_axioms.sh` and CI).

First release: the **rooted closure of the three infinities**,
`PhysmathLemmas/ThreeInfinities.lean`.

## The theorem

For a rooted family of cluster activities `H : scale → order → target → ℝ≥0∞`
obeying the root–leaf budget

```
H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y
```

with uniform leaf ratio `L * ε k ≤ q`, rooted geometric entropy
`∑' Y, w Y ≤ K`, and scale profile `∑' k, ε k ≤ G`, the **total rooted
influence** — cluster orders `n → ∞`, target geometries `Y → ∞` and RG
scales `k → ∞` closed *simultaneously* — satisfies

```
𝕴(r) = ∑' k n Y, H k n Y ≤ M * G * K * (1 - q)⁻¹        (rootedTripleInfinity_closure_le)
```

and, under the marginal profile `ε k ≤ A · exp(-(c₀·t)) · g k` with
`∑' g ≤ G₀`,

```
𝕴_t(r) ≤ M * A * K * G₀ * (1 - q)⁻¹ * exp (-(c₀ * t))    (rootedTripleInfinity_closure_le_exp)
```

The proof is exactly what the source announces — Tonelli plus a geometric
series. The design decision that makes it robust: the core lives in
`ℝ≥0∞`, where Tonelli (`ENNReal.tsum_prod`) is free and **no summability
hypotheses exist to be carried**; the real/normed-valued consumer layer is
then *derived*, not assumed:

| declaration | content |
|---|---|
| `tsum_geometric_le_of_le` | uniform geometric tail `∑' rⁿ ≤ (1-q)⁻¹` for `r ≤ q` |
| `rootedTripleInfinity_closure_le` | the `ℝ≥0∞` closure |
| `rootedTripleInfinity_closure_le_exp` | the `e^{-c₀ t}` card form |
| `tsum_prod_nnnorm_le_of_rootedLeafBudget` | joint product-indexed `nnnorm` bound |
| `summable_of_rootedLeafBudget` | `Summable` over `ℕ × ℕ × ι` for normed-valued `H` (finite constants, `q < 1`) |
| `norm_tsum_le_of_rootedLeafBudget` | `‖∑' p, H p‖ ≤ M·G·K·(1-q)⁻¹` in `ℝ` |

A fully structural toy instance (`M = 1`, `ε k = (1/4)^{k+1}`, `L = 1/2`,
`w Y = (1/2)^Y`, hence `q = 1/8`, `K = 2`, `G = 1/3`, bound `16/21`) is
included as a documented `example`.

## Scope contract

These are **bookkeeping lemmas**: they collapse three convergence budgets
into one observable and prove nothing about any *source* estimate. The
budget hypotheses are exactly the carried inputs of the Appendix-F front.
Nothing here claims `hRpoly`, a physical activity bound, the continuum
limit, or any Clay-adjacent statement. Distance to any of those after this
repo: unchanged.

## Position in the Eriksson programme

Implementation satellite of the
[physmath-knowledge-tree](https://github.com/lluiseriksson/physmath-knowledge-tree)
node `bridge.three_infinities_rooted_closure` (batch
`batch-2026-07-03-ym-unblock`, Bridge Card 6; source:
`What_is_Infinity.txt`, three-infinities section). The card's minimal Lean
target `rootedTripleInfinity_closure_le` is discharged here in abstract
form; its programme instantiation (feeding it with
`summable_abs_of_omegaRootedClusterWithHolesActivityDecay`-style inputs)
belongs to [THE-ERIKSSON-PROGRAMME](https://github.com/lluiseriksson/THE-ERIKSSON-PROGRAMME).

**Consumption guidance:** the sorry-free YM core should *not* take this
repository as a lake dependency. When instantiating, vendor the single
file `PhysmathLemmas/ThreeInfinities.lean` (Apache-2.0, self-contained
over Mathlib) into the core and cite this satellite as origin — one
audited copy, no external dependency in the trust chain.

For the exact current consumer interface, including theorem signatures,
required hypotheses and verification anchors, see
[`docs/mother-interface-digest.md`](docs/mother-interface-digest.md).

## Mathlib?

Evaluated in [MATHLIB.md](MATHLIB.md). Short version: **not a Mathlib
candidate as stated** — every ingredient already exists in Mathlib and the
theorem is a programme-specific composition of them; the honest reversal
condition (what would flip the verdict) is documented there.

## Build

```bash
# toolchain pinned in lean-toolchain (leanprover/lean4:v4.31.0, mathlib v4.31.0)
lake exe cache get
lake build                    # 0 errors, 0 sorry
./scripts/check_axioms.sh     # only propext / Classical.choice / Quot.sound
```

CI does exactly this on every push, plus a source-level `sorry`/`admit`
grep gate.

## Roadmap (next general lemmas)

In dependency order of the tree's Lean targets: the abstract Schur–Catalan
multiscale coercivity closure (`bridge.schur_catalan_multiscale_closure`);
the Loewner-monotone splitting Lemma S and `Matrix.PosSemidef` of moment
matrices (feeding the `hausdorff-certificates` satellite); Stieltjes
transforms of positive measures (`bridge.penrose_stieltjes_spectral_compactification`).
Each enters only when its statement is consumable by at least one card.

## License

Apache-2.0 (Mathlib convention, so any piece that ever does get upstreamed
carries no friction). See [CITATION.cff](CITATION.cff).
