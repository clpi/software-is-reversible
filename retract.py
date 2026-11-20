#!/usr/bin/env python3
"""Lane 2 follow-on battery: retraction repair and wall-clock forms.

Closes the open remainder named in validation-lane2.md and
lane5.md: epochs with weight increases or withdrawals
(retraction repair) in proposition 3, and wall-clock forms of
propositions 3 and 4. Same contracts as the selecting
battery; counted operation units are the primary contract
exactly as in validation-lane2.py, and wall time is measured
under the discipline stated below.

Held-out seeds, disjoint from every prior lane (lane 2 used
the 2000-6000 series, lane 5 used 71000-79999): retraction
battery 81000, timing repair workload 82000, timing closure
workload 83000. The retraction battery is also the timing
workload for its own arms.

Retraction repair, constructed form: a weight increase or a
withdrawal can only raise distances, and only along shortest
paths that used the retracted edge. The repair state is the
before distances. An edge is tight when its tail distance
plus its weight equals its head distance; shortest paths run
over tight edges only. The cone is every node reachable from
the retracted head over tight edges of the before graph. A
cone node is hit when every tight edge into it is the
retracted edge itself or comes from a hit node (decided in
node order, which is the topological order of these graphs).
Hit nodes are reset and rederived in node order from the
after graph: every predecessor has a smaller index, so one
pass gives exact distances. Nodes outside the hit set keep a
shortest path that never used the retracted edge, so their
distances stand. Counted unit: one relaxation is one edge
examination, the selecting battery's unit, applied to every
examination this repair performs (cone scan, support scan,
rederivation scan alike).

Naive control: the append-only cone repair of the selecting
battery (the built form in stack.py) applied unchanged. For
a lift its changed edge carries the new weight, which can
never raise a distance; for a withdrawal it is given no
changed edge at all, the only form the append-only contract
admits. Its mismatches are printed as losses.

Wall-clock discipline: one machine, one process. Workloads
are generated once per battery, with the from-scratch truth
for every epoch and prefix precomputed at generation time,
outside every timed region. Each arm's timed replay runs
the work its own form requires, plus the exactness
comparison against the stored truth, a comparison every
arm pays identically. The stateful forms (cone repair,
retraction repair, the naive control) carry their adjacency
maps as state, maintained incrementally across epochs
inside the timed region, exactly as the built stack's own
re-validation maintains them; from-scratch carries no
state and pays no such maintenance. Timing workloads are
the counted batteries extended at the same seeds (repair
grow 82000 and retraction 81000 at 2000 cases, closure
83000 at 1500 systems), so every timed replay re-verifies
exactness at the larger scale as well. Arms are interleaved
with the starting arm rotated each round; 11 rounds; per-arm
per-round totals in nanoseconds by a monotonic counter;
median, least, greatest reported and every raw round kept
in the results file. The harness refuses to report timings
for a battery whose round summaries disagree.
"""

import json
import os
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict, deque

import stack

TOP = 10 ** 9
ROUNDS = 11


# ---------------------------------------------------------- shared forms

def oracle(n, edges):
    """From-scratch distances, the selecting battery's oracle:
    one pass in tail order over the sorted edge list."""
    d = [TOP] * n
    d[0] = 0
    relax = 0
    for (u, v, w) in edges:
        relax += 1
        if d[u] + w < d[v]:
            d[v] = d[u] + w
    return d, relax


def outmap(edges):
    out = defaultdict(list)
    for e in edges:
        out[e[0]].append(e)
    return out


def inmap(edges):
    inn = defaultdict(list)
    for e in edges:
        inn[e[1]].append(e)
    return inn


# ---------------------------------------------------------- retraction repair

def repair(before, out, inn, gone, fresh):
    """Exact repair after one retraction epoch. before is the
    distance list before the epoch; out and inn are the
    maintained adjacency maps of the graph as it stood before
    the epoch; gone is the retracted edge (tail, head, weight)
    as it stood before; fresh is its new weight for a lift, or
    None for a withdrawal. The after graph's incoming edges of
    any node are its before edges with the single retracted
    edge replaced or removed, which the rederivation applies
    on the fly. Returns (distances, relaxations, hit count)."""
    d = list(before)
    (gu, gv, gw) = gone
    if before[gv] >= TOP or before[gu] + gw != before[gv]:
        return d, 0, 0
    relax = 0
    cone = {gv}
    q = deque([gv])
    while q:
        x = q.popleft()
        for (u, v, w) in out.get(x, []):
            relax += 1
            if before[v] < TOP and before[u] + w == before[v] \
                    and v not in cone:
                cone.add(v)
                q.append(v)
    hit = set()
    for x in sorted(cone):
        keep = False
        used = False
        for e in inn.get(x, []):
            relax += 1
            if not used and e == gone:
                used = True
                continue
            if before[e[0]] + e[2] == before[x] and e[0] not in hit:
                keep = True
                break
        if not keep:
            hit.add(x)
    if not hit:
        return d, relax, 0
    for x in hit:
        d[x] = TOP
    for x in sorted(hit):
        used = False
        for e in inn.get(x, []):
            relax += 1
            if not used and e == gone:
                used = True
                if fresh is None:
                    continue
                e = (gone[0], gone[1], fresh)
            if d[e[0]] + e[2] < d[x]:
                d[x] = d[e[0]] + e[2]
    return d, relax, len(hit)


