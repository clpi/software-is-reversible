# Lane 6 — the action-determination spectrum

Meta-search solve-and-validate program (Chris, direct,
2026-11-20 02:04 PST). Home pin before this landing: master
at baa6f25 (the steering hold append; lanes 1 to 4 landed
beneath it). The harness is the spectrum file in this repo;
its full machine output is the spectrum results file beside
it. Two consecutive runs byte-identical; verdict OK.

## The spectrum, as ordered

For each algorithm in the program's scope, its action
construction is produced and validated under each applicable
route of the spectrum:

1. Structurally determined explicitly — a stated closed-form
   rule or planner; no search over candidates, no weighting.
2. Through minimization — the output is the minimiser of a
   stated scalar score over an enumerated candidate set.
3. Through the obscurity vector above threshold — construction
   driven by the obscurity reading (unresolved, unprojected,
   uncertain; the decomposition family of the recursive file),
   acting only where the reading reaches the threshold of two
   clauses, by probe-and-observe or by resolving the
   highest-obscurity region first.
4. Through decomposition into finer-grain resolution by the
   deterministic algorithm on a tensor set — cone-scoped
   incremental updates, waiter-index firing, subtree or heap
   decomposition, stage factorisation, scope widening.
5. The terminal form — the native constructed minimum
   compressed tensor representing the equivalent behavior
   without the algorithmic overhead: one stored tensor, read
   by projection or lookup, no search, loop, or scan at query
   time. Tensor size is measured against the algorithmic
   form's size; the tensor's construction cost is accounted
   separately, under the break-even discipline.

Where a route is not applicable to an algorithm, this record
says why in one line — never a silent skip. Equivalence
between routes is a claim per algorithm and is printed in
exactly one state: proved (a named theorem at a named pin),
measured (executed equality on the proposition's contract
battery, same contract across routes), or UNMEASURED with an
owner. Measured non-equivalence is printed as a loss with its
differing component, by the program's standing rule.

Concluding order, as ordered: algorithms with unique results
or large potential downstream consequence first — best-first
certified decoding; the two-face stop form; frontier-first
selection; the combination action route — then the remaining
algorithms in this order: cone-scoped repair, the
distinct-count worklist, the break-even hybrid, canonical
tie-break, the matrix resolution pair, the tensor loop, the
meta level. The steering hold stands: no reach-based ranking
ordered anything in this lane.

## Fidelity controls (executed before any spectrum figure)

Every lane battery was re-run at its own pin and seeds, and
its headline figures checked against the lane's committed
results file. All controls passed: lane 2's five propositions
reproduce exactly (695 frontier members and 620 weight-first
recoveries; 192 false budget-stop claims; 936 of 936 repair
epochs with 2,173 against 17,964 relaxations; 3,208 worklist
prefixes with 192 duplicate-blind mismatches; break-even
crossover 17, predicted 17); lane 3's three propositions
reproduce (frontier of the decoding rivals, certificate
soundness, the tensor loop digest); lane 1's meta level
reproduces (13 reaching configurations, meta-frontier of 6,
the demonstration selection); lane 4's action totals
reproduce (391, 419, 419, 46). The spectrum harness fails
loudly if any control fails. The Lean gate was not re-run in
this lane: no Lean toolchain exists on this machine, and no
Lean file is touched; proof states below cite the gate as
last recorded, cold PASS at the base pin of the program,
exactly as lane 1 recorded it.

## Landing note — lane 5, and one classification determination

Lane 5 landed during this lane's run (its commit at
984f1fa, since merged over by three further landings; this
lane's commit is rebased over them, the one conflict — the
README pointer list — resolved by keeping both appends, and
the search file's expansion log carries both lanes'
entries). Lane 5's coverage table had recorded the
spectrum's unexecuted cells as UNMEASURED with lane 6 as
owner — route 5 across the board among them — and this
record is that execution; lane 5's table stands as the
prior record and is not rewritten. Lane 5 also re-validated
every down-selected winner on a disjoint held-out seed
range (71000 to 79999): all ten propositions passed, which
corroborates, at independent seeds, the winners this
spectrum takes as its home forms. One classification
determination differs from lane 5's narrower reading and is
stated openly: lane 5 recorded cone-scoped repair's route 4
cell as not covered in the spectrum sense (a premise cone
is a scope, not a tensor decomposition). This lane counts
the cone form as route 4 — the epoch's resolution is
decomposed to exactly the changed edge's premise cone, a
finer grain than the graph — and separately executes the
tensor-set forms for repair under routes 2 and 5, so the
determination costs the record nothing: both readings'
cells are executed and printed in the repair section.

