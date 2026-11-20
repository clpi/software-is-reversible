# Lane 3 — proposition validation, set B

Meta-search solve-and-validate program (Chris, direct,
2026-11-20 01:56 PST). Base pin: master
d05ff699511099e6b4b28b2ae50e5c7cd590507e. Method, binding:
candidate sets constructed over the one hypergraph; the
frontier is solved weight-free before any weighting selects;
every candidate is empirically validated on its proposition's
contract battery, the same contract for all rivals, in executed
runs at the pin above; down-selection is the frontier
survivors. No run means UNMEASURED, never a winner by absence.

Harness: lane3.py in this repo (stdlib only, integer
milli-log-prob arithmetic, seeded generators only, counted work
instead of wall time). Full machine output: lane3-results.json.
Two consecutive whole-harness runs produced byte-identical
results files (sha256 of the results file:
ef0c54176e30a6199cdb5fe749d972e7cd4ac371a2c30213119c80614fff4e3a).

## Proposition 1 — deterministic decoding rivals

Candidate set (four rivals, one contract): greedy; canonical
tie-break; factored recipe (rows stored as row maximum plus
per-token deltas, reconstructed exactly, then canonical
selection); best-first certified (heap search; a complete
answer is certified only once it beats or ties both the heap
maximum and every unresolved bound — the optimal face of the
stop rule, census section 1).

Contract battery: five fixtures of archived next-token rows
keyed by the behavioral key (prefix, token, checkpoint,
protocol), checkpoint synth-ckpt-1, protocol archived-rows-v1 —
a deterministic chain, a three-way tie with scrambled row
order, a trap (the greedy first step leads to a continuation
1,700 milli worse than the optimum), a missing-row fixture
(the continuation row is absent: an unresolved branch, never
a zero and never dropped), and a generated branching tree
(depth 4, width 3). Axes, all measured: optimality gap against
an independent exhaustive oracle (milli, lower better);
counted candidate evaluations; archive storage bytes under a
compact JSON encoding; permutation invariance of the output
under six row-order permutations (one full reversal and five
seeded shuffles); certified fixtures; determinism on repeat.

Executed results at the pin:

| candidate | gap | evaluations | storage bytes | permutation invariant | certified |
|---|---|---|---|---|---|
| greedy | 1700 | 24 | 4488 | NO | 0 of 4 completable |
| canonical | 1700 | 24 | 4488 | yes | 0 of 4 completable |
| factored | 1700 | 24 | 4971 | yes | 0 of 4 completable |
| best-first certified | 0 | 114 | 4488 | yes | 4 of 4, all sound |

