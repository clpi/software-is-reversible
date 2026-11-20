# Widening the configuration space — specification

Successor lane to lane 1 (the meta level) and lane 6 (the
spectrum), in the meta-search solve-and-validate program.
This file specifies the widening pass and states its
implemented behavior. The harness is the widen file in this
repo; its executed output is the widen results files in
this repo. Four states are kept separate throughout:
settled intent, proposed semantics, implemented behavior,
verified behavior.

## The open item this lane closes

The spectrum record (lane 6, section on frontier-first
selection) measured, over the lane 2 proposition 1 battery
(300 point sets, seed 2000 series, coordinates integers
0 to 20, 695 frontier members in total):

- the positive linear grid, weights 1 to 9 by 1 to 9 with
  the lexicographic tie-break of the lane 2 harness,
  recovers 620 of 695 members;
- the nonlinear enumerated set of the meta level (the 21
  configurations of the squared, weighted max, and balance
  overlay families, selection by unique minimiser) recovers
  545 of 695;
- the union recovers 667 of 695. The remaining 28 members
  are selected by no enumerated configuration of any family
  run in the program, and the spectrum record leaves them
  as an open item owned by the lane 1 successor.

Precision on where the 28 live: they are not members of
the meta level's three instances. On those three instances
the enumerated 39 configurations already select every
frontier member (the extremes by linear configurations,
the middles by 13 nonlinear configurations), so the
unselectable count there is 0 of 9. The 28 live in the
spectrum battery above: 300 random instances, reconstructed
exactly by this lane's harness as a fidelity control
against the committed spectrum results file (every figure
above reproduced before any new family runs; the harness
verdict is FAIL if any figure differs).

## Discipline

Frontier before weights throughout: each instance's
Pareto frontier is computed weight-free from its
candidates, and every configuration, old or new, selects
only from that frontier. A configuration selects a member
only when that member is the unique minimiser under it
(the meta level's rule); a tie selects nothing. The one
exception is inherited, not new: the old linear grid's
recovery figure of 620 was measured with the lane 2
harness's tie-break pick, and the fidelity control
reproduces that figure under its own semantics so the 28
are the same 28. Every new family below uses the unique
minimiser rule with no tie-break.

No benchmark gaming: same instances, same contract. The
battery is the spectrum battery, regenerated from its
stated seed and generator order. Families are defined in
this file, in full, before any new family's selection is
executed; every parameter grid below is derived from the
battery's stated coordinate range (integers 0 to 20) or
from the family's own construction, never from which
members any family turns out to select. A family that
selects nothing new is reported as such.

## The new families, as defined before execution

Each family is structurally distinct from the five
enumerated families of the meta level (linear, squared,
weighted max on a 1 to 3 grid, lexicographic, balance
overlay on a fixed linear base) and from each other.

- eps, the epsilon form. Two orders. First order: minimise
  the first axis subject to the second axis at most e.
  Second order: minimise the second axis subject to the
  first axis at most e. The bound e ranges over every value
  the battery axes take, 0 to 20. 42 configurations. The
  selection domain is the frontier, as everywhere here;
  feasibility is read on the frontier.
- lex, lexicographic over permuted axis orders. Both
  permutations of the two axes: 2 configurations. (The meta
  level enumerated this family on its three instances, but
  the spectrum battery's union never included it; on this
  battery it is new.)
- cheby, the achievement form. The reference point is the
  instance frontier's ideal point shifted by one on each
  axis (the least first-axis value minus 1, the least
  second-axis value minus 1); it is computed from the
  weight-free frontier, never from a weighting. The score
  of a point is the larger of the two weighted gaps to the
  reference, plus an augmentation of one thousandth of the
  sum of the weighted gaps. Weights range 1 to 21 on each
  axis (the gaps range 1 to 21 under the stated shift).
  441 configurations. Scores are exact fractions.
- pmax, weighted max with varied exponents and wide
  weights. The score is the larger of the two weighted
  powered axes. Exponent 1 with weights 1 to 40 on each
  axis (twice the axis range, covering the extreme ratios
  a zero coordinate demands); exponents 2 and 3 with
  weights 1 to 12 on each axis. 1888 configurations.
- power, weighted power sums beyond the squared family.
  The score is the weighted sum of the powered axes, for
  exponents 3 and 4, weights 1 to 9 on each axis (the
  weight range of the record's linear grid). 162
  configurations.
- rand, seeded pseudo-random linear weightings. A stated
  seed, 91000, disjoint from every seed range used in this
  repo. 4000 configurations; each draws its two weights in
  order as uniform integers from 1 to 997. This family is
  linear, so the proved unreachable class bounds it before
  it runs: it can only ever recover members the coarse grid
  missed for want of ratio range or resolution, never a
  member no positive linear weighting selects.
- center, the centered form, reported separately. One
  configuration per frontier member of the instance, its
  center set to that member's own vector; the score is the
  squared distance to the center. Its selection of its
  center is guaranteed by construction (distance zero,
  attained by no other point), so it is not evidence of the
  same kind as the fixed families above: it is the
  constructive selector the spectrum record named as the
  alternative closing route. It is counted apart, and the
  headline union is stated with and without it.

## Classification of the 28, as defined before execution

Independently of the families, the harness classifies each
of the 28 by exact rational arithmetic over all positive
weights, not over any grid:

- linear class: whether some positive linear weighting
  makes the member a minimiser at all, and whether some
  positive linear weighting makes it the unique minimiser.
  The three outcomes are named unique, weak (a minimiser
  only ever tied), and none. The none outcome is the proved
  unreachable class of the Lean core, generalised from the
  two plan triples to arbitrary frontiers: no linear
  configuration, on any grid or sample, at any resolution,
  can select such a member.
- power classes: the same question for the squared,
  cubed, and fourth power sum families over all positive
  weights, decided on the powered points by the same
  interval computation.
- the weighted max class over all positive weights is
  settled by construction, not interval: for a member with
  both coordinates positive, the weights formed from its
  own coordinates crossed (second coordinate as the first
  weight, first coordinate as the second weight) make it
  the unique minimiser, since every other frontier member
  exceeds it on one axis or the other; a member with a zero
  coordinate is selected by an extreme ratio within the
  pmax exponent 1 grid. The harness verifies this
  construction by direct execution on every frontier
  member of the battery, all 695.

## Controls

- Fidelity: the old figures (695, 620, 545 with its three
  family counts, 667, and 900 of 900 permutation agreement)
  equal the committed spectrum results file exactly.
- Dominated: no configuration, old or new, selects a
  dominated candidate. Verified on the battery (every
  selection is a frontier member, and no frontier member is
  dominated by any candidate of its instance) and on the
  meta level's decoding fixture (the two dominated
  continuations are selected by no new configuration).
- Linear agreement: the linear grid selects no middle
  member of the two proved segment cases and no member of
  the none class anywhere on the battery; the random linear
  family likewise selects no member of the none class. The
  grid check is a grid check, not the proof; the proof is
  the Lean core's frontier section.
- The meta harness itself is re-run unchanged and its
  verdict recorded beside this lane's.

## What stands UNMEASURED, with owners

- The widened space over any battery beyond this one (the
  guidance vector space, the decoding system): UNMEASURED,
  owners as carried in the meta file.
- A Lean form of any statement in this file: UNMEASURED as
  a proof state. Owner: lane 1. The classifications here
  are exact executed arithmetic over a finite battery, not
  theorems.
- The balance overlay family over all positive overlay
  constants is not classified; only its enumerated three
  configurations enter the old union. Owner: lane 1
  successor.
