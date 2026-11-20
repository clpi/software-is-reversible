#!/usr/bin/env python3
"""Widening harness: new weighting families over the
spectrum battery. Spec: the widen file in this repo.

What this harness does, exactly:
  (a) regenerates the lane 2 proposition 1 battery (300
      point sets, seed 2000, the spectrum harness's own
      generator order) and reproduces the old recovery
      figures as a fidelity control against the committed
      spectrum results file, identifying the 28 frontier
      members the old union does not select;
  (b) runs the new families defined in the spec (the
      epsilon form, lexicographic over permuted orders,
      the achievement form, weighted max with varied
      exponents and wide weights, power sums beyond the
      squared family, seeded pseudo-random linear
      weightings, and the centered form counted apart)
      over the same battery, frontier first, selection by
      unique minimiser only;
  (c) classifies every battery frontier member, and in
      detail each of the 28, by exact rational arithmetic
      over all positive weights for the linear family and
      the power sum families;
  (d) verifies the weighted max construction on all 695
      members and runs the standing controls: no dominated
      selection anywhere, and no linear configuration
      selecting a member of the none class.

Stdlib only. Deterministic: seeded generators only, no
clocks. Two consecutive runs byte-identical.
"""

import json
import os
import random
import sys
from fractions import Fraction

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

import meta as M

BASE = "12047b21f0af62f4dc3272199dec5184d14cfd3a"
FAIL = []


def check(name, cond, detail=""):
    if not cond:
        FAIL.append("%s %s" % (name, detail))
    return cond


