# The guided search space — first expansion

The space lives over the one append-only hypergraph (spec.md).
A candidate is a record over the graph: an algorithm, an
architecture, or a design, with the measures of the candidate
space (frontier home, 60f33193): net newness, impact, novelty of
composition, gaps closed, unblocks, redundancy change — and the
six improvement axes, each present only with evidence of its
stated kind.

## The guidance vector

Every candidate in this space is additionally scored on the
guidance vector, five coordinates, each a reading with its
evidence stated, never a vibe:

1. Novelty. The candidate's construction is not a restatement of
   a construction already in the space or in the cited
   literature. Evidence: the search that found no prior form,
   named with its corpus.
2. Not pre-existing. No incumbent, in the row's domain or any
   adjacent one, already does this. Evidence: the incumbent
   census of the domain row.
3. Much improved. Against the incumbent's actual result, the
   constructed approach is better on at least one axis by a
   margin that matters, and no worse on any axis the row claims.
   Evidence: a same-contract measurement, or the cell prints
   UNMEASURED.
4. Unique. The candidate exploits a property only this
   construction has (for this program: derivation from the one
   hypergraph, with its append-only, premise-carrying form).
   Evidence: the property named, and the check that no incumbent
   in the row has it.
5. Compositional synthesis potential. The candidate composes
   with proved components already in the space to derive further
   candidates. Evidence: the compositions actually derived,
   appended as new candidates.

The driving tests are the payoff-bearing ones: payoff-weighted
test-driven search (spec.md states the reading of the order's
phrase). A candidate enters the expansion queue ordered by its
guidance vector under the current weighting epoch; the frontier
of the queue is computed before the weights, as everywhere in
this program.

## Expansion rule

The space expands by append only. Each landed result appends:
the result itself, the candidates its composition with existing
proved components derives, and the gaps it opens, each gap a
first-class object with its own measure vector. Nothing is
removed; a superseded candidate is painted superseded by a later
epoch, and its record stands.

## Domain rows — first expansion

Each row: the previous computer science actual result (the
incumbent, at citation grade), the constructed approach, how it
was done via the hypergraph, and the comparison state in exactly
one form: proved at Pareto optimum, measured, or UNMEASURED.

### Row: Pareto frontier and skyline computation

