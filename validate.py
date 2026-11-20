#!/usr/bin/env python3
"""Reversibility validation harness for idol-eyes actions.

Lane 4 first pass, for the reversible search-space program.
Implements the rule in candidate-space-scratch/eyes/docs/harness.md
requirement 2 and protocol/harness.id exactly, over an in-memory
state model faithful to the harness vocabulary:

  set      inverts to set of the value the observation carries
  check    inverts to uncheck, when the carried state is unchecked
  uncheck  inverts to check, when the carried state is checked
  toggle   inverts to toggle, when a state is carried
  navigate (browser face) inverts to navigate of the prior
           place the observation carries
  click    no semantic inverse is derivable: refusal by name
           R-NOINVERSE (harness.id vocabulary)

Per action the harness:
  (1) snapshots the pre-action state via observe(),
  (2) executes the action on the live state model,
  (3) takes a FRESH observation of the post-action state via
      observe() -- never reusing the action's own report
      (action executors return nothing used as evidence),
  (4) executes the constructed inverse,
  (5) takes a fresh observation again via observe() and
      compares it for exact equality against the pre-action
      snapshot. Equality is PASS; any difference is MISMATCH
      naming the differing component(s).

For click, inverse derivation refuses by name before any
effect is delivered (harness.md solve loop, qualify step),
and the verdict is REFUSED-BY-NAME, never PASS.

Negative controls deliberately construct a wrong inverse.
They must produce MISMATCH; if they passed, this harness
could not detect failure and its PASS verdicts would mean
nothing.

Scope honesty: this validates the harness's state model,
NOT a live desktop or a live browser. No OS, accessibility
tree, or browser is touched.

Stdlib only. Deterministic: no clocks, no randomness.
"""

import copy
import hashlib
import json
import sys

# ---------------------------------------------------------------- state

class LiveState:
    """The mutable 'surface' behind observe(). Only observe()
    reads it for evidence; action executors mutate it and
    return nothing."""

    def __init__(self):
        self.face = "browser"
        # Field values, harness E-row value field. None = '-'
        # (the observation carries no value).
        self.fields = {"name": "Ada", "search": "idol"}
        # Checkbox states, harness E-row state field:
        # "checked" / "unchecked". None = '-' (no state carried).
        self.checkboxes = {"newsletter": "unchecked", "alerts": "checked"}
        # Navigation: history stack and the place it points at.
        # current / prior are derived from this stack, exactly
        # as the harness U row carries <current> <prior>.
        self.history = ["https://example.test/one"]
        self.history_index = 0
        # Application-owned activation effects. A click changes
        # this; no observation-derived inverse can undo it.
        self.click_effects = {"submit": 0}

    @property
    def current_place(self):
        return self.history[self.history_index]

    @property
    def prior_place(self):
        if self.history_index == 0:
            return None  # '-' in the U row: no place precedes it
        return self.history[self.history_index - 1]


def observe(state):
    """A fresh observation: a brand-new, deep snapshot built by
    re-reading the live state at call time. Nothing is cached
    and no action report is consulted."""
    return {
        "face": state.face,
        "fields": copy.deepcopy(state.fields),
        "checkboxes": copy.deepcopy(state.checkboxes),
        "navigation": {
            "current": state.current_place,
            "prior": state.prior_place,
            # Visible history: the traversal path up to the
            # current place, as an observation carries it.
            "history": list(state.history[: state.history_index + 1]),
            "index": state.history_index,
        },
        "click_effects": copy.deepcopy(state.click_effects),
    }


def snapshot_hash(snapshot):
    blob = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def snapshot_summary(snapshot):
    nav = snapshot["navigation"]
    return (
        "fields=%r checkboxes=%r nav.current=%r nav.prior=%r "
        "nav.history=%r clicks=%r"
        % (
            snapshot["fields"],
            snapshot["checkboxes"],
            nav["current"],
            nav["prior"],
            nav["history"],
            snapshot["click_effects"],
        )
    )