## (a) Best-first certified decoding — CONCLUDED

Battery: lane 3 proposition 1 (five archived-row fixtures,
exhaustive oracle; counted evaluations; certificates
re-checked sound in the run).

- Route 1, explicit: exhaustive enumeration of every complete
  sequence, maximum total winning, ties by smallest stream.
  Produced and validated: streams, totals, and statuses equal
  the best-first form on 5 of 5 fixtures.
- Route 2, minimization: the home form itself is the global
  minimization (the certified argmin over complete sequences).
  The local per-step form (greedy argmin) was executed by
  lane 3 and is measured non-equivalent: gap 1,700 milli,
  entirely the trap fixture — differing component: the first
  step (token 4 against 5). Global form: equivalent (below).
  Local form: a printed loss, not a route to this algorithm.
- Route 3, obscurity: not applicable — decoding has no probe
  surface: an archived row is fully observed or absent, and
  an absent row is carried as an unresolved bound by the
  certification rule, never probed.
- Route 4, decomposition: the archive decomposed by first
  token into independent subtrees (134 subproblems across the
  five fixtures), each subtree's optimum solved once and the
  minima composed. Equal on 5 of 5 fixtures.
- Route 5, terminal: the policy tensor — per fixture, per
  archived prefix, the certified-optimal next token and the
  value from that prefix, stored. Lookup walks 14 entries in
  total across the battery against the home form's 114 heap
  evaluations, and reproduces streams, totals, and statuses
  on 5 of 5 fixtures, the missing-row fixture carried as
  unresolved with no certificate, as at home. Size: the
  tensor is 5,795 bytes against the plain archive's 4,488 —
  at fixture scale the terminal form eliminates the search
  but does not compress; the size loss is printed as such.
- Equivalence: route 1 against home — measured (5 of 5,
  certificates re-checked sound). Route 4 against home —
  measured (5 of 5). Route 5 against home — measured on the
  battery (5 of 5); beyond the battery, UNMEASURED (below).
  The certificate's soundness shape is proved: the
  certification theorem of the Lean core's stop section (a
  chosen plan certified against the whole remaining set is
  no worse than every remaining plan), at the program's base
  pin. No stronger equivalence is claimed.

## (b) The two-face stop form — CONCLUDED

Battery: lane 2 proposition 2 (400 plan streams, seed 3000
series, adversarial permutations included).

- Route 1, explicit: the home form — the threshold rule for
  the acceptable face, certification against every remaining
  plan for the optimal face, the faces reported separately.
  400 streams, 0 false optimality claims, 397 acceptable
  reports (397 streams hold an acceptable plan).
- Route 2, minimization: two executed forms, both measured
  non-equivalent to the two-face form as a whole. The
  full-scan argmin (lane 2's optimal candidate) matches the
  optimal face exactly (400 claims, 0 false) but produces no
  acceptable face at all — differing component: the
  acceptable face. The truncated argmin (stop after three,
  claim optimality) is false on 192 of 400 claims —
  differing component: truncation without certification.
- Route 3, obscurity: not applicable — the stop decision's
  inputs are the plans themselves; an obscurity reading over
  unexamined plans is unobservable without examining them,
  and gating on it collapses to the truncated form measured
  false above.
- Route 4, decomposition: certification decomposed into
  blocks of three plans; a block certificate is its minimum;
  the chosen plan is certified exactly when it beats or ties
  every block certificate. Decisions equal the home form on
  400 of 400 streams. Counted cost is not better: 2,806
  comparisons against 2,406 for the flat form (one extra
  comparison per stream, against the chosen plan's own block
  minimum). The decomposition's value is compositional —
  block certificates compose — and is claimed as nothing
  more.
- Route 5, terminal: the certification predicate as a stored
  tensor over the battery's finite domain (latencies 1 to
  20): 400 entries, plus the 20-entry acceptable tensor —
  420 bits packed (898 bytes in the stated JSON encoding).
  The tensor agrees with the rule on all 400 domain pairs
  (exhaustive over the domain), and the table-driven
  two-face form reproduces the home form exactly: 400
  claims, 0 false, 397 acceptable reports.
