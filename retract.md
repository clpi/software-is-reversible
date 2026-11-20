# Lane 2 follow-on — retraction repair and wall-clock forms

Executed 2026-11-20. Home pin before this landing: master at
92fd8f21 (the widening lane). This lane closes item R7 of the
left-on-the-table program: the open remainder carried in
validation-lane2.md and lane5.md — retraction repair (weight
increases and withdrawals) in proposition 3, and the
wall-clock forms of propositions 3 and 4. Harness and raw
machine output beside this file (the retract harness and its
results file). Counted operation units remain the primary
contract, exactly as in the selecting battery; wall time is
reported under the discipline stated in section 3 and is
never substituted for the counted contract.

Held-out seeds, disjoint from every prior lane (lane 2 used
the 2000-6000 series, lane 5 used 71000-79999): retraction
battery seed 81000; timing workloads extend the same seeds
(repair grow 82000, retraction 81000, closure 83000).

## 1. Fidelity control

Before any new measurement, the selecting battery was
re-run in a fresh clone and its propositions 3 and 4
compared exactly against the committed results file:
proposition 3 reproduces (936 of 936 exact epochs;
relaxations 2,173 incremental, 17,964 from scratch, 35,713
semi-naive) and proposition 4 reproduces (0 worklist
mismatches over 3,208 append prefixes; checks 9,932
worklist, 48,597 naive, 54,804 scan-per-round). The lane 5
stack figures were also re-run and reproduce (941 of 941;
2,193 against 18,781 and 36,968; 0 mismatches over 3,124
prefixes). The harness re-runs this control on every
execution and refuses to report past a failure. Verdict:
the selecting figures stand as the control for everything
below.

## 2. Retraction repair (proposition 3, extended contract)

Contract, extended: epochs lift (increase) one edge weight
or drop (withdraw) one edge, in the selecting battery's own
graph style (200 directed acyclic graphs, 5 epochs each,
seed 81000). The repaired distance list must equal the
from-scratch distance list after every epoch.

Constructed form: a retraction can only raise distances,
and only along shortest paths that used the retracted edge.
An edge is tight when its tail distance plus its weight
equals its head distance. The repair finds the cone of
nodes reachable from the retracted head over tight edges of
the before graph; a cone node is hit when every tight edge
into it is the retracted edge or comes from a hit node
(decided in node order, the topological order here); hit
nodes are reset and rederived in node order from the after
graph. Nodes outside the hit set keep a shortest path that
never used the retracted edge. Counted unit: one relaxation
is one edge examination, applied to every examination the
repair performs (cone scan, support scan, rederivation
alike). The adjacency maps are carried as state and
maintained incrementally, as the built stack's own
re-validation maintains them.

Executed: 1,000 epochs, all executed (no skips).

- Exactness: repair 1,000 of 1,000 epochs equal to
  from-scratch. No inexact regime was found at any measured
  boundary; the timing-scale replay (section 3) extends
  this to 10,000 of 10,000 epochs at the same seed.
- Relaxations: repair 5,469; from scratch 16,203.
- Regime counts: the retracted edge was tight (carried a
  shortest path) in 438 of 1,000 epochs; in the remaining
  562 the repair is a no-op by the tightness test. Hit nodes
  totalled 1,221 over the tight epochs, largest hit set 18.
- Cost boundary, measured: in 131 of 1,000 epochs (13.1
  percent; 1,422 of 10,000 at timing scale) the repair's
  per-epoch relaxations met or exceeded that epoch's
  from-scratch count — the large-cone regime, where the
  cone and support scans cost more than one flat pass. The
  aggregate win stands (5,469 against 16,203); the
  per-epoch win does not, and its boundary is the tight
  cone's size, printed here rather than smoothed over.

Loss, held-out: the naive control — the append-only cone
repair of the selecting battery, applied unchanged (a lift
epoch hands it the edge at its new weight, which can never
raise a distance; a withdrawal hands it no changed edge at
all). Exact in 335 of 1,000 epochs, wrong in 665 (3,191 of
10,000 at timing scale). Differing component: the
append-only form has no operation that raises a distance,
so every epoch whose retracted edge was tight and load
bearing leaves a stale, too-small distance. This is the
measured content of the old contract's exclusion of
retraction.

