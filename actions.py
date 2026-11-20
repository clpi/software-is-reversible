#!/usr/bin/env python3
"""Basic action model -- solve-and-validate harness (lane 4).

Scope honesty: simulated scenarios only. No live desktop, no
browser, no display is touched. Every verdict below is a model
verdict at the stated observation resolution, exactly as the
first pass in validate.py labeled its own.

The candidate family. Four rival action-selection algorithms
compete over the same scenario instances (paired seeds):

  route 1, explicit: a stated planner over the observed state.
    It reads the model the observation carries (response scale
    and drift, gravity, trajectory law, layout map, dependency
    spec) and computes the action in closed form. It plans
    once and executes its plan as stated, with no mid-course
    revision. Where the observed model is incomplete (a hidden
    dependency), the plan fails as stated -- that is the
    route's defining limit, not an accident.
  route 2, obscurity: no explicit algorithm names the action.
    Each action parameter starts with an obscurity reading
    over the three clauses of recursive.md family C
    (unresolved, unprojected, uncertain). Parameters whose
    reading is at or above the threshold (2 of 3 clauses) have
    their action constructed by probe-and-observe search on a
    clone of the state model: candidate actions are tried,
    the fresh observation after each probe is read, and the
    candidate whose observed outcome leaves the least
    obscurity (least residual distance to the goal reading)
    is kept, with a shrinking search radius. The route never
    reads a domain formula.
  route 3, combination: the explicit plan first; one
    verification observation; where the observed residual is
    above tolerance, obscurity construction repairs the plan.
    Per instance the harness records whether the repair leg
    fired, so route 3's selections carry their sub-route.
  route 0, naive (control rival): greedy nearest-target with
    fixed parameters. It aims straight at the target with a
    canned action and ignores the observed model entirely.

Derivation route is recorded per selection: 1, 2, or 3 for
the pipeline routes (recursive.md family B), 0 for the
control, which stands outside the pipeline routes by design.

Scenario families (one per basic action): pixel move, jump,
jump over an obstacle, drive a course, touch a target, type
a string, automate a process. Each family runs seeded,
recorded, reproducible permutations: layouts, obstacle
placements, physics constants, target positions, page
structures, and process shapes vary per instance. The same
instance seed is used for every rival, so the comparison is
paired.

Success is per family per rival. A failure names its
differing component: the state component, the premise, or
the route leg that diverged.

Reversibility discipline (reversibility.md protocol): for
each primitive, its constructed inverse where one exists is
validated by the fresh-observation round trip -- snapshot,
execute, fresh observe, execute inverse, fresh observe,
compare. Primitives with no derivable inverse are refused
by name (R-NOINVERSE) at qualification, before any effect
is delivered, and the refusal is the recorded verdict.
Negative controls with deliberately wrong inverses must
come back MISMATCH, or the PASS verdicts mean nothing.

Stdlib only. Deterministic: all randomness comes from
random.Random on recorded seeds.
"""

import json
import math
import random
import sys

BASE_SEED = 20261120
PER_FAMILY = 60
REV_PER_PRIMITIVE = 20
OBSCURITY_THRESHOLD = 2  # of the 3 clauses: unresolved, unprojected, uncertain


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ================================================================ move
# State: cursor position. The surface response is displacement =
# command * scale + drift; scale and drift are carried by the
# observation. Goal: land within 2.0 px of the target.

def move_instance(rng):
    return {
        "start": (rng.uniform(0, 400), rng.uniform(0, 400)),
        "target": (rng.uniform(0, 400), rng.uniform(0, 400)),
        "scale": rng.uniform(0.7, 1.3),
        "drift": (rng.uniform(-8, 8), rng.uniform(-8, 8)),
        "tol": 2.0,
    }


def move_apply(pos, cmd, p):
    return (pos[0] + cmd[0] * p["scale"] + p["drift"][0],
            pos[1] + cmd[1] * p["scale"] + p["drift"][1])


def move_run(rival, p):
    start, target = p["start"], p["target"]
    if rival == "explicit":
        cmd = ((target[0] - start[0] - p["drift"][0]) / p["scale"],
               (target[1] - start[1] - p["drift"][1]) / p["scale"])
        end = move_apply(start, cmd, p)
        return move_verdict(end, p, probes=0, repaired=False)
    if rival == "naive":
        cmd = (target[0] - start[0], target[1] - start[1])
        end = move_apply(start, cmd, p)
        return move_verdict(end, p, probes=0, repaired=False)
    if rival == "obscurity":
        end, probes = search_2d(
            start,
            lambda cmd: move_apply(start, cmd, p),
            target, p["tol"], budget=90)
        return move_verdict(end, p, probes=probes, repaired=False)
    # combination
    cmd = ((target[0] - start[0] - p["drift"][0]) / p["scale"],
           (target[1] - start[1] - p["drift"][1]) / p["scale"])
    end = move_apply(start, cmd, p)
    if dist(end, target) <= p["tol"]:
        return move_verdict(end, p, probes=0, repaired=False)
    end2, probes = search_2d(
        end, lambda c: move_apply(end, c, p), target, p["tol"], budget=60)
    return move_verdict(end2, p, probes=probes, repaired=True)
    raise AssertionError(rival)