- Equivalence: route 4 — measured (400 of 400 decisions).
  Route 5 — measured, exhaustive over the stated finite
  domain. The faces' soundness components are proved in the
  Lean core's stop section: the fuel-loop soundness results,
  the certification theorem, and the threshold control (a
  threshold accepts the worse plan while the better is still
  open — the standing refutation of any threshold-only
  optimality claim), at the program's base pin.

## (c) Frontier-first selection — CONCLUDED

Battery: lane 2 proposition 1 (300 point sets, seed 2000
series, 900 order permutations; 695 frontier members).

- Route 1, explicit: block nested loops over the point set.
  Exact on 300 of 300 sets, invariant on 900 of 900
  permutations.
- Route 2, minimization: linear minimization is proved
  non-equivalent — the middle plan of the counterexample
  triples stands on the frontier and is selected by no
  positive linear weighting (the Lean core's frontier
  section, both scales) — and measured non-equivalent at
  random scale: the 1-to-9 grid recovers 620 of 695 members;
  the 75 missed members are the non-supported points, the
  proved class. Nonlinear minimization (the meta level's 21
  enumerated nonlinear configurations, frontier-restricted)
  recovers 545 of 695 — by family: weighted max 541, squared
  413, balance overlay 306. The union of the linear grid and
  the nonlinear set recovers 667 of 695. The remaining 28
  members are selected by no enumerated configuration of any
  family run in this program: UNMEASURED, owned below.
- Route 3, obscurity: not applicable — the point sets are
  fully observed finite objects; their obscurity reading is
  identically zero and nothing is ever probed.
- Route 4, decomposition: the one-append incremental form
  (the insert-exact update). Exact on 300 of 300 sets.
- Route 5, terminal: the frontier itself as a stored tensor,
  with a precomputed selection tensor over 102 weightings.
  Across the battery the frontier tensors total 4,814 bytes
  against 19,100 for the point sets (a fourfold compression,
  because dominated points are not stored); all 30,600
  selection lookups equal direct computation.
- Equivalence: route 1 against route 4 — proved (the
  one-append update theorem in the Lean core, plus the
  incremental-equals-full result cited at its pin in the
  census) with measured corroboration (300 of 300). Route 5
  lookups against direct selection — measured (30,600 of
  30,600). Route 2 linear — proved and measured
  non-equivalence, above. Route 2 nonlinear — measured
  partial recovery; full recovery by any fixed enumerated
  family is not claimed anywhere in this program.

## (d) The combination action route — CONCLUDED

The algorithm is basic action selection over the seven
scenario families; its down-selected form is the combination
route (explicit plan, one verification observation, obscurity
repair). Battery: lane 4 (60 paired instances per family,
base seed 20261120), re-run per instance in this lane so
route-pair agreement is measured instance by instance, not
inferred from totals. Simulated scenarios only, as at home.

