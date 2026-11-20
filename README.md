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