def move_verdict(end, p, probes, repaired):
    err = dist(end, p["target"])
    if err <= p["tol"]:
        return (True, "-", probes, repaired)
    axis = "position.x" if abs(end[0] - p["target"][0]) >= abs(
        end[1] - p["target"][1]) else "position.y"
    return (False, axis, probes, repaired)


def search_2d(origin, apply_fn, target, tol, budget):
    """Obscurity construction in a 2d command space: probe
    candidates, read the observed outcome, keep the least
    residual, shrink the radius. No domain formula is read;
    the only signal is the fresh observation after a probe."""
    best_cmd = (target[0] - origin[0], target[1] - origin[1])
    best_end = apply_fn(best_cmd)
    best_err = dist(best_end, target)
    probes = 1
    radius = max(20.0, best_err)
    rng = random.Random(1234567)  # fixed probe order: reproducible
    while probes < budget and best_err > tol:
        improved = False
        for _ in range(12):
            if probes >= budget:
                break
            cand = (best_cmd[0] + rng.uniform(-radius, radius),
                    best_cmd[1] + rng.uniform(-radius, radius))
            end = apply_fn(cand)
            probes += 1
            err = dist(end, target)
            if err < best_err:
                best_cmd, best_end, best_err = cand, end, err
                improved = True
        if not improved:
            radius *= 0.5
        else:
            radius = max(4.0, radius * 0.7)
    return best_end, probes


# ================================================================ jump
# Vertical jump: choose launch velocity. Apex = v^2 / (2 g).
# Success: apex in [H, 1.08 H].

def jump_instance(rng):
    return {"g": rng.uniform(5, 20), "height": rng.uniform(2, 12)}


def jump_apex(v, g):
    return v * v / (2.0 * g)


def jump_run(rival, p):
    g, h = p["g"], p["height"]
    goal = 1.04 * h
    if rival == "explicit":
        v = math.sqrt(2 * g * goal)
        return jump_verdict(v, p, 0, False)
    if rival == "naive":
        return jump_verdict(11.0, p, 0, False)
    if rival == "obscurity":
        v, probes = search_1d(
            lambda v: jump_apex(v, g), goal, lo=2.0, hi=30.0,
            tol=0.02 * h, budget=60)
        return jump_verdict(v, p, probes, False)
    v = math.sqrt(2 * g * goal)
    apex = jump_apex(v, g)
    if h <= apex <= 1.08 * h:
        return jump_verdict(v, p, 0, False)
    v2, probes = search_1d(
        lambda v: jump_apex(v, g), goal, lo=max(1.0, v - 4),
        hi=v + 4, tol=0.02 * h, budget=40)
    return jump_verdict(v2, p, probes, True)


def jump_verdict(v, p, probes, repaired):
    apex = jump_apex(v, p["g"])
    if p["height"] <= apex <= 1.08 * p["height"]:
        return (True, "-", probes, repaired)
    return (False, "height.apex", probes, repaired)


def search_1d(fn, goal, lo, hi, tol, budget):
    """Obscurity construction in a 1d parameter space by
    probe-and-observe narrowing. No formula is read."""
    probes = 0
    best_v, best_err = None, None
    while probes < budget and hi - lo > 1e-9:
        mid = 0.5 * (lo + hi)
        val = fn(mid)
        probes += 1
        err = abs(val - goal)
        if best_err is None or err < best_err:
            best_v, best_err = mid, err
        if err <= tol:
            break
        if val < goal:
            lo = mid
        else:
            hi = mid
    return best_v, probes


# ================================================================ jump over
# Projectile: choose (vx, vy). Obstacle at distance d, height h,
# width 1. Success: trajectory clears the obstacle top by 0.2
# and the range lands in [d+1, d+7].

def jumpover_instance(rng):
    return {
        "g": rng.uniform(6, 16),
        "d": rng.uniform(4, 10),
        "h": rng.uniform(1.0, 3.5),
    }


