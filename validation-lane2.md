# Validation lane 2 — meta-search solve and validate, set A

Executed 2026-11-20. Home pin before this landing: master at
d05ff699. Battery: the Python harness stored beside this file
(validation lane 2 harness and its results file, counted
operation counts throughout; wall time is reported only where
stated and is never the contract). Held-out discipline: every
scenario set below uses seeds disjoint from every prior lane
(seeds 2000, 3000, 4000, 5000, 6000 series), and every
proposition adds order permutations the selection was not made
on. A candidate with no run is UNMEASURED, never a winner.

Verdicts reused, not recomputed (pipeline verification lanes,
redundant compute expands repo, third pull head fdc8049c, main
a7171c6a): 160 synthetic frontiers matched exhaustive search;
incremental repair 1,771 relaxations against 2,835 from
scratch; subset oracle agreement at all 256 checkpoints;
the threshold control (latency 9 accepted while latency 2 was
open), proved in this repo. The closure worklist lane's counts
are also reused where named: its indexed form proved in Lean
(51 theorems, local pin eb29b7d, nothing pushed) and its
duplicate premise finding (the duplicate-blind counter
disagreed on 40 of 256 menu systems).

## Proposition 1 — frontier selection and reweighting

Candidate set, over the one hypergraph (joint plans as terms,
dominance as the premise relation): (a) frontier first, then
weights select within the frontier (the constructed form);
(b) weight first, the ranking head of a positive linear
weighting (the incumbent scalarized form); (c) block nested
loops skyline computation of the frontier; (d) one-append
incremental frontier computation; (e) exhaustive brute force,
the oracle.

Solved frontier, weight-free (axes: frontier set exactness,
selection recovery of frontier members): (a), (c), (d), (e)
are exact and recover every frontier member as selectable;
(b) is off the frontier on the recovery axis.

Validation, executed: 300 random point sets (seed 2000
series); block nested loops and the incremental form agreed
with the oracle on 300 of 300; 900 held-out input order
permutations (3 shuffles per set) changed no frontier, 900 of
900. Selection recovery over a positive weight grid (both
weights 1 to 9): frontier members totalled 695; weight first
recovered 620 of 695 (89.2 percent); frontier first recovered
695 of 695. The segment counterexample family reproduced: the
middle plans (6, 6) and (11, 11) were selected by no grid
weight, matching the proved form in this repo.

Down-selection: frontier first, computed by block nested
loops or the incremental form (equal here), weights within
the frontier only.

Loss, held-out: weight first. Differing component: scalarized
ranking — 75 of 695 frontier members are non-supported points
no positive linear weighting selects; reweighting cannot
recover them, exactly the proved counterexample class at
random scale.

## Proposition 2 — stop rules, acceptable face vs optimal face

Candidate set: (a) threshold stop, claiming acceptability
only; (b) optimal stop, certifying against every remaining
alternative before claiming optimality; (c) fixed budget stop
(3 plans) that claims optimality; (d) the two-face form:
threshold for the acceptable face, certification for the
optimal face, the faces reported separately (constructed).

Solved frontier, weight-free (axes: plans examined, false
optimality claims): (a) and (d) stand on the frontier —
(a) cheapest with no optimality claim, (d) claim-complete at
full examination cost. (c) is dominated by (a) on both axes.

Validation, executed: 400 random plan streams (seed 3000
series), 30 percent of trials adversarially permuted so the
best plan arrives last (held-out permutations). Threshold:
779 plans examined in total, no false optimality claims (it
makes none), every acceptable claim sound. Optimal stop:
2,806 examined, 400 optimality claims, 0 false. Two-face:
2,806 examined, 400 optimality claims, 0 false, acceptable
face reported at threshold. The reused control stands: plans
9 and 2, threshold 10 — the first acceptable plan is 9 while
2 is open.

Down-selection: the two-face form (d). It is the only
candidate that reports both faces soundly.

Loss, held-out: the fixed budget stop (c). Differing
component: truncation without certification — 192 of 400
optimality claims false (48 percent), and it examined more
plans (1,200) than the threshold form while claiming more.

## Proposition 3 — incremental repair

Candidate set: (a) cone-scoped incremental repair (only edges
out of improved nodes are relaxed); (b) from-scratch
recomputation each epoch; (c) semi-naive rounds that scan the
full edge set each round and fire only frontier-tailed edges.
Contract, stated: epochs append an edge or decrease an edge
weight (the append-only setting). Weight increases are
retraction and are out of this contract, named below.

Solved frontier, weight-free (axes: exactness against the
oracle distances, relaxation count): (a) alone — exact and
cheapest. (b) and (c) are exact here but cost-dominated.

Validation, executed: 200 random directed acyclic graphs,
5 epochs each, 936 executed epochs (seed 4000 series, held
out from the reused 32 cases). Agreement with from-scratch
oracle distances: incremental 936 of 936, semi-naive 936 of
936. Relaxations: incremental 2,173; from scratch 17,964;
semi-naive 35,713. Incremental was strictly cheapest in 933 of 936
epochs. Direction corroborated by the reused verdict at the
prior pin: 1,771 against 2,835.

Down-selection: cone-scoped incremental repair (a).