def stale(before, out, gone, lifted):
    """The naive control: the append-only cone repair applied
    unchanged, over the maintained out map of the after graph.
    lifted is the new weight for a lift epoch, or None for a
    withdrawal. Returns (distances, relaxations)."""
    if lifted:
        changed = [(gone[0], gone[1], lifted)]
    else:
        changed = []
    return stack.cone_scoped_repair(before, out, changed)


def remap(out, inn, gone, fresh):
    """Maintain the adjacency state across one epoch: remove
    the retracted edge instance, insert its lifted form when
    the epoch is a lift."""
    out[gone[0]].remove(gone)
    inn[gone[1]].remove(gone)
    if fresh is not None:
        e = (gone[0], gone[1], fresh)
        out[gone[0]].append(e)
        inn[gone[1]].append(e)


# ---------------------------------------------------------- graph scripts

def base(rng):
    """One initial graph in the selecting battery's style."""
    n = rng.randint(8, 20)
    edges = []
    for i in range(n):
        for j in range(i + 1, min(n, i + 4)):
            if rng.random() < 0.5:
                edges.append((i, j, rng.randint(1, 9)))
    edges.sort()
    return n, edges


def apply(edges, act):
    """Apply one scripted epoch to an edge list copy.
    Returns (edges after, gone, fresh weight or None)."""
    (kind, gone, fresh) = act
    edges = list(edges)
    if kind == "grow":
        edges.append(fresh)
        edges.sort()
        return edges, fresh, None
    pos = edges.index(gone)
    if kind == "drop":
        edges.pop(pos)
        return edges, gone, None
    if kind == "lift":
        edges[pos] = (gone[0], gone[1], fresh)
        return edges, gone, fresh
    edges[pos] = fresh
    return edges, gone, fresh[2]


def truth(n, edges, acts):
    """Attach the from-scratch truth to every scripted epoch:
    each entry becomes (act, truth distances, truth
    relaxations), or stays None for a skipped epoch."""
    mine = list(edges)
    out = []
    for act in acts:
        if act is None:
            out.append(None)
            continue
        mine, _g, _f = apply(mine, act)
        d, r = oracle(n, mine)
        out.append((act, d, r))
    return out


def retractscript(seed, cases, epochs):
    """Cases whose every epoch lifts (increases) one edge
    weight or drops (withdraws) one edge. An action names the
    edge as it stands when the epoch begins, so every arm
    replays the identical script on its own copy."""
    rng = random.Random(seed)
    script = []
    for _c in range(cases):
        n, edges = base(rng)
        live = list(edges)
        acts = []
        for _e in range(epochs):
            if not live:
                acts.append(None)
                continue
            gone = rng.choice(live)
            pos = live.index(gone)
            if rng.random() < 0.5:
                fresh = gone[2] + rng.randint(1, 8)
                live[pos] = (gone[0], gone[1], fresh)
                acts.append(("lift", gone, fresh))
            else:
                live.pop(pos)
                acts.append(("drop", gone, None))
        script.append((n, edges, truth(n, edges, acts)))
    return script


def growscript(seed, cases, epochs):
    """Cases in the selecting battery's own contract: each
    epoch appends an edge or decreases an edge weight."""
    rng = random.Random(seed)
    script = []
    for _c in range(cases):
        n, edges = base(rng)
        live = [list(e) for e in edges]
        acts = []
        for _e in range(epochs):
            if rng.random() < 0.5 or not live:
                i = rng.randrange(n - 1)
                j = rng.randint(i + 1, n - 1)
                e = (i, j, rng.randint(1, 9))
                live.append(list(e))
                live.sort()
                acts.append(("grow", None, e))
            else:
                pick = rng.choice(live)
                if pick[2] <= 1:
                    acts.append(None)
                    continue
                gone = tuple(pick)
                fresh = rng.randint(1, pick[2] - 1)
                pick[2] = fresh
                acts.append(("ease", gone,
                             (gone[0], gone[1], fresh)))
        script.append((n, edges, truth(n, edges, acts)))
    return script


# ---------------------------------------------------------- repair replays