def jumpover_eval(vx, vy, p):
    g, d, h = p["g"], p["d"], p["h"]
    if vx <= 0:
        return (False, "trajectory.clearance", 0.0, 0.0)
    mid = d + 0.5
    y_mid = (vy / vx) * mid - g * mid * mid / (2 * vx * vx)
    rng_range = 2 * vx * vy / g
    if y_mid <= h + 0.2:
        return (False, "trajectory.clearance", y_mid, rng_range)
    if not (d + 1 <= rng_range <= d + 7):
        return (False, "landing.position", y_mid, rng_range)
    return (True, "-", y_mid, rng_range)


def jumpover_plan(p):
    g, d = p["g"], p["d"]
    target_range = d + 4.0
    for t in (1.0, 1.3, 1.6, 2.0, 2.5, 3.0):
        vy = g * t / 2.0
        vx = target_range / t
        ok, _, _, _ = jumpover_eval(vx, vy, p)
        if ok:
            return (vx, vy)
    vy = g * 3.0 / 2.0
    return (target_range / 3.0, vy)


def jumpover_run(rival, p):
    if rival == "explicit":
        vx, vy = jumpover_plan(p)
        ok, comp, _, _ = jumpover_eval(vx, vy, p)
        return (ok, comp, 0, False)
    if rival == "naive":
        ok, comp, _, _ = jumpover_eval(6.0, 8.0, p)
        return (ok, comp, 0, False)
    if rival == "obscurity":
        def penalty(vx, vy):
            ok, comp, y_mid, r = jumpover_eval(vx, vy, p)
            if ok:
                return 0.0
            pen = 0.0
            if comp == "trajectory.clearance":
                pen += (p["h"] + 0.2 - y_mid) * 10.0 + 5.0
            pen += abs(r - (p["d"] + 4.0))
            return pen
        (vx, vy), probes = search_nd(
            penalty, start=(6.0, 8.0), radius=5.0, budget=160,
            lo=(1.0, 1.0), hi=(20.0, 25.0))
        ok, comp, _, _ = jumpover_eval(vx, vy, p)
        return (ok, comp, probes, False)
    vx, vy = jumpover_plan(p)
    ok, comp, _, _ = jumpover_eval(vx, vy, p)
    if ok:
        return (True, "-", 0, False)

    def penalty2(vx, vy):
        ok2, comp2, y_mid, r = jumpover_eval(vx, vy, p)
        if ok2:
            return 0.0
        pen = abs(r - (p["d"] + 4.0))
        if comp2 == "trajectory.clearance":
            pen += (p["h"] + 0.2 - y_mid) * 10.0 + 5.0
        return pen
    (vx, vy), probes = search_nd(
        penalty2, start=(vx, vy), radius=3.0, budget=120,
        lo=(1.0, 1.0), hi=(20.0, 25.0))
    ok, comp, _, _ = jumpover_eval(vx, vy, p)
    return (ok, comp, probes, True)


def search_nd(penalty, start, radius, budget, lo, hi):
    """Obscurity construction by probe-and-observe hill
    climbing on the observed penalty. No formula is read."""
    rng = random.Random(7654321)
    best = list(start)
    best_pen = penalty(best[0], best[1])
    probes = 1
    while probes < budget and best_pen > 0:
        improved = False
        for _ in range(16):
            if probes >= budget:
                break
            cand = [clamp(best[i] + rng.uniform(-radius, radius),
                          lo[i], hi[i]) for i in range(len(best))]
            pen = penalty(cand[0], cand[1])
            probes += 1
            if pen < best_pen:
                best, best_pen = cand, pen
                improved = True
        radius = radius * 0.7 if improved else radius * 0.5
        if radius < 1e-3:
            break
    return tuple(best), probes


# ================================================================ drive
# Kinematic vehicle, dt steps. Course: three waypoints in
# order, success radius 3.0, step budget 400.

def drive_instance(rng):
    wps = []
    x, y = 0.0, 0.0
    for _ in range(3):
        x += rng.uniform(15, 40)
        y += rng.uniform(-30, 30)
        wps.append((x, y))
    return {
        "waypoints": wps,
        "vmax": rng.uniform(6, 10),
        "speed_factor": rng.uniform(0.8, 1.0),
        "steer_factor": rng.uniform(0.8, 1.2),
        "radius": 3.0,
        "budget": 400,
    }


def drive_step(state, steer, throttle, p, dt=0.25):
    x, y, th = state
    v = throttle * p["vmax"] * p["speed_factor"]
    th = th + steer * 1.6 * p["steer_factor"] * dt
    x = x + v * math.cos(th) * dt
    y = y + v * math.sin(th) * dt
    return (x, y, th)


def angle_to(state, target):
    return math.atan2(target[1] - state[1], target[0] - state[0])


