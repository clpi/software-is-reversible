# Recursive algorithms — specs, obligations, empirical states

Each family is specified at agent-proof resolution: inputs,
outputs, the recursion, the invariants an implementer has no
choice about, and the refusal cases. Theorem obligations are
handed to lane 1 by the census identifiers of census.md. Empirical
state is printed per family: executed, or UNMEASURED with the gap
named. Nothing in this file is implemented behavior unless the
state line says executed and names where.

## Family A — the token stream that rewrites its own weightings

Statement. A deterministic output token stream drives tensor
edits that produce the weightings on the fly: output stream,
then tensor edit, then new weightings, then next output, all
deterministic, the original checkpoint pinned throughout.

Inputs. A pinned checkpoint; an archived next-token row set keyed
by the behavioral key (prefix, token, checkpoint, protocol) —
never by token alone; an overlay store of edit records, each
naming its coordinate set, its before and after bytes, its
constraint set, and the hash of the state it produces.

The recursion. State is the triple of the current stream prefix,
the current overlay stack, and the current weighting epoch.
One step: (1) decode the next token by the best-first rule over
the archived rows under the current weightings — pop the highest
scored prefix; a missing row leaves the prefix as an unresolved
branch carrying its score as an upper bound, never dropped;
(2) read the step's derived vector from the semantics and intent
vectors at the current log prefix; (3) where the derived vector
names an edit, construct the edit tensor over the current
weightings: coordinates selected explicitly, every other byte
protected, tied weights preserved as a stated constraint;
(4) apply the edit to a writable copy, never to the pinned
checkpoint; append the edit record; the new weightings are the
recomputed projection under the appended overlay stack;
(5) recurse on the extended prefix. Removing the overlay stack
restores the original result exactly, by the round trip of the
edit layer.

Invariants. Determinism: the same archive, checkpoint, and
parameter record give the same stream, the same edits, and the
same weightings. Protection: no byte outside a selected
coordinate set ever changes. Certification shape: a claim that an
edit achieved a target vector stands only on a recomputed
projection after the edit, or on independent certification —
never on the proposing vector alone.

Refusals. An edit whose constraint set would break (a tied weight
split, a coordinate outside the writable copy) is refused by
name and applies nothing. A prefix whose row is absent is an
unresolved branch, not a refusal and not a zero.

Obligations handed to lane 1. The overlay algebra: protection,
application, round trip, tied preservation — proved in this repo
(overlay protects, overlay applies, edit roundtrip, tied
preserved). The decoder certification shape: the best complete
answer is certified only once it beats or ties both the heap
maximum and every unresolved bound — the optimal face of the
stop rule (census section 1). The reweighting routes: changing
what wins reuses feature bounds and recomputes winners; changing
how tokens are weighted applies exact per-token multipliers at
selected recorded prefixes with rows renormalized — the
incremental equals full result of census section 1 is the
obligation's engine, in its log level premise form (P1).

Empirical state. Reported, not reproduced here: the deterministic
decoding line's fixtures — 384 incremental updates across 12
fixtures matched clean rebuilds; four sign bit overlays exercised
the edit mechanism (mechanism only, not arbitrary steering).
The standalone repo is blocked on access on the relaying side;
the recursive loop as specified here is UNMEASURED as an executed
system. Owner: the deterministic decoding line, with lane 3.

## Family B — determining and reweighting actions

Statement. The same machinery, read as action selection: the
pipeline determines the next action from the hypergraph state,
and reweighting actions is an appended weighting epoch, never an
edit of history.

The recursion. State is a log prefix and a parameter record.
One step: derive the semantics and intent vectors; take the
structured view; compute the weight-free Pareto frontier of
joint action plans first (frontier before weights, census
section 2); select within the frontier under the current epoch;
execute; append the outcome; reevaluate incrementally over the
premise cone only. A reweighting is a new epoch appended between
any two steps; every earlier epoch's selection stays exactly
reproducible from its record.

Invariants. Frontier before weights at every step, without
exception: a reweighting can pick a different plan on the
frontier and can never recover a plan the frontier excluded, and
can never exclude a plan the frontier holds. Selection is unique
under the stated total order. Reversibility: a selected action
is selectable only when its inverse is derivable at its layer
(reading layer compensation for derivation actions, the reverse
edit for edit actions, the harness inverse for executor
actions); otherwise it is refused by name and the refusal is
appended.

