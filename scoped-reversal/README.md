# Software is reversible

A constructive, scoped claim: a finite deterministic state transition can
be made logically reversible by retaining enough information to separate
its predecessors. This neither erases external effects nor guarantees a
native executor can restore that state. Test logical inverse, replay, scoped
restoration and compensation separately.

## Main construction

Fix the original observation, exact program and environment versions,
a finite admissible trace family T, and a projection P of final observables.
For each observed y, the fiber is the set of traces t with P(t) = y.
A reversible residual encoder retains a stable identifier within each fiber.
An inverse exists exactly when the pair (P(t), residual(t)) is injective.
The least fixed-width number of residual bits in this finite model is
ceil(log2(max fiber size)), taking zero bits for singleton fibers. A rank
in a canonical sorted fiber attains the information bound. This is not a
bound on decoder tables, checkpoints, query time, or physical storage.

Sequential inverses compose in reverse order, provided each inverse refers
to the same scope and to the actual independently observed post-state of
its forward action. Replaying from a saved start is different from issuing
the original effect again. For a mutable external system, obtain a fresh
observation and an authoritative, idempotent inverse grant for that exact
transition. Refuse stale, ambiguous, partial, out-of-scope or irreversible
effects; an approved compensating action is not exact historical reversal.

## Hypergraph and search

One append-only logical graph stores typed source symbols, transitions,
observations, residual codecs, scopes, composition witnesses, and refutations.
Structured cut, incidence, trace, intent, obscurity and action matrices are
projections. A record's presence is not a verification or authority grant.
A compound inverse checks the conjunction of all premise receipts, not a
collection of independent reachable paths.

Candidate generators include direct inverses, residual or snapshot logs,
deterministic replay under a captured environment, conditional compensation,
and split-checkpoint hybrids. Model admissibility first, then optimize
retained payload and index bytes, capture time, worst undo latency, replay
work, ambiguity, verified scope and externally observed effects. Keep the
nondominated set, not only weighted optima; weights may retune selection but
cannot admit unknown candidates. Certify the selected plan only for an
enumerated/covered finite candidate universe; report unmeasured dimensions.

For an append, a weight-only edit reranks stable evidence; changes to a scope,
operation, data or observation invalidate its dependent slice. Keep symbolic
contracts precise enough to determine which cache/trace is stale. A stop
threshold is an acceptance test, not optimality: every remaining contender
must be excluded by admissible bounds, and ties need a stable rule.

## Tests of the high-payoff directions

| Direction | Falsifiable test | Payoff / rejection |
|---|---|---|
| Whole-trace residual versus per-step codecs | Exhaustively decode all traces through the same observable. Measure rank index, retained payload, decode latency and maximum temporary space. | Global conditioning can avoid paying for mutually incompatible worst cases. Reject a small residual that depends on an uncharged large table. |
| Mixed inverse and checkpoint scheduling | Enumerate the small complete schedule domain; independently compute its exact Pareto frontier; reconstruct each selected trace backward. | A hybrid can add nondominated points neither pure logging nor replay can attain. Reject false pruning and loss of history. |
| Reversible tensor edits vs latent semantics | Apply and undo named parameter transforms, with cache and missing-residual negative controls. Measure bit recovery and contextual metrics separately. | Exact parameter reversibility does not identify a unique intent. Reject unchecked extrapolation to runtime logits/episodes. |
| Token stream and stop | Bind model checkpoint, tokenizer, graph cut, objective, scope and actual recorded rows. Reuse unchanged prefixes; invalidate affected probabilities. | A better weighted score can change the look-ahead and stop. Abstain on missing rows; do not present a deterministic candidate as the exact optimum without a cut certificate. |
| Native Idol Eyes | On owned fixtures, capture pre-state, run the native action, independently observe post-state, derive a fresh inverse, and independently observe restored state. Compare DOM/accessibility/visual sources and cursor/process routes at equal scope. | Verified undo can replace guessing or replay-by-resubmission. Reject stale target, one-sided evidence, effect escape, missing grants, and recovery after a partially committed effect. |

For each proposal record whether there is established prior art, a
compositional improvement, a measured win or a loss, and the exact test
needed to separate those claims. Unknown novelty is not novel by default.
This suite is a first witness-backed slice, not a proof for unidentified
theorems or a claim of globally optimal architecture.

## Established baselines

- [Bennett, Logical Reversibility of Computation (1973)](https://www.cs.princeton.edu/courses/archive/fall06/cos576/papers/bennett73.html):
  log history, save output, uncompute temporary work.
- [Bennett, Time/Space Trade-Offs (1989)](https://research.ibm.com/publications/timespace-trade-offs-for-reversible-computation):
  pebbling provides distinct proven simulation trade-offs, not one universal winner.
- [Griewank and Walther, Revolve (2000)](https://doi.org/10.1145/347837.347846):
  proven checkpoint scheduling under the paper's primary and secondary
  criteria. Do not compare our heterogeneous cost domain without aligning contracts.
- [O’Callahan et al., rr (USENIX ATC 2017), Table 1](https://www.usenix.org/system/files/conference/atc17/atc17-o_callahan.pdf):
  warm recording ranged 1.49–1.79× on four listed workloads and 7.85× on
  `make`; `make` replay was 11.93×. These are paper results, not our
  measurements or evidence of reversing a third-party effect.

## Reproduce

Use Lean 4.19.0 and Python 3.11+. No network or model inference is required
for the bundled controls. The receipts distinguish modeled operation counts,
actual comparisons of same bytes, and empirical native execution; do not
pool them into a single performance score.

```sh
python3 -B empirical/fibers.py | cmp - empirical/fibers.json
```

- `proof/Reversible.lean`: constructive scoped inverse, finite enumeration,
  composition, collision refutation, finite residual alphabet lower bounds and
  reversing already-admitted transition traces.
- `empirical/fibers.py`: exact maximum-fiber calculations, constructive rank
  round trips, and strict controls on stale/mismatched post-state, wrong scope,
  damaged residuals and external effects.
- `empirical/schedule.py`: compare exhaustive Pareto enumeration, dynamic
  programming, retained prefix updates, and common convenience baselines.
  Charge modeled resource axes independently and reverse every retained
  frontier trace. Its modeled costs are not hardware benchmarks.
- `empirical/tensor_bridge.py`: scoped exact rational tensor perturbation and
  reverse projection controls. No actual model checkpoint or inference.

Run all with `sh check.sh` (or set `LEAN=/path/to/lean`).