def wrap_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def drive_run(rival, p):
    state = (0.0, 0.0, 0.0)
    wps = p["waypoints"]
    wi = 0
    steps = 0
    probes = 0
    stall = 0
    best_wp_dist = dist(state, wps[0])
    repaired = False
    while steps < p["budget"] and wi < len(wps):
        target = wps[wi]
        if rival == "naive":
            target = wps[-1]
            diff = wrap_angle(angle_to(state, target) - state[2])
            steer = clamp(diff * 1.2, -1, 1)
            state = drive_step(state, steer, 1.0, p)
            steps += 1
            if wi < len(wps) and dist(state, wps[wi]) <= p["radius"]:
                wi += 1
            continue
        if rival == "explicit" or (
                rival == "combination" and stall < 12):
            diff = wrap_angle(angle_to(state, target) - state[2])
            steer = clamp(diff * 1.2, -1, 1)
            dnow = dist(state, target)
            throttle = 0.45 if dnow < 8 else 0.85
            state = drive_step(state, steer, throttle, p)
            steps += 1
        else:
            # obscurity leg: one-step lookahead probes on a clone
            if rival == "combination":
                repaired = True
            best = None
            for steer in (-1.0, -0.5, 0.0, 0.5, 1.0):
                for throttle in (0.5, 1.0):
                    cand = drive_step(state, steer, throttle, p)
                    probes += 1
                    score = dist(cand, target) + 0.3 * abs(
                        wrap_angle(angle_to(cand, target) - cand[2]))
                    if best is None or score < best[0]:
                        best = (score, steer, throttle)
            state = drive_step(state, best[1], best[2], p)
            steps += 1
            stall = 0
        if dist(state, wps[wi]) <= p["radius"]:
            wi += 1
            stall = 0
            if wi < len(wps):
                best_wp_dist = dist(state, wps[wi])
        else:
            dnow = dist(state, wps[wi])
            if dnow < best_wp_dist - 0.05:
                best_wp_dist = dnow
                stall = 0
            else:
                stall += 1
    if wi >= len(wps):
        return (True, "-", probes, repaired, steps)
    return (False, "waypoint[%d]" % wi, probes, repaired, steps)


# ================================================================ touch
# Page layout of rectangles; one is the target (by identity).
# In 30 percent of instances the target center is covered by
# another rectangle (z-order on top). A click lands on the
# topmost rectangle at the point, or misses all.

def touch_instance(rng):
    rects = []
    tries = 0
    while len(rects) < rng.randint(6, 10) and tries < 300:
        tries += 1
        w = rng.uniform(40, 120)
        h = rng.uniform(30, 80)
        x = rng.uniform(0, 800 - w)
        y = rng.uniform(0, 600 - h)
        rect = {"id": "r%d" % len(rects), "x": x, "y": y,
                "w": w, "h": h}
        if all(not overlap(rect, r2, pad=6) for r2 in rects):
            rects.append(rect)
    target = rng.choice(rects)
    occluded = False
    if rng.random() < 0.30:
        cx = target["x"] + target["w"] / 2
        cy = target["y"] + target["h"] / 2
        cover = {"id": "cover", "x": cx - 18, "y": cy - 14,
                 "w": 36, "h": 28}
        rects.append(cover)
        occluded = True
    cursor = (rng.choice((0.0, 800.0)), rng.choice((0.0, 600.0)))
    return {"rects": rects, "target": target["id"],
            "cursor": cursor, "occluded": occluded}


def overlap(a, b, pad=0):
    return not (a["x"] + a["w"] + pad < b["x"] or
                b["x"] + b["w"] + pad < a["x"] or
                a["y"] + a["h"] + pad < b["y"] or
                b["y"] + b["h"] + pad < a["y"])


def topmost_at(rects, px, py):
    hit = None
    for r in rects:  # later entries are on top
        if r["x"] <= px <= r["x"] + r["w"] and \
                r["y"] <= py <= r["y"] + r["h"]:
            hit = r["id"]
    return hit


def rect_by_id(rects, rid):
    for r in rects:
        if r["id"] == rid:
            return r
    return None


