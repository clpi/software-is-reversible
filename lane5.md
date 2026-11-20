# Lane 5 — build-out and re-validation

Executed 2026-11-20. Home pin before this landing: master at
baa6f25 (lanes 1-4 at c710c2a, 9623cd6, 38d3005, ce06d30, plus
the steering-hold append). Steering hold honoured throughout:
no reach-based ranking ordered the build-out queue; the queue
order is the lanes' own executed validation order only.

## The built stack (stack.py, stack-results.json)

One coherent built form with a single entry point
(stack.py's main), not four disconnected lane scripts. The
meta level of lane 1 sits on top as the weighting-selection
layer; below it, in composition order: frontier-first
selection, the two-face stop, cone-scoped repair, the
distinct-count worklist, the hybrid break-even rule (lane 2);
canonical tie-break and best-first certified decoding,
incremental cone-scoped matrix resolution with the on-the-fly
budgeted form, and the tensor loop certified by recomputed
projection (lane 3); the action combination route with the
obscurity route retained in its home module as the fallback
member (lane 4).

Reuse, stated exactly: lanes 1, 3 and 4 winners are imported
from their own harness modules (meta.py, lane3.py,
actions.py) -- the functions the stack calls are the winners'
actual implementations. Lane 2's five winners existed only
as battery-internal code inside validation-lane2.py, a
script that runs its battery at import, so those five forms
are extracted faithfully into stack.py, each marked EXTRACTED
at its definition with its source battery named. The on-the-fly
budgeted matrix form likewise existed only inside lane3.py's
prop2 battery block; its re-validation copy in revalidate5.py
is extracted the same way and marked.

Demonstration run: stack.py runs the whole stack end to end
on a workload drawn from the lanes' own batteries (the lane 1
instances, a lane 2 point set, stream, DAG epoch and rule
system, the compounding family at 4 stages, the lane 3
fixtures, dataset and loop, one lane 4 instance per family).
Verdict OK; two consecutive runs byte-identical. Full output
in stack-results.json.

## Re-validation (revalidate5.py, revalidation-lane5-results.json)

Method, binding from the program's step 5: each built winner
re-validated (a) against the full candidate set of its
proposition, the eliminated rivals run again against the
built form on the selecting lane's contract, and (b) against
held-out scenario permutations it was not selected on.
Held-out seeds: the lane 5 range 71000-79999, allocated per
proposition in revalidate5.py's docstring, disjoint from
every selecting lane's seeds (lane 2: 2000-6000 series;
lane 3: -1, 1-5, 11-55 and the hash tags d1/d3; lane 4: base
seed 20261120 and offsets; lane 1: none). Two consecutive
whole-battery runs byte-identical (results file sha256
9b0dff7302db9f7428f4f5e2ad0c17a04a21cfd7d7cff345dbf83b99946eea78).

Verdicts, per proposition -- all PASS, no winner returned:

- Meta layer (lane 1). Full set: all 39 configurations run
  again on the three selecting instances; 13 reach every
  middle member, the built selection (weighted max (1, 1),
  from the weight-free meta-frontier of 6) among them.
  Held-out: two new instances at new scales (scale three and
  a decoding-shaped instance with dominated members); the
  built selection selects both middle members; 13 of 39
  configurations reach both; no linear configuration reaches
  any held-out middle member. PASS.
- Proposition 1, frontier-first (lane 2). 300 sets (seed
  71100), 900 order permutations: built form exact against
  the brute-force oracle on every set and permutation;
  recovery 734 of 734 frontier members against weight-first
  626 of 734 -- the weight-first loss re-measured on held-out
  data at 108 non-supported members (selecting run: 75 of
  695). PASS.
- Proposition 2, two-face stop (lane 2). 400 streams (seed
  71200), 30 percent adversarially permuted: built form 400
  optimality claims, 0 false; threshold 766 examined, no
  claims; the fixed-budget rival's false claims re-measured
  at 195 of 400 (selecting run: 192 of 400). PASS.
- Proposition 3, cone-scoped repair (lane 2). 200 DAGs, 941
  executed epochs (seed 71300), append / weight-decrease
  contract: built form exact 941 of 941, 2,193 relaxations
  against 18,781 from scratch and 36,968 scan-per-round
  semi-naive. PASS.
- Proposition 4, distinct-count worklist (lane 2). 300 rule
  systems, 3,124 append prefixes (seed 71400): built form 0
  mismatches against the least-closure oracle, 9,765 checks
  against 45,421 naive and 51,815 semi-naive; the
  duplicate-blind rival re-measured at 147 mismatches
  (selecting run: 192 of 3,208). PASS.
- Proposition 5, hybrid break-even rule (lane 2). Main
  family (seed 71500): built form predicts break-even 15
  queries; the independent empirical crossover on the same
  held-out sample is 15. Regime directions hold at 9, 27, 81,
  729 and 6,561 rows: the rule selects dense at 1 query and
  factored at 2,000 queries in every regime. PASS.
