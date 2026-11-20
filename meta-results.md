# Meta-search first pass — harness results

Harness: meta.py in this repo (Python, stdlib only)
Run command: python3 meta.py
Base pin: d05ff699511099e6b4b28b2ae50e5c7cd590507e (master, before this lane's append)
Exit code: 0. Output is deterministic (two consecutive runs byte-identical).
Spec: meta.md in this repo.

## Scope honesty

The frontier selection instances are the proved plan triples of Reversible.lean section A. The deterministic decoding instance is a harness fixture with the same geometry, stated as a fixture in meta.md: it is not a measurement of any decoder system, and no result here is a claim about a live decoder, a live desktop, or any incumbent system.

## Exact run output

```
meta-search harness -- lane 1, meta level over weightings
scope: the three stated instances only; the decoding instance is a harness fixture, not a decoder measurement
rule: frontier first, weight-free, at both levels; a weighting selects only from the frontier beneath it

instance: frontier selection scale one
  candidates: plan a (0, 10), plan b (6, 6), plan c (10, 0)
  frontier (weight-free): plan a (0, 10), plan b (6, 6), plan c (10, 0)
instance: frontier selection scale two
  candidates: plan a2 (0, 20), plan b2 (11, 11), plan c2 (20, 0)
  frontier (weight-free): plan a2 (0, 20), plan b2 (11, 11), plan c2 (20, 0)
instance: deterministic decoding fixture
  candidates: empty (0, 10), balanced (6, 6), verbose (10, 0), padded (7, 8), rambling (12, 3)
  frontier (weight-free): empty (0, 10), balanced (6, 6), verbose (10, 0)
  excluded as dominated, before any weighting: padded, rambling

hand-set weightings in the current record:
  linear grid 1..9 by 1..9: unique selections recorded per instance below
  threshold rule on frontier selection scale one: plan a
  threshold rule on frontier selection scale two: no candidate meets the threshold
  threshold rule on deterministic decoding fixture: empty
  constant weighting: tie over every frontier, selects nothing uniquely
  frontier selection scale one: hand selections ['plan a', 'plan c']; middle member plan b hand-selected: no
  frontier selection scale two: hand selections ['plan a2', 'plan c2']; middle member plan b2 hand-selected: no
  deterministic decoding fixture: hand selections ['empty', 'verbose']; middle member balanced hand-selected: no

meta-search space: 39 configurations (linear 16, squared 9, max 9, lex 2, overlay 3)

configuration                          scale one              scale two              decoding fixture       measures (miss, tie, simp, rank)
linear weights (1, 1)                  tie plan a/plan c      tie plan a2/plan c2    tie empty/verbose      (3, 3, 2, 1)
linear weights (1, 2)                  plan c                 plan c2                verbose                (3, 0, 3, 1)
linear weights (1, 3)                  plan c                 plan c2                verbose                (3, 0, 4, 1)
linear weights (1, 4)                  plan c                 plan c2                verbose                (3, 0, 5, 1)
linear weights (2, 1)                  plan a                 plan a2                empty                  (3, 0, 3, 1)
linear weights (2, 2)                  tie plan a/plan c      tie plan a2/plan c2    tie empty/verbose      (3, 3, 4, 1)
linear weights (2, 3)                  plan c                 plan c2                verbose                (3, 0, 5, 1)
linear weights (2, 4)                  plan c                 plan c2                verbose                (3, 0, 6, 1)
linear weights (3, 1)                  plan a                 plan a2                empty                  (3, 0, 4, 1)
linear weights (3, 2)                  plan a                 plan a2                empty                  (3, 0, 5, 1)
linear weights (3, 3)                  tie plan a/plan c      tie plan a2/plan c2    tie empty/verbose      (3, 3, 6, 1)
linear weights (3, 4)                  plan c                 plan c2                verbose                (3, 0, 7, 1)
linear weights (4, 1)                  plan a                 plan a2                empty                  (3, 0, 5, 1)
linear weights (4, 2)                  plan a                 plan a2                empty                  (3, 0, 6, 1)
linear weights (4, 3)                  plan a                 plan a2                empty                  (3, 0, 7, 1)
linear weights (4, 4)                  tie plan a/plan c      tie plan a2/plan c2    tie empty/verbose      (3, 3, 8, 1)
squared weights (1, 1)                 plan b                 plan b2                balanced               (0, 0, 2, 4)
squared weights (1, 2)                 plan c                 plan b2                verbose                (2, 0, 3, 4)
squared weights (1, 3)                 plan c                 plan c2                verbose                (3, 0, 4, 4)
squared weights (2, 1)                 plan a                 plan b2                empty                  (2, 0, 3, 4)
squared weights (2, 2)                 plan b                 plan b2                balanced               (0, 0, 4, 4)
squared weights (2, 3)                 plan b                 plan b2                balanced               (0, 0, 5, 4)
squared weights (3, 1)                 plan a                 plan a2                empty                  (3, 0, 4, 4)
squared weights (3, 2)                 plan b                 plan b2                balanced               (0, 0, 5, 4)
squared weights (3, 3)                 plan b                 plan b2                balanced               (0, 0, 6, 4)
max weights (1, 1)                     plan b                 plan b2                balanced               (0, 0, 2, 3)
max weights (1, 2)                     plan c                 plan c2                verbose                (3, 0, 3, 3)
max weights (1, 3)                     plan c                 plan c2                verbose                (3, 0, 4, 3)
max weights (2, 1)                     plan a                 plan a2                empty                  (3, 0, 3, 3)
max weights (2, 2)                     plan b                 plan b2                balanced               (0, 0, 4, 3)
max weights (2, 3)                     plan b                 plan b2                balanced               (0, 0, 5, 3)
max weights (3, 1)                     plan a                 plan a2                empty                  (3, 0, 4, 3)
max weights (3, 2)                     plan b                 plan b2                balanced               (0, 0, 5, 3)
max weights (3, 3)                     plan b                 plan b2                balanced               (0, 0, 6, 3)
lex first axis first                   plan a                 plan a2                empty                  (3, 0, 0, 2)
lex second axis first                  plan c                 plan c2                verbose                (3, 0, 0, 2)
overlay balance k=1 on linear (1, 1)   plan b                 plan b2                balanced               (0, 0, 3, 3)
overlay balance k=2 on linear (1, 1)   plan b                 plan b2                balanced               (0, 0, 4, 3)
overlay balance k=3 on linear (1, 1)   plan b                 plan b2                balanced               (0, 0, 5, 3)

configurations selecting the middle member on all three instances (miss = 0): 13
  squared weights (1, 1) -> plan b, plan b2, balanced
  squared weights (2, 2) -> plan b, plan b2, balanced
  squared weights (2, 3) -> plan b, plan b2, balanced
  squared weights (3, 2) -> plan b, plan b2, balanced
  squared weights (3, 3) -> plan b, plan b2, balanced
  max weights (1, 1) -> plan b, plan b2, balanced
  max weights (2, 2) -> plan b, plan b2, balanced
  max weights (2, 3) -> plan b, plan b2, balanced
  max weights (3, 2) -> plan b, plan b2, balanced
  max weights (3, 3) -> plan b, plan b2, balanced
  overlay balance k=1 on linear (1, 1) -> plan b, plan b2, balanced
  overlay balance k=2 on linear (1, 1) -> plan b, plan b2, balanced
  overlay balance k=3 on linear (1, 1) -> plan b, plan b2, balanced
configurations selecting a middle member on some but not all instances: 2
  squared weights (1, 2) -> middle on: plan b2
  squared weights (2, 1) -> middle on: plan b2

meta-frontier (weight-free, over the declared measures): 6 of 39 configurations
  linear weights (1, 1) measures (3, 3, 2, 1) -> tie plan a/plan c, tie plan a2/plan c2, tie empty/verbose
  linear weights (1, 2) measures (3, 0, 3, 1) -> plan c, plan c2, verbose
  linear weights (2, 1) measures (3, 0, 3, 1) -> plan a, plan a2, empty
  max weights (1, 1) measures (0, 0, 2, 3) -> plan b, plan b2, balanced
  lex first axis first measures (3, 0, 0, 2) -> plan a, plan a2, empty
  lex second axis first measures (3, 0, 0, 2) -> plan c, plan c2, verbose

demonstration meta-weighting (4, 2, 1, 1) over (miss, tie, simp, rank), restricted to the meta-frontier:
  selected: max weights (1, 1) measures (0, 0, 2, 3) -> plan b, plan b2, balanced
  check: every meta-weighted selection is a meta-frontier member: yes

control, linear grid: no positive linear weighting on 1..9 by 1..9 selects any middle member: yes
control, frontier restriction: dominated decoding continuations selected by no configuration: yes
control, reachability: at least one enumerated configuration selects every middle member: yes

harness verdict: OK -- frontier computed first at both levels; 13 configurations select frontier members no hand-set weighting in the record selects; the demonstration meta-weighting selected only from the meta-frontier
```
