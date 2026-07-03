/-
Copyright (c) 2026 Lluis Eriksson. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Lluis Eriksson
-/
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Topology.Algebra.InfiniteSum.Constructions
import Mathlib.Topology.Algebra.InfiniteSum.ENNReal

/-!
# Rooted closure of the three infinities

Formalization of the *three-infinities closure* organizing theorem
(knowledge-tree node `bridge.three_infinities_rooted_closure`, batch
`batch-2026-07-03-ym-unblock`).  A rooted family of cluster activities
`H : scale → order → target → ℝ≥0∞` obeying a root–leaf budget

  `H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y`

with a uniform leaf ratio `L * ε k ≤ q`, a rooted geometric-entropy bound
`∑' Y, w Y ≤ K` and a summable scale profile `∑' k, ε k ≤ G`, has its
**total rooted influence** — summed over cluster orders `n → ∞`, target
geometries `Y → ∞` and RG scales `k → ∞` *simultaneously* — bounded by one
closed constant:

  `𝕴(r) = ∑' k n Y, H k n Y ≤ M * G * K * (1 - q)⁻¹`.

The proof is exactly what the source announces: Tonelli plus a geometric
series.  Working in `ℝ≥0∞` makes Tonelli free and removes every
summability side condition; the real/normed-valued consumer statements
(`Summable`, norm bounds over the *product* index) are then derived, not
assumed.

## Main results

* `PhysmathLemmas.tsum_geometric_le_of_le` — uniform geometric tail bound.
* `PhysmathLemmas.rootedTripleInfinity_closure_le` — the `ℝ≥0∞` closure.
* `PhysmathLemmas.rootedTripleInfinity_closure_le_exp` — the card form
  `𝕴_t(r) ≤ (M·A·K·G₀/(1-q)) · exp (-(c₀ t))` under the marginal profile
  `ε k ≤ A · exp (-(c₀ t)) · g k`.
* `PhysmathLemmas.summable_of_rootedLeafBudget` — joint absolute
  summability over `ℕ × ℕ × ι`.
* `PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget` — the consumable real
  bound `‖∑' p, H p‖ ≤ M * G * K * (1 - q)⁻¹`.

## Scope contract

These are bookkeeping lemmas: they collapse three convergence budgets into
one observable and prove nothing about any *source* estimate.  The budget
hypotheses are exactly the carried inputs of the Appendix-F front; nothing
here claims `hRpoly`, a physical activity bound, or any Clay-adjacent
statement.
-/

open ENNReal NNReal

namespace PhysmathLemmas

variable {ι : Type*}

/-- Uniform geometric bound: if the ratio is dominated, `r ≤ q`, then
`∑' n, r ^ n ≤ (1 - q)⁻¹`.  With the `ℝ≥0∞` conventions no `q < 1`
hypothesis is needed (the bound is `∞` when `q ≥ 1`). -/
theorem tsum_geometric_le_of_le {r q : ℝ≥0∞} (hrq : r ≤ q) :
    ∑' n : ℕ, r ^ n ≤ (1 - q)⁻¹ := by
  rw [ENNReal.tsum_geometric]
  exact ENNReal.inv_le_inv.mpr (tsub_le_tsub_left hrq 1)

/-- **Rooted closure of the three infinities** (`ℝ≥0∞` form).

Under the root–leaf budget `H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y`, the
uniform leaf ratio `L * ε k ≤ q`, the rooted entropy `∑' Y, w Y ≤ K` and
the scale profile `∑' k, ε k ≤ G`, the total rooted influence over scales,
cluster orders and targets simultaneously satisfies

`∑' k n Y, H k n Y ≤ M * G * K * (1 - q)⁻¹`.