Obligations. Insert exact and retract insert of fresh (proved
here); selected undominated and epochs reproducible (cited,
census sections 1 and 2).

Empirical state. The pipeline program's live loop executed this
recursion in manual derivation form on the fleet's own queue
(its record: 4 of 8 iterations used, closed by refusal closure);
the executor form is UNMEASURED — the solve loop executor is the
idol-eyes gap G2 of the candidate space record. Owner: the
pipeline program, with idol-eyes.

## Family C — decomposition and resolution across the vectors

Statement. Obscurity, stop, and interaction are vectors over one
coordinate list, and resolving a region decomposes across them:
a region is worked exactly where its obscurity reading is above
threshold, its stop reading is insufficient, or an interaction
reading names it — and the decomposition is over the one
hypergraph, never over copies.

Definitions. Obscurity of a coordinate: the count, over the three
clauses (unresolved, unprojected, uncertain), weighted at the
coordinate, of the clauses that hold; a region's reading is the
sum over its coordinates. Stop: the two faces of census section 1
kept separate at every coordinate — acceptable and optimal are
different readings and are never merged. Interaction: the reading
that names which coordinates' resolutions change which other
coordinates' readings, read off the derivability relation before
and after an append (the unblocks coordinate of the action
vector is its first form).

The recursion. Pick the region with the highest combined reading
under the current epoch; resolve it by the append operations
alone (admit, join on a witness, record the level, paint);
recompute only the affected coordinates — the premise cone of
the append; recurse. Resolution is monotone: a coordinate that
becomes resolved, projected, and certain never returns to
obscurity under growth, because each clause is a reading of the
log and growth only appends.

Refusals. A region whose resolution would need a witness that
does not exist is deferred with the witness named, and nothing is
appended for it. A threshold is a parameter adopted only on a
stated metric over a named instance set; no instance set is named
in any foundation yet — that absence is gap S14 of the pipeline
spec, carried here: until it closes, no claim in this family
depends on a threshold value for soundness.

Obligations. Obscurity monotonicity rests on the canonical
premise (persistence under growth); the finite list instances are
the persistence results cited in census section 1. The cone
scoping obligation is incremental equals full on the covered
cone (census section 1, premise P1 at log level).

Empirical state. One executed instance: the pipeline live loop's
third subject, where the obscurity route constructed the action
on a real item with no hand-written lane (the temporary volume
hunt: the producer region scored above threshold on all three
clauses; the constructed measurement named every major producer;
the follow-on action was constructed from the measurement and
executed). The general loop is UNMEASURED. Owner: lane 3 with
the pipeline program.

## Family D — on-the-fly resolution of semantic and intent matrices

Statement. The semantics vector and the intent vector are two
vectors over one coordinate list, kept as two vectors at every
resolution; a matrix in this family is the pairing of the two
over a level's coordinates, and resolving it on the fly means:
given a level and a budget in counted form, produce the paired
readings for exactly the coordinates the budget covers, at the
level's recorded bound, with the uncovered coordinates printed
as unresolved — never placeholdered, never silently truncated.

The recursion. Widen the scope one step at a time (trivial,
first, full); at each widening, resolve the newly in-scope
coordinates by append only, reconcile them onto the same graph
(mismatched levels are views of the one graph, per the ruling),
and recompute the paired readings over the union coordinate
list. The recursion bottoms out at symbolic resolution: no
analysis resolves below a symbol.

Invariants. The two filters are never conflated: no count is
computed by trading the observed filter for the qualified
filter. A view is a function of the graph and the level alone.
Bounds are recorded as data at the moment a level is recorded
and are never recomputed; the bound reading on a grown graph is
a different object from the record and the two are never
substituted.

Obligations. The resolution algorithm's thirteen claims are this
family's obligation list (census section 3), with the eight
specification gaps carried beside them. View extensionality and
the mask soundness are proved in the frontier home (cited in the
pipeline spec, stage B).

Empirical state. The registry increment of the canonical home
executed the incremental fold against from-scratch at symbolic
grain: exact agreement, epoch colors matching (the pipeline
empirical lane's controlled re-run over the 321 registry
records). The general matrix resolution over arbitrary levels
and budgets is UNMEASURED. Owner: lane 3 with the canonical
home's proof lane.