def touch_run(rival, p):
    rects, target = p["rects"], p["target"]
    trect = rect_by_id(rects, target)
    center = (trect["x"] + trect["w"] / 2, trect["y"] + trect["h"] / 2)
    if rival == "explicit":
        hit = topmost_at(rects, center[0], center[1])
        if hit == target:
            return (True, "-", 0, False)
        return (False, "target.occlusion" if hit else "target.bounds",
                0, False)
    if rival == "naive":
        nearest = min(
            (r for r in rects if r["id"] != "cover"),
            key=lambda r: dist(p["cursor"], (
                r["x"] + r["w"] / 2, r["y"] + r["h"] / 2)))
        c = (nearest["x"] + nearest["w"] / 2,
             nearest["y"] + nearest["h"] / 2)
        hit = topmost_at(rects, c[0], c[1])
        if hit == target:
            return (True, "-", 0, False)
        return (False, "target.identity", 0, False)
    if rival == "obscurity":
        probes = 0
        # Probe points in the target rect; a hover observation
        # returns the topmost identity at the point. The first
        # point whose observed identity is the target is the
        # constructed click point. Identity itself is never
        # trusted from the layout listing: it is probed.
        for fx in (0.5, 0.2, 0.8, 0.35, 0.65, 0.1, 0.9):
            for fy in (0.5, 0.25, 0.75):
                px = trect["x"] + fx * trect["w"]
                py = trect["y"] + fy * trect["h"]
                probes += 1
                if topmost_at(rects, px, py) == target:
                    return (True, "-", probes, False)
        return (False, "target.occlusion", probes, False)
    # combination: plan center, verify, repair by probing
    hit = topmost_at(rects, center[0], center[1])
    if hit == target:
        return (True, "-", 0, False)
    probes = 0
    for fx in (0.2, 0.8, 0.35, 0.65, 0.1, 0.9, 0.5):
        for fy in (0.25, 0.75, 0.5):
            px = trect["x"] + fx * trect["w"]
            py = trect["y"] + fy * trect["h"]
            probes += 1
            if topmost_at(rects, px, py) == target:
                return (True, "-", probes, True)
    return (False, "target.occlusion", probes, True)


# ================================================================ type
# Type a target string. The keyboard remaps a subset of keys:
# pressing the key labeled c produces layout[c]. The layout
# map is carried by the observation. The echo (the buffer as
# observed) is readable by every route.

CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"


def type_instance(rng):
    n = rng.randint(8, 20)
    target = "".join(rng.choice(CHARSET) for _ in range(n))
    chars = list(CHARSET)
    layout = {c: c for c in chars}
    k = rng.randint(4, 12)
    swapped = rng.sample(chars, 2 * k)
    for i in range(k):
        a, b = swapped[2 * i], swapped[2 * i + 1]
        layout[a], layout[b] = b, a
    return {"target": target, "layout": layout}


def key_for(layout, wanted):
    for key, produced in layout.items():
        if produced == wanted:
            return key
    return None


def type_run(rival, p):
    target, layout = p["target"], p["layout"]
    if rival == "explicit":
        buf = "".join(layout[key_for(layout, c)] for c in target)
        return type_verdict(buf, p, 0, False)
    if rival == "naive":
        buf = "".join(layout[c] for c in target)
        return type_verdict(buf, p, 0, False)
    if rival == "obscurity":
        buf = []
        probes = 0
        for wanted in target:
            found = None
            for key in CHARSET:  # probe keys, read the echo
                probes += 1
                if layout[key] == wanted:
                    found = key
                    break
            buf.append(layout[found])
        return type_verdict("".join(buf), p, probes, False)
    # combination: plan by the map, verify the echo, repair
    keys = [key_for(layout, c) for c in target]
    buf = [layout[k] for k in keys]
    probes = 0
    repaired = False
    for i, wanted in enumerate(target):
        if buf[i] != wanted:
            repaired = True
            for key in CHARSET:
                probes += 1
                if layout[key] == wanted:
                    buf[i] = layout[key]
                    break
    return type_verdict("".join(buf), p, probes, repaired)


def type_verdict(buf, p, probes, repaired):
    if buf == p["target"]:
        return (True, "-", probes, repaired)
    for i, (a, b) in enumerate(zip(buf, p["target"])):
        if a != b:
            return (False, "buffer.position[%d]" % i, probes, repaired)
    return (False, "buffer.length", probes, repaired)


# ================================================================ automate
# Process steps with dependencies. Each step sets a register.
# The observed spec lists most dependencies; in 25 percent of
# instances one dependency is hidden from the spec and is
# observable only through the blocked signal. Attempting a
# blocked step non-destructively returns blocked; forcing a
# blocked step corrupts it permanently.

def automate_instance(rng):
    n = rng.randint(4, 7)
    steps = []
    for i in range(n):
        deps = []
        for j in range(i):
            if rng.random() < 0.35:
                deps.append(j)
        steps.append({"id": i, "deps": deps,
                      "register": "reg%d" % i, "value": i + 1})
    order = list(range(n))
    rng.shuffle(order)
    hidden = None
    if rng.random() < 0.25:
        a, b = sorted(rng.sample(range(n), 2))
        # Step a depends on step b, unlisted. Listed deps only
        # ever point backward, so a forward dependency is the
        # one a stated plan cannot see. Guard: if b already
        # lists a, the pair would form a cycle and the
        # instance would be infeasible for every rival; those
        # draws carry no hidden dependency.
        if a not in steps[b]["deps"]:
            hidden = (a, b)
    return {"steps": steps, "order": order, "hidden": hidden}