Loss: none on exactness under this contract. Cost loss:
semi-naive as scanned here — its differing component is the
full scan per round, which costs more than from scratch.
UNMEASURED, owned by lane 2 follow-on: epochs with weight
increases or withdrawals (retraction repair), and wall time
(all figures here are counted relaxations, as in the reused
verdict, not wall-clock speed).

## Proposition 4 — the closure worklist

Candidate set: (a) the worklist with distinct missing-premise
counts and a waiter index (constructed, proved form cited in
the preamble); (b) naive least closure by full scan to a
fixed point (the oracle); (c) scan-per-round semi-naive
closure; (d) the duplicate-blind worklist, whose count starts
at the premise list length (the refuted rival of the worklist
lane's Finding 2).

Solved frontier, weight-free (axes: exactness against the
least closure at every append prefix, rule checks): (a)
alone — exact and cheapest. (b) and (c) exact but dominated
on checks.

Validation, executed: 300 random rule systems (seed 5000
series), compared at every append prefix: 3,208 prefix
comparisons. Mismatches against the least closure oracle:
worklist 0, scan-per-round 0, duplicate-blind 192. Rule
checks: worklist 9,932; naive oracle 48,597; scan-per-round
54,804. Duplicated premises occur in this corpus by
construction, matching the canonical semantics (membership,
not multiplicity — the worklist lane's Finding 2, whose own
corpus gave the same component at 40 of 256 systems).

Down-selection: the worklist (a). Its Lean equality form
(L-close) remains lane 1's open lemma; the empirical side
here is closed at these bounds.

Loss, held-out: the duplicate-blind worklist (d). Differing
component: the count itself — a duplicated premise is counted
twice and decremented once, so a rule whose premises are all
derived may never fire; 192 of 3,208 prefixes derived a
strictly smaller set than the least closure.

## Proposition 5 — the break-even rule, full cost form

Theorem state: proved in this repo in full cost form (setup,
validation, persistence, restart). Empirical state before
this lane: UNMEASURED. This section is the empirical battery
the brief ordered; it runs on the compounding witness family
(8 stages of 3 choices, 6,561 joint plans), not on the
relayed Pythia fixture bytes, which are absent from this
machine — those figures stay UNMEASURED, owner: the
deterministic decoding line, blocked on its standalone repo
access on the relaying side.

Candidate set: (a) the factored recipe — plans held as a
product of per-stage pools, fixed cost paid once (setup plus
validation against the dense oracle on 16 queries, both scans
counted, plus persistence of the pools at 208 bytes and
restart as a pool re-read), per query a per-stage scan;
(b) dense materialization — all 6,561 rows built, per query a
row scan; (c) the hybrid: compute the predicted break-even
count from the measured unit costs in the full cost form and
use the factored recipe exactly when the expected query count
reaches it (constructed).

Solved frontier, weight-free (axes: total counted operations
at a stated query count, fixed cost): dense stands at low
query counts in small regimes, factored at high counts, the
hybrid weakly dominates both by selecting per regime — the
frontier is the pair (dense, factored) with the hybrid as
the selection rule over it.

Validation, executed (seed 6000 series): main family —
factored per query 16.48 counted operations against dense
3,375.8; fixed cost in full form 56,408 operations excluding
persistence (26 operation equivalents at 8 bytes per
operation) — validation against the dense oracle is the
dominant fixed component, which is exactly why the full cost
form matters. Predicted break-even from the measured units:
17 queries. Empirical crossover, counted totals: 17 queries
against query-only dense totals, and 1 query against dense
totals that include materialization (6,561 rows). Wall time,
secondary and not the contract: 512 queries took 2.8407
seconds dense against 0.0014 seconds factored, as printed
in the results file.
Held-out permutation: shuffling the 512 query order left the
factored total exactly unchanged.

Regime sweep, same protocol, family size varied (the rule
must also say when reuse loses, and it does): 2 stages
(9 rows) — fixed 162, crossover 145 queries; 3 stages
(27 rows) — fixed 323, crossover 47; 4 stages (81 rows) —
fixed 823, crossover 25; 6 stages (729 rows) — fixed 5,893,
crossover 17; 8 stages (6,561 rows) — fixed 41,776 on that
sample, crossover 15. The main run's 17 and the sweep's 15
at 8 stages are two samples of the same quantity; the rule's
prediction tracks the measured crossover in every regime.

Down-selection: the hybrid (c) — the break-even rule itself,
now empirically validated in both directions.

Loss, named: the factored recipe below its crossover (for
example the 2-stage regime under 145 queries, and the
8-stage regime under 15 to 17 queries) — differing
component: the fixed cost, dominated by validation against
the oracle. Dense alone loses above every crossover by the
per-query scan component.

## What stands UNMEASURED after this lane

- The relayed Pythia recipe figures (the five-byte recipe
  against the dense mask): still UNMEASURED. Owner: the
  deterministic decoding line; blocker: the standalone repo
  is not on this machine (relaying-side access).
- Retraction repair (weight increases, withdrawals) in
  proposition 3, and wall-clock forms of propositions 3 and
  4: UNMEASURED. Owner: lane 2 follow-on.
- L-gen and L-close as Lean lemmas: unchanged, lane 1.
- Execution-layer reversibility: unchanged, lane 4.