Per fixture: on the trap, greedy, canonical, and factored all
return the stream [4] at total -2100 against the oracle optimum
-400; best-first returns [5, 6] at -400, certified. On the tie,
greedy returns token 3 (the first maximum in archived row
order) and changes under row permutation; canonical and
factored return token 1 under every permutation. On the
generated tree all four return the optimum -782 (the gap is
entirely the trap's). On the missing fixture, greedy,
canonical, and factored return the partial stream [7] flagged
unresolved; best-first returns no complete answer and carries
the branch as an unresolved bound of -300, issuing no
certificate. Every certificate best-first issued was re-checked
against the oracle and the heap maximum at certification time:
all sound. All four candidates repeated byte-identically.

Frontier (weight-free, over the five axes): canonical and
best-first certified. Neither dominates the other: canonical
is cheaper (24 against 114 evaluations) with no certificate
and a 1700 gap on the trap; best-first is gap-free and
certified at the higher counted cost.

Down-selection: frontier survivors are canonical tie-break
and best-first certified; a weighting may select between them
inside the frontier and nowhere else. Eliminated, with the
differing component named: greedy is dominated by canonical —
identical on gap, evaluations, and storage, worse on exactly
one axis, permutation invariance (its tie pick is a function
of archived row order). Factored recipe is dominated by
canonical — identical on gap, evaluations, invariance, and
certification, worse on exactly one axis, storage: under the
stated compact encoding at fixture scale the factored form
costs 4,971 bytes against 4,488 plain, because the per-row
maximum and delta framing outweigh the smaller delta digits.
That is a measured loss at this scale and encoding, printed
as such; it is not a claim about the recipe at model scale.

UNMEASURED, with owners: everything that needs the real
fixtures. (1) Any figure on a real checkpoint's distribution —
the pinned Pythia fixture bytes are absent on this machine and
the standalone deterministic-llms repo is blocked on the
relaying side (access): owner, the deterministic decoding
line; the closing route is that repo's landing plus the
fixture bytes, then this same battery re-run with the archive
swapped. (2) The break-even figures behind census section 6
(the recipe against the dense mask) stay reported and
UNMEASURED for the same reason and owner. (3) Editing quality
and any wall-time figure: UNMEASURED here by design — counted
work only. What this proposition does settle is the rivals'
relative standing under the contract on executable fixtures:
the certification shape is not vacuous (it fires, and its
certificates check), greedy's tie behavior is a measured
defect, and the factored form's storage claim fails at
fixture scale.

## Proposition 2 — semantic and intent matrix resolution

Candidate set (three rivals, one contract): from-scratch
resolution; incremental cone-scoped resolution (an append
updates exactly the coordinates the record touches); on-the-fly
budgeted resolution (a query resolves exactly the coordinates
its budget covers and prints the rest unresolved). The matrix
is the pairing of the semantic vector and the intent vector
over one coordinate list; a reading per coordinate is the
tuple (semantic sum, intent sum, joint sum of products,
count). Equality is exact on all four components.

Carried foundation, not recomputed (never blindly recompute):
the pipeline empirical lane's executed result over the 321
registry records at extract pin
69ee40eb000f557e07dae548efa9a503703ecb35 — incremental
reevaluation equaled full reevaluation exactly at every
checkpoint measured (after homes 1, 6, and 14, and in suffix
form, 150 prior plus 171 appended), derived measures and both
epoch colors matching the recorded registry entry. This lane
extends that result; it does not re-derive it.

Extensions, executed at the pin:

- Analogue scale (321 synthetic records, 64 coordinates,
  checkpoints at 10, 150, 321): incremental equaled
  from-scratch at 3 of 3 checkpoints. Counted work:
  incremental 2,448 coordinate updates against 3,652 for
  from-scratch re-derivation at the same checkpoints.
- Held-out permutations (five seeded permutations of the same
  321 records, checkpoints at 80, 200, 321): incremental
  equaled from-scratch at 3 of 3 checkpoints in every
  permutation, and the final paired readings are identical
  across all five permutations and to the unpermuted order —
  the resolved matrix is a function of the record set, not
  of append order, at final state; intermediate readings are
  order-dependent and were compared only within each
  permutation, never across.
- Larger synthetic matrix (5,000 records, 256 coordinates,
  checkpoints every 500): incremental equaled from-scratch
  at 10 of 10 checkpoints. Counted work: incremental 39,450
  against 216,721 from-scratch.
- Suffix form on the large matrix (2,000 records carried,
  3,000 appended from the carried state): the result equals
  the from-scratch derivation of all 5,000 exactly.
- On-the-fly budgeted query on the large matrix's final
  state, budget covering 64 of 256 coordinates: every covered
  coordinate's reading equals the full resolution exactly;
  the remaining 192 coordinates are printed unresolved as
  explicit nulls — verified none is a placeholder value.
  Counted query work 9,750.

Frontier (weight-free; axes: exactness, counted work,
coverage): incremental cone-scoped resolution and on-the-fly
budgeted resolution. Incremental dominates from-scratch on
work at identical exactness and coverage at every scale run.
On-the-fly is incomparable with incremental: lowest counted
work per query, exact on what it covers, but coverage is the
budget's fraction (64 of 256 here) against incremental's
full coverage.

Down-selection: frontier survivors are incremental
cone-scoped resolution (the production candidate for full
resolution) and on-the-fly budgeted resolution (the candidate
where a stated budget bounds the query, with uncovered
coordinates printed, never truncated silently). From-scratch
is eliminated as a production candidate and retained as the
battery's checker — the same role the exhaustive oracle plays
in proposition 1. No failure was observed in any run: every
equality check passed, so there is no differing component to
name; the negative space is stated instead — equality was
checked on sums over integers, where append order cannot
matter at final state by construction, so the permutation
result confirms the harness rather than stressing a
non-commutative reading. A reading whose components do not
commute (for example a last-writer component) is outside
this battery.

UNMEASURED, with owners: the general matrix resolution over
arbitrary levels and budgets in the canonical home's sense
(the resolution algorithm's thirteen claims, census section
3) stays theorem-to-be / UNMEASURED as a general claim —
owner, lane 3 with the canonical home's proof lane; this
battery covers the counted-budget, symbolic-grain form only.
Wall time is UNMEASURED by design (counted work only).

## Proposition 3 — the tensor-rewriting loop as a system

The overlay algebra is proved in this repo (protection,
application, round trip, tied preservation). What stood
UNMEASURED was the loop as a system: a deterministic output
token stream rewriting tensors to produce weightings on the
fly. Candidate set, qualified against the family's invariants
before any frontier: (a) the loop with certification by
recomputed projection; (b) the loop trusting the proposing
vector's own report of the post-edit weightings; (c) the loop
editing the pinned checkpoint in place. Candidates (b) and
(c) fail qualification, not a traded axis: (b) violates the
certification shape (a claim standing on the proposing vector
alone), and (c) violates protection of the pinned checkpoint
and the round trip. The executed battery below runs (a), and
runs (b)'s failure as a negative control with the differing
component named.

Executed loop at the pin: base weightings are a pinned
16-coordinate integer vector (coordinates 3 and 4 tied, 13
and 14 tied). The stream runs over the proposition 1 archive
(the trap fixture, then the branching tree) under the current
weightings. The derived-vector edit rule, stated once and
followed exactly: an intent-named edit where the trigger
table names one; otherwise, where the decoded row contains a
candidate scoring at or below -300, an obscurity-named edit
of +150 on the worst candidate's coordinate; an edit on a
tied coordinate is constructed over the whole tied group at
one value. Each edit appends an overlay record; the new
weightings are the recomputed projection under the appended
stack; the loop recurses on the extended prefix.

Results: stream [4, 0, 46, 19, 43, 48, 0]; four edits
appended (step 1, coordinate 5 to 160, intent-named; step 3,
coordinate 0 to 150, obscurity-named; step 4, coordinates
13 and 14 to 195, obscurity-named over the tied group; step
6, coordinates 3 and 4 to 350, obscurity-named over the tied
group). At every edit, the incremental copy was checked
against a projection recomputed from the pinned base under
the full stack: 4 of 4 equal — that recomputation is the
only basis on which any weighting is reported. Protection:
every coordinate never named by an edit holds its base value
in the final weightings. Round trip: removing the stack
restores the base vector exactly. The pinned checkpoint was
never mutated (verified by value at the end).

Determinism: the loop ran twice in one process and once in a
separate process; the serialized result (stream, edits,
final weightings) is byte-identical across all three, digest
ca46229572007e598cb5aac3832ea2a6b7eaac5d3ce41aaf29f885a24f1bb5a2.

Certification rule, negative control: a claim that coordinate
6 of the post-edit weightings equals the proposing vector's
figure (base + 999) was put to the recomputed projection
(base + 250 under the appended edit). The claim is REFUSED;
the differing component is named: coordinate 6, claimed 919
against recomputed 170 (the base value -80 plus the +250
edit the stack actually carries; the numbers are the
control's own, read from lane3-results.json).
No claim in this run rests on a proposing vector.

Refusal control: an edit naming coordinate 3 alone (a tied
split) is refused by name R-TIED-SPLIT and applies nothing —
the overlay stack is byte-identical before and after the
attempt.

Down-selection: the qualified candidate set is the single
candidate (a), so the frontier is (a) alone: the loop with
certification by recomputed projection is the down-selected
form of the tensor-rewriting loop on this battery.
Eliminated at qualification, with differing components:
(b) — its claim differs from the recomputed projection at
coordinate 6 in the control; (c) — it differs from the
contract at the pinned checkpoint itself (mutation where
the algebra requires an append-only overlay) and forfeits
the round trip.

UNMEASURED, with owners: (1) The loop over a real
checkpoint's tensors and a real model's archive — the same
fixture blocker as proposition 1: owner, the deterministic
decoding line; closing route, the standalone repo's landing
plus fixture bytes, then this loop re-run with the archive
and base vector swapped. (2) Editing quality — whether the
edits move any external behavior in a wanted direction — is
UNMEASURED; this battery measures determinism, protection,
the round trip, and the certification rule, and no quality
claim is made. (3) The loop at widths beyond 16 coordinates
and streams beyond 7 tokens is UNMEASURED; the algebra is
proved generally, the executed system is this scale.
