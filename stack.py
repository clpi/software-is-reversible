#!/usr/bin/env python3
"""Built stack -- meta-search solve-and-validate, lane 5 build-out.

One coherent built form of the down-selected winners of lanes
1-4, with a single entry point (this file's main) that runs the
stack end to end on a demonstration workload drawn from the
lanes' own batteries. Re-validation lives in revalidate5.py;
this file is the built form itself.

Composition, top to bottom (the meta level is the
weighting-selection layer over everything below it):

  meta layer (lane 1, meta.py imported, its actual code):
    weighting configurations as candidates; the weight-free
    meta-frontier over the declared measures; a stated
    meta-weighting selects only from the meta-frontier. The
    selected configuration for the stack is the lane 1
    demonstration selection, weighted max (1, 1).
  frontier-first selection (lane 2 proposition 1): the
    weight-free frontier is computed first (block nested
    loops form); selections and weightings act only inside
    it. Weight-first scalarized ranking is not in the stack.
  two-face stop (lane 2 proposition 2): the threshold face
    reports acceptability only; the certification face
    examines every remaining alternative before any
    optimality claim; the faces are reported separately.
  cone-scoped repair (lane 2 proposition 3): incremental
    distance repair that relaxes only edges out of improved
    nodes. Contract: append or weight-decrease epochs only.
  distinct-count worklist (lane 2 proposition 4): least
    closure by a worklist whose missing-premise counts are
    over distinct premises, with a waiter index.
  hybrid break-even rule (lane 2 proposition 5): factored
    form used exactly when the expected query count reaches
    the break-even computed from measured unit costs in the
    full cost form (setup, validation, persistence, restart).
  decoding (lane 3 proposition 1, lane3.py imported): the
    canonical tie-break decoder and the best-first certified
    decoder, the two frontier survivors.
  matrix resolution (lane 3 proposition 2, lane3.py
    imported): incremental cone-scoped readings, with the
    on-the-fly budgeted form for partial-coordinate queries
    (uncovered coordinates are explicit nulls).
  tensor loop (lane 3 proposition 3, lane3.py imported): the
    loop whose every edit is certified by a projection
    recomputed from the pinned base under the full stack.
  action model (lane 4, actions.py imported): the
    combination route -- explicit plan first, one
    verification observation, obscurity construction repairs
    where the residual is above tolerance. The obscurity
    route is retained in actions.py as the fallback member.

Extraction honesty: lane 2's winners existed only as
battery-internal code inside validation-lane2.py (a script
that runs its battery at import), so the five lane 2 forms
below are extracted faithfully from that battery -- same
algorithms, same counted-cost conventions -- and are marked
EXTRACTED at each definition. Lanes 1, 3 and 4 winners are
imported, not copied: their harness modules are importable
and the functions used here are the winners' actual
implementations.

Action-determination spectrum coverage (added specification,
Chris direct 2026-11-20 02:04 PST; the spectrum execution is
lane 6's, this file only records coverage): for each
algorithm in the stack, SPECTRUM below records which of the
five routes its built form covers -- (1) structurally
determined explicitly, (2) through minimization, (3) through
the obscurity vector above threshold, (4) through
decomposition into finer-grain resolution by the
deterministic algorithm on a tensor set, (5) the terminal
native constructed minimum compressed tensor form -- and the
state of each route-equivalence claim. No equivalence is
asserted here: each is marked proved, measured, or
UNMEASURED exactly as the lanes left it.

Steering hold (search.md at baa6f25): no reach-based ranking
orders anything in this stack; the composition order above
is the lanes' executed validation order only.

Stdlib only. Deterministic: seeded generators only.
"""

import itertools
import json
import sys
from collections import defaultdict, deque

import actions
import lane3
import meta

# ------------------------------------------------------------ spectrum