Incumbent actual result. The skyline operator of Börzsönyi,
Kossmann, and Stocker, "The Skyline Operator," ICDE 2001, pages
421 to 430: the Pareto set as the tuples not dominated on all
dimensions, computed by block nested loops (best case linear in
the input when the skyline fits the window, worst case quadratic
— the paper's own statement) or by divide and conquer over
partial skylines. A later external memory result (Tao and
co-authors, ACM Transactions on Database Systems, 2012) settles
the fixed-dimension case in block transfers; the exact exponent
is UNVERIFIED at digit level in this program's lane.

Gap. The frontier is recomputed from a flat tuple set per query:
no persistent equivalence structure under the points, no record
of why a point was dominated or by what premise, no cone-bounded
incremental guarantee, and no separation between computing the
frontier and applying a weighting — a weighting change is a new
query, not a re-reading.

Constructed approach, via the hypergraph. Candidates and their
dominance premises are terms of the one graph; the frontier is
computed exactly from the graph before any weighting; a
weighting is an appended epoch read over the computed frontier;
insertion, retraction, and reweighting reevaluate incrementally
with equality to the full solve on the covered cone (proved:
frontier home 60f33193, and in place in this repo).

Comparison state. Proved at the frontier layer (exactness of the
solved set). The skyline asymptotics are the incumbent's own;
no same-contract speed run against a skyline implementation has
been executed: speed UNMEASURED. Guidance: novelty in the
premise-carrying persistence, not in the frontier notion itself;
compositional potential high (this row's components are the
search core every other row uses).

### Row: incremental maintenance and closure

Incumbent actual results. Semi-naive bottom-up Datalog
evaluation (standard account: Ketsman and Koutris, "Modern
Datalog Engines," Foundations and Trends in Databases, 2022):
each iteration derives only from facts new in the previous one;
Datalog evaluation is P-complete in data complexity and
EXPTIME-complete combined. Incremental maintenance proper:
Gupta, Mumick, and Subrahmanian, "Maintaining Views
Incrementally," SIGMOD 1993, pages 157 to 166 — the counting
method (stores only the number of alternative derivations per
tuple, stated optimal for nonrecursive views) and the delete
and rederive method for recursive views. Current high-water
mark: DBSP (Budiu, Chajed, McSherry, Ryzhyk, and Tannen, PVLDB
16(7), 2023, best paper): the incremental form of any query is
differentiate after the query after integrate, cost proportional
to the size of the change, theorems checked in a proof
assistant.

Gap. Counting deliberately discards the derivations, so a
maintenance step cannot be explained, audited, or inverted;
delete and rederive pays an over-deletion pass not cone-bounded
by construction; DBSP's state is operator state inside a
dataflow circuit, not one shared inspectable equivalence graph
with a premise cone a third party can read, and it carries no
frontier before weighting discipline and no action inverses.

Constructed approach, via the hypergraph. Derivations live as
edges of the one graph; an insertion or retraction rederives
only over its premise cone and the incremental verdict is
proved equal to full evaluation on that cone (census section 1;
the worklist count lemmas of census section 4 are the firing
engine). Maintenance, explanation, and inversion are the same
graph read.

Comparison state. Proved for the one-append and compensation
forms; the general worklist equality is lemma L-close, stated
and unproved, owner lane 1. Against DBSP no same-contract run
exists: speed UNMEASURED. Guidance: much improved on the audit
and inversion axes by construction; novelty in the single
shared graph; compositional potential high.

### Row: deterministic decoding

Incumbent actual results. Greedy decoding and beam search, with
the canonical negative results: Holtzman, Buys, Du, Forbes, and
Choi, "The Curious Case of Neural Text Degeneration," ICLR
2020 — maximisation decoding degenerates (beam width 32 already
repetitive on GPT-2; at width 64 or more the model prefers to
stop immediately), and the distribution's unreliable tail must
be truncated, hence stochastic sampling. Stahlberg and Byrne,
EMNLP-IJCNLP 2019 — exact search on WMT15 English to German
shows beam search at width 100 still misses the global best
score in most cases, and for 51.8 percent of sentences the
global best score is the empty translation (exact decoding
about 2.1 BLEU against about 30.3 for beam width 10): the
search error masks a model error. No published certified
deterministic decoder was found by this program's lane; that
absence is UNVERIFIED as a universal claim.

Gap. Determinism is bought by giving up any certificate: no
bound on distance from the model optimum, no record of what was
pruned, no re-decision under a new weighting without a rerun.

Constructed approach, via the hypergraph. Decoding is search
over the graph: every partial continuation is a term with its
premises; the qualified frontier of continuations is computed
before any weighting; certification follows the optimal face of
the stop rule (census section 1) — the best complete answer is
certified only once it beats or ties the heap maximum and every
unresolved bound, and unresolved branches are never dropped.
Recursive family A of recursive.md extends the same search so
the output stream rewrites the weightings on the fly.

Comparison state. The certification shape is proved in its stop
rule form; the decoder as a system is reported (the decoding
line's fixtures) and UNMEASURED here. Guidance: unique in the
certificate plus premise record; compositional potential high.

### Row: tensor editing and steering

Incumbent actual results. ROME (Meng, Bau, Andonian, and
Belinkov, "Locating and Editing Factual Associations in GPT,"
NeurIPS 2022): a closed-form rank-one update writes one factual
association into one feed-forward matrix; on CounterFact, the
reported harmonic score is 89.2 for GPT-2 XL against 66.9 for
constrained fine-tuning, efficacy 100.0, paraphrase 96.4,
neighbourhood 75.4 (as read in this program's lane). MEMIT
(Meng and co-authors, ICLR 2023) spreads batch edits across
layers. Steering: activation addition (Turner and co-authors,
arXiv 2308.10248) and contrastive activation addition (Rimsky
and co-authors, ACL 2024, pages 15504 to 15522) — contrast-pair
activation differences added at inference, no training. The
scale limit: Gupta, Rao, and Anumanchipalli, ACL 2024 Findings
— sequential ROME and MEMIT edits forget gradually, then
catastrophically; downstream ability collapses.

Gap. An edit is an opaque numeric overwrite: no premise, no
derivation record, no derivable inverse; undo means storing a
full prior copy. Steering directions carry no qualification
contract; off-target effects are measured after the fact. And
the forgetting result shows edit sequences are not incremental
in any proved sense — later edits silently degrade earlier
ones, which is exactly the failure this program's monotone
rule exists to exclude.

Constructed approach, via the hypergraph. A weight is a
first-class program value — a table plus a shape descriptor —
in the one derivation machinery (the standing weights ruling).
An edit is an appended structural map with its premises, its
coordinate set, and its before and after bytes; the overlay
algebra is proved in this repo (protection, application, round
trip, tied preservation); its effect rederives only over the
affected cone; its inverse is derivable from the record, so
edits compose, audit, and reverse by construction, and removing
the overlay restores the original exactly.

Comparison state. The algebra is proved. Editing quality
against ROME or MEMIT at the same contract is UNMEASURED; the
forgetting failure mode is excluded by the append-only form at
the record layer, and whether that exclusion holds at the
behavior layer is a measurement, not a claim. Owner: lane 3
with the obscure weights goal (monotone and incremental by
Chris's constraint on that goal).

### Row: equality saturation and e-graphs

Incumbent actual result. egg (Willsey, Nandi, Wang, Flatt,
Tatlock, and Panchekha, "egg: Fast and Extensible Equality
Saturation," PACMPL 5, POPL, Article 23, 2021, distinguished
paper): an e-graph represents a congruence relation over many
expressions; equality saturation saturates one e-graph for one
input program and extracts the best program under a cost
function; contributions are rebuilding (amortised invariant
restoration, stated asymptotic speedups in practice) and
e-class analyses. A secondary summary's solver speedup figure
(15 times, 47 times batched) is UNVERIFIED in this lane.

Gap, against the ruling. The e-graph is per-run and per-program:
built, saturated, extracted from, discarded. There is no single
persistent append-only graph shared across programs and time,
no qualification colouring distinct from equivalence, no
frontier computed independently of the extraction cost model
(a new weighting is a new extraction problem), no premise cone
giving incremental equality across edits to the world, and no
actions with derivable inverses. Under the ruling of
2026-11-19, any single e-graph is at most a projection of the
one total equivalence terms graph.

Constructed approach, via the hypergraph. Saturation is a
derived view over the one graph; the qualified frontier is
computed before any extraction weighting; later terms and rules
reevaluate incrementally with equality to the full result on
the covered cone; extraction, editing, and action all read and
extend the same persistent graph.

Comparison state. The view and frontier forms are proved in
their homes (census sections 1 and 5). No same-contract run
against egg exists: speed and coverage UNMEASURED. Guidance:
novelty in persistence plus qualification, not in saturation
itself; unique by the singular graph property; compositional
potential high.

Row 4 of the lane's census — the computer-use incumbents
(Playwright, Selenium, Nova Act, the Cua family, the Vercel
desktop tool, at the pins verified in the candidate space
record) — is carried in full by the idol-eyes row below, which
is where this program develops it.

### Row: computer use — idol-eyes, the standing not-good-enough

Incumbent actual results (verified at their primary repositories
2026-11-19, candidate space record part B): Playwright v1.65.1,
Selenium selenium-4.53.0, Nova Act v4.0.234.0, the Cua family at
cua-spaces-v0.38.16 (driver component unverified beyond family
identity), the Vercel desktop tool release v1.3.1. No rival is
installed in this environment; no same-contract run against any
rival has been executed.

Constructed approach. Idol-eyes as it stands is NOT GOOD ENOUGH,
and this row prints why in the incumbent record's own terms:
observation implemented on one face; action partly implemented
(ten native tools on the Linux face; the sixteen semantic
actions, held input, waits, window and application management,
notifications, and clipboard of the beat spec absent); browser
absent; graph authority proposed only (preview references, not
graph identity); packaging absent. Its one landed increment is
the harness decision program (inversion derived for set, check,
uncheck, toggle, and browser navigation; refusal by name where
no inverse is derivable), source-checked at 133 tests with its
compiled battery unrun (gap G1).

The development this row orders — actions more structurally: an
action is a structural map derived from the hypergraph, not a
dispatch entry. Concretely, as candidate families appended to
this space:
- F1, action as derivation. The candidate action set at a state
  is the frontier of the candidate space over the current view:
  actions are derived from the semantics and intent matrices
  (recursive.md family D) at the moment of selection, with their
  premises carried, instead of enumerated in a tool table.
- F2, inverse as derivation. An action's inverse is derived from
  the same graph facts that derived the action — the observation
  it changes is a graph reading, so the inverse is a derived
  candidate with its own premises, refused by name when the
  reading does not carry the prior (the reversibility protocol
  of reversibility.md is its validation).
- F3, outcome as append. Every executed outcome appends back as
  an observed record with its receipt; the next action set is
  rederived from the grown graph, incrementally, over the cone.
- F4, faces as views. Desktop, browser, process, and visual
  faces are views of the one graph at recorded levels, not
  separate stacks; a face that cannot be derived from the graph
  is a named gap, as the browser face stands today (G4).

How via the hypergraph. The executor's state is a log prefix;
its actions are qualified candidates over the view at that
prefix; its reweighting is an appended epoch; its certification
is the monotone certification chain of the certification home
(first certificate issued: NOT CERTIFIED, three dimensions
unmeasured).

Comparison state. UNMEASURED on every speed and setup cell;
losses printed in the ledger (section 564 of the zero loss
ledger): browser task coverage absent, on-the-fly solvability
specified not built, reweightability specified not built.
Semantic fidelity and reconversibility stand at implemented in
preview, source-checked — explicitly not wins. Guidance vector
for the F families: novelty high (no incumbent derives its
action set from an equivalence graph), not pre-existing per the
incumbent census above, much improved UNMEASURED until the
matched campaign runs on an owned desktop, unique by the
hypergraph property, compositional potential high (F1 to F4
compose with the proved frontier and certification components).
Owner: idol-eyes line; closing route: the matched campaign plus
the live reversibility pass of reversibility.md.

### Row: deterministic decoding and the recursive weighting loop

Incumbent actual result. Ordinary serving samples or greedily
decodes from a fixed checkpoint: the weighting is an input, not
a program value, and no serving stack derives its next
weighting from its own output stream. The deterministic version
in the decoding line (Chris's statements of 2026-11-19, reported):
best-first decoding over an archived row set with unresolved
branches carried, certification only against the heap maximum
and all unresolved bounds; 384 incremental reweighting updates
across 12 fixtures matched clean rebuilds.

Constructed approach. Recursive family A of recursive.md: the
output stream rewrites the tensors that produce the weightings
on the fly, through the proved overlay algebra of this repo
(protection, round trip, tied preservation), with the claim
discipline that a target vector is claimed only on a recomputed
projection.

How via the hypergraph. Behavioral vectors are keyed by prefix,
token, checkpoint, and protocol as terms of the graph; an edit
is an appended record over those terms; the weighting at any
step is a view of the graph at that prefix.

Comparison state. The overlay algebra is proved (this repo).
The loop as a system is UNMEASURED; the fixture figures are
reported, with the standalone repo blocked on access on the
relaying side. Owner: the deterministic decoding line.

### Candidate family: the basic action model (lane 4, 2026-11-20)

Appended by composition of the F families above with the
reversibility protocol: the seven basic actions (move by a
pixel delta, jump, jump over an object, drive, touch, type,
automate a process step) as one candidate family whose
members are rival selection algorithms, not designs — the
explicit planner (route 1), the obscurity construction
(route 2, the action constructed from the obscurity vector
above threshold where no explicit algorithm names it), the
combination (route 3), and a greedy nearest-target control
(route 0). The spec is the action model file in this repo;
the harness is its actions file; the executed results are
its action results file.

Comparison state, executed in simulation at the stated
fidelity (60 paired permutations per family per rival, base
seed 20261120, two runs byte-identical): combination and
obscurity tie on the frontier at 419 of 420 selections and
dominate the explicit route at 391 of 420; the control is
refuted at 46 of 420. The combination route is down-selected
on the probe-cost axis (zero probes wherever the observed
model is complete; the obscurity route pays up to a mean of
525.2 probes per drive selection). Reversibility per
primitive is executed in the same run: move, drive, type,
and automate over setting steps pass the fresh-observation
round trip; jump, jump over, and touch are refused by name;
automate with a submission step is refused by name with the
step named. Live-surface execution of the whole family is
UNMEASURED; owner the idol-eyes line, closing route the
matched campaign. Guidance: novelty high (selection as a
competition of derivation routes over one scenario
distribution is not an incumbent form), not pre-existing per
the computer-use row's census, much improved measured only
inside the family (against its own control), unique by the
route record each selection carries, compositional potential
high (the family is F1 to F3 instantiated per primitive, and
its scenario families are the matched campaign's source).

## Expansion log

- 2026-11-20, epoch zero: this file. Rows entered: the domains
  above. Candidates appended by composition at epoch zero: the
  idol-eyes F families (from composing the proved frontier core
  with the harness increment); the recursive weighting loop
  (from composing the overlay algebra with the decoder
  certification shape). Gaps appended: L-gen and L-close
  (census.md), the live reversibility pass, the matched
  computer-use campaign, the threshold instance set (gap S14).
- 2026-11-20, meta-search lane 1 append: the meta level of
  meta.md — weighting configurations as candidates over this
  space, their measure vectors, their weight-free
  meta-frontier, and an executed first pass (meta.py;
  results in meta-results.md). Executed: 13 of 39 enumerated
  configurations select the middle frontier member on all
  three of the pass's instances (the two frontier selection
  scales and the deterministic decoding fixture), members no
  hand-set weighting in this record selects; the
  meta-frontier holds 6 of the 39. Gaps appended, owners in
  meta.md: the meta level over this file's guidance vector
  space, the meta level over the decoding system (not the
  fixture), a Lean form of the meta level, and sampling
  beyond the enumerated space — all UNMEASURED.
- 2026-11-20, lane 4: the basic action model candidate family
  appended and executed in simulation (the family entry
  above). Gap appended: the shared touch failure's closing
  candidate (finer probe grid, or scroll and reprobe),
  owner the action model family's successor lane.

- 2026-11-20, lane 5 build-out and re-validation: the
  down-selected winners of lanes 1-4 consolidated into one
  built stack (stack.py; meta level as the weighting-selection
  layer over frontier-first selection, the two-face stop,
  cone-scoped repair, the distinct-count worklist, the hybrid
  break-even rule, canonical and best-first certified
  decoding, incremental and on-the-fly budgeted matrix
  resolution, the recomputed-projection tensor loop, and the
  action combination route with the obscurity route retained
  as fallback). Every winner re-validated against its full
  candidate set and held-out permutations at the disjoint
  seed range 71000-79999 (revalidate5.py): all ten
  propositions PASS, no winner returned as a loss, no
  down-selection re-run. Record: lane5.md; results:
  revalidation-lane5-results.json. The steering hold below
  was honoured: no reach-based ranking ordered the build-out
  queue. Spectrum coverage per algorithm is recorded in
  stack.py (route 5, the terminal compressed tensor form,
  UNMEASURED across the board; owner lane 6).

## Steering hold appended 2026-11-20 (C relay via Chris, 02:01 PST)

HOLD: the candidate-space round-2 ranking — jq n first, and the
D1 layering that rests on reach figures — is SUSPENDED as
steering input for down-selection in the meta-search program
until reach is compiler-resolved with bindings resolved. Reason:
C reproduced a priority flaw — retaining only the enclosing
binding link reduces jq n's lexical reach from 48 to 3; that is
a sensitivity check, not compiler-resolved reach. It lands on
top of the pipeline lane's definitional reconciliation (50 =
unblocks append delta, 48 = static reach, gaps-closed agrees
at 1), which stands. No reach-based ranking orders the
build-out queue while this hold stands. The rest of the
program's method is unaffected.