def diff_snapshots(pre, restored, path=""):
    """Return a list of differing component paths, recursively.
    Exact equality over the whole snapshot is the verdict."""
    diffs = []
    if isinstance(pre, dict) and isinstance(restored, dict):
        for key in sorted(set(pre) | set(restored)):
            child = "%s.%s" % (path, key) if path else key
            if key not in pre:
                diffs.append("%s (only in restored: %r)" % (child, restored[key]))
            elif key not in restored:
                diffs.append("%s (only in pre: %r)" % (child, pre[key]))
            else:
                diffs.extend(diff_snapshots(pre[key], restored[key], child))
    elif pre != restored:
        diffs.append("%s (pre=%r restored=%r)" % (path, pre, restored))
    return diffs


# ------------------------------------------------------- inverse derivation

class Refusal:
    def __init__(self, code, action, message):
        self.code = code
        self.action = action
        self.message = message

    def __repr__(self):
        return "%s action=%s: %s" % (self.code, self.action, self.message)


def derive_inverse_from_pre(pre, action, target):
    """Derive the inverse from the pre-action observation alone,
    mirroring harness.id for set / check / uncheck / toggle /
    click. Returns an inverse tuple or a Refusal."""
    if action == "set":
        prior = pre["fields"].get(target)
        if prior is None or prior == "-":
            return Refusal(
                "R-NOINVERSE", "set",
                "the observation carries no prior value for this "
                "element; a set cannot be inverted without the "
                "value it replaces")
        return ("set", target, prior)
    if action == "check":
        state = pre["checkboxes"].get(target)
        if state == "unchecked":
            return ("uncheck", target, None)
        if state == "checked":
            return Refusal(
                "R-NOINVERSE", "check",
                "the element already holds the checked state; "
                "there is no state change to invert")
        return Refusal(
            "R-NOINVERSE", "check",
            "the observation carries no prior state for this "
            "element; a check cannot be inverted without the "
            "state it changes")
    if action == "uncheck":
        state = pre["checkboxes"].get(target)
        if state == "checked":
            return ("check", target, None)
        if state == "unchecked":
            return Refusal(
                "R-NOINVERSE", "uncheck",
                "the element already holds the unchecked state; "
                "there is no state change to invert")
        return Refusal(
            "R-NOINVERSE", "uncheck",
            "the observation carries no prior state for this "
            "element; an uncheck cannot be inverted without "
            "the state it changes")
    if action == "toggle":
        state = pre["checkboxes"].get(target)
        if state in ("checked", "unchecked"):
            return ("toggle", target, None)
        return Refusal(
            "R-NOINVERSE", "toggle",
            "the observation carries no prior state for this "
            "element; a toggle cannot be inverted without "
            "the state it flips")
    if action == "click":
        return Refusal(
            "R-NOINVERSE", "click",
            "an activation has no semantic inverse derivable "
            "from the observation; its effects belong to the "
            "application")
    if action == "navigate":
        # Qualification only, from the pre-action observation:
        # a navigation is reversible exactly when there is a
        # current place to return to. The exact inverse target
        # is read from the post-action fresh observation (see
        # derive_navigate_inverse_from_post), which is the
        # block whose U row carries the place the navigation
        # left as its prior place -- the harness.id arm.
        if pre["navigation"]["current"] is None:
            return Refusal(
                "R-NOINVERSE", "navigate",
                "the observation carries no current place; a "
                "navigation cannot be inverted without the "
                "place it leaves")
        return ("navigate-pending", None, None)
    return Refusal("R-ARGS", action, "unknown action")


def derive_navigate_inverse_from_post(post):
    """harness.id navigate arm, applied to the post-action fresh
    observation: inverts to navigate of the prior place that
    observation's U row carries."""
    if post["face"] != "browser":
        return Refusal(
            "R-NOINVERSE", "navigate",
            "navigate is a browser face action; this block is "
            "on the desktop face")
    prior = post["navigation"]["prior"]
    if prior is None or prior == "-":
        return Refusal(
            "R-NOINVERSE", "navigate",
            "the observation carries no prior place; a "
            "navigation cannot be inverted without the place "
            "it leaves")
    return ("navigate-back", None, prior)