Down-selection, extended: cone-scoped repair with the
retraction form above — one repair discipline covering
append, decrease, lift, and drop epochs, exact on every
epoch measured.

## 3. Wall-clock forms (propositions 3 and 4)

Discipline: one machine, one process; workloads generated
once with from-scratch truths precomputed outside every
timed region; each arm's timed replay runs the work its own
form requires (stateful forms maintain their adjacency or
index state inside the timed region; from-scratch carries
none) plus the exactness comparison every arm pays
identically; arms interleaved with the starting arm rotated
each round; 11 rounds; nanosecond totals by a monotonic
counter; medians and paired per-round wins reported, every
raw round kept in the results file. Timing workloads:
proposition 3 grow battery at 2,000 cases (9,363 executed
epochs), retraction battery at 2,000 cases (10,000 epochs),
proposition 4 closure at 1,500 systems (15,883 append
prefixes). Every timed replay re-verified exactness at that
scale: grow arms all exact 9,363 of 9,363 (relaxations:
cone 22,103; from scratch 182,448; scan-per-round 367,002);
closure worklist, naive, and scan-per-round all 0
mismatches over 15,883 prefixes (checks: worklist 49,213;
naive 233,139; scan-per-round 263,254; the duplicate-blind
rival mismatched on 1,014 prefixes, its counted loss
re-measured at scale).

Verdict, proposition 3 (append and decrease contract): the
counted ordering SURVIVES as a time ordering. Medians over
11 rounds: cone repair 105.2 ms, from scratch 118.2 ms,
scan-per-round 159.5 ms — the same order as the counted
22,103 / 182,448 / 367,002. Paired rounds agree: cone beat
scan-per-round in 9 of 11 rounds and from scratch in 7 of
11. Spreads are wide on this shared machine (per-arm least
to greatest spans up to roughly fivefold); the paired
counts, not any single round, carry the verdict.

Verdict, proposition 3 under retraction: the counted
ordering REVERSES in wall time — a printed loss. Repair is
exact and cheapest by counted relaxations (60,247 against
165,334 over the 10,000 epochs), yet its median round is
the slowest of the three arms: from scratch 57.7 ms, the
naive control 97.1 ms, repair 123.9 ms; from scratch beat
repair in 11 of 11 paired rounds. Differing component: the
repair's per-epoch set and map machinery (cone set, sorted
hit pass, per-node scans) against the from-scratch form's
single tight loop over the edge list — at these graph sizes
(8 to 20 nodes) the counted unit's saving does not cover
the machinery's constant factor in this Python form.

Verdict, proposition 4: the counted ordering REVERSES in
wall time — a printed loss. The down-selected worklist is
the cheapest by counted checks (49,213 against naive
233,139 and scan-per-round 263,254) and the slowest by
median wall time: naive 120.8 ms, scan-per-round 180.3 ms,
duplicate-blind 195.2 ms, worklist 378.0 ms. The worklist
lost to naive in 11 of 11 paired rounds and to
scan-per-round in 11 of 11. Differing component: the
counted check unit prices only waiter examinations; the
worklist's per-prefix construction of its missing-premise
sets and waiter index is real work outside that unit, and
in this Python form it costs more than the naive scan's
tight loop saves. The counted down-selection stands on its
own contract; its wall-clock form does not transfer, and
any future speed claim for the worklist must be made in
wall-clock terms on a form whose index construction is
counted or amortised, not from the check counts.

## What stands UNMEASURED after this lane

- Wall-clock forms beyond this machine and these Python
  forms (a compiled form of either winner could restore the
  counted ordering; nothing here measures that). Owner:
  lane 2 follow-on successor.
- Retraction in the closure proposition (rule withdrawal
  against the worklist): this lane's retraction contract
  covers the repair proposition only, as briefed. Owner:
  lane 2 follow-on successor.
- Everything the selecting lanes left UNMEASURED stands
  with its owners unchanged (the relayed Pythia figures,
  L-gen and L-close, execution-layer reversibility).
