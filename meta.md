# The meta-search level — specification

Lane 1 of the meta-search solve-and-validate program (Chris,
direct, 2026-11-20 01:56 PST). This file specifies the meta
level and states its implemented behavior and its executed
state. The harness is meta.py in this repo; its executed
output is meta-results.md. Four states are kept separate
throughout, as everywhere in this program: the specification
below is settled intent as ordered; the semantics of the
configuration space are proposed here and implemented in the
harness; implemented behavior is exactly what meta.py does;
verified behavior is exactly what meta-results.md records
from executed runs at the pin named there.

## What the meta level is

Every level below this one takes a weighting as an input: a
guidance vector weighting orders the expansion queue
(search.md), a weighting epoch selects within a computed
frontier (recursive.md family B), a weighting over tokens
drives the recursive weighting loop (recursive.md family A).
The weightings in the current record were set by hand, and
the record's central proved result is a limit on them: the
middle plan of the frontier counterexample is selected by
no positive linear weighting at all (Reversible.lean
section A; census section 2). A hand-set weighting therefore
cannot even name some frontier members as its selection.

The meta level searches the weightings themselves. Its
objects are weighting configurations: a scoring family, its
parameters, its objective axes, and any reweighting overlay
it carries. A configuration is a candidate in the sense of
this repo: a node over the one append-only hypergraph
(spec.md), whose premises are the frontier computation it
reads and the instance records it was run on. The meta
level proposes configurations no hand-set weighting named —
in the executed pass, whole families (the squared family,
the weighted max family, the balance overlay family) that
appear nowhere in the record's hand-set weightings.

## The configuration space, as specified

A configuration is a family plus its parameters. The space
as implemented enumerates five families over two axes:

- Linear: the score is the weighted sum of the axes. This
  is the hand-set family of the record, included so the
  meta level contains the level below it as a subspace.
- Squared: the score is the weighted sum of the squared
  axes. A nonlinear rescaling of the objective axes.
- Weighted max: the score is the larger of the weighted
  axes. A bottleneck reading of the objective axes.
- Lexicographic: the axes are read in a stated order, the
  first axis deciding unless tied. Carries no numeric
  parameters.
- Balance overlay: a linear base score plus an overlay term
  proportional to the gap between the axes. This is the
  reweighting overlay form: an appended term over a base
  weighting, in the spirit of the overlay algebra of
  Reversible.lean section H, here at the selection layer.

The enumeration as implemented is finite and stated in the
harness: 39 configurations. Sampling a larger space is a
later expansion move, appended, never a rewrite of this
record.

## Frontier before weights, at the meta level

The discipline binds absolutely, recursively:

1. Level zero: each instance's Pareto frontier is computed
   weight-free from its candidates. A configuration's
   selection domain is that frontier and nothing else; a
   dominated candidate is unreachable by every configuration
   in the space, by construction of the domain, not by any
   weighting's preference.
2. Level one: each configuration carries a measure vector
   over four declared axes, all lower-is-better: how many of
   the instances it fails to select the middle member of;
   its tie excess; the sum of its numeric parameters; and a
   declared family rank (a stated reading of family
   complexity, declared as an axis, not measured as a fact).
   The meta-frontier is the weight-free Pareto frontier of
   the configurations over these axes, computed before any
   meta-weighting exists.
3. A meta-weighting, when one is used at all, selects only
   from the meta-frontier. No meta-weighting may be used to
   claim a configuration that is not on the meta-frontier,
   exactly as no weighting may claim a candidate not on the
   frontier beneath it. The harness demonstrates one stated
   meta-weighting and checks, in the run, that its selection
   is a meta-frontier member.

A configuration selects a member only when that member is
the unique minimiser under it. A tie is recorded as a tie;
no hidden tie-break manufactures a selection.

## Where the recursion bottoms out, and why that is sound