- Lane 3 proposition 1, decoding. Full set run again:
  frontier recomputed as canonical and best-first certified,
  exactly the selecting frontier. Held-out: archive row-order
  permutations at seeds 71601-71608 -- canonical and
  best-first invariant on all eight, greedy not; best-first
  gap 0, 4 certificates issued and sound against the oracle;
  factored's storage loss re-measured (4,971 against 4,488
  bytes). PASS.
- Lane 3 proposition 2, matrix resolution. Held-out datasets
  under new hash tags (lane5a: 321 records, 64 coordinates;
  lane5b: 5,000 records, 256 coordinates): incremental equal
  to full at 3 of 3 and 10 of 10 checkpoints, work 2,435
  against 3,647 and 39,473 against 217,169; order
  permutations at seeds 71611-71613 equal at every checkpoint
  with final readings identical across permutations and to
  the unpermuted order; on-the-fly budgeted covered readings
  equal full exactly on both datasets. PASS.
- Lane 3 proposition 3, tensor loop. Built loop re-run:
  stream [4, 0, 46, 19, 43, 48, 0], certification 4 of 4 by
  recomputed projection, protection and round trip hold,
  digest ca46229572007e59... identical to the selecting run.
  Held-out negative controls on ground lane 3 did not use: a
  phantom claim on coordinate 13 refused (differing
  component: coordinate 13), and a tied-split attempt on the
  group {13, 14} refused by name R-TIED-SPLIT, applying
  nothing. The pinned checkpoint is intact. PASS.
- Lane 4, action combination route. Full set run again on
  420 paired held-out instances (seeds 71000 + family*1000 +
  i, 60 per family): combination 419 of 420, obscurity 418,
  explicit 383, naive control 30. The frontier recomputed
  over (success, total probes) holds combination and explicit
  (explicit survives on the zero-probe axis at lower success;
  combination is the success-maximal member and is not
  dominated). The combination repair leg's near-tie with its
  fallback is re-measured: obscurity's single extra failure
  is move, component position.x; the shared touch failure of
  the selecting run did not recur on this range (combination
  touch 60 of 60). PASS.

No winner failed re-validation, so no proposition's
down-selection was re-run and no new loss is appended by
this lane. The losses named above are the selecting lanes'
losses re-measured on held-out data, printed with their new
figures; they supersede nothing in the earlier records.

## Action-determination spectrum coverage

Added specification (Chris, direct, 2026-11-20 02:04 PST):
for each algorithm in scope, record which spectrum routes
the built form covers and the state of each route-equivalence
claim -- proved, measured, or UNMEASURED, never asserted.
The full per-algorithm table is the SPECTRUM record in
stack.py, which is the built form's own statement. Summary
of that record: route 1 (structurally determined explicitly)
is covered by every built algorithm, with equivalence proved
only where a proof exists in this repo (the frontier segment
family, the break-even theorem) and measured elsewhere;
route 2 (minimization) is covered by the meta selection, the
two-face optimal face, cone-scoped repair, the hybrid rule
and best-first decoding, and is REFUTED as an equivalence
for weight-first against frontier-first and for canonical
against best-first (measured gaps, printed above); route 3
(obscurity vector above threshold) is covered by the action
combination route's repair leg and, in part, by the tensor
loop's obscurity-named edit clause, with route equivalence
measured on success and refuted on probe cost for the action
routes, and UNMEASURED for the loop clause; route 4
(decomposition into finer-grain resolution on a tensor set)
is covered in part by the factored form of the hybrid rule,
the per-coordinate matrix forms, and the tensor loop's
overlay decomposition -- the spectrum's tensor-set sense is
UNMEASURED for all of them; route 5 (the terminal native
constructed minimum compressed tensor form) is covered by
no built algorithm: UNMEASURED across the board. Spectrum
execution is lane 6's; this lane records coverage only and
does not expand into it.

## What stands UNMEASURED, with owners

Everything the selecting lanes left UNMEASURED stands,
unchanged in owner: the relayed Pythia figures and every
real-checkpoint figure (deterministic decoding line);
retraction repair and wall-clock forms of lane 2
propositions 3-4 (lane 2 follow-on); L-gen and L-close
(lane 1); the meta level over the guidance vector space and
over the decoding system, a Lean form of the meta level, and
sampling beyond the 39 configurations (lane 1 successor);
live-surface execution of the action family and its probe
costs (the idol-eyes line); the shared touch failure's
closing candidate (the action model family's successor
lane -- note the failure did not recur on lane 5's range, so
the candidate stays unrun, not closed). Added by this lane:
the spectrum route-equivalence claims marked UNMEASURED in
stack.py's SPECTRUM record (owner: lane 6, which owns the
spectrum execution); the built stack over any workload
beyond the lanes' batteries (owner: lane 5 successor); the
Lean gate at this lane's pin -- Lean was not touched, and
check.sh was not re-run by this lane, so the gate stands as
last recorded by the selecting lanes, UNMEASURED at the new
pin by this lane.