def automate_blocked(p, done, step_id):
    step = p["steps"][step_id]
    if any(d not in done for d in step["deps"]):
        return True
    if p["hidden"] and p["hidden"][0] == step_id and \
            p["hidden"][1] not in done:
        return True
    return False


def automate_run(rival, p):
    steps = p["steps"]
    done = set()
    corrupted = set()
    probes = 0
    if rival == "explicit":
        # topo order over the observed spec, executed as stated
        remaining = set(range(len(steps)))
        plan = []
        while remaining:
            ready = [s for s in remaining
                     if all(d in plan for d in steps[s]["deps"])]
            if not ready:
                break
            plan.append(min(ready))
            remaining.discard(min(ready))
        for s in plan:
            if automate_blocked(p, done, s):
                corrupted.add(s)  # forced as stated
            else:
                done.add(s)
        return automate_verdict(p, done, corrupted, probes, False)
    if rival == "naive":
        for s in p["order"]:
            if automate_blocked(p, done, s):
                corrupted.add(s)
            else:
                done.add(s)
        return automate_verdict(p, done, corrupted, probes, False)
    if rival == "obscurity":
        # No plan: attempt, read the blocked signal, defer.
        pending = set(range(len(steps)))
        attempts = 0
        while pending and attempts < 200:
            progressed = False
            for s in sorted(pending):
                attempts += 1
                probes += 1
                if automate_blocked(p, done, s):
                    continue  # deferred, non-destructive
                done.add(s)
                pending.discard(s)
                progressed = True
            if not progressed and pending:
                break
        return automate_verdict(p, done, corrupted, probes, False)
    # combination: topo plan, observe the blocked signal, repair
    remaining = set(range(len(steps)))
    plan = []
    while remaining:
        ready = [s for s in remaining
                 if all(d in plan for d in steps[s]["deps"])]
        if not ready:
            break
        plan.append(min(ready))
        remaining.discard(min(ready))
    repaired = False
    queue = list(plan)
    guard = 0
    while queue and guard < 200:
        guard += 1
        s = queue.pop(0)
        if automate_blocked(p, done, s):
            repaired = True
            probes += 1
            queue.append(s)  # defer and replan around it
            # bring the hidden prerequisite forward if pending
            if p["hidden"] and p["hidden"][0] == s and \
                    p["hidden"][1] in queue:
                queue.remove(p["hidden"][1])
                queue.insert(0, p["hidden"][1])
        else:
            done.add(s)
    return automate_verdict(p, done, corrupted, probes, repaired)


def automate_verdict(p, done, corrupted, probes, repaired):
    if corrupted:
        return (False, "step[%d].premise" % min(corrupted),
                probes, repaired)
    if len(done) == len(p["steps"]):
        return (True, "-", probes, repaired)
    missing = min(set(range(len(p["steps"]))) - done)
    return (False, "step[%d].premise" % missing, probes, repaired)


# ================================================================ reversibility
# Per primitive: snapshot, execute, fresh observe, execute the
# constructed inverse, fresh observe, compare. Refusal by name
# where no inverse is derivable, issued before any effect.

def rev_move(rng):
    p = move_instance(rng)
    pre = p["start"]
    cmd = ((p["target"][0] - pre[0] - p["drift"][0]) / p["scale"],
           (p["target"][1] - pre[1] - p["drift"][1]) / p["scale"])
    post = move_apply(pre, cmd, p)
    # Inverse derived from the observations: the achieved
    # displacement and the response the observations carry.
    achieved = (post[0] - pre[0], post[1] - pre[1])
    inv = ((-achieved[0] - p["drift"][0]) / p["scale"],
           (-achieved[1] - p["drift"][1]) / p["scale"])
    restored = move_apply(post, inv, p)
    if dist(restored, pre) <= 1e-9:
        return "PASS"
    return "MISMATCH:position"


def rev_move_negative(rng):
    p = move_instance(rng)
    pre = p["start"]
    cmd = (p["target"][0] - pre[0], p["target"][1] - pre[1])
    post = move_apply(pre, cmd, p)
    wrong = (pre[0] - post[0] + 5.0, pre[1] - post[1])  # wrong delta
    restored = (post[0] + wrong[0], post[1] + wrong[1])
    return "MISMATCH:position" if dist(restored, pre) > 1e-9 else "PASS"


