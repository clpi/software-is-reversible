# Reversibility validation — the system, and its verdicts

## The claim under test

An action is reversible when executing its constructed inverse
restores the state the action started from — not as the action
reports it, but as a fresh observation reads it. The pipeline's
reversibility claim at the execution layer rests on premise P5
(execution fidelity) until this system demonstrates the round
trip per action. The model layer is proved (census section 1);
this system is about the executor layer, where the known open
gap stands: the executor can propose an inverse but has never
shown that executing it restores fresh observed state (the
candidate space record, part B; the harness spec's requirement
two and gap register G1 to G9 in the idol-eyes repo).

## The protocol (exact)

For each action in scope, in order:

1. Observe. Take a fresh observation of the pre-action state
   through the executor's observe face. The snapshot is the
   observation's own value, hashed; nothing the action later
   reports may stand in for it.
2. Execute. Run the action through the executor's face. Record
   the outcome in the four states (verified, delivered, not
   delivered, uncertain); a submitted action is never recorded
   as succeeded.
3. Observe again. Take a fresh observation of the post-action
   state. It must differ from the snapshot exactly where the
   action's postcondition says it differs; a postcondition
   mismatch is a defect named before any inverse is attempted.
4. Execute the inverse. The inverse is the one derived from the
   pre-action observation by the harness rule. Where no inverse
   is derivable from what the observation carries, the action is
   refused by name at selection time and never reaches this
   protocol; a refusal is a verdict, recorded as such.
5. Observe a third time. Compare the third observation against
   the snapshot for exact equality. Equality is the verdict
   PASS. Any difference is the verdict MISMATCH, and the record
   names the differing component — the field, the element, the
   window, the page — never a bare failure.

Verdicts per action are appended, never rewritten. A later pass
over the same action is a new record, not an edit.

## Scope of the first pass

The actions reachable today, from the harness program in the
idol-eyes tree (protocol harness file at the candidate space
pin 036df3b3): the field actions set, check, uncheck, toggle,
for which the program derives inverses, and the click action,
for which it refuses by name. The browser navigation inverse is
specified in the harness spec over a carried block; the browser
face itself is absent in the executor (gap G4), so navigation
stands as specified, not executed.

## First pass — state model run (executed 2026-11-20)

The harness of lane 4, run against a state model faithful to the
harness vocabulary (field values, checkbox states, a navigation
history, and click as the no-inverse case), with fresh
observation implemented as a re-read of the state through an
observe function at each protocol step, and one negative control
(a deliberately wrong inverse) that the harness must catch.

<!-- LANE4-RESULTS -->

Scope honesty: this pass validates the protocol against the
harness's state model. It does not validate a live desktop: the
executor's compiled battery is itself unrun (gap G1), no browser
or display exists on the measuring machine, and the native
dispatcher is gap G2. The live pass is owed on an owned desktop
through the executor's own faces. Until it runs, the execution
layer claim stays premise P5 / UNMEASURED, and the per-action
verdicts below are model verdicts, labeled as such wherever they
are cited.

## What closes the claim

Per action, the claim closes only when the protocol above runs
through the executor's own faces on a live surface and prints
PASS on fresh observed state — or MISMATCH, which is a defect
against the landed change and is printed as one. The refusal
verdict for click closes by the refusal being issued by name at
selection time in the live executor, not in the model.