# ------------------------------------------------------------ execution
# Executors mutate the live state and return nothing. Evidence
# comes only from observe() calls made after they run.

def execute_action(state, action, target, argument):
    if action == "set":
        state.fields[target] = argument
    elif action == "check":
        state.checkboxes[target] = "checked"
    elif action == "uncheck":
        state.checkboxes[target] = "unchecked"
    elif action == "toggle":
        current = state.checkboxes[target]
        state.checkboxes[target] = (
            "unchecked" if current == "checked" else "checked")
    elif action == "navigate":
        # Forward navigation: drop any forward entries, push
        # the new place, point at it. Prior becomes the place
        # this navigation leaves.
        del state.history[state.history_index + 1:]
        state.history.append(argument)
        state.history_index += 1
    elif action == "click":
        state.click_effects[target] += 1
    else:
        raise ValueError("unknown action %r" % (action,))


def execute_inverse(state, inverse):
    kind, target, argument = inverse
    if kind == "set":
        state.fields[target] = argument
    elif kind == "check":
        state.checkboxes[target] = "checked"
    elif kind == "uncheck":
        state.checkboxes[target] = "unchecked"
    elif kind == "toggle":
        current = state.checkboxes[target]
        state.checkboxes[target] = (
            "unchecked" if current == "checked" else "checked")
    elif kind == "navigate-back":
        # Returning to the prior place is a back traversal,
        # not a new forward entry: move the pointer back to
        # the named place. The visible history, current, and
        # prior in the next fresh observation are then the
        # pre-action ones if the round trip is exact.
        if state.current_place == argument:
            return
        state.history_index -= 1
        if state.current_place != argument:
            raise ValueError(
                "navigate-back target %r does not match history"
                % (argument,))
    else:
        raise ValueError("unknown inverse %r" % (inverse,))


# -------------------------------------------------------------- cases

class Result:
    def __init__(self, name, action, pre, verdict, differing, note):
        self.name = name
        self.action = action
        self.pre_hash = snapshot_hash(pre)
        self.pre_summary = snapshot_summary(pre)
        self.verdict = verdict
        self.differing = differing
        self.note = note


def run_round_trip(name, action, target, argument):
    """The five-step rule, for one derivable action."""
    state = LiveState()
    pre = observe(state)                                    # (1) snapshot
    derived = derive_inverse_from_pre(pre, action, target)
    if isinstance(derived, Refusal):
        return Result(name, action, pre, "REFUSED-BY-NAME",
                      "-", "refusal %s" % (derived,))
    execute_action(state, action, target, argument)         # (2) execute
    post = observe(state)                                   # (3) fresh obs
    if action == "navigate":
        inverse = derive_navigate_inverse_from_post(post)
        if isinstance(inverse, Refusal):
            return Result(name, action, pre, "REFUSED-BY-NAME",
                          "-", "refusal %s" % (inverse,))
        # Cross-check: the post-action prior place must be the
        # pre-action current place, or the model itself drifted.
        if post["navigation"]["prior"] != pre["navigation"]["current"]:
            return Result(
                name, action, pre, "MISMATCH",
                "navigation.prior",
                "post prior %r != pre current %r"
                % (post["navigation"]["prior"],
                   pre["navigation"]["current"]))
    else:
        inverse = derived
    execute_inverse(state, inverse)                         # (4) inverse
    restored = observe(state)                               # (5) fresh obs
    diffs = diff_snapshots(pre, restored)
    if not diffs:
        return Result(name, action, pre, "PASS", "-",
                      "inverse=%r" % (inverse,))
    return Result(name, action, pre, "MISMATCH",
                  "; ".join(diffs), "inverse=%r" % (inverse,))


def run_click(name):
    """Click: derivation refuses by name at qualification, so
    no effect is delivered and there is no round trip to pass."""
    state = LiveState()
    pre = observe(state)                                    # (1) snapshot
    derived = derive_inverse_from_pre(pre, "click", "submit")
    if isinstance(derived, Refusal):
        return Result(name, "click", pre, "REFUSED-BY-NAME", "-",
                      "refusal %s; action not delivered" % (derived,))
    return Result(name, "click", pre, "MISMATCH",
                  "derivation", "click unexpectedly derived %r"
                  % (derived,))