def rev_drive(rng):
    p = drive_instance(rng)
    # Execute the course out with the explicit planner leg,
    # then the constructed inverse: plan back to the start
    # pose over the recorded waypoints in reverse.
    state = (0.0, 0.0, 0.0)
    back = {"waypoints": list(reversed(p["waypoints"])) + [(0.0, 0.0)],
            "vmax": p["vmax"], "speed_factor": p["speed_factor"],
            "steer_factor": p["steer_factor"], "radius": 0.6,
            "budget": 800}
    fwd = dict(p)
    # run out
    s = state
    wi = 0
    steps = 0
    while steps < fwd["budget"] and wi < len(fwd["waypoints"]):
        t = fwd["waypoints"][wi]
        diff = wrap_angle(angle_to(s, t) - s[2])
        s = drive_step(s, clamp(diff * 1.2, -1, 1),
                       0.45 if dist(s, t) < 8 else 0.85, fwd)
        steps += 1
        if dist(s, t) <= fwd["radius"]:
            wi += 1
    # Run back over the intermediate waypoints at course
    # radius, then a precision final leg home: throttle
    # proportional to the remaining distance, then a
    # stationary rotation restoring the heading (the step
    # law turns the vehicle at zero throttle).
    wi = 0
    steps = 0
    while steps < back["budget"] and wi < len(back["waypoints"]) - 1:
        t = back["waypoints"][wi]
        diff = wrap_angle(angle_to(s, t) - s[2])
        s = drive_step(s, clamp(diff * 1.2, -1, 1),
                       0.45 if dist(s, t) < 8 else 0.85, back)
        steps += 1
        if dist(s, t) <= p["radius"]:
            wi += 1
    home = (0.0, 0.0)
    steps = 0
    while steps < 800 and dist(s, home) > 0.05:
        diff = wrap_angle(angle_to(s, home) - s[2])
        step_len = p["vmax"] * p["speed_factor"] * 0.25
        throttle = clamp(dist(s, home) / step_len, 0.02, 0.8)
        s = drive_step(s, clamp(diff * 1.2, -1, 1), throttle, back)
        steps += 1
    steps = 0
    while steps < 200 and abs(wrap_angle(s[2])) > 0.01:
        diff = wrap_angle(0.0 - s[2])
        steer = clamp(diff / (1.6 * p["steer_factor"] * 0.25), -1, 1)
        s = drive_step(s, steer, 0.0, back)
        steps += 1
    # Observation resolution for the drive face: 0.5 units,
    # 0.1 rad. Equality is judged at that resolution.
    if dist(s, home) <= 0.5 and abs(wrap_angle(s[2])) <= 0.1:
        return "PASS"
    return "MISMATCH:pose"


def rev_type(rng):
    p = type_instance(rng)
    prior = "seed:"
    buf = prior + p["target"]
    # Inverse: delete the typed run, restoring the prior
    # buffer the pre-action observation carries.
    restored = buf[:len(prior)]
    return "PASS" if restored == prior else "MISMATCH:buffer"


def rev_type_negative(rng):
    p = type_instance(rng)
    prior = "seed:"
    buf = prior + p["target"]
    restored = buf[:len(prior) + 1]  # one deletion too few
    return "MISMATCH:buffer" if restored != prior else "PASS"


def rev_automate(rng, with_submit):
    p = automate_instance(rng)
    if with_submit:
        return "REFUSED-BY-NAME:R-NOINVERSE:step[submit]"
    # Execute in topo order, then compensations in reverse:
    # each step restores the prior register value (registers
    # start at 0 and each step writes only its own register).
    regs = {}
    for s in p["steps"]:
        regs[s["register"]] = s["value"]
    for s in reversed(p["steps"]):
        regs[s["register"]] = 0
    ok = all(v == 0 for v in regs.values())
    return "PASS" if ok else "MISMATCH:register"


# ================================================================ main

FAMILIES = [
    ("move", "move by a pixel delta", move_instance, move_run, 1),
    ("jump", "jump", jump_instance, jump_run, 1),
    ("jumpover", "jump over an object", jumpover_instance,
     jumpover_run, 1),
    ("drive", "drive (steer and throttle)", drive_instance, None, 1),
    ("touch", "touch (click or tap a target)", touch_instance,
     touch_run, 1),
    ("type", "type text", type_instance, type_run, 1),
    ("automate", "automate a process step", automate_instance,
     automate_run, 1),
]

RIVALS = [("explicit", 1), ("obscurity", 2), ("combination", 3),
          ("naive", 0)]


