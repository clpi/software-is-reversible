# software-is-reversible

The reversible search space: theorem completion for the derivation
to action algorithm system, a payoff-guided candidate space over
the one append-only hypergraph, the recursive algorithm families,
and an empirical system that validates the reversible map of
actions all the way backwards on fresh observed state.

- spec.md — the program spec and its binding foundation.
- census.md — the theorem census: found and unidentified, each
  proved, premise-labeled, a refuted control, or a named gap.
- Reversible.lean — the Lean core proved in this repo.
  Gate: ./check.sh (Lean 4.19.0, cold, warnings as errors,
  axiom audit printed; every result within the three standard
  axioms, most within fewer).
- search.md — the guided search space, first expansion.
- recursive.md — the recursive algorithm families, with their
  theorem obligations and empirical states.
- reversibility.md — the validation system and its per-action
  verdicts. Its harness is validate.py in this repo, with the
  first pass's full output in validation-results.md.
- action-model.md — the basic action model: seven primitives
  (move, jump, jump over, drive, touch, type, automate) as a
  candidate family of four rival selection algorithms.
  Its harness is the actions file in this repo; its executed
  generalization table, frontier, and down-selection are in
  action-results.md.

Foundation, cited not rebuilt: the canonical hypergraph is the
total equivalence terms graph (ruling of 2026-11-19 15:43 PST),
home the redundancy is equivalence repo at 37514fb7. The candidate
space core is the frontier is solvable repo at 60f33193. The
pipeline model proofs are the derivation to action proof lane's
module at its local pin bf814c1.
- meta.md — the meta-search level: weighting configurations
  as candidates, their weight-free meta-frontier, and the
  recursion discipline. Its harness is meta.py in this repo,
  with the first pass's full output in meta-results.md.

- [Scoped reversal and exact reconstruction results](scoped-reversal/README.md) — constructive finite inverses, residual lower bounds, and reproducible empirical frontiers. Run `sh scoped-reversal/check.sh`.
- lane5.md — the build-out and re-validation lane: the
  down-selected winners of lanes 1-4 consolidated into one
  built stack (stack.py, single entry point, demonstration
  output in stack-results.json), and every winner
  re-validated against its full candidate set and held-out
  permutations at a disjoint seed range (revalidate5.py,
  results in revalidation-lane5-results.json).

- [Resolution Lab browser demos](examples/resolution-lab/README.md) — scoped action reversal, archive-only inference search, and compositional pruning with an independently checked Lean proof.
- spectrum.md — lane 6, the action-determination spectrum:
  every algorithm of the program constructed under each
  applicable route (explicit, minimization, obscurity,
  decomposition, the terminal compressed tensor) and
  validated on its own battery, with every route-pair
  equivalence proved, measured, or UNMEASURED with an
  owner. Its harness is spectrum.py in this repo, with its
  full machine output in spectrum-results.json.
- widen.md — the widening lane: new weighting families
  (the epsilon form, lexicographic over permuted orders,
  the achievement form, weighted max with varied
  exponents and wide weights, power sums beyond the
  squared family, seeded pseudo-random linear weightings,
  and the centered form counted apart) run over the
  spectrum battery, closing the spectrum record's open
  item of the 28 frontier members no enumerated
  configuration selected: all 28 are selected by the
  enlarged fixed space, each classified exactly by its
  linear and power classes. Its harness is the widen
  file in this repo, with its executed output in the
  widen results files.
