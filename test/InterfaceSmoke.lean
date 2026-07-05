import PhysmathLemmas

#check PhysmathLemmas.tsum_geometric_le_of_le
#check PhysmathLemmas.rootedTripleInfinity_closure_le
#check PhysmathLemmas.rootedTripleInfinity_closure_le_exp
#check PhysmathLemmas.tsum_prod_nnnorm_le_of_rootedLeafBudget
#check PhysmathLemmas.summable_of_rootedLeafBudget
#check PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget

namespace PhysmathLemmasInterfaceSmoke

variable {ι E : Type*}

example {r q : ENNReal} (hrq : r ≤ q) :
    ∑' n : ℕ, r ^ n ≤ (1 - q)⁻¹ :=
  PhysmathLemmas.tsum_geometric_le_of_le hrq

example
    (H : ℕ → ℕ → ι → ENNReal) (ε : ℕ → ENNReal) (w : ι → ENNReal)
    {M L K q G : ENNReal}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hε : ∑' k, ε k ≤ G) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y ≤ M * G * K * (1 - q)⁻¹ :=
  PhysmathLemmas.rootedTripleInfinity_closure_le H ε w hH hq hw hε

example
    (H : ℕ → ℕ → ι → ENNReal) (ε g : ℕ → ENNReal) (w : ι → ENNReal)
    {M L K q A G₀ : ENNReal} {c₀ t : ℝ}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hprofile : ∀ k, ε k ≤ A * ENNReal.ofReal (Real.exp (-(c₀ * t))) * g k)
    (hg : ∑' k, g k ≤ G₀) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y
      ≤ M * A * K * G₀ * (1 - q)⁻¹ * ENNReal.ofReal (Real.exp (-(c₀ * t))) :=
  PhysmathLemmas.rootedTripleInfinity_closure_le_exp H ε g w hH hq hw hprofile hg

example [SeminormedAddCommGroup E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → NNReal) (w : ι → NNReal)
    {M L K q G : NNReal}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, (w Y : ENNReal) ≤ K)
    (hε : ∑' k, (ε k : ENNReal) ≤ G) :
    ∑' p : ℕ × ℕ × ι, (‖H p.1 p.2.1 p.2.2‖₊ : ENNReal)
      ≤ (M : ENNReal) * G * K * (1 - (q : ENNReal))⁻¹ :=
  PhysmathLemmas.tsum_prod_nnnorm_le_of_rootedLeafBudget H ε w hH hq hw hε

example [SeminormedAddCommGroup E] [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → NNReal) (w : ι → NNReal)
    {M L K q G : NNReal}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ENNReal) ≤ K)
    (hε : ∑' k, (ε k : ENNReal) ≤ G) :
    Summable fun p : ℕ × ℕ × ι => H p.1 p.2.1 p.2.2 :=
  PhysmathLemmas.summable_of_rootedLeafBudget H ε w hH hq hq1 hw hε

example [SeminormedAddCommGroup E] [CompleteSpace E]
    (H : ℕ → ℕ → ι → E) (ε : ℕ → NNReal) (w : ι → NNReal)
    {M L K q G : NNReal}
    (hH : ∀ k n Y, ‖H k n Y‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ENNReal) ≤ K)
    (hε : ∑' k, (ε k : ENNReal) ≤ G) :
    ‖∑' p : ℕ × ℕ × ι, H p.1 p.2.1 p.2.2‖
      ≤ ((M * G * K * (1 - q)⁻¹ : NNReal) : ℝ) :=
  PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget H ε w hH hq hq1 hw hε

example [SeminormedAddCommGroup E] [CompleteSpace E]
    (Hprod : ℕ × ℕ × ι → E) (ε : ℕ → NNReal) (w : ι → NNReal)
    {M L K q G : NNReal}
    (hH : ∀ k n Y, ‖Hprod (k, n, Y)‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ENNReal) ≤ K)
    (hε : ∑' k, (ε k : ENNReal) ≤ G) :
    Summable Hprod := by
  simpa [Prod.eta] using
    PhysmathLemmas.summable_of_rootedLeafBudget
      (fun k n Y => Hprod (k, n, Y)) ε w hH hq hq1 hw hε

example [SeminormedAddCommGroup E] [CompleteSpace E]
    (Hprod : ℕ × ℕ × ι → E) (ε : ℕ → NNReal) (w : ι → NNReal)
    {M L K q G : NNReal}
    (hH : ∀ k n Y, ‖Hprod (k, n, Y)‖₊ ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q) (hq1 : q < 1)
    (hw : ∑' Y, (w Y : ENNReal) ≤ K)
    (hε : ∑' k, (ε k : ENNReal) ≤ G) :
    ‖∑' p : ℕ × ℕ × ι, Hprod p‖
      ≤ ((M * G * K * (1 - q)⁻¹ : NNReal) : ℝ) := by
  simpa [Prod.eta] using
    PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget
      (fun k n Y => Hprod (k, n, Y)) ε w hH hq hq1 hw hε

end PhysmathLemmasInterfaceSmoke
