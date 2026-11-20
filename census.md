# Theorem census — found and unidentified

Compiled 2026-11-20. Every theorem and lemma the algorithm system
needs, in exactly one state. Proved here means in Reversible.lean
at this repo's head, gate cold PASS, axiom audit printed in the
gate log: 38 results, every axiom set a subset of the three
standard axioms, none using the choice axiom at all. Cited means
proved in the named home at the named pin and not re-proved here
(never blindly recompute). Premise means the claim rests on the
named assumption, with its falsification route. Control means a
kernel-checked refutation standing in a tree. Gap means
unmeasured or unproved, with an owner and a closing route.

## 1. The pipeline core (five items of the pipeline order)

Determinism of the derivation.
- Proved, cited: derived view congruence, intent congruence,
  selection congruence, space congruence, derived view exactness,
  reweighting invariance — pipeline proof lane, local pin bf814c1
  (scratch copy of the frontier home; nothing pushed — the pin is
  local and the citation carries that fact).

Reversibility of the action step, model layer.
- Proved, cited: dominance unchanged by growth, eligibility of the
  grown space, compensation restores (full form, no cone
  restriction), compensation restores in solved form, log level
  inverse — pipeline proof lane, bf814c1.
- Proved here: compensation in place — retract after insert, for a
  fresh candidate, restores the prior frontier at every other
  point (retract insert of fresh); the action structure with its
  round trip law, composition of actions, and the field set and
  toggle instances (act restores, comp restores, set field
  restores, toggle restores); the refusal form — an action carried
  as the empty option has no restoration claim (no inverse no
  claim).

Reversibility at the execution layer.
- Premise P5 (execution fidelity), pipeline proof lane: that an
  external executor performs the selected action as modeled is
  outside the model proofs. Falsification route: the
  reversibility validation system of reversibility.md — execute,
  execute the constructed inverse, compare fresh observed state.
  State until that system demonstrates it per action: UNMEASURED.
  Owner: lane 4 of this repo.

Pareto optimality of the selected action.
- Proved, cited: selection membership, selected frontier, selected
  undominated, selected qualified, ranking head best in both
  forms — pipeline proof lane, bf814c1. The optimality comes from
  the frontier filter, not the ranking: standing control below.

Incremental reevaluation equals full reevaluation.
- Proved, cited: incremental equals full, full from scratch, dead
  append — pipeline proof lane, bf814c1; the candidate module's
  step and weighted results underneath, frontier home at 60f33193.
- Proved here: the one-append update in place (insert exact): the
  frontier of the grown space is exactly the old frontier filtered
  by the appended candidate, plus the appended candidate when
  nothing old dominates it.
- Premise P1 (extraction fidelity) rides the log level form: the
  projection of a grown log is the grown space of the projection.
  Falsification route: the extraction checker of the owning
  system, run on the log. Owner: pipeline lane.

Stop soundness, two faces (the split adopted 2026-11-20 01:17).
- Acceptable face. Proved, cited: loop soundness, stops only when
  sufficient — pipeline proof lane, bf814c1. Proved here in place:
  the fuel loop over a signal that grows by one (loop sound,
  loop stops only when sufficient).
- Optimal face. Proved here: the certificate shape — a chosen
  plan certified against the whole remaining set is no worse than
  every remaining plan (certified optimal sound), with the
  concrete instance over the control's own plan set (two certified
  over nine two).
- Control, proved here: the threshold control — with threshold ten
  over latencies nine and two, the first acceptable plan is the
  latency nine plan while the latency two plan is still open
  (threshold accepts worse). A threshold therefore supports an
  acceptability claim only, never an optimality claim.
- Premise P6 (progress): completeness of the stop loop is
  conditional on the caller's step raising the signal at
  insufficient states. Falsification route: a per-step signal
  check in the running loop. The unconditional form is refuted by
  the no progress control below.

## 2. Frontier before weights

- Proved here, the counterexample class in concrete form: the
  middle plan of (0, 10), (6, 6), (10, 0) is undominated by each
  rival and by itself, stands on the frontier of the three, and is
  selected by no positive linear weighting (b not dominated by a,
  by c, by b; b on frontier; b never selected). A second scale,
  (0, 20), (11, 11), (20, 0), is likewise never selected
  (b2 never selected).
