# Mother Interface Digest

Satellite: `physmath-lean-lemmas`
Node: `bridge.three_infinities_rooted_closure`
Lean file to vendor: `PhysmathLemmas/ThreeInfinities.lean`

This digest is for `THE-ERIKSSON-PROGRAMME` consumers. It records the
current public Lean interface and the hypotheses the mother repository must
provide when instantiating the satellite. It is bookkeeping/interface
documentation only; it does not claim any source estimate, raw activity
bound, continuum Yang-Mills construction, mass gap, OS/Wightman
reconstruction, or Clay-adjacent progress.

## Consumption Rule

Do not add this repository as a Lake dependency of the sorry-free core.
Vendor the single file `PhysmathLemmas/ThreeInfinities.lean` when the YM
side has the required budget hypotheses, and cite this satellite as the
origin.

Current anchors:

- Public repository: `https://github.com/lluiseriksson/physmath-lean-lemmas`
- Machine-readable interface contract: `docs/interface-contract.json`
- Contract consumption rule: Vendor PhysmathLemmas/ThreeInfinities.lean into the mother repository only after the required budget hypotheses exist; do not add this satellite as a Lake dependency of the sorry-free core.
- Machine-readable source imports: `source_imports` in
  `docs/interface-contract.json`
- Direct Lake requirements: `direct_lake_requirements` in
  `docs/interface-contract.json` currently contains only
  `leanprover-community/mathlib@v4.31.0`
- Top-level import after vendoring: `import PhysmathLemmas`
- Main file sha256: `72ec2d77b2ae1959d90e7767ee986f4aa9b4582e3036409a1e65559fe9eb4edc`
- Toolchain: `leanprover/lean4:v4.31.0`
- Mathlib pin: `v4.31.0`, manifest rev
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
- Release zip sha256:
  `edcaa76668dce5dd87fbef1930bf765aefdca1519a7b3a540730e5418b7e062b`

## Imports And Namespace

The vendored file imports:

```lean
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Topology.Algebra.InfiniteSum.Constructions
import Mathlib.Topology.Algebra.InfiniteSum.ENNReal
```

All public declarations below live in:

```lean
namespace PhysmathLemmas
```

Fully qualified public API names:

- `PhysmathLemmas.tsum_geometric_le_of_le`
- `PhysmathLemmas.rootedTripleInfinity_closure_le`
- `PhysmathLemmas.rootedTripleInfinity_closure_le_exp`
- `PhysmathLemmas.tsum_prod_nnnorm_le_of_rootedLeafBudget`
- `PhysmathLemmas.summable_of_rootedLeafBudget`
- `PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget`

## ENNReal Core

Use this layer when the target quantity is nonnegative extended real and no
summability side condition should be carried.

```lean
theorem tsum_geometric_le_of_le {r q : ℝ≥0∞} (hrq : r ≤ q) :
    ∑' n : ℕ, r ^ n ≤ (1 - q)⁻¹
```

```lean
theorem rootedTripleInfinity_closure_le
    (H : ℕ → ℕ → ι → ℝ≥0∞) (ε : ℕ → ℝ≥0∞) (w : ι → ℝ≥0∞)
    {M L K q G : ℝ≥0∞}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hε : ∑' k, ε k ≤ G) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y ≤ M * G * K * (1 - q)⁻¹
```

Inputs the mother repo must supply:

- `ι`: target/geometry index type.
- `H`: nonnegative extended real activity indexed by scale, order, target.
- `ε`: scale profile.
- `w`: target/geometry weight.
- `hH`: root-leaf budget.
- `hq`: uniform leaf ratio budget.
- `hw`: rooted geometry/entropy budget.
- `hε`: scale-profile budget.

```lean
theorem rootedTripleInfinity_closure_le_exp
    (H : ℕ → ℕ → ι → ℝ≥0∞) (ε g : ℕ → ℝ≥0∞) (w : ι → ℝ≥0∞)
    {M L K q A G₀ : ℝ≥0∞} {c₀ t : ℝ}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hprofile : ∀ k, ε k ≤ A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * g k)
    (hg : ∑' k, g k ≤ G₀) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y
      ≤ M * A * K * G₀ * (1 - q)⁻¹ * ENNReal.ofReal (Real.exp (-(c₀ * t)))
```

Additional inputs for the exponential/card form:

- `g`: marginal profile carrier.
- `hprofile`: pointwise profile bound for `ε`.
- `hg`: summable profile budget.

## Normed-Valued Consumer Layer

Use this layer when the mother repo has a normed-valued object and needs
joint summability over `ℕ × ℕ × ι` or a real norm bound. Here constants are
in `ℝ≥0`, and the consumer must provide `hq1 : q < 1`.

Ambient assumptions:

```lean
variable {E : Type*} [SeminormedAddCommGroup E]
```

Public helper:

```lean
theorem tsum_prod_nnnorm_le_of_rootedLeafBudget
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    ∑' p : ℕ × ℕ × ι, (‖H p.1 p.2.1 p.2.2‖₊ : ℝ≥0∞)
      ≤ (M : ℝ≥0∞) * G * K * (1 - (q : ℝ≥0∞))⁻¹
```

Joint summability:

```lean
theorem summable_of_rootedLeafBudget [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    Summable fun p : ℕ × ℕ × ι => H p.1 p.2.1 p.2.2
```

Consumable real bound:

```lean
theorem norm_tsum_le_of_rootedLeafBudget [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    ‖∑' p : ℕ × ℕ × ι, H p.1 p.2.1 p.2.2‖
      ≤ ((M * G * K * (1 - q)⁻¹ : ℝ≥0) : ℝ)
```

## Suggested Instantiation Order

1. Prove the mother-side pointwise bound `hH`.
2. Prove the uniform ratio budget `hq`; for the real consumer also prove
   `hq1 : q < 1`.
3. Prove `hw` and `hε` in the exact casted forms above.
4. Use `summable_of_rootedLeafBudget` first when a downstream `tsum`
   requires summability.
5. Use `norm_tsum_le_of_rootedLeafBudget` for the exported real bound.
6. Use `rootedTripleInfinity_closure_le_exp` only after the marginal
   profile `hprofile` and `hg` exist on the mother side.

## Verification Gate

Before vendoring a changed copy into the mother repo, rerun:

```bash
lake exe cache get
lake build
./scripts/check_axioms.sh
python3 scripts/check_axioms.py
python3 scripts/check_interface_contract.py
python3 scripts/check_forbidden_tokens.py
```

Expected public axiom set for the six exported theorems:

```text
[propext, Classical.choice, Quot.sound]
```

Forbidden proof tokens in public Lean sources:

```text
[sorry, admit, native_decide]
```