Tonelli is free in `ℝ≥0∞`: no summability hypotheses appear, and the
statement is vacuously safe when any constant is `∞`. -/
theorem rootedTripleInfinity_closure_le
    (H : ℕ → ℕ → ι → ℝ≥0∞) (ε : ℕ → ℝ≥0∞) (w : ι → ℝ≥0∞)
    {M L K q G : ℝ≥0∞}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hε : ∑' k, ε k ≤ G) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y ≤ M * G * K * (1 - q)⁻¹ := by
  have step : ∀ k, ∑' (n : ℕ) (Y : ι), H k n Y
      ≤ M * ε k * ((1 - q)⁻¹ * K) := by
    intro k
    calc ∑' (n : ℕ) (Y : ι), H k n Y
        ≤ ∑' (n : ℕ) (Y : ι), M * ε k * (L * ε k) ^ n * w Y :=
          ENNReal.tsum_le_tsum fun n => ENNReal.tsum_le_tsum fun Y => hH k n Y
      _ = ∑' n : ℕ, (M * ε k * (L * ε k) ^ n) * ∑' Y, w Y :=
          tsum_congr fun n => ENNReal.tsum_mul_left
      _ = (∑' n : ℕ, M * ε k * (L * ε k) ^ n) * ∑' Y, w Y :=
          ENNReal.tsum_mul_right
      _ = (M * ε k * ∑' n : ℕ, (L * ε k) ^ n) * ∑' Y, w Y := by
          rw [ENNReal.tsum_mul_left]
      _ = M * ε k * ((∑' n : ℕ, (L * ε k) ^ n) * ∑' Y, w Y) := by
          ring
      _ ≤ M * ε k * ((1 - q)⁻¹ * K) := by
          gcongr
          exact tsum_geometric_le_of_le (hq k)
  calc ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y
      ≤ ∑' k : ℕ, M * ε k * ((1 - q)⁻¹ * K) := ENNReal.tsum_le_tsum step
    _ = ∑' k : ℕ, M * (ε k * ((1 - q)⁻¹ * K)) := by
        simp_rw [mul_assoc]
    _ = M * ∑' k : ℕ, ε k * ((1 - q)⁻¹ * K) := ENNReal.tsum_mul_left
    _ = M * ((∑' k : ℕ, ε k) * ((1 - q)⁻¹ * K)) := by
        rw [ENNReal.tsum_mul_right]
    _ ≤ M * (G * ((1 - q)⁻¹ * K)) := by gcongr
    _ = M * G * K * (1 - q)⁻¹ := by ring

/-- The card form of the closure: with the marginal profile
`ε k ≤ A * exp (-(c₀ * t)) * g k` and `∑' k, g k ≤ G₀`, the total rooted
influence decays exponentially in the RG/collar time `t`:

`𝕴_t(r) ≤ M * A * K * G₀ * (1 - q)⁻¹ * exp (-(c₀ * t))`. -/
theorem rootedTripleInfinity_closure_le_exp
    (H : ℕ → ℕ → ι → ℝ≥0∞) (ε g : ℕ → ℝ≥0∞) (w : ι → ℝ≥0∞)
    {M L K q A G₀ : ℝ≥0∞} {c₀ t : ℝ}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hprofile : ∀ k, ε k ≤ A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * g k)
    (hg : ∑' k, g k ≤ G₀) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y
      ≤ M * A * K * G₀ * (1 - q)⁻¹ * ENNReal.ofReal (Real.exp (-(c₀ * t))) := by
  have hε : ∑' k, ε k ≤ A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * G₀ :=
    calc ∑' k, ε k
        ≤ ∑' k, A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * g k :=
          ENNReal.tsum_le_tsum hprofile
      _ = A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * ∑' k, g k :=
          ENNReal.tsum_mul_left
      _ ≤ A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * G₀ := by gcongr
  calc ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y
      ≤ M * (A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * G₀) * K * (1 - q)⁻¹ :=
        rootedTripleInfinity_closure_le H ε w hH hq hw hε
    _ = M * A * K * G₀ * (1 - q)⁻¹ * ENNReal.ofReal (Real.exp (-(c₀ * t))) := by
        ring

section RealConsumer

variable {E : Type*} [SeminormedAddCommGroup E]

/-- The `ℝ≥0∞` bound for the joint (product-indexed) `nnnorm` sum of a
normed-valued rooted family under the leaf budget with `ℝ≥0` constants. -/
theorem tsum_prod_nnnorm_le_of_rootedLeafBudget
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    ∑' p : ℕ × ℕ × ι, (‖H p.1 p.2.1 p.2.2‖₊ : ℝ≥0∞)
      ≤ (M : ℝ≥0∞) * G * K * (1 - (q : ℝ≥0∞))⁻¹ := by
  have hH' : ∀ k n Y, (‖H k n Y‖₊ : ℝ≥0∞)
      ≤ (M : ℝ≥0∞) * (ε k : ℝ≥0∞) * ((L : ℝ≥0∞) * (ε k : ℝ≥0∞)) ^ n * (w Y : ℝ≥0∞) := by
    intro k n Y
    exact_mod_cast hH k n Y
  have hq' : ∀ k, (L : ℝ≥0∞) * (ε k : ℝ≥0∞) ≤ (q : ℝ≥0∞) := fun k => by
    exact_mod_cast hq k
  have hsplit : ∑' p : ℕ × ℕ × ι, (‖H p.1 p.2.1 p.2.2‖₊ : ℝ≥0∞)
      = ∑' (k : ℕ) (n : ℕ) (Y : ι), (‖H k n Y‖₊ : ℝ≥0∞) :=
    (ENNReal.tsum_prod
        (f := fun (k : ℕ) (r : ℕ × ι) => (‖H k r.1 r.2‖₊ : ℝ≥0∞))).trans
      (tsum_congr fun k =>
        ENNReal.tsum_prod (f := fun (n : ℕ) (Y : ι) => (‖H k n Y‖₊ : ℝ≥0∞)))
  exact hsplit ▸ rootedTripleInfinity_closure_le _ _ _ hH' hq' hw hε

/-- Real/normed-valued consumer: under the leaf budget with **finite**
constants and `q < 1`, the rooted family is (absolutely) summable over the
product `ℕ × ℕ × ι` of scales, orders and targets — the three infinities
are closed jointly, not iteratively. -/
theorem summable_of_rootedLeafBudget [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    Summable fun p : ℕ × ℕ × ι => H p.1 p.2.1 p.2.2 := by
  have hq1' : (q : ℝ≥0∞) < 1 := by exact_mod_cast hq1
  have h1q : (1 - (q : ℝ≥0∞)) ≠ 0 := (tsub_pos_of_lt hq1').ne'
  have hfin : ((M : ℝ≥0∞) * G * K * (1 - (q : ℝ≥0∞))⁻¹) ≠ ⊤ :=
    ENNReal.mul_ne_top
      (ENNReal.mul_ne_top (ENNReal.mul_ne_top ENNReal.coe_ne_top ENNReal.coe_ne_top)
        ENNReal.coe_ne_top)
      (ENNReal.inv_ne_top.mpr h1q)
  have key := tsum_prod_nnnorm_le_of_rootedLeafBudget H ε w hH hq hw hε
  exact Summable.of_nnnorm
    (ENNReal.tsum_coe_ne_top_iff_summable.mp (ne_top_of_le_ne_top hfin key))

/-- The consumable real bound: `‖∑' p, H p‖ ≤ M * G * K * (1 - q)⁻¹`
(right-hand side computed in `ℝ≥0` and coerced to `ℝ`). -/
theorem norm_tsum_le_of_rootedLeafBudget [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → ℝ≥0) (w : ι → ℝ≥0)
    {M L K q G : ℝ≥0}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ℝ≥0∞) ≤ K)
    (hε : ∑' k, (ε k : ℝ≥0∞) ≤ G) :
    ‖∑' p : ℕ × ℕ × ι, H p.1 p.2.1 p.2.2‖
      ≤ ((M * G * K * (1 - q)⁻¹ : ℝ≥0) : ℝ) := by
  have hq1' : (q : ℝ≥0∞) < 1 := by exact_mod_cast hq1
  have h1q : (1 - (q : ℝ≥0∞)) ≠ 0 := (tsub_pos_of_lt hq1').ne'
  have h1qR : (1 - q : ℝ≥0) ≠ 0 := (tsub_pos_of_lt hq1).ne'
  have hfin : ((M : ℝ≥0∞) * G * K * (1 - (q : ℝ≥0∞))⁻¹) ≠ ⊤ :=
    ENNReal.mul_ne_top
      (ENNReal.mul_ne_top (ENNReal.mul_ne_top ENNReal.coe_ne_top ENNReal.coe_ne_top)
        ENNReal.coe_ne_top)
      (ENNReal.inv_ne_top.mpr h1q)
  have key := tsum_prod_nnnorm_le_of_rootedLeafBudget H ε w hH hq hw hε
  have hnn : Summable fun p : ℕ × ℕ × ι => ‖H p.1 p.2.1 p.2.2‖₊ :=
    ENNReal.tsum_coe_ne_top_iff_summable.mp (ne_top_of_le_ne_top hfin key)
  have hRHS : ((M * G * K * (1 - q)⁻¹ : ℝ≥0) : ℝ≥0∞)
      = (M : ℝ≥0∞) * G * K * (1 - (q : ℝ≥0∞))⁻¹ := by
    rw [ENNReal.coe_mul, ENNReal.coe_mul, ENNReal.coe_mul,
      ENNReal.coe_inv h1qR, ENNReal.coe_sub, ENNReal.coe_one]
  have hleNN : (∑' p : ℕ × ℕ × ι, ‖H p.1 p.2.1 p.2.2‖₊)
      ≤ M * G * K * (1 - q)⁻¹ := by
    rw [← ENNReal.coe_le_coe, ENNReal.coe_tsum hnn, hRHS]
    exact key
  calc ‖∑' p : ℕ × ℕ × ι, H p.1 p.2.1 p.2.2‖
      ≤ ∑' p : ℕ × ℕ × ι, ‖H p.1 p.2.1 p.2.2‖ := by
        refine norm_tsum_le_tsum_norm ?_
        simpa [← NNReal.summable_coe, coe_nnnorm] using hnn
    _ = ((∑' p : ℕ × ℕ × ι, ‖H p.1 p.2.1 p.2.2‖₊ : ℝ≥0) : ℝ) := by
        rw [NNReal.coe_tsum]
        simp [coe_nnnorm]
    _ ≤ ((M * G * K * (1 - q)⁻¹ : ℝ≥0) : ℝ) := by
        exact_mod_cast hleNN

end RealConsumer

section ToyInstance

/-- Documented toy instance of the closure (the "next finite computation"
of the bridge card), fully structural: `M = 1`, `ε k = (1/4)^(k+1)`,
`L = 1/2`, `w Y = (1/2)^Y` over `ι = ℕ`.  The uniform leaf ratio is
`q = 1/2 · 1/4 = 1/8`, the rooted entropy is `K = (1 - 1/2)⁻¹ = 2` and the
profile mass is `G = (1 - 1/4)⁻¹ · 1/4 = 1/3`, so the closed bound equals
`M·G·K·(1-q)⁻¹ = 16/21`; the constants are kept symbolic below so that the
example is independent of `ℝ≥0∞` numeral arithmetic. -/
example :
    ∑' (k : ℕ) (n : ℕ) (Y : ℕ),
        ((4 : ℝ≥0∞)⁻¹ ^ (k + 1) * (2⁻¹ * 4⁻¹ ^ (k + 1)) ^ n * 2⁻¹ ^ Y)
      ≤ 1 * ((1 - 4⁻¹)⁻¹ * 4⁻¹) * (1 - 2⁻¹)⁻¹ * (1 - 2⁻¹ * 4⁻¹)⁻¹ := by
  refine rootedTripleInfinity_closure_le (L := 2⁻¹)
    (fun k n Y => (4 : ℝ≥0∞)⁻¹ ^ (k + 1) * (2⁻¹ * 4⁻¹ ^ (k + 1)) ^ n * 2⁻¹ ^ Y)
    (fun k => (4 : ℝ≥0∞)⁻¹ ^ (k + 1)) (fun Y => (2 : ℝ≥0∞)⁻¹ ^ Y)
    (fun k n Y => le_of_eq (by ring)) (fun k => ?_) ?_ ?_
  · -- uniform leaf ratio:  2⁻¹ * 4⁻¹ ^ (k+1) ≤ 2⁻¹ * 4⁻¹  (= q)
    calc (2 : ℝ≥0∞)⁻¹ * 4⁻¹ ^ (k + 1)
        = 2⁻¹ * (4⁻¹ ^ k * 4⁻¹) := by rw [pow_succ]
      _ ≤ 2⁻¹ * (1 * 4⁻¹) := by
          gcongr
          exact pow_le_one' (by simp) k
      _ = 2⁻¹ * 4⁻¹ := by rw [one_mul]
  · -- rooted entropy:  ∑' Y, (1/2)^Y = (1 - 1/2)⁻¹  (= K)
    exact le_of_eq (ENNReal.tsum_geometric _)
  · -- scale profile:  ∑' k, (1/4)^(k+1) = (1 - 1/4)⁻¹ * 1/4  (= G)
    refine le_of_eq ?_
    calc ∑' k : ℕ, (4 : ℝ≥0∞)⁻¹ ^ (k + 1)
        = ∑' k : ℕ, 4⁻¹ ^ k * 4⁻¹ := tsum_congr fun k => by rw [pow_succ]
      _ = (∑' k : ℕ, (4 : ℝ≥0∞)⁻¹ ^ k) * 4⁻¹ := ENNReal.tsum_mul_right
      _ = (1 - 4⁻¹)⁻¹ * 4⁻¹ := by rw [ENNReal.tsum_geometric]

end ToyInstance

end PhysmathLemmas