- Unidentified lemma L-gen, found during the proof attempt: the
  fully general symmetric form — a plan whose coordinate sum
  strictly exceeds the rivals' shared sum, at the symmetric point,
  is never selected by positive weights. The proof needs a
  nonlinear step the linear arithmetic solver does not close.
  State: stated, unproved. Owner: lane 1. Closing route: a
  two-case argument on the weight order with the product terms
  carried explicitly, or a convexity lemma over the segment.
- Proved, cited: weightings move order, never membership; epochs
  are reproducible and never rewrite — candidate module, frontier
  home at 60f33193.

## 3. The resolution algorithm (13 theorem-to-be claims, 8 gaps)

From the algorithm spec in the canonical home (algorithm file and
case register, 83 cases), claims one to thirteen and fifteen.

- Inherited in model form, proved in the canonical home at
  37514fb7 (217 theorems, including all eight section 13 claims):
  levels reconciled (claim seven) and bound correctness (claim
  eight). Their algorithm level forms remain theorem-to-be in
  that home. Owner: the canonical home's proof lane.
- Covered in finite list form by the frontier and pipeline homes,
  algorithm form still theorem-to-be: output soundness (one),
  scope soundness (three), determinism (four), view growth
  (nine), coloring (ten), composition (eleven), intent paints no
  equivalence (twelve), resume composes (fifteen). Owner:
  coordinator, as the next lane in the canonical home.
- One graph only (two): rests on the canonical premise — the
  model admits no second graph by construction. Premise-labeled
  with the canonical premise; falsification route is the
  re-founding disposition, which has landed and confirms the
  ruling.
- Termination (five): the finite term bound argument is stated in
  the worklist item (section 4 below); the algorithm form is
  theorem-to-be. Owner: canonical home proof lane.
- Coverage at the stop (six): the acceptable face is proved
  (section 1); coverage in the algorithm's projection sense is
  theorem-to-be. Owner: canonical home proof lane.
- Pareto optimal algorithm (thirteen): UNMEASURED as a theorem;
  its axes are the resolved set by inclusion, counted spend, and
  counted waste (zero by construction). The methodology claim
  (fourteen) is a premise with a falsification route, as the
  algorithm spec itself labels it.
- The 8 open specification gaps stand as the algorithm spec
  carries them, each with its interim rule (defer or refuse,
  append nothing) and its owner: level name reuse (coordinator);
  rank of appended scopes (coordinator); availability in forms
  other than a counted budget (coordinator with the measurement
  lane); intent in forms other than terms (coloring and
  qualification lane); two runs at once on one graph
  (coordinator); the witness check procedure per ground kind
  (proof lane); the filter language over colors (coloring and
  qualification lane); whether an unpaid target record counts as
  a projection of that target (coordinator).

## 4. The closure worklist (the decompiler cue item, 2026-11-20 01:16)

Construction: per rule, the count of distinct premises still
absent from the derived set, plus an index from each term to the
rules waiting on it; the queue is seeded with zero-premise rules;
a rule fires when its count reaches zero.

- Proved here: the count itself (missing, over the miss count
  recursion) — zero exactly when every premise is derived
  (missing zero of all), bounded by the premise count (missing
  le), positive while a named premise is absent (missing of mem),
  and antitone under growth of the derived set (missing
  antitone). Derivability as the least closure (the Deriv
  predicate) is monotone in the seed and persists under append
  (deriv monotone, deriv growth).
- Unidentified lemma L-close, found during this census: the
  worklist algorithm's computed set equals the least full closure
  at every append prefix, including rules incomplete before the
  append — against the exact view semantics of the canonical
  home, not an assumed encoding. The count lemmas above are its
  engine; the queue algorithm itself (the waiter index, the
  firing order) is not yet formalized, and where the worklist's
  assumed semantics and the canonical view semantics differ, the
  canonical semantics governs and the difference is a named
  finding. State: stated, unproved. Owner: lane 1 with the
  worklist lane of the pipeline program (its pull in the expands
  repo is the construction carried as code). Closing route:
  formalize the queue state and prove the invariant that a rule
  is queued exactly when its missing count is positive.
