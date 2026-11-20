# The basic action model — spec

Order: Chris, direct, 2026-11-20 01:56 PST. The basic actual
actions, named in the order: move by a pixel delta, jump,
jump over an object, drive (steer and throttle a vehicle),
touch (click or tap a target), type text, automate a process
step. The model must generalize against any scenario. This
file is the spec; the harness that executes it is the actions
file in this repo; the executed results are in the action
results file in this repo. Four states are kept apart
throughout: the intent is settled (the order above), the
semantics here are proposed, the harness behavior is
implemented in simulation, and verified behavior exists only
where the results file prints an executed run — simulated
scenarios, never a live surface.

## The primitives

Each primitive is a structural map over an observed state,
not a dispatch entry (the F1 family of the search file:
action as derivation). A primitive names its state
components, its parameters, its postcondition, and its
inverse or its refusal.

1. Move. State components: cursor position (two coordinates).
   Parameters: a commanded delta. The surface response is the
   command scaled plus a drift; both are carried by the
   observation. Postcondition: the position lands within the
   stated tolerance of the target. Inverse: derivable — the
   negated achieved displacement, corrected by the response
   the observations carry (the same shape as the first pass:
   the set inverse restores the value the observation
   carries).
2. Jump. State components: height, vertical velocity,
   gravity. Parameters: launch velocity. Postcondition: the
   apex lands in the stated band above the launch point.
   Inverse: none derivable. The ballistic phase is not
   traversable backward by any action in the family — time
   and gravity do not run in reverse — so derivation refuses
   by name at qualification.
3. Jump over an object. State components: horizontal
   position, height, gravity, the obstacle (distance, height,
   width). Parameters: horizontal and vertical launch
   velocities. Postcondition: the trajectory clears the
   obstacle top by the stated margin and the range lands in
   the stated zone past it. Inverse: none derivable, refused
   by name, same ground as jump.
4. Drive. State components: pose (two coordinates and a
   heading), the course (an ordered waypoint list), the
   vehicle constants (top speed, speed factor, steering
   factor) carried by the observation. Parameters: a sequence
   of steering and throttle pairs. Postcondition: every
   waypoint is visited in order within the stated radius,
   inside the step budget. Inverse: derivable — the recorded
   course traversed in reverse with a precision final leg,
   judged at the drive face's observation resolution (half a
   unit, a tenth of a radian), stated here because continuous
   pose has no exact-equality reading below that resolution.
5. Touch. State components: the page layout (rectangles with
   identities and a stacking order), the cursor position.
   Parameters: a point. Postcondition: the topmost element at
   the point is the target identity. Inverse: none derivable.
   A touch is an activation; its effects belong to the
   application, exactly the ground on which the first pass
   refused click. Refused by name at qualification.
6. Type. State components: the text buffer, the keyboard
   layout map carried by the observation, the echo (the
   buffer as freshly observed). Parameters: a key sequence.
   Postcondition: the buffer equals the target string.
   Inverse: derivable — delete the typed run and restore the
   prior buffer the pre-action observation carries.
7. Automate. State components: the step list (each step sets
   one register), the dependency relation, the done set, the
   register values. Parameters: an execution order.
   Postcondition: every step done, no step forced against a
   blocked signal. Inverse: derivable per step as the
   compensation that restores the prior register value,
   executed in reverse order — except a step with no
   compensation (a submission step is the standing example),
   whose presence makes the whole action refused by name at
   qualification, the refusing step named in the refusal.

## The rival selection algorithms (the candidate family)

The model enters the search space as a candidate family, not
a hand-picked design: four rival algorithms select the
action for every primitive, over the same instances, and the
down-selection is by executed result (the results file).

- Route 1, the explicit route. A stated planner over the
  observed state: it reads the model the observation carries
  and computes the action in closed form — the response
  correction for move, the energy relation for jump, the
  trajectory solution for jump over, a pursuit steering law
  for drive, the target center for touch, the layout map for
  type, a topological order for automate. It plans once and
  executes its plan as stated, with no mid-course revision.
  Its defining limit follows: where the observed model is
  incomplete or the plan's premise is not verified against
  the surface (a covered target center, an unlisted
  dependency), the plan fails as stated.
- Route 2, the obscurity route. No explicit algorithm names
  the action. Each action parameter carries an obscurity
  reading over the three clauses of the decomposition family
  (unresolved, unprojected, uncertain); a parameter at or
  above the threshold of two clauses has its action
  constructed by probe-and-observe search on a clone of the
  state model: candidate actions are tried, the fresh
  observation after each probe is read, and the candidate
  leaving the least residual is kept under a shrinking
  search radius. The route reads no domain formula; its only
  signal is observed outcome. Its cost is printed as probes
  per selection.
- Route 3, the combination route. The explicit plan first,
  one verification observation, and obscurity construction
  as the repair leg wherever the observed residual exceeds
  tolerance or a premise signal contradicts the plan. Every
  selection records its derivation route; a route 3 selection
  additionally records whether the repair leg fired, so the
  sub-route of every repaired selection is on the record.
- Route 0, the naive control. Greedy nearest-target with
  canned parameters: aim straight at the target, ignore the
  observed model entirely. It stands outside the pipeline
  routes by design; it is the control the other three must
  beat, and its failure profile is the evidence that the
  scenario families actually discriminate.

## The solve loop, per selection

Observe; derive the candidate action under the rival's route;
qualify (the inverse check of the reversibility discipline
runs here — an action with no derivable inverse is refused
by name and never delivered, where the task requires a
reversible action); act; independently observe the outcome;
record the route, the probe count, and, on failure, the
differing component. This is the six-step loop of the harness
spec carried over unchanged, with the rival route as the
derivation step's parameter.

## Generalization discipline

A scenario family is a distribution, not an instance.
Permutations vary, per family: response scale and drift and
target placement (move); gravity and target height (jump);
gravity, obstacle placement, and obstacle height (jump
over); waypoint geometry, top speed, speed factor, and
steering factor (drive); layout, target identity, stacking,
and cursor placement (touch); string content and the layout
remap (type); step count, dependency shape, listed order,
and hidden dependencies (automate). All draws are seeded and
recorded; the same instance seed faces every rival, so the
comparison is paired. A claim of generalization is exactly
the success rate over the permutations actually run, per
family, per rival — nothing wider is claimed.

## Failure structuralization

Every failure names its differing component before it counts:
the state component (a position axis, the apex, a waypoint,
the buffer position, a register), the premise (a step whose
dependency premise failed, a target whose occlusion premise
failed), or the route leg (plan, probe search, repair). The
results file prints the component counts beside every rate,
so a loss is a located loss, and the located component is
the work order for the next candidate in the family.

## What this model does not claim

Live-surface execution is UNMEASURED: no desktop, browser,
or display exists on the measuring machine, and every
verdict here is a simulated-scenario verdict at the stated
fidelity. The matched campaign on an owned desktop, through
the executor's own faces, is the closing route; its owner is
the idol-eyes line, with this lane's harness as the scenario
source. Probe-based routes probe a clone of the state model
here; on a live surface the same probes are real actions and
their cost and reversibility must be re-qualified there —
that re-qualification is part of the owed live pass, not a
detail. The threshold of two obscurity clauses is adopted
for this run as a stated parameter; the threshold instance
set that would adopt it on a metric is gap S14 of the
pipeline spec, still open, and no soundness claim here
depends on the threshold value.