def replayretract(script, arm):
    """Replay the retraction script under one arm against the
    stored truths. Returns executed epochs, exact epochs,
    relaxations, and arm-specific regime counts."""
    agree = 0
    relax = 0
    done = 0
    tight = 0
    costly = 0
    hitsum = 0
    hitmax = 0
    for (n, edges, acts) in script:
        mine = list(edges)
        d, _r = oracle(n, mine)
        out = outmap(mine) if arm != "scratch" else None
        inn = inmap(mine) if arm != "scratch" else None
        for entry in acts:
            if entry is None:
                continue
            (act, want, trelax) = entry
            before = d
            mine, gone, fresh = apply(mine, act)
            done += 1
            if before[gone[1]] < TOP and \
                    before[gone[0]] + gone[2] == before[gone[1]]:
                tight += 1
            if arm == "scratch":
                d, r = oracle(n, mine)
                relax += r
            elif arm == "repair":
                d, r, hit = repair(before, out, inn, gone, fresh)
                relax += r
                hitsum += hit
                hitmax = max(hitmax, hit)
                if r >= trelax:
                    costly += 1
                remap(out, inn, gone, fresh)
            else:
                remap(out, inn, gone, fresh)
                d, r = stale(before, out, gone, fresh)
                relax += r
            if d == want:
                agree += 1
    out = {"done": done, "agree": agree, "relax": relax,
           "tight": tight}
    if arm == "repair":
        out["costly"] = costly
        out["hitsum"] = hitsum
        out["hitmax"] = hitmax
    return out


def replaygrow(script, arm):
    """Replay the append and decrease script under one arm of
    the selecting battery's proposition 3 candidate set."""
    agree = 0
    relax = 0
    done = 0
    for (n, edges, acts) in script:
        mine = list(edges)
        d, _r = oracle(n, mine)
        out = outmap(mine)
        for entry in acts:
            if entry is None:
                continue
            (act, want, _t) = entry
            before = d
            mine, gone, _f = apply(mine, act)
            if arm == "cone":
                if act[0] == "grow":
                    out[act[2][0]].append(act[2])
                else:
                    slot = out[gone[0]]
                    slot[slot.index(gone)] = act[2]
            done += 1
            if arm == "scratch":
                d, r = oracle(n, mine)
                relax += r
            elif arm == "cone":
                d, r = stack.cone_scoped_repair(
                    before, out, [act[2]])
                relax += r
            else:
                d = list(before)
                front = {gone[0]}
                r = 0
                left = 0
                while front and left < 100:
                    left += 1
                    nxt = set()
                    for (u, v, w) in mine:
                        r += 1
                        if u in front and d[u] + w < d[v]:
                            d[v] = d[u] + w
                            nxt.add(v)
                    front = nxt
                relax += r
            if d == want:
                agree += 1
    return {"done": done, "agree": agree, "relax": relax}


# ---------------------------------------------------------- closure forms

def least(rules):
    """Naive least closure by full scan to a fixed point."""
    derived = set()
    changed = True
    checks = 0
    while changed:
        changed = False
        for (pre, head) in rules:
            checks += 1
            if head not in derived and set(pre) <= derived:
                derived.add(head)
                changed = True
    return derived, checks


def scan(rules):
    """Scan-per-round closure: full scan each round, all newly
    derivable heads added together."""
    derived = set()
    checks = 0
    while True:
        new = set()
        for (pre, head) in rules:
            checks += 1
            if head not in derived and set(pre) <= derived:
                new.add(head)
        if not new:
            break
        derived |= new
    return derived, checks


def blind(rules):
    """The duplicate-blind worklist: the count starts at the
    premise list length and decrements once per processed
    term, so a duplicated premise can block its rule forever."""
    derived = set()
    miss = [len(pre) for (pre, _h) in rules]
    q = deque()
    for i, (pre, h) in enumerate(rules):
        if miss[i] == 0 and h not in derived:
            derived.add(h)
            q.append(h)
    seen = set()
    while q:
        x = q.popleft()
        if x in seen:
            continue
        seen.add(x)
        for i, (pre, h) in enumerate(rules):
            if x in pre:
                miss[i] -= 1
                if miss[i] == 0 and h not in derived:
                    derived.add(h)
                    q.append(h)
    return derived


def closurescript(seed, systems):
    """Rule systems in the selecting battery's style, compared
    at every append prefix. Returns one (prefix rules, least
    closure) pair per prefix, truths precomputed here."""
    rng = random.Random(seed)
    pairs = []
    for _s in range(systems):
        nterms = rng.randint(4, 12)
        nrules = rng.randint(3, 18)
        rules = []
        for _ in range(nrules):
            k = rng.randint(0, 3)
            pre = [rng.randrange(nterms) for _ in range(k)]
            rules.append((pre, rng.randrange(nterms)))
        for pref in range(1, len(rules) + 1):
            sub = rules[:pref]
            want, _c = least(sub)
            pairs.append((sub, want))
    return pairs


