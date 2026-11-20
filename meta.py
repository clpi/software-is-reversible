#!/usr/bin/env python3
"""Meta-search harness: search over weightings themselves.

Lane 1 of the meta-search solve-and-validate program
(Chris, direct, 2026-11-20 01:56 PST). Spec: meta.md in this
repo. Style and scope discipline follow validate.py.

What this harness does, exactly:
  (a) enumerates a finite weighting-configuration space over
      five families (linear, squared, weighted max, the two
      lexicographic orders, and a balance overlay on a linear
      base);
  (b) computes each configuration's induced selection on each
      instance, where the selection domain is the weight-free
      Pareto frontier of the instance, computed first;
  (c) identifies the configurations that uniquely select a
      frontier member that no hand-set weighting in the
      current record selects (the middle member of each
      instance: on the frontier, selected by no positive
      linear weighting -- proved in Reversible.lean, section
      A, for the two plan scales);
  (d) treats the configurations themselves as candidates:
      computes each configuration's measure vector, computes
      the meta-frontier weight-free, and only then applies
      one stated meta-weighting, restricted to the
      meta-frontier, as a demonstration selection.

Instances. Three, all lower-is-better on both axes.
  - Frontier selection, scale one: the plans (0, 10), (6, 6),
    (10, 0) of Reversible.lean section A.
  - Frontier selection, scale two: the plans (0, 20),
    (11, 11), (20, 0) of the same section.
  - Deterministic decoding (a harness fixture, stated as
    such): continuations read on two axes, model cost and
    adequacy cost. The empty continuation (0, 10), the
    balanced continuation (6, 6), the verbose continuation
    (10, 0), plus two dominated continuations, padded (7, 8)
    and rambling (12, 3), which the frontier computation
    must exclude before any weighting runs. The fixture's
    geometry is the plan geometry of section A read as a
    decoding row (search.md, deterministic decoding row);
    it is a fixture of this harness, not a measurement of
    any decoder system, and the record says so wherever its
    results are cited.

Hand-set weightings in the current record, enumerated as
the baseline the meta level is compared against:
  - every positive linear weighting on the grid 1..9 by 1..9
    (the class the Lean counterexample covers, all weights);
  - the threshold rule: the first listed candidate whose
    coordinates both meet the threshold 10 (the acceptable
    face of the stop rule, census section 1);
  - the constant weighting (every score equal; the ranking
    head control of census section 7).

Ties. A configuration selects a member only when that member
is the unique minimiser on the frontier. A tie is recorded
as a tie, never resolved by a hidden tie-break to manufacture
a selection.

Meta measures, all lower-is-better, all declared here before
any run (meta.md states them as the meta level's axes):
  - miss: of the three instances, how many the configuration
    does not uniquely select the middle member of;
  - tie excess: summed over instances, minimisers minus one;
  - simplicity: the sum of the configuration's numeric
    parameters (a lexicographic order carries none);
  - family rank: a declared reading of family complexity --
    linear 1, lexicographic 2, balance overlay 3, weighted
    max 3, squared 4. Declared, not measured: it is an axis
    of the meta space as specified, and the meta-frontier is
    computed over exactly these four axes.

Recursion discipline (meta.md states it in full): the meta
frontier is computed weight-free, and the one demonstration
meta-weighting selects only from it. The recursion bottoms
out at this level because the reachability claim is an
existence claim discharged by exhibiting and running one
configuration, not an optimality claim under a weighting;
no level of linear weighting over the level below can add
the unreachable member, which is the proved counterexample.

Stdlib only. Deterministic: no clocks, no randomness.
"""

import sys


# ------------------------------------------------------------ instances

# Each candidate: (name, axis one, axis two). Lower is better.
INSTANCES = [
    ("frontier selection scale one",
     [("plan a", 0, 10), ("plan b", 6, 6), ("plan c", 10, 0)],
     "plan b"),
    ("frontier selection scale two",
     [("plan a2", 0, 20), ("plan b2", 11, 11), ("plan c2", 20, 0)],
     "plan b2"),
    ("deterministic decoding fixture",
     [("empty", 0, 10), ("balanced", 6, 6), ("verbose", 10, 0),
      ("padded", 7, 8), ("rambling", 12, 3)],
     "balanced"),
]


def dominates(p, q):
    """p dominates q: no worse on either axis, better on one."""
    return p[1] <= q[1] and p[2] <= q[2] and (p[1] < q[1] or p[2] < q[2])


def frontier_of(candidates):
    """The weight-free Pareto frontier, computed first."""
    return [c for c in candidates
            if not any(dominates(d, c) for d in candidates if d is not c)]


# ------------------------------------------------------------ scoring

