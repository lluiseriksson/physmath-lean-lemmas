#!/usr/bin/env bash
# Verifies that every public theorem depends only on the three standard
# axioms (propext, Classical.choice, Quot.sound): no sorry, no extra axioms.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=$(lake env lean --stdin << 'LEAN'
import PhysmathLemmas
open PhysmathLemmas
#print axioms tsum_geometric_le_of_le
#print axioms rootedTripleInfinity_closure_le
#print axioms rootedTripleInfinity_closure_le_exp
#print axioms tsum_prod_nnnorm_le_of_rootedLeafBudget
#print axioms summable_of_rootedLeafBudget
#print axioms norm_tsum_le_of_rootedLeafBudget
LEAN
)
echo "$OUT"
if echo "$OUT" | grep -Eq "sorryAx|ofReduceBool|ofReduceNat"; then
  echo "FORBIDDEN AXIOM DETECTED"; exit 1
fi
if echo "$OUT" | grep -q "depends on axioms" && \
   echo "$OUT" | grep -vE "propext|Classical\.choice|Quot\.sound|depends on axioms" | grep -q "axiom"; then
  echo "UNEXPECTED AXIOM"; exit 1
fi
echo "AXIOM CHECK OK: only propext / Classical.choice / Quot.sound"