# Route keys: explicit, minimization, obscurity, decomposition,
# terminal. Values: the state of that route's equivalence claim
# for the built form, with the basis in one clause.
SPECTRUM = {
    "meta weighting selection (weighted max (1, 1))": {
        "explicit": "covered -- the configuration is a stated scoring form; equivalence to other routes UNMEASURED",
        "minimization": "covered -- selection is a unique minimiser over the weight-free meta-frontier; equivalence measured on the lane 1 instances only",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "frontier-first selection": {
        "explicit": "covered -- dominance is the stated structural rule; frontier exactness proved in Reversible.lean for the segment family, measured at random scale in lanes 2 and 5",
        "minimization": "covered in part -- weightings minimise inside the frontier only; equivalence of weight-first to frontier-first is REFUTED (measured loss, lanes 2 and 5), not an equivalence",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "two-face stop": {
        "explicit": "covered -- threshold and certification are stated rules; false-claim absence measured in lanes 2 and 5",
        "minimization": "covered in part -- the optimal face certifies the minimum over the stream; equivalence to the threshold face is not claimed (the faces are distinct by construction)",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "cone-scoped repair": {
        "explicit": "covered -- the propagation rule is stated; exactness against from-scratch measured in lanes 2 and 5 under the append / weight-decrease contract",
        "minimization": "covered -- repair follows distance improvements only; equivalence to from-scratch is the measured exactness claim itself",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered in the spectrum sense -- the cone is a premise-cone scope, not a finer-grain tensor decomposition; UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "distinct-count worklist": {
        "explicit": "covered -- the waiter-index rule is stated; its Lean equality form (L-close) is an open lemma, so equivalence to naive closure is measured (lanes 2 and 5), not proved",
        "minimization": "not applicable as stated -- UNMEASURED, lane 6",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "hybrid break-even rule": {
        "explicit": "covered -- the rule is a stated comparison of measured unit costs in full cost form; the break-even theorem is proved in this repo, its empirical crossover measured in lanes 2 and 5",
        "minimization": "covered -- the rule selects the total-cost minimum of the dense and factored forms per regime; equivalence claim is the measured crossover agreement",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "covered in part -- the factored form is a per-stage decomposition of the joint plan set; equivalence to the dense form is measured (same answers, counted costs), the spectrum's finer-grain tensor sense is UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "canonical tie-break decoding": {
        "explicit": "covered -- the tie-break is a stated canonical order; permutation invariance measured in lanes 3 and 5",
        "minimization": "not covered as a route -- canonical decoding is greedy under the tie-break and its gap to the optimum is measured (the trap fixture), so equivalence to best-first is REFUTED on the gap axis",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "best-first certified decoding": {
        "explicit": "covered -- the search and certificate rules are stated; certificate soundness measured against the exhaustive oracle in lanes 3 and 5",
        "minimization": "covered -- best-first is minimisation over complete-sequence totals with a heap-maximum certificate; equivalence to the oracle is measured per fixture",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "incremental matrix resolution": {
        "explicit": "covered -- the append rule is stated; equality to full recomputation measured in lanes 3 and 5",
        "minimization": "not applicable as stated -- UNMEASURED, lane 6",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "covered in part -- readings decompose per coordinate and per record; equivalence to the full form is the measured equality claim",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "on-the-fly budgeted resolution": {
        "explicit": "covered -- the covered-coordinate set is stated; covered readings equal full exactly, measured in lanes 3 and 5; uncovered coordinates are nulls, never placeholders",
        "minimization": "not applicable as stated -- UNMEASURED, lane 6",
        "obscurity": "not covered -- UNMEASURED, lane 6",
        "decomposition": "covered in part -- per-coordinate decomposition, as above; the tensor-set sense is UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
    "tensor loop with recomputed-projection certification": {
        "explicit": "covered -- the edit and certification rules are stated; certification is by recomputation, measured in lanes 3 and 5",
        "minimization": "not covered as a route -- UNMEASURED, lane 6",
        "obscurity": "covered in part -- the loop's edit rules include the obscurity-named clause of lane 3; route equivalence to the explicit clause is UNMEASURED, lane 6",
        "decomposition": "covered in part -- the overlay stack decomposes the weighting into appended edits over a pinned base; equivalence of the incremental copy to the recomputed projection is measured at every edit",
        "terminal": "not covered -- the overlay stack is not claimed to be the minimum compressed tensor form; UNMEASURED, lane 6",
    },
    "action combination route": {
        "explicit": "covered -- route 3's first leg is the explicit planner of actions.py; measured in lanes 4 and 5",
        "minimization": "covered in part -- the repair leg keeps the least-residual probed candidate; equivalence to the obscurity route is measured on success (frontier tie in lane 4, near-tie in lane 5) and refuted on probe cost (combination cheaper), so the routes are not equivalent as costed forms",
        "obscurity": "covered -- route 3's repair leg is the obscurity construction of actions.py above its residual tolerance, and route 2 stands in actions.py as the retained fallback member; equivalence measured as above",
        "decomposition": "not covered -- UNMEASURED, lane 6",
        "terminal": "not covered -- UNMEASURED, lane 6",
    },
}

# ------------------------------------------------- meta layer (lane 1)
# Imported from meta.py: configurations, frontier_of, induced,
# and the meta-frontier computation pattern of its main. The
# stack's weighting-selection layer is this function.


def select_weighting_configuration():
    """Run the lane 1 meta level: enumerate the configuration
    space, compute each configuration's measure vector over
    the three instances, compute the weight-free meta-frontier,
    and apply the demonstration meta-weighting (4, 2, 1, 1)
    restricted to the meta-frontier. Returns the selected
    configuration's (family, params)."""
    fronts = [meta.frontier_of(cands)
              for _n, cands, _m in meta.INSTANCES]
    rows = []
    for family, params in meta.configurations():
        tie_excess = 0
        miss = 0
        for idx, front in enumerate(fronts):
            pick, winners = meta.induced(family, params, front)
            tie_excess += len(winners) - 1
            if pick != meta.INSTANCES[idx][2]:
                miss += 1
        measures = (miss, tie_excess,
                    meta.simplicity(family, params),
                    meta.FAMILY_RANK[family])
        rows.append((family, params, measures))

    def meta_dominates(a, b):
        return (all(x <= y for x, y in zip(a, b))
                and any(x < y for x, y in zip(a, b)))

    meta_front = [r for r in rows
                  if not any(meta_dominates(o[2], r[2])
                             for o in rows if o is not r)]
    weights = (4, 2, 1, 1)
    scored = [(sum(w * m for w, m in zip(weights, r[2])), r)
              for r in meta_front]
    best = min(s for s, _r in scored)
    winners = [r for s, r in scored if s == best]
    assert len(winners) == 1 and winners[0] in meta_front
    family, params, _measures = winners[0]
    return family, params, len(rows), len(meta_front)


# --------------------------------------- frontier-first (lane 2 P1)
# EXTRACTED faithfully from validation-lane2.py (frontier_bnl,
# frontier_incremental, and the weight_pick selection restricted
# to the frontier).


def _dominates(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


def frontier_first(points):
    """The weight-free frontier, block nested loops form."""
    win = []
    for p in points:
        if any(_dominates(w, p) for w in win):
            continue
        win = [w for w in win if not _dominates(p, w)]
        win.append(p)
    return sorted(set(win))


def select_within_frontier(points, weights):
    """A weighting selects only inside the frontier."""
    front = frontier_first(points)
    return min(front, key=lambda p: (weights[0] * p[0]
                                     + weights[1] * p[1], p))


# -------------------------------------------- two-face stop (lane 2 P2)
# EXTRACTED faithfully from validation-lane2.py run_p2's twoface
# candidate: threshold face for acceptability, full examination
# with certification for the optimality claim, faces separate.


def two_face_stop(stream, threshold):
    """Returns (acceptable, optimal, examined_for_optimal).
    acceptable is the first stream member at or below the
    threshold, or None; optimal is the certified minimum over
    the whole stream. The acceptable face makes no optimality
    claim; the optimal face is certified by full examination."""
    acceptable = None
    for x in stream:
        if x <= threshold:
            acceptable = x
            break
    optimal = min(stream) if stream else None
    return acceptable, optimal, len(stream)


# ----------------------------------------- cone-scoped repair (lane 2 P3)
# EXTRACTED faithfully from validation-lane2.py run_p3's
# incremental candidate. Contract: append or weight-decrease
# epochs only.


def cone_scoped_repair(distances_before, out_edges, changed):
    """Propagate only from the changed edges' heads, relaxing
    only edges out of improved nodes. out_edges maps a node to
    its (tail, head, weight) edges. Returns (distances,
    relaxations)."""
    d = list(distances_before)
    relax = 0
    q = deque()
    for (u, v, w) in changed:
        relax += 1
        if d[u] + w < d[v]:
            d[v] = d[u] + w
            q.append(v)
    while q:
        x = q.popleft()
        for (u, v, w) in out_edges.get(x, []):
            relax += 1
            if d[u] + w < d[v]:
                d[v] = d[u] + w
                q.append(v)
    return d, relax


# ----------------------------------- distinct-count worklist (lane 2 P4)
# EXTRACTED faithfully from validation-lane2.py's worklist
# candidate: distinct missing-premise counts, waiter index.


def distinct_count_worklist(rules, seeds=()):
    """Least closure of rules (premise list, head) from seeds.
    Returns (derived, checks). Premise duplicates count once:
    the missing set is a set, per the canonical semantics."""
    derived = set(seeds)
    missing = []
    waiters = defaultdict(list)
    for idx, (pre, head) in enumerate(rules):
        miss = set(pre) - derived
        missing.append(set(miss))
        for p in miss:
            waiters[p].append(idx)
    q = deque(seeds)
    checks = 0
    for idx, (pre, head) in enumerate(rules):
        if not missing[idx] and head not in derived:
            derived.add(head)
            q.append(head)
    processed = set(seeds)
    while q:
        x = q.popleft()
        processed.add(x)
        for idx in waiters.get(x, []):
            checks += 1
            if x in missing[idx]:
                missing[idx].discard(x)
                if not missing[idx]:
                    head = rules[idx][1]
                    if head not in derived:
                        derived.add(head)
                        q.append(head)
    return derived, checks


# -------------------------------------- hybrid break-even rule (lane 2 P5)
# EXTRACTED faithfully from validation-lane2.py run_p5's cost
# accounting: factored per-stage pools against dense
# materialization, fixed cost in full form.


def hybrid_choice(stages, per, expected_queries, sample_queries):
    """Compounding family: `stages` stages of `per` witnesses.
    Measures dense and factored per-query counted operations
    on sample_queries (deterministic targets), computes the
    full fixed cost (setup + validation against the dense
    oracle + persistence at 8 bytes per operation + restart),
    predicts the break-even, and returns the form the hybrid
    rule selects for expected_queries with its accounting."""
    pools = [[f"s{i}w{j}" for j in range(per)] for i in range(stages)]
    dense = list(itertools.product(*pools))

    def dense_query(target):
        ops = 0
        for row in dense:
            ops += 1
            if tuple(int(x[-1]) for x in row) == target:
                return ops
        return ops

    def factored_query(target):
        ops = 0
        for i, t in enumerate(target):
            for j, _w in enumerate(pools[i]):
                ops += 1
                if j == t:
                    break
        return ops

    dense_per = sum(dense_query(q) for q in sample_queries) \
        / len(sample_queries)
    factored_per = sum(factored_query(q) for q in sample_queries) \
        / len(sample_queries)
    setup = sum(len(p) for p in pools)
    validation = sum(dense_query(q) + factored_query(q)
                     for q in sample_queries[:16])
    persistence = len(json.dumps(pools).encode()) // 8
    restart = setup
    fixed = setup + validation + persistence + restart
    import math
    predicted = math.ceil(fixed / max(1.0, dense_per - factored_per)) \
        if dense_per > factored_per else None
    use_factored = predicted is not None \
        and expected_queries >= predicted
    return {
        "form": "factored" if use_factored else "dense",
        "rows": len(dense),
        "dense_per_query": round(dense_per, 2),
        "factored_per_query": round(factored_per, 2),
        "fixed_full_cost": fixed,
        "predicted_break_even_q": predicted,
    }


# --------------------------------------------- demonstration workload

def main():
    out = {}
    # Meta layer selects the weighting configuration.
    family, params, n_configs, n_meta_front = \
        select_weighting_configuration()
    out["meta_layer"] = {
        "configurations": n_configs,
        "meta_frontier": n_meta_front,
        "selected": "%s %s" % (family, params),
        "selected_label": meta.label(family, params),
    }
    # Frontier-first on a lane 2 battery-style point set.
    points = [(0, 10), (6, 6), (10, 0), (7, 8), (3, 4), (12, 3)]
    out["frontier_first"] = {
        "frontier": frontier_first(points),
        "selection_under_selected_configuration":
            select_within_frontier(points, (1, 1)),
    }
    # Two-face stop on a lane 2 battery-style stream.
    acc, opt, examined = two_face_stop([9, 5, 2, 7], 10)
    out["two_face_stop"] = {"acceptable": acc, "optimal": opt,
                            "examined_for_optimal": examined}
    # Cone-scoped repair: one append epoch on a small DAG.
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 1), (1, 3, 2), (2, 3, 9)]
    out_edges = defaultdict(list)
    for e in edges:
        out_edges[e[0]].append(e)
    before = [0, 2, 1, 4]
    changed = [(2, 3, 3)]
    after, relax = cone_scoped_repair(before, out_edges, changed)
    out["cone_scoped_repair"] = {"distances": after,
                                 "relaxations": relax}
    # Distinct-count worklist on rules with a duplicated premise.
    rules = [([0, 0, 1], 2), ([2], 3), ([3, 1], 4), ([], 0), ([0], 1)]
    derived, checks = distinct_count_worklist(rules)
    out["distinct_count_worklist"] = {"derived": sorted(derived),
                                      "checks": checks}
    # Hybrid rule on the compounding family, small regime.
    import random
    rng = random.Random(71050)
    sample = [tuple(rng.randrange(3) for _ in range(4))
              for _ in range(32)]
    out["hybrid_break_even"] = hybrid_choice(4, 3, 64, sample)
    # Decoding: both frontier survivors on the lane 3 fixtures.
    out["decoding"] = {
        fid: {
            "canonical": lane3.decode_canonical(fid),
            "bestfirst": lane3.decode_bestfirst(fid),
            "oracle": lane3.exhaustive_optimum(fid),
        } for fid in lane3.FIXTURES
    }
    # Matrix resolution: incremental over a lane 3 dataset.
    recs = lane3.make_records(321, 64, "d1")
    mres = lane3.run_matrix_dataset(recs, 64, {10, 150, 321})
    out["matrix_resolution"] = {
        "checkpoints": mres["checkpoints"], "equal": mres["equal"],
        "incremental_work": mres["incr_work"],
        "full_work": mres["full_work"],
    }
    # Tensor loop with recomputed-projection certification.
    loop = lane3.run_loop()
    out["tensor_loop"] = {
        "stream": loop["stream"], "edits": loop["edits"],
        "certification": "%d/%d" % (loop["cert_ok"],
                                    loop["cert_checks"]),
        "protected": loop["protected_ok"],
        "roundtrip": loop["roundtrip_ok"],
    }
    # Action model: the combination route on one instance per
    # family (seed drawn from the lane 5 demonstration range).
    act = {}
    for fi, (fname, _label, make, run, _r) in \
            enumerate(actions.FAMILIES):
        rng = random.Random(71060 + fi)
        inst = make(rng)
        if fname == "drive":
            ok, comp, probes, repaired, _s = actions.drive_run(
                "combination", inst)
        else:
            ok, comp, probes, repaired = run("combination", inst)
        act[fname] = {"success": ok, "component": comp,
                      "probes": probes, "repaired": repaired}
    out["action_combination"] = act
    print(json.dumps(out, indent=1, sort_keys=True))
    ok = (
        out["meta_layer"]["selected"] == "max (1, 1)"
        and out["frontier_first"]["frontier"] == [(0, 10), (3, 4),
                                                  (10, 0)]
        and out["two_face_stop"]["optimal"] == 2
        and out["cone_scoped_repair"]["distances"] == [0, 2, 1, 4]
        and out["distinct_count_worklist"]["derived"] == [0, 1, 2, 3, 4]
        and out["decoding"]["trap"]["bestfirst"]["total"] == -400
        and out["matrix_resolution"]["equal"] == 3
        and out["tensor_loop"]["certification"] == "4/4"
    )
    print("stack verdict: %s" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