def run_negative_set_wrong_prior(name):
    """Negative control: set inverse carrying the WRONG prior
    value. Must produce MISMATCH on fields.name."""
    state = LiveState()
    pre = observe(state)                                    # (1)
    execute_action(state, "set", "name", "Grace")           # (2)
    observe(state)                                          # (3) fresh obs
    wrong_inverse = ("set", "name", "NotAda")  # deliberate error
    execute_inverse(state, wrong_inverse)                   # (4)
    restored = observe(state)                               # (5)
    diffs = diff_snapshots(pre, restored)
    verdict = "MISMATCH" if diffs else "PASS"
    return Result(name, "set (negative control)", pre, verdict,
                  "; ".join(diffs) if diffs else "-",
                  "deliberately wrong inverse=%r" % (wrong_inverse,))


def run_negative_toggle_double_from_stale(name):
    """Negative control: toggle inverse applied TWICE, as if
    re-derived from a stale observation and replayed. Must
    produce MISMATCH on checkboxes.newsletter."""
    state = LiveState()
    pre = observe(state)                                    # (1)
    execute_action(state, "toggle", "newsletter", None)     # (2)
    observe(state)                                          # (3) fresh obs
    stale_inverse = ("toggle", "newsletter", None)
    execute_inverse(state, stale_inverse)                   # (4) once: correct
    execute_inverse(state, stale_inverse)                   # (4) twice: wrong
    restored = observe(state)                               # (5)
    diffs = diff_snapshots(pre, restored)
    verdict = "MISMATCH" if diffs else "PASS"
    return Result(name, "toggle (negative control)", pre, verdict,
                  "; ".join(diffs) if diffs else "-",
                  "deliberately wrong inverse: toggle applied twice")


# ---------------------------------------------------------------- main

def main():
    results = [
        run_round_trip("set", "set", "name", "Grace"),
        run_round_trip("check", "check", "newsletter", None),
        run_round_trip("uncheck", "uncheck", "alerts", None),
        run_round_trip("toggle", "toggle", "newsletter", None),
        run_round_trip("navigate", "navigate", None,
                       "https://example.test/two"),
        run_click("click"),
        run_negative_set_wrong_prior("negative-set-wrong-prior"),
        run_negative_toggle_double_from_stale(
            "negative-toggle-double-from-stale"),
    ]

    print("reversibility validation harness -- lane 4 first pass")
    print("scope: in-memory state model only; NOT a live desktop "
          "or browser")
    print("rule: snapshot -> execute -> fresh observe -> execute "
          "inverse -> fresh observe -> exact equality")
    print("")
    print("%-34s %-26s %-16s %-16s %s"
          % ("case", "action", "pre-state hash", "verdict",
             "differing component"))
    for r in results:
        print("%-34s %-26s %-16s %-16s %s"
              % (r.name, r.action, r.pre_hash, r.verdict,
                 r.differing))
    print("")
    for r in results:
        print("case %s" % r.name)
        print("  pre-state: %s" % r.pre_summary)
        print("  note: %s" % r.note)
    print("")

    expected = {
        "set": "PASS",
        "check": "PASS",
        "uncheck": "PASS",
        "toggle": "PASS",
        "navigate": "PASS",
        "click": "REFUSED-BY-NAME",
        "negative-set-wrong-prior": "MISMATCH",
        "negative-toggle-double-from-stale": "MISMATCH",
    }
    failures = []
    for r in results:
        want = expected[r.name]
        if r.verdict != want:
            failures.append("%s: got %s, expected %s"
                            % (r.name, r.verdict, want))
    if failures:
        print("harness verdict: FAIL -- " + "; ".join(failures))
        return 1
    print("harness verdict: OK -- derivable actions PASS, click "
          "REFUSED-BY-NAME (R-NOINVERSE), both negative controls "
          "detected as MISMATCH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