- Termination at a fixed view: each term enters the queue once,
  so a finite term bound gives termination — stated in the cue,
  carried here as part of L-close's closing route.

## 5. The subset oracle

- Proved here: the powerset count law — the number of subsets of
  a finite list is two to its length (powerset count), with the
  eight checkpoint instance (powerset count eight).
- Reproduced, cited: the independent subset oracle agreed at all
  256 growing graph checkpoints of the compounding family —
  verification lane of the pipeline program, executed at the
  expands repo pin and matched against an independent exhaustive
  powerset oracle (its record is the first verification record of
  the pipeline program, 2026-11-20 ~01:21 PST). The general
  two-enumeration agreement over arbitrary extracts is
  UNMEASURED; owner: lane 1, closing route is the count law plus
  an extensionality lemma over the two enumerations.

## 6. The break-even rule, full cost form

- Proved here: reuse wins only when avoided work exceeds setup,
  validation, persistence, and restart combined — the definition
  in full cost form with its two directions (reuse wins of cover,
  no win without cover), monotonicity in the avoided work
  (win monotone avoided), and antitonicity in any cost component
  (win antitone cost, stated for the setup component; the other
  components are the same proof by the sum's symmetry — that
  symmetry step is noted here as a one-line extension, not a
  separate lemma).
- Not located, carried from the pipeline verification lane: the
  rule as a theorem in the sibling trees was searched and not
  found; the form proved here is this repo's own statement.
  The empirical figures behind it (the five byte recipe against
  the dense mask) are reported, not reproduced: UNMEASURED.
  Owner: the deterministic decoding line, blocked on the
  standalone repo's access on the relaying side.

## 7. Standing refuted controls

- Threshold accepts worse (proved here, section 1): refutes
  threshold stop as an optimality claim.
- Ranking head alone (pipeline proof lane, bf814c1): under a
  constant weighting the ranking head is dominated on both axes;
  refutes optimality by ranking.
- Uncompensated append (candidate module, frontier home
  60f33193): appending a dominating candidate with no
  compensation removes a solved member; refutes reversibility
  without the compensation step.
- No progress, no stop (pipeline proof lane, bf814c1): a step
  whose record never qualifies never raises the signal; refutes
  unconditional stop completeness.
- Epoch shift (candidate module, 60f33193): changing epoch axes
  changes the solved set; refutes reading an epoch change as a
  reweighting.

## 8. Premise register (all premises in force across the system)

- Canonical premise: the ruled model is the model. Falsification
  route: the re-founding disposition — landed, confirms.
- Witness honesty (inherited): an entry's witness is what it
  names. Route: a named entry whose witness fails re-checking.
- Reading fidelity (inherited): facts are proved about terms as
  read. Route: a named datum whose re-reading differs.
- P1 extraction fidelity; P2 witness honesty at the pipeline
  layer; P3 axis meaning in the world (route: the measurement
  campaign); P4 threshold choice (the stop results hold for every
  threshold); P5 execution fidelity (route: lane 4's system);
  P6 progress (route: per-step signal check). All as stated by
  the pipeline proof lane at bf814c1.
- Counted cost (resolution algorithm): counted cost stands for
  real cost. Route: a counted run whose real cost order differs.
- Demand D1 (candidate space session, confirmed by Chris
  2026-11-20 08:06Z as reported): every definition in the main
  library qualifies — a stated demand, not a premise; the
  layering figures under it are reported, not reproduced.

## 9. Counts

Proved in this repo: 38 theorems, 0 escapes, axiom audit clean.
Cited proved: the pipeline core (25 results and 3 controls at
bf814c1), the candidate space core (frontier home 60f33193), the
canonical theory (217 at 37514fb7). Premise-labeled: the register
of section 8. Refuted controls standing: 5. Named unproved
lemmas found by this census: L-gen, L-close. Open specification
gaps carried: the resolution algorithm's 8. UNMEASURED empirical
cells named: execution layer reversibility (lane 4's first pass
is its closing route), the break-even figures, the general
subset agreement over extracts.