def score(family, params, point):
    x, y = point[1], point[2]
    if family == "linear":
        return params[0] * x + params[1] * y
    if family == "squared":
        return params[0] * x * x + params[1] * y * y
    if family == "max":
        return max(params[0] * x, params[1] * y)
    if family == "lex":
        return (x, y) if params == ("first",) else (y, x)
    if family == "overlay":
        return x + y + params[0] * abs(x - y)
    raise ValueError("unknown family %r" % (family,))


FAMILY_RANK = {"linear": 1, "lex": 2, "overlay": 3, "max": 3,
               "squared": 4}


def configurations():
    """The enumerated meta-search space: 39 configurations."""
    out = []
    for w1 in range(1, 5):
        for w2 in range(1, 5):
            out.append(("linear", (w1, w2)))
    for w1 in range(1, 4):
        for w2 in range(1, 4):
            out.append(("squared", (w1, w2)))
    for w1 in range(1, 4):
        for w2 in range(1, 4):
            out.append(("max", (w1, w2)))
    out.append(("lex", ("first",)))
    out.append(("lex", ("second",)))
    for k in range(1, 4):
        out.append(("overlay", (k,)))
    return out


def simplicity(family, params):
    if family == "lex":
        return 0
    if family == "overlay":
        return 2 + params[0]  # the linear base (1, 1) plus k
    return params[0] + params[1]


def label(family, params):
    if family == "lex":
        return "lex %s axis first" % (params[0],)
    if family == "overlay":
        return "overlay balance k=%d on linear (1, 1)" % (params[0],)
    return "%s weights (%d, %d)" % (family, params[0], params[1])


def induced(family, params, front):
    """The induced selection on one frontier: the unique
    minimiser's name, or None with the tied names when the
    minimum is shared."""
    scored = [(score(family, params, c), c[0]) for c in front]
    best = min(s for s, _ in scored)
    winners = sorted(n for s, n in scored if s == best)
    if len(winners) == 1:
        return winners[0], winners
    return None, winners


# ------------------------------------------------------------ hand set

def hand_selections(fronts):
    """Selections of the hand-set weightings in the record,
    per instance: (set of uniquely selected names, notes)."""
    selected = [set() for _ in fronts]
    notes = []
    # Positive linear weightings on the grid 1..9 by 1..9.
    for idx, front in enumerate(fronts):
        for w1 in range(1, 10):
            for w2 in range(1, 10):
                pick, _ = induced("linear", (w1, w2), front)
                if pick is not None:
                    selected[idx].add(pick)
    notes.append("linear grid 1..9 by 1..9: unique selections "
                 "recorded per instance below")
    # Threshold rule, threshold 10 on both axes, first listed.
    for idx, (name, cands, _mid) in enumerate(INSTANCES):
        front_names = [c[0] for c in fronts[idx]]
        pick = None
        for c in cands:
            if c[0] in front_names and c[1] <= 10 and c[2] <= 10:
                pick = c[0]
                break
        if pick is not None:
            selected[idx].add(pick)
        notes.append("threshold rule on %s: %s"
                     % (name, pick if pick else "no candidate "
                        "meets the threshold"))
    # Constant weighting: a tie over the whole frontier.
    notes.append("constant weighting: tie over every frontier, "
                 "selects nothing uniquely")
    return selected, notes


# ------------------------------------------------------------ main