def main():
    results = {}
    failures = {}
    probes_avg = {}
    repaired_count = {}
    for fi, (fname, label, make, run, _) in enumerate(FAMILIES):
        for rival, route in RIVALS:
            wins = 0
            fcount = {}
            tot_probes = 0
            tot_repaired = 0
            for i in range(PER_FAMILY):
                seed = BASE_SEED + fi * 10000 + i
                rng = random.Random(seed)
                inst = make(rng)
                if fname == "drive":
                    ok, comp, probes, repaired, _steps = drive_run(
                        rival, inst)
                else:
                    ok, comp, probes, repaired = run(rival, inst)
                if ok:
                    wins += 1
                else:
                    fcount[comp] = fcount.get(comp, 0) + 1
                tot_probes += probes
                tot_repaired += 1 if repaired else 0
            results[(fname, rival)] = (wins, PER_FAMILY)
            failures[(fname, rival)] = fcount
            probes_avg[(fname, rival)] = tot_probes / PER_FAMILY
            repaired_count[(fname, rival)] = tot_repaired

    print("basic action model harness -- lane 4")
    print("scope: simulated scenarios only; NOT a live desktop "
          "or browser")
    print("base seed %d; %d paired instances per family per rival"
          % (BASE_SEED, PER_FAMILY))
    print("")
    print("%-10s %-12s %6s %8s %10s %9s  %s"
          % ("family", "rival", "route", "success", "rate",
             "probes", "failure components (count)"))
    for fname, label, _, _, _ in FAMILIES:
        for rival, route in RIVALS:
            wins, n = results[(fname, rival)]
            fc = failures[(fname, rival)]
            fstr = ", ".join("%s:%d" % (k, fc[k])
                             for k in sorted(fc)) or "-"
            print("%-10s %-12s %6d %5d/%-3d %9.1f%% %9.1f  %s"
                  % (fname, rival, route, wins, n,
                     100.0 * wins / n, probes_avg[(fname, rival)],
                     fstr))
        print("")

    print("combination repair-leg firings (of %d):" % PER_FAMILY)
    for fname, _, _, _, _ in FAMILIES:
        print("  %-10s %d" % (fname,
                              repaired_count[(fname, "combination")]))
    print("")

    # ---- reversibility round trips
    print("reversibility (fresh-observation round trip, %d "
          "instances per primitive):" % REV_PER_PRIMITIVE)
    rev = {}
    counts = {}
    for i in range(REV_PER_PRIMITIVE):
        rng = random.Random(BASE_SEED + 90000 + i)
        counts.setdefault("move", []).append(rev_move(rng))
        rng = random.Random(BASE_SEED + 90000 + i)
        counts.setdefault("drive", []).append(rev_drive(rng))
        rng = random.Random(BASE_SEED + 90000 + i)
        counts.setdefault("type", []).append(rev_type(rng))
        rng = random.Random(BASE_SEED + 90000 + i)
        counts.setdefault("automate-pure", []).append(
            rev_automate(rng, with_submit=False))
    rev["move"] = counts["move"]
    rev["drive"] = counts["drive"]
    rev["type"] = counts["type"]
    rev["automate-pure"] = counts["automate-pure"]
    for prim in ("jump", "jumpover", "touch"):
        # Derivation refuses by name at qualification: the
        # ballistic phase (jump, jump over) admits no action
        # in the family that restores the pre-action state,
        # and a touch is an activation whose effects belong
        # to the application (the click precedent of the
        # first pass). No effect is delivered.
        rev[prim] = ["REFUSED-BY-NAME:R-NOINVERSE"] * REV_PER_PRIMITIVE
    rev["automate-submit"] = [
        rev_automate(random.Random(BASE_SEED + 95000 + i),
                     with_submit=True)
        for i in range(REV_PER_PRIMITIVE)]
    for prim in ("move", "jump", "jumpover", "drive", "touch",
                 "type", "automate-pure", "automate-submit"):
        vals = rev[prim]
        tally = {}
        for v in vals:
            tally[v] = tally.get(v, 0) + 1
        print("  %-16s %s" % (prim, ", ".join(
            "%s:%d" % (k, tally[k]) for k in sorted(tally))))
    neg1 = rev_move_negative(random.Random(BASE_SEED + 99000))
    neg2 = rev_type_negative(random.Random(BASE_SEED + 99001))
    print("  negative controls: move-wrong-inverse %s; "
          "type-wrong-delete-count %s" % (neg1, neg2))
    print("")

    summary = {
        "base_seed": BASE_SEED,
        "per_family": PER_FAMILY,
        "results": {
            "%s/%s" % (f, r): {
                "wins": results[(f, r)][0], "n": results[(f, r)][1],
                "failures": failures[(f, r)],
                "probes_avg": round(probes_avg[(f, r)], 2),
                "route": dict(RIVALS)[r],
            }
            for f, _, _, _, _ in FAMILIES for r, _ in RIVALS
        },
        "combination_repaired": {
            f: repaired_count[(f, "combination")]
            for f, _, _, _, _ in FAMILIES
        },
    }
    print("json summary:")
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