- Route 1, explicit: the explicit rival — 391 of 420.
- Route 2, minimization (new in this lane): a fixed candidate
  grid per family, the output the argmin of a stated scalar
  residual, no adaptive shrinking, no obscurity gating.
  Successes: move 53, jump 60, jump over 60, drive 60, touch
  60, type 60, automate 60 — 413 of 420 in total, at grid
  evaluation totals across the 60 instances from 1,089
  (automate) to 253,500 (move). Two located results. Move loses 7 instances
  to the combination route — differing component: the fixed
  command grid's step of 2.0 against the 2.0 tolerance under
  response scales up to 1.3. Touch succeeds on all 60,
  including the one instance (index 2 of the family) where
  both the obscurity route and the combination route fail —
  differing component: grid resolution (the minimization
  grid reads 63 points of the target rectangle against the
  obscurity probe set's 21); the finer-grid closing candidate
  lane 4 left open is therefore measured, in simulation, to
  close the shared failure. No live-surface claim follows.
- Route 3, obscurity: the obscurity rival — 419 of 420. Its
  success set is identical to the combination route's on
  this battery (both succeed on the same 419 instances;
  symmetric difference 0). Outcome equivalence of the two
  routes is therefore measured on the battery; their action
  parameters are not claimed equal — the routes construct
  different actions that land within the same tolerances.
- Route 4, decomposition (new in this lane, three families):
  move as two composed half-legs with re-observation between
  legs — 60 of 60; drive as per-waypoint legs, each leg
  freshly planned at its boundary — 60 of 60; automate as
  dependency layers with in-layer deferral — 60 of 60. Each
  agrees with the combination route on all 60 of its
  instances. For the remaining families no separate
  decomposition was constructed: jump is a one-parameter
  action with no finer grain; jump over's stated plan already
  searches a one-parameter flight-time decomposition, which
  is the explicit form's own structure; touch selects a
  point, which has no sub-action grain; type already acts at
  its finest grain, one character.
- Route 5, terminal: attempted as a memorised tensor —
  nearest-neighbour lookup over the battery instances'
  features, the stored instance's action applied — and
  measured refuted on held-out instances (fresh seeds, 60
  per family): move 0 of 60, jump 12 of 60. A stored-action
  tensor does not represent this family's behavior off its
  training instances. No terminal form is constructed for
  this algorithm; owner below.
- Equivalence: route 3 against the combination form —
  measured outcome equivalence (identical success sets,
  419). Route 1 against the combination form — measured:
  the combination route succeeds on every instance the
  explicit route succeeds on, and on 28 more (the repair
  leg's measured margin; the 29th repair attempt is the
  shared touch failure). Route 2 — measured per family
  above (agreement with the combination route: 53, 60, 60,
  60, 59, 60, 60). Route 4 — measured on the three families
  run. Live-surface execution of every route remains
  UNMEASURED (the idol-eyes line's matched campaign).

## Cone-scoped repair — concluded

Battery: lane 2 proposition 3 (200 graphs, 936 executed
append or weight-decrease epochs, seed 4000 series).

- Route 1, explicit: from-scratch recomputation per epoch —
  exact, 17,964 relaxations.
- Route 2, minimization (new): label-setting minimization
  (a Dijkstra pass from the source over the whole graph, per
  epoch) — distances equal the oracle on 936 of 936 epochs,
  at 11,496 relaxations: cheaper than the flat from-scratch
  count, 5.3 times the cone cost.
- Route 3, obscurity: not applicable — the graph is fully
  observed at every epoch; the repair trigger is the changed
  edge and its premise cone, not an obscurity reading.
- Route 4, decomposition: the home form (cone-scoped repair)
  — exact on 936 of 936 epochs at 2,173 relaxations, cheapest
  in 933 of 936.
- Route 5, terminal: the all-pairs distance tensor per epoch,
  the query a row projection — on a stated sub-battery (the
  first 300 executed epochs) the tensor's source row equals
  the oracle distances on 300 of 300. Cost, printed as a
  trade and not a win: building the tensor costs 372,192
  counted operations over the sub-battery and the tensors
  total 498,799 bytes against 50,502 for the edge lists; the
  terminal form pays a full rebuild per epoch to make the
  query free, and under this contract (an epoch per query)
  that trade loses. It wins only where many queries read one
  epoch's tensor — a regime this battery does not run:
  UNMEASURED, owned below.
- Equivalence: routes 1, 2, 4 — measured pairwise through
  the oracle (936 of 936 each). Route 5 — measured on the
  sub-battery (300 of 300).

## The distinct-count worklist — concluded

Battery: lane 2 proposition 4 (300 rule systems, every
append prefix, 3,208 comparisons, seed 5000 series).

- Route 1, explicit: the naive least-closure scan (the
  oracle) — 48,597 rule checks.
- Route 2, minimization (new): priority firing — at each
  step fire the ready rule whose distinct missing count is
  minimal. Exact: 0 mismatches across all 3,208 prefixes.
  Cost: 54,610 checks — worse than the naive scan; the
  minimization determines the firing order correctly and
  buys nothing, printed as a cost loss.
- Route 3, obscurity: not applicable — rule systems are
  fully observed; no coordinate carries an obscurity reading.
- Route 4, decomposition: the home form (distinct counts
  plus the waiter index) — 0 mismatches, 9,932 checks.
- Route 5, terminal: two tensors measured. The per-term
  closure bitsets, queried by union over the seed set, are
  refuted: 289 of 12,878 seed-set queries disagree with the
  least closure — differing component: a rule whose premises
  are derived from different seeds joins them only in the
  joint closure (first instance: seeds 0 and 5, term 6
  missing from the union). The powerset tensor — the closure
  of every seed subset, stored — is exact: on the stated
  sub-battery (191 systems of at most 9 terms, all 31,136
  subset entries) every lookup equals the independent scan
  oracle. Its size is the verdict on compression: 621,479
  bytes of tensor against 18,883 for the rule lists. The
  terminal form exists and is exact, and the worklist is
  its compression — the same shape as the proved powerset
  count law of the Lean core (two to the length).
- Equivalence: routes 1, 2, 4 — measured (0 mismatches,
  3,208 prefixes). Route 5 powerset form — measured,
  exhaustive over the sub-battery's subsets. The general
  worklist equality as a theorem (the census lemma for
  closure) remains stated and unproved — UNMEASURED as a
  proof state, owner lane 1 with the worklist lane, exactly
  as the census carries it; the count lemmas beneath it are
  proved in the Lean core.

## The break-even hybrid — concluded

Battery: lane 2 proposition 5 (the compounding family, 8
stages of 3, 6,561 joint plans, seed 6000 series; counted
operations throughout).

- Route 1, explicit: the home form — the stated rule
  (compute the predicted break-even from the measured unit
  costs in full cost form; use the factored form exactly
  when the expected query count reaches it). Predicted 17,
  empirical crossover 17.
- Route 2, minimization: per query count, the argmin of the
  two total-cost forms. Its choices equal the stated rule's
  choices at every count from 1 to 512 — no disagreements.
- Route 3, obscurity: not applicable — the costs are counted
  exactly, not observed through probes; no obscurity reading
  exists over a counted cost vector.
- Route 4, decomposition: the factored leg itself (per-stage
  pools, per-stage scan) — 16.48 counted operations per query
  against the dense form's 3,375.8.
- Route 5, terminal: the factored pools are the terminal
  tensor (the standing example named in the order): 208
  bytes stored against 380,539 for the dense tensor of all
  6,561 rows. Read by per-stage projection, it returns the
  dense scan's result on 512 of 512 queries. Routes 4 and 5
  are the same object read two ways — built stage-wise, it
  is the decomposition; stored and projected, it is the
  terminal form — and this record says so rather than
  counting it twice. Whether the terminal form wins is not
  a property of the tensor but of the query count, governed
  by the proved break-even theorem (the Lean core's
  break-even section, full cost form) and the measured
  regime crossovers (145, 47, 25, 17, 15 queries for 9, 27,
  81, 729, 6,561 rows).
- Equivalence: factored against dense outputs — measured
  (512 of 512). Route 1 against route 2 choices — measured
  (512 of 512 counts). The cost rule itself — proved, above.

## Canonical tie-break — concluded

Battery: lane 3 proposition 1, shared with (a).

- Route 1, explicit: the home form — rows read in the stated
  total order (token order), the first maximum taken. Gap
  1,700 milli (the trap), 24 evaluations, permutation
  invariant.
- Route 2, minimization: the same rule read as lexicographic
  minimization over the pair (negated score, token),
  implemented independently in this lane — streams and
  totals equal the home form on 5 of 5 fixtures and on all
  30 permutation checks (six row orders, five fixtures).
- Route 3, obscurity: not applicable — ties are resolved by
  the stated order, not by observation; there is no probe
  surface.
- Route 4, decomposition: not applicable — the rule decides
  each step from that step's row alone; any finer
  decomposition either restates the same per-step rule (no
  decomposition) or changes the choice (a different
  algorithm).
- Route 5, terminal: the pick tensor — per fixture, per
  prefix, the canonical pick, stored (2,509 bytes; the
  archive's scores are still read for totals, so the tensor
  is a pick table, not a standalone archive). Lookup
  reproduces the home form's streams, totals, and statuses
  on 35 of 35 checks (the five fixtures under the unpermuted
  archive and all six permutations — the tensor stays valid
  under permutation precisely because the home form is
  permutation invariant).
- Equivalence: route 2 — measured (5 of 5, 30 of 30).
  Route 5 — measured (35 of 35). Against (a): measured
  non-equivalence — the 1,700 gap on the trap is the price
  of the cheaper rule; the two stand together on the
  decoding frontier, as lane 3 down-selected them.

## The matrix resolution pair — concluded

The pair: incremental cone-scoped resolution (full coverage)
and on-the-fly budgeted resolution (stated-budget coverage).
Battery: lane 3 proposition 2 (321 records over 64
coordinates; 5,000 records over 256 coordinates; suffix form;
budgeted query at 64 of 256).

- Route 1, explicit: from-scratch resolution — exact at every
  checkpoint (counted work 3,652 at the small scale, 216,721
  at the large).
- Route 2, minimization: not applicable — resolution produces
  readings, not a selection; there is no candidate set and
  no score from which a reading could be a minimiser.
- Route 3, obscurity (new in this lane): the decomposition
  family's route, executed — each coordinate's obscurity
  reading taken over a stated probe prefix (the first 50
  records; clauses as specified in this lane's harness);
  coordinates at or above threshold (1 of 64 at the small
  scale, 54 of 256 at the large) are resolved first, the
  rest after, region by region. The final paired readings
  equal the full resolution exactly at both scales. The
  claim is final-state only: intermediate readings under a
  resolution order are order-dependent by construction, as
  lane 3 recorded, and no intermediate equivalence is
  claimed.
- Route 4, decomposition: the home pair — incremental
  cone-scoped (equal at 3 of 3 and 10 of 10 checkpoints,
  suffix form exact, counted work 2,448 and 39,450) and
  on-the-fly budgeted (covered readings exact, the 192
  uncovered coordinates printed as explicit nulls).
- Route 5, terminal: the resolved reading tensor at the
  final state (four components over 256 coordinates):
  3,890 bytes against 503,671 for the record set; 200 of
  200 sampled coordinate projections equal the full
  resolution. The tensor represents the final-state reading
  function only — it carries no appends; growth returns to
  route 4, which is the pair's standing division of labor.
- Equivalence: route 1 against route 4 — measured at every
  checkpoint run (and the premise-labeled log-level form is
  carried in the census, section 1). Route 3 — measured at
  final state, both scales. Route 5 — measured for the
  final-state reading function. The general resolution over
  arbitrary levels and budgets remains UNMEASURED (the
  resolution algorithm's thirteen claims) — owner lane 3
  with the canonical home's proof lane, as carried.

## The tensor loop — concluded

Battery: lane 3 proposition 3 (16-coordinate pinned base,
two tied groups, the trap and branching archives; the loop
re-implemented in this lane with its two edit clauses
switchable, fidelity-checked against lane 3's run: stream,
edits, and final weightings reproduce exactly).

- The home form is routes 1 and 3 combined (intent-named
  edits where the trigger table names one; obscurity-named
  edits where the decoded row's worst candidate scores at or
  below the stated bound), certified by recomputed
  projection at every edit (4 of 4), protection and round
  trip exact.
- Route 1 alone (intent edits only): 1 edit fires. The stream
  is unchanged; the final weightings differ from the full
  loop at exactly the obscurity-edited coordinates (0, 3, 4,
  13, 14) — measured non-equivalence at the weighting level,
  equivalence at the stream level, on this battery.
- Route 3 alone (obscurity edits only): 3 edits fire. The
  stream is unchanged; the final weightings differ at
  exactly coordinate 5 (the intent-edited coordinate) —
  same disposition as route 1 alone.
- Route 2, minimization (new): obscurity edits with the
  delta chosen as the minimiser, over the stated delta set,
  of the worst candidate's residual score. 4 edits fire,
  certification holds 4 of 4, the stream is unchanged; the
  final weightings differ from the home form at coordinates
  0, 13, and 14 (the delta choices: 250 where the home form
  applies 150) — measured non-equivalence at the weighting
  level, differing component named.
- Route 4, decomposition: the home loop's own structure —
  the overlay stack over coordinates, each edit's effect
  recomputed over its cone and certified against the pinned
  base. Carried from lane 3, re-validated by the fidelity
  control.
- Route 5, terminal: the stack collapsed to one overlay
  tensor (the last value at each edited coordinate): 51
  bytes against the stack's 189 (the final weighting vector
  itself is 58). One application of the collapsed overlay
  from the pinned base reproduces the loop's final
  weightings exactly, and its inverse overlay restores the
  base exactly — both executed. The terminal form
  represents the final weightings only: the stream depends
  on the weightings as they evolve, and no static tensor
  constructed here represents the stream; a stream policy
  tensor (over prefix and stack states) is not constructed —
  owner below. The overlay algebra beneath the collapse
  (protection, application, round trip, tied preservation)
  is proved in the Lean core; the collapse step itself —
  that a stack and its collapsed overlay apply identically
  — is measured here and stated as a lemma for lane 1:
  UNMEASURED as a proof state, owner lane 1, closing route
  the same function-extensionality and case split the round
  trip proof already uses.
- Equivalence: stream level — measured across all routes
  run (identical stream in every variant). Weighting level —
  route 5 measured equal; routes 1, 2, 3 alone measured
  non-equivalent, components named above.

## The meta level — concluded

Battery: lane 1 (39 enumerated configurations over three
instances; the weight-free meta-frontier of 6).

- Route 1, explicit (new reading, executed): the winning
  configuration stated directly — weighted max at weights
  (1, 1), no enumeration — induces the three middle members
  (plan b, plan b2, balanced), equal to the meta search's
  demonstration selection. The explicit form is only
  available because the search exhibited the object; the
  record keeps that order.
- Route 2, minimization: the home form — the demonstration
  meta-weighting (4, 2, 1, 1) minimised over the
  meta-frontier selects the same configuration.
- Route 3, obscurity: not applicable — the configuration
  space is fully enumerated and exactly scored; nothing is
  probed and no coordinate is unresolved, unprojected, or
  uncertain.
- Route 4, decomposition (new): the meta-frontier computed
  per family (five families), the per-family frontiers
  merged and re-frontiered — the result equals the global
  meta-frontier exactly (the same 6 configurations).
- Route 5, terminal: the winner as a tensor — the family and
  its two weights, plus its score tensor over the three
  fronts (213 bytes against 3,640 for the full 39-row
  configuration table). Lookup (the argmin read off the
  tensor) reproduces the winner's three selections.
- Equivalence: routes 1, 2, 5 — measured on the three
  instances. Route 4 — measured (frontier set equality).
  Beyond the three instances everything stays as lane 1
  left it: the meta level over the real guidance queue and
  over the decoding system, and a Lean form of the meta
  level, are UNMEASURED — owner lane 1 successor and the
  deterministic decoding line, as carried in the meta file.

## The spectrum table

States: P = produced, V = validated on the contract battery.
Equivalence is against the algorithm's home form unless a
pair is named. A dash is a not-applicable cell whose one-line
reason stands in the algorithm's section above.

| Algorithm | 1 explicit | 2 minimization | 3 obscurity | 4 decomposition | 5 terminal |
|---|---|---|---|---|---|
| (a) best-first certified decoding | P, V — measured equal 5/5 | home form (global); local form measured non-equal (trap) | — | P, V — measured equal 5/5 | P, V — measured equal 5/5; larger than the archive at this scale |
| (b) two-face stop | home | measured non-equal (both forms) | — | P, V — decisions equal 400/400 | P, V — exhaustive over the domain; claims equal 400/400 |
| (c) frontier-first selection | home (block nested loops) | linear: proved + measured non-equal; nonlinear: measured partial (545/695; union 667/695) | — | P, V — proved equal, measured 300/300 | P, V — lookups equal 30,600/30,600; fourfold compression |
| (d) combination action route | rival, 391/420 | P, V — 413/420; touch grid closes the shared failure in simulation | rival, 419/420 — success sets identical to home | P, V — 60/60 on the three families run | attempted, measured refuted on held-out (move 0/60, jump 12/60); not constructed |
| cone-scoped repair | from-scratch, exact | P, V — equal 936/936, costlier than home | — | home | P, V — equal 300/300 on the sub-battery; rebuild trade loses per-epoch |
| distinct-count worklist | naive scan (oracle) | P, V — equal, 0 mismatches; cost loss | — | home | bitset union refuted (289/12,878); powerset tensor exact, 33 times the rule size |
| break-even hybrid | home (stated rule) | P, V — choices equal at 512/512 counts | — | factored leg (same object as route 5) | pools tensor, 208 against 380,539 bytes; outputs equal 512/512; win governed by the proved rule |
| canonical tie-break | home | P, V — equal 5/5 and 30/30 permutations | — | — | P, V — pick tensor equal 35/35 |
| matrix resolution pair | from-scratch | — | P, V — final-state equal at both scales | home pair | P, V — final-state tensor; 200/200 projections |
| tensor loop | alone: stream equal, weightings non-equal (5 coordinates) | alone: stream equal, weightings non-equal (3 coordinates) | alone: stream equal, weightings non-equal (1 coordinate) | home (overlay stack, certified) | P, V — collapsed overlay equal; stream not represented |
| meta level | P, V — winner stated directly, equal | home (meta-weighting) | — | P, V — per-family frontiers merge to the global frontier | P, V — score tensor lookup equal on 3 instances |

## What stands UNMEASURED, with owners

- All real-checkpoint decoding figures, and with them route
  equivalence for (a) and the tensor loop beyond the fixture
  battery. Owner: the deterministic decoding line; blocker:
  the standalone repo and the pinned fixture bytes are absent
  from this machine (relaying-side access), as carried since
  lane 3.
- The 28 frontier members (of 695) selected by no enumerated
  configuration — wider configuration families or a
  constructive selector are unbuilt. Owner: lane 1 successor
  (the meta level's sampling gap, widened by this lane's
  measurement).
- Live-surface execution of every action route in (d), and
  probe re-qualification there. Owner: the idol-eyes line;
  closing route: the matched campaign, as carried since
  lane 4. The finer touch grid is now measured in simulation
  (route 2 above) and is the campaign's first candidate for
  the shared touch failure.
- A terminal form for the combination action route: the
  memorised-tensor attempt is refuted on held-out instances;
  a constructed terminal form (if one exists for continuous
  scenario families) is unbuilt. Owner: the action model
  family's successor lane.
- The distance tensor's winning regime for cone-scoped
  repair (many queries per epoch): unrun. Owner: lane 6
  successor in this repo.
- The overlay collapse lemma (a stack and its collapsed
  overlay apply identically), stated in the tensor loop
  section. Owner: lane 1; the Lean gate was not re-run in
  this lane (no toolchain on this machine) and no Lean file
  was touched.
- Retraction repair (weight increases, withdrawals) and the
  wall-clock forms of the lane 2 propositions; the general
  matrix resolution (thirteen claims); a Lean form of the
  meta level; the meta level over the real guidance queue —
  all carried from lanes 1 to 3 with their owners unchanged.
- The obscurity threshold's metric-adopted instance set
  (gap S14 of the pipeline spec): still open; the threshold
  of two clauses remains a stated parameter everywhere it
  is used, and no soundness claim in this lane depends on
  its value.

## Reproduction

Run the spectrum harness from a fresh clone of this repo at
the landed head: it re-runs every lane battery it cites as a
fidelity control, executes the spectrum batteries, writes
the spectrum results file, and prints its verdict. Exit 0
and a byte-identical results file across two runs is the
reproduction bar, the same bar the earlier lanes set.
