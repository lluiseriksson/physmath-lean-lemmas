import PhysmathLemmas.ThreeInfinities

#check PhysmathLemmas.tsum_geometric_le_of_le
#check PhysmathLemmas.rootedTripleInfinity_closure_le
#check PhysmathLemmas.rootedTripleInfinity_closure_le_exp
#check PhysmathLemmas.tsum_prod_nnnorm_le_of_rootedLeafBudget
#check PhysmathLemmas.summable_of_rootedLeafBudget
#check PhysmathLemmas.norm_tsum_le_of_rootedLeafBudget

namespace PhysmathLemmasDirectSourceImportSmoke

variable {ι : Type*}

example
    (H : ℕ → ℕ → ι → ENNReal) (ε : ℕ → ENNReal) (w : ι → ENNReal)
    {M L K q G : ENNReal}
    (hH : ∀ k n Y, H k n Y ≤ M * ε k * (L * ε k) ^ n * w Y)
    (hq : ∀ k, L * ε k ≤ q)
    (hw : ∑' Y, w Y ≤ K)
    (hε : ∑' k, ε k ≤ G) :
    ∑' (k : ℕ) (n : ℕ) (Y : ι), H k n Y ≤ M * G * K * (1 - q)⁻¹ :=
  PhysmathLemmas.rootedTripleInfinity_closure_le H ε w hH hq hw hε

end PhysmathLemmasDirectSourceImportSmoke