def dom(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


def frontier(pts):
    return sorted({p for p in pts
                   if not any(dom(q, p) for q in pts if q != p)})


def pick(pts, w):
    return min(pts, key=lambda p: (w[0] * p[0] + w[1] * p[1], p))


def sole(pairs):
    best = min(s for s, _p in pairs)
    wins = [p for s, p in pairs if s == best]
    if len(wins) == 1:
        return wins[0]
    return None


def battery():
    rng = random.Random(2000)
    sets = []
    perms = 0
    agree = 0
    for _t in range(300):
        n = rng.randint(4, 14)
        pts = [(rng.randint(0, 20), rng.randint(0, 20)) for _ in range(n)]
        sets.append(pts)
        base = frontier(pts)
        for _k in range(3):
            q = pts[:]
            rng.shuffle(q)
            perms += 1
            if frontier(q) == base:
                agree += 1
    return sets, perms, agree


def old(sets):
    grid = [(a, b) for a in range(1, 10) for b in range(1, 10)]
    nonlin = [(f, p) for f, p in M.configurations()
              if f in ("squared", "max", "overlay")]
    counts = {"members": 0, "grid": 0, "nonlinear": 0,
              "squared": 0, "max": 0, "overlay": 0, "union": 0}
    missing = []
    chosen = {}
    for t, pts in enumerate(sets):
        front = frontier(pts)
        named = [("m%d" % i, p[0], p[1]) for i, p in enumerate(front)]
        gridpicks = {pick(pts, w) for w in grid}
        for i, p in enumerate(front):
            counts["members"] += 1
            got = False
            for name in ("squared", "max", "overlay"):
                for fam, par in nonlin:
                    if fam != name:
                        continue
                    pk, _w = M.induced(fam, par, named)
                    if pk == "m%d" % i:
                        got = True
                        counts[name] += 1
                        break
            if got:
                counts["nonlinear"] += 1
            if p in gridpicks:
                counts["grid"] += 1
            if got or p in gridpicks:
                counts["union"] += 1
                chosen[(t, p)] = True
            else:
                missing.append({"trial": t, "point": p, "front": front})
    seg = [[(0, 10), (6, 6), (10, 0)], [(0, 20), (11, 11), (20, 0)]]
    segmid = False
    for pts in seg:
        picks = {pick(pts, w) for w in grid}
        if pts[1] in picks:
            segmid = True
    counts["segmid"] = segmid
    return counts, missing, chosen


def classify(front, target, pw):
    tx = Fraction(target[0] ** pw)
    ty = Fraction(target[1] ** pw)
    low = Fraction(0)
    high = None
    for q in front:
        if q == target:
            continue
        qx = Fraction(q[0] ** pw)
        qy = Fraction(q[1] ** pw)
        dx = tx - qx
        dy = qy - ty
        if dx > 0:
            bound = dy / dx
            if high is None or bound < high:
                high = bound
        elif dx < 0:
            bound = dy / dx
            if bound > low:
                low = bound
    weak = (high is None or low <= high) and (high is None or high > 0)
    uniq = high is None or low < high
    span = [str(low), "inf" if high is None else str(high)]
    if uniq:
        return "unique", span
    if weak:
        return "weak", span
    return "none", span


def configs(family, rng):
    if family == "eps":
        return [(o, e) for o in (0, 1) for e in range(0, 21)]
    if family == "lex":
        return [0, 1]
    if family == "cheby":
        return [(a, b) for a in range(1, 22) for b in range(1, 22)]
    if family == "pmax":
        out = [(1, a, b) for a in range(1, 41) for b in range(1, 41)]
        out += [(2, a, b) for a in range(1, 13) for b in range(1, 13)]
        out += [(3, a, b) for a in range(1, 13) for b in range(1, 13)]
        return out
    if family == "power":
        out = [(3, a, b) for a in range(1, 10) for b in range(1, 10)]
        out += [(4, a, b) for a in range(1, 10) for b in range(1, 10)]
        return out
    if family == "rand":
        return [(rng.randint(1, 997), rng.randint(1, 997))
                for _ in range(4000)]
    raise ValueError(family)


def select(family, param, front):
    if family == "eps":
        order, bound = param
        if order == 0:
            feas = [p for p in front if p[1] <= bound]
            if not feas:
                return None
            return sole([(p[0], p) for p in feas])
        feas = [p for p in front if p[0] <= bound]
        if not feas:
            return None
        return sole([(p[1], p) for p in feas])
    if family == "lex":
        if param == 0:
            return sole([((p[0], p[1]), p) for p in front])
        return sole([((p[1], p[0]), p) for p in front])
    if family == "cheby":
        a, b = param
        rx = min(p[0] for p in front) - 1
        ry = min(p[1] for p in front) - 1
        pairs = []
        for p in front:
            dx = p[0] - rx
            dy = p[1] - ry
            top = max(a * dx, b * dy)
            s = Fraction(top) + Fraction(a * dx + b * dy, 1000)
            pairs.append((s, p))
        return sole(pairs)
    if family == "pmax":
        pw, a, b = param
        return sole([(max(a * p[0] ** pw, b * p[1] ** pw), p)
                     for p in front])
    if family == "power":
        pw, a, b = param
        return sole([(a * p[0] ** pw + b * p[1] ** pw, p)
                     for p in front])
    if family == "rand":
        a, b = param
        return sole([(a * p[0] + b * p[1], p) for p in front])
    if family == "center":
        cx, cy = param
        return sole([((p[0] - cx) ** 2 + (p[1] - cy) ** 2, p)
                     for p in front])
    raise ValueError(family)


def main():
    sets, perms, agree = battery()
    counts, missing, chosen = old(sets)
    fronts = [frontier(pts) for pts in sets]

    with open(os.path.join(here, "spectrum-results.json")) as f:
        committed = json.load(f)["batteries"]["frontier"]
    check("fidelity members", counts["members"] == committed["frontier_members"],
          "%s" % counts["members"])
    check("fidelity grid", counts["grid"] == committed["weight_first_recovery"])
    check("fidelity nonlinear",
          counts["nonlinear"] == committed["nonlinear_recovery"])
    for name in ("squared", "max", "overlay"):
        check("fidelity " + name,
              counts[name] == committed["nonlinear_recovery_by_family"][name])
    check("fidelity union", counts["union"] == committed["union_grid_or_nonlinear_recovery"])
    check("fidelity perms", perms == committed["perm_checks"]
          and agree == committed["perm_agree"])
    check("segment grid", counts["segmid"] is False)

    misskeys = {(m["trial"], m["point"]) for m in missing}
    check("missing count", len(missing) == 28, "%d" % len(missing))

    classes = {"unique": 0, "weak": 0, "none": 0}
    linearkind = {}
    for t, front in enumerate(fronts):
        for p in front:
            kind = classify(front, p, 1)[0]
            classes[kind] += 1
            linearkind[(t, p)] = kind

    gridbad = 0
    grid = [(a, b) for a in range(1, 10) for b in range(1, 10)]
    for t, pts in enumerate(sets):
        picks = {pick(pts, w) for w in grid}
        for p in picks:
            if (t, p) in linearkind and linearkind[(t, p)] == "none":
                gridbad += 1
    check("linear grid none class", gridbad == 0, "%d" % gridbad)

    built = 0
    for front in fronts:
        for p in front:
            if p[0] > 0 and p[1] > 0:
                w = (p[1], p[0])
            elif p[0] == 0 and p[1] == 0:
                w = (1, 1)
            elif p[0] == 0:
                w = (21, 1)
            else:
                w = (1, 21)
            got = sole([(max(w[0] * q[0], w[1] * q[1]), q) for q in front])
            if got == p:
                built += 1
    check("max construction", built == counts["members"], "%d" % built)

    rng = random.Random(91000)
    fams = ["eps", "lex", "cheby", "pmax", "power", "rand"]
    famsets = {}
    famtotal = {}
    randbad = 0
    for family in fams:
        confs = configs(family, rng)
        sel = set()
        for t, front in enumerate(fronts):
            for param in confs:
                got = select(family, param, front)
                if got is not None:
                    sel.add((t, got))
        famsets[family] = sel
        famtotal[family] = {"configs": len(confs), "total": len(sel),
                            "ofmissing": len(sel & misskeys)}
        if family == "rand":
            for key in sel:
                if linearkind[key] == "none":
                    randbad += 1
    check("rand none class", randbad == 0, "%d" % randbad)

    centersel = set()
    for t, front in enumerate(fronts):
        for c in front:
            got = select("center", c, front)
            if got is not None:
                centersel.add((t, got))
    famtotal["center"] = {"configs": "per instance", "total": len(centersel),
                          "ofmissing": len(centersel & misskeys)}

    fixed = set(chosen)
    for family in fams:
        fixed |= famsets[family]
    remaining = [m for m in missing
                 if (m["trial"], m["point"]) not in fixed]
    withcenter = fixed | centersel
    remainingc = [m for m in missing
                  if (m["trial"], m["point"]) not in withcenter]

    detail = []
    for m in missing:
        t = m["trial"]
        p = m["point"]
        front = m["front"]
        by = {}
        for family in fams:
            by[family] = (t, p) in famsets[family]
        by["center"] = (t, p) in centersel
        detail.append({
            "trial": t, "point": list(p),
            "front": [list(q) for q in front],
            "linear": classify(front, p, 1)[0],
            "span": classify(front, p, 1)[1],
            "squared": classify(front, p, 2)[0],
            "cube": classify(front, p, 3)[0],
            "fourth": classify(front, p, 4)[0],
            "by": by,
            "fixed": (t, p) in fixed,
            "centered": (t, p) in withcenter,
        })

    domfree = 0
    for pts, front in zip(sets, fronts):
        for p in front:
            if not any(dom(c, p) for c in pts):
                domfree += 1
    check("frontier undominated", domfree == counts["members"])

    mfronts = [M.frontier_of(cands) for _n, cands, _m in M.INSTANCES]
    metabad = 0
    metamid = {}
    rng2 = random.Random(91000)
    for family in fams + ["center"]:
        if family == "center":
            confs = None
        else:
            confs = configs(family, rng2)
        mid = 0
        for idx, front in enumerate(mfronts):
            pfront = [(q[1], q[2]) for q in front]
            names = {(q[1], q[2]): q[0] for q in front}
            params = pfront if family == "center" else confs
            got = set()
            for param in params:
                s = select(family, param, pfront)
                if s is not None:
                    got.add(names[s])
            for name in got:
                if name in ("padded", "rambling"):
                    metabad += 1
            if M.INSTANCES[idx][2] in got:
                mid += 1
        metamid[family] = mid
    check("meta dominated", metabad == 0, "%d" % metabad)

    linbad = 0
    for idx, front in enumerate(mfronts):
        for a in range(1, 10):
            for b in range(1, 10):
                pk, _w = M.induced("linear", (a, b), front)
                if pk == M.INSTANCES[idx][2]:
                    linbad += 1
    check("meta linear grid", linbad == 0, "%d" % linbad)

    out = {
        "base": BASE,
        "battery": {"trials": 300, "members": counts["members"],
                    "grid": counts["grid"],
                    "nonlinear": counts["nonlinear"],
                    "squared": counts["squared"], "max": counts["max"],
                    "overlay": counts["overlay"], "union": counts["union"],
                    "missing": len(missing), "perms": perms, "agree": agree},
        "classes": classes,
        "families": famtotal,
        "union": {"fixed": len(fixed & misskeys),
                  "remaining": [{"trial": m["trial"], "point": list(m["point"])}
                                for m in remaining],
        "centered": len(withcenter & misskeys),
                  "remainingcentered": [{"trial": m["trial"],
                                         "point": list(m["point"])}
                                        for m in remainingc]},
        "missingdetail": detail,
        "meta": metamid,
        "controls": {"fidelity": not FAIL, "built": built,
                     "gridbad": gridbad, "randbad": randbad,
                     "metabad": metabad, "linbad": linbad},
        "verdict": "FAIL" if FAIL else "OK",
    }
    with open(os.path.join(here, "widen-results.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("battery: members %d, grid %d, nonlinear %d, union %d, missing %d"
          % (counts["members"], counts["grid"], counts["nonlinear"],
             counts["union"], len(missing)))
    for family in fams + ["center"]:
        print("family %s: total %s, of the 28: %s"
              % (family, famtotal[family]["total"],
                 famtotal[family]["ofmissing"]))
    print("union over old and new fixed families: %d of 28; remaining %d"
          % (len(fixed & misskeys), len(remaining)))
    print("union with the centered form: %d of 28; remaining %d"
          % (len(withcenter & misskeys), len(remainingc)))
    print("linear classes over 695: %s" % classes)
    if FAIL:
        print("verdict: FAIL -- " + "; ".join(FAIL))
        return 1
    print("verdict: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