def main():
    fronts = [frontier_of(cands) for _n, cands, _m in INSTANCES]

    print("meta-search harness -- lane 1, meta level over weightings")
    print("scope: the three stated instances only; the decoding "
          "instance is a harness fixture, not a decoder measurement")
    print("rule: frontier first, weight-free, at both levels; a "
          "weighting selects only from the frontier beneath it")
    print("")

    for (name, cands, _mid), front in zip(INSTANCES, fronts):
        print("instance: %s" % name)
        print("  candidates: %s"
              % ", ".join("%s (%d, %d)" % c for c in cands))
        print("  frontier (weight-free): %s"
              % ", ".join("%s (%d, %d)" % c for c in front))
        excluded = [c[0] for c in cands if c not in front]
        if excluded:
            print("  excluded as dominated, before any weighting: %s"
                  % ", ".join(excluded))
    print("")

    hand, notes = hand_selections(fronts)
    print("hand-set weightings in the current record:")
    for note in notes:
        print("  %s" % note)
    for (name, _c, mid), sel in zip(INSTANCES, hand):
        print("  %s: hand selections %s; middle member %s hand-selected: %s"
              % (name, sorted(sel), mid,
                 "yes" if mid in sel else "no"))
    print("")

    configs = configurations()
    print("meta-search space: %d configurations "
          "(linear 16, squared 9, max 9, lex 2, overlay 3)"
          % len(configs))
    print("")
    header = ("%-38s %-22s %-22s %-22s %s"
              % ("configuration", "scale one", "scale two",
                 "decoding fixture", "measures (miss, tie, simp, rank)"))
    print(header)
    rows = []
    for family, params in configs:
        picks = []
        tie_excess = 0
        miss = 0
        for idx, front in enumerate(fronts):
            pick, winners = induced(family, params, front)
            picks.append(pick if pick else "tie " + "/".join(winners))
            tie_excess += len(winners) - 1
            if pick != INSTANCES[idx][2]:
                miss += 1
        measures = (miss, tie_excess, simplicity(family, params),
                    FAMILY_RANK[family])
        rows.append((family, params, picks, measures))
        print("%-38s %-22s %-22s %-22s %s"
              % (label(family, params), picks[0], picks[1],
                 picks[2], measures))
    print("")

    reach = [r for r in rows if r[3][0] == 0]
    print("configurations selecting the middle member on all "
          "three instances (miss = 0): %d" % len(reach))
    for family, params, picks, _m in reach:
        print("  %s -> %s" % (label(family, params), ", ".join(picks)))
    partial = [r for r in rows if 0 < r[3][0] < 3]
    print("configurations selecting a middle member on some but "
          "not all instances: %d" % len(partial))
    for family, params, picks, measures in partial:
        got = [INSTANCES[i][2] for i in range(3)
               if picks[i] == INSTANCES[i][2]]
        if got:
            print("  %s -> middle on: %s"
                  % (label(family, params), ", ".join(got)))
    print("")

    # The meta level: configurations as candidates, their
    # frontier computed weight-free over the declared measures.
    def meta_dominates(a, b):
        return (all(x <= y for x, y in zip(a, b))
                and any(x < y for x, y in zip(a, b)))

    meta_front = [r for r in rows
                  if not any(meta_dominates(o[3], r[3])
                             for o in rows if o is not r)]
    print("meta-frontier (weight-free, over the declared "
          "measures): %d of %d configurations" % (len(meta_front),
                                                  len(rows)))
    for family, params, picks, measures in meta_front:
        print("  %s measures %s -> %s"
              % (label(family, params), measures, ", ".join(picks)))
    print("")

    # One stated meta-weighting, applied only after the meta
    # frontier exists and only to its members.
    weights = (4, 2, 1, 1)
    print("demonstration meta-weighting %s over (miss, tie, "
          "simp, rank), restricted to the meta-frontier:" % (weights,))
    scored = [(sum(w * m for w, m in zip(weights, r[3])), r)
              for r in meta_front]
    best = min(s for s, _r in scored)
    winners = [r for s, r in scored if s == best]
    for family, params, picks, measures in winners:
        print("  selected: %s measures %s -> %s"
              % (label(family, params), measures, ", ".join(picks)))
    assert all(r in meta_front for r in winners)
    print("  check: every meta-weighted selection is a "
          "meta-frontier member: yes")
    print("")

    # Controls.
    failures = []
    # Control 1: the finite grid check of the proved class --
    # no positive linear weighting on the grid selects a
    # middle member. (A grid check, not the proof; the proof
    # is Reversible.lean section A, over all weights.)
    for idx, front in enumerate(fronts):
        for w1 in range(1, 10):
            for w2 in range(1, 10):
                pick, _w = induced("linear", (w1, w2), front)
                if pick == INSTANCES[idx][2]:
                    failures.append("linear (%d, %d) selected the "
                                    "middle member of %s"
                                    % (w1, w2, INSTANCES[idx][0]))
    print("control, linear grid: no positive linear weighting "
          "on 1..9 by 1..9 selects any middle member: %s"
          % ("yes" if not failures else "NO"))
    # Control 2: frontier restriction -- no configuration's
    # selection domain contains a dominated candidate, and
    # the dominated decoding continuations are never selected.
    dominated = {"padded", "rambling"}
    bad = [label(f, p) for f, p, picks, _m in rows
           if any(pk in dominated for pk in picks)]
    if bad:
        failures.append("dominated candidate selected by: %s" % bad)
    print("control, frontier restriction: dominated decoding "
          "continuations selected by no configuration: %s"
          % ("yes" if not bad else "NO"))
    # Control 3: at least one meta-found configuration exists,
    # or the reachability claim fails loudly here.
    if not reach:
        failures.append("no configuration reached a middle member")
    print("control, reachability: at least one enumerated "
          "configuration selects every middle member: %s"
          % ("yes" if reach else "NO"))
    print("")
    if failures:
        print("harness verdict: FAIL -- " + "; ".join(failures))
        return 1
    print("harness verdict: OK -- frontier computed first at "
          "both levels; %d configurations select frontier "
          "members no hand-set weighting in the record selects; "
          "the demonstration meta-weighting selected only from "
          "the meta-frontier" % len(reach))
    return 0


if __name__ == "__main__":
    sys.exit(main())