def replayclosure(pairs, arm):
    """Replay every append prefix under one closure arm."""
    checks = 0
    bad = 0
    for (sub, want) in pairs:
        if arm == "least":
            got, c = least(sub)
            checks += c
        elif arm == "work":
            got, c = stack.distinct_count_worklist(sub)
            checks += c
        elif arm == "scan":
            got, c = scan(sub)
            checks += c
        else:
            got = blind(sub)
        if got != want:
            bad += 1
    out = {"prefixes": len(pairs), "bad": bad}
    if arm != "blind":
        out["checks"] = checks
    return out


# ---------------------------------------------------------- clock

def clock(jobs):
    """Interleaved timing. jobs maps an arm name to a zero
    argument replay. Returns raw round nanoseconds per arm
    and the one summary every round agreed on, per arm."""
    raw = {name: [] for name in jobs}
    sums = {}
    names = list(jobs)
    for r in range(ROUNDS):
        shift = r % len(names)
        order = names[shift:] + names[:shift]
        for name in order:
            start = time.perf_counter_ns()
            got = jobs[name]()
            raw[name].append(time.perf_counter_ns() - start)
            if name in sums and sums[name] != got:
                raise SystemExit(
                    "nondeterministic replay in arm %s" % name)
            sums[name] = got
    return raw, sums


def report(raw):
    out = {}
    for name, vals in raw.items():
        out[name] = {
            "rounds": vals,
            "median": statistics.median(vals),
            "least": min(vals),
            "greatest": max(vals),
        }
    return out


def paired(raw):
    """Paired per-round wins: paired[a][b] counts the rounds
    in which arm a's total was strictly below arm b's. Under
    shared-machine noise this is the robust companion to the
    per-arm medians, which are computed independently."""
    out = {}
    for a in raw:
        out[a] = {}
        for b in raw:
            if a != b:
                out[a][b] = sum(
                    1 for x, y in zip(raw[a], raw[b]) if x < y)
    return out


# ---------------------------------------------------------- fidelity

def fidelity():
    """Re-run the selecting battery in this repo and compare
    propositions 3 and 4 against its committed results file,
    exactly. Returns the comparison block."""
    here = os.path.dirname(os.path.abspath(__file__))
    done = subprocess.run(
        [sys.executable, "validation-lane2.py"], cwd=here,
        capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit("selecting battery failed to run")
    fresh = json.loads(done.stdout)
    with open(os.path.join(
            here, "validation-lane2-results.json")) as f:
        kept = json.load(f)
    return {
        "p3": fresh["p3"],
        "p4": fresh["p4"],
        "p3match": fresh["p3"] == kept["p3"],
        "p4match": fresh["p4"] == kept["p4"],
    }


# ---------------------------------------------------------- main

def main():
    out = {}
    out["fidelity"] = fidelity()
    if not out["fidelity"]["p3match"] or \
            not out["fidelity"]["p4match"]:
        print(json.dumps(out, indent=1, sort_keys=True))
        raise SystemExit("fidelity control FAILED: the "
                         "selecting battery does not reproduce")
    rscript = retractscript(81000, 200, 5)
    out["retract"] = {
        arm: replayretract(rscript, arm)
        for arm in ("repair", "scratch", "stale")
    }
    gscript = growscript(82000, 2000, 5)
    tscript = retractscript(81000, 2000, 5)
    pairs = closurescript(83000, 1500)
    craw, csums = clock({
        "cone": lambda: replaygrow(gscript, "cone"),
        "scratch": lambda: replaygrow(gscript, "scratch"),
        "rounds": lambda: replaygrow(gscript, "rounds"),
    })
    rraw, rsums = clock({
        "repair": lambda: replayretract(tscript, "repair"),
        "scratch": lambda: replayretract(tscript, "scratch"),
        "stale": lambda: replayretract(tscript, "stale"),
    })
    wraw, wsums = clock({
        "work": lambda: replayclosure(pairs, "work"),
        "least": lambda: replayclosure(pairs, "least"),
        "scan": lambda: replayclosure(pairs, "scan"),
        "blind": lambda: replayclosure(pairs, "blind"),
    })
    out["clock"] = {
        "rounds": ROUNDS,
        "grow": {"arms": report(craw), "sums": csums,
                 "paired": paired(craw)},
        "retract": {"arms": report(rraw), "sums": rsums,
                    "paired": paired(rraw)},
        "closure": {"arms": report(wraw), "sums": wsums,
                    "paired": paired(wraw)},
    }
    with open("retract-results.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
