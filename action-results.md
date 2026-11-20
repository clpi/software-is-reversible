# Basic action model — executed results

Executed 2026-11-20 by the actions harness in this repo
(standard library only, deterministic). Two consecutive runs
were byte-identical. Base seed 20261120; 60 paired instances
per scenario family per rival algorithm (the same instance
seed faces every rival); 20 instances per primitive for the
reversibility round trips. Scope: simulated scenarios only —
not a live desktop, not a browser, no display touched. Every
rate below is over the permutations actually run, and no
wider generalization is claimed.

## The generalization table

Success counts out of 60, with the mean probe count per
selection (the obscurity route's cost) and the failure
components named with their counts.

| Family | Explicit (route 1) | Obscurity (route 2) | Combination (route 3) | Naive control (route 0) |
|---|---|---|---|---|
| Move | 60/60, 0 probes | 60/60, 47.4 probes | 60/60, 0 probes | 1/60 — position axis 30, position axis 29 (one success, 59 failures) |
| Jump | 60/60, 0 probes | 60/60, 6.2 probes | 60/60, 0 probes | 3/60 — the apex component, 57 |
| Jump over | 60/60, 0 probes | 60/60, 11.4 probes | 60/60, 0 probes | 21/60 — trajectory clearance 35, landing position 4 |
| Drive | 60/60, 0 probes | 60/60, 525.2 probes | 60/60, 0 probes | 4/60 — first waypoint 51, second waypoint 5 |
| Touch | 39/60 — target occlusion 21 | 59/60, 2.6 probes — target occlusion 1 | 59/60, 1.3 probes — target occlusion 1 | 6/60 — target identity 54 |
| Type | 60/60, 0 probes | 60/60, 244.7 probes | 60/60, 0 probes | 2/60 — first differing buffer position named per instance (position 0 in 30) |
| Automate | 52/60 — step premise failures 8, spread over steps 0 to 3 | 60/60, 5.7 probes | 60/60, 0.4 probes | 9/60 — step premise failures 51, spread over steps 0 to 5 |
| Total | 391/420 (93.1 percent) | 419/420 (99.8 percent) | 419/420 (99.8 percent) | 46/420 (11.0 percent) |

Failure reading, per located component:

- The naive control fails everywhere the observed model
  matters, which is the evidence the families discriminate:
  it ignores the response scale and drift (move), the
  gravity draw (jump), the dependency relation (automate),
  the layout remap (type), and the waypoint order (drive).
  Its one strong cell, jump over at 21/60, is the family
  whose canned parameters happen to sit nearest the drawn
  ranges — a control artifact, printed as one.
- The explicit route's 29 failures are exactly its stated
  limit, in two located places. Touch: in 21 of 60 layouts
  the target center is covered by a stacked element, the
  plan clicks the center as stated, and the topmost element
  there is the cover — component: target occlusion, premise:
  the plan never verifies the point. Automate: 8 of 60
  processes carry a dependency the spec does not list; the
  stated order forces the dependent step against its blocked
  signal and corrupts it — component: the step premise.
- The obscurity route's single failure is shared with the
  combination route: one touch layout where no probed point
  of the target rectangle is uncovered at the probe grid's
  resolution — component: target occlusion, route leg: the
  probe grid. The closing candidate is a finer probe grid or
  a scroll-and-reprobe step; it is appended to the family as
  an open gap, not silently fixed in this run.
- The combination route's repair leg fired in exactly the
  instances the explicit plan needed it: 21 touch instances
  (20 repaired, 1 the shared grid failure) and 8 automate
  instances (all 8 repaired). On the five families where the
  observed model is complete, the repair leg never fired and
  route 3 costs exactly route 1.

## The frontier and the down-selection

The frontier is computed before any weighting, as everywhere
in this program. On success, obscurity and combination tie
at 419/420 and dominate explicit at 391/420; naive at 46/420
is dominated by all three and stands refuted as a selection
algorithm (it remains in the family as the standing
control). Between the two frontier members, the separating
axis is cost: the obscurity route pays a mean of 47.4 probes
per move selection, 525.2 per drive selection, and 244.7 per
type selection, where the combination route pays zero probes
on every family whose observed model is complete and a mean
of 1.3 (touch) and 0.4 (automate) where it is not.

Down-selection: the combination route (route 3) is the
selected algorithm for the basic action model — frontier on
success, cheapest on the probe axis, and the only route
whose per-selection record shows which leg derived the
action. The obscurity route is retained as the family's
fallback member: it is the route that still constructs an
action where no explicit model exists at all, and its
success profile here (419/420 with no formula read) is the
evidence that the fallback is real. The explicit route is
retained as the combination route's planning leg, not as a
standalone selection algorithm: standalone, it is dominated.
This down-selection is a measured result over the stated
permutations in simulation; on a live surface it is
UNMEASURED until the matched campaign runs.

## Reversibility, per primitive

The protocol of the reversibility file, unchanged: snapshot,
execute, fresh observe, execute the constructed inverse,
fresh observe, compare. Twenty instances per primitive.

| Primitive | Verdict | Count |
|---|---|---|
| Move | PASS | 20/20 |
| Jump | REFUSED-BY-NAME (the refusal code of the first pass; no derivable inverse) | 20/20 |
| Jump over | REFUSED-BY-NAME (same code) | 20/20 |
| Drive | PASS, at the drive face's stated observation resolution (half a unit, a tenth of a radian) | 20/20 |
| Touch | REFUSED-BY-NAME (same code; an activation, as click before it) | 20/20 |
| Type | PASS | 20/20 |
| Automate, setting steps only | PASS | 20/20 |
| Automate, with a submission step present | REFUSED-BY-NAME, the refusing step named in the refusal | 20/20 |

Negative controls, both detected as MISMATCH with the
differing component named: a move inverse carrying a
deliberately wrong delta (component: position), and a type
inverse deleting one character too few (component: the
buffer). The PASS verdicts are therefore not vacuous, by the
same standard as the first pass.

Refusals are issued at qualification, before any effect is
delivered, and the refusal itself is the recorded verdict —
never a pass, never a silent skip.

## What stands UNMEASURED

- Live-surface execution of every primitive and every route:
  no desktop, browser, or display exists on this machine.
  Owner: the idol-eyes line; closing route: the matched
  campaign on an owned desktop through the executor's own
  faces, with this harness's scenario families as the
  campaign's source.
- Probe cost on a live surface, where probes are real
  actions rather than clone trials, and the re-qualification
  of probe reversibility there. Same owner, same campaign.
- The one shared touch failure's closing candidate (finer
  probe grid, or scroll and reprobe): specified as a gap in
  the family, not yet run even in simulation. Owner: this
  lane's successor in the action model family.
- Every speed axis: the harness records probe counts, not
  wall-clock timings, and no timing claim is made.