A level two, searching meta-weightings, is not built, and
the reason is structural, not a stopping convenience. The
claim the meta level makes is an existence claim: there are
configurations, exhibited by name, whose induced selection
is a frontier member no hand-set weighting in the record
selects. An existence claim is discharged by exhibiting the
object and running it; it needs no weighting over the
configuration space, at any level, to be true. What a
further level could add is only an optimality claim —
this configuration is best under some meta-weighting — and
that claim form is exactly the one the proved
counterexample limits: a linear weighting over any level's
frontier can leave frontier members unselectable, so
ascending a level never closes reachability and never
upgrades an existence result into a completeness result.
The recursion therefore bottoms out at the first level
where the frontier is computed weight-free and the sought
objects are exhibited: level one. The soundness rests on
two weight-free computations (the frontier at level zero,
the meta-frontier at level one), each exact over its stated
finite space, and on every selection claim being an
executed run of a named configuration, never a weighting's
promise.

## The instances of the first pass

Three instances, each with its middle member on its
frontier and selected by no hand-set weighting in the
record (the harness enumerates the record's hand set: the
positive linear grid, the threshold rule of the acceptable
stop face, and the constant weighting of the ranking head
control):

- Frontier selection at scale one and at scale two: the
  plan triples of Reversible.lean section A, where the
  middle member's unreachability by positive linear
  weightings is proved, not merely observed.
- Deterministic decoding, as a harness fixture: five
  continuations on a model cost axis and an adequacy cost
  axis — the empty, balanced, and verbose continuations on
  the frontier, and two dominated continuations the
  frontier computation excludes before any weighting runs.
  The fixture's geometry is the plan geometry read as the
  decoding row of search.md. State, stated once and
  binding wherever these results are cited: this is a
  fixture of the harness, implemented behavior over a
  stated model, not a measurement of any decoder system;
  the decoder as a system stands UNMEASURED (search.md,
  deterministic decoding row), owner the deterministic
  decoding line.

## Executed state of the first pass

Executed 2026-11-20 at the pin meta-results.md names; two
consecutive runs byte-identical; verdict OK. Headline
results, all from the run, none from design:

- Hand-set weightings select, per instance, only the two
  extreme frontier members; no middle member is
  hand-selected on any instance.
- 13 of the 39 enumerated configurations select the middle
  member on all three instances: five squared, five
  weighted max, and the three balance overlay
  configurations. Two further squared configurations select
  a middle member on one instance only. The full table,
  with every configuration's induced selections and measure
  vector, is meta-results.md.
- The meta-frontier holds 6 of the 39 configurations. The
  demonstration meta-weighting, weights (4, 2, 1, 1) over
  the four declared axes, restricted to the meta-frontier,
  selects the weighted max configuration with weights
  (1, 1), whose induced selections are the three middle
  members.
- Controls in the run: the linear grid check agrees with
  the proved counterexample class on the grid (a grid
  check, not the proof); no configuration selects a
  dominated continuation; at least one reaching
  configuration exists, or the harness would have failed.

## What stands UNMEASURED, with owners

- The meta level over the guidance vector space of
  search.md (configurations over the five guidance
  coordinates and the candidate space measures, run over
  the expansion queue's real candidates): UNMEASURED.
  Owner: lane 1 successor in this repo; closing route is
  this harness's enumeration widened to that candidate
  set, with the queue's candidates appended as instances.
- The meta level over the deterministic decoding system
  (configurations run against the decoding line's archived
  rows, not the fixture): UNMEASURED, with the decoding
  system itself. Owner: the deterministic decoding line;
  its standalone repo access blocker stands as recorded in
  recursive.md family A.
- A Lean form of the meta level (the configuration space
  and the reachability of the middle member by an exhibited
  nonlinear configuration, as theorems): UNMEASURED as a
  proof state — stated, unproved. Owner: lane 1. Closing
  route: the squared configuration at weights (1, 1) is a
  finite arithmetic instance of the same shape the section
  A proofs already close by the linear arithmetic solver;
  the general statement that some family reaches every
  frontier member is not claimed and not proved.
- Sampling beyond the enumerated 39 (a larger parameter
  grid, further families): UNMEASURED. Owner: lane 1
  successor; the enumeration here is the executed pass,
  and any widening appends its own results record.
