# Lane 4 first pass — reversibility validation harness: results

Harness: `~/workspace/reversible-scratch/validate.py` (Python, stdlib only)
Run command: `python3 ~/workspace/reversible-scratch/validate.py`
Exit code: 0. Output is deterministic (two consecutive runs byte-identical).

Source rule: `~/workspace/candidate-space-scratch/eyes/protocol/harness.id`
and `~/workspace/candidate-space-scratch/eyes/docs/harness.md`, requirement 2
(inverse derivation for set, check, uncheck, toggle, browser navigation;
named refusal R-NOINVERSE where no inverse is derivable, e.g. click).
Note: the parent record at `~/workspace/research/reversible-search-space-2026-11-20.md`
was not present at the stated path when this lane ran; the rule was taken
from the two harness files above, which the task named as read-first.

## Scope honesty

This validates the harness's state model, NOT a live desktop and NOT a
live browser. The state model is an in-memory page/block state faithful
to the harness vocabulary (field values for set, checkbox states for
check / uncheck / toggle, navigation history / current / prior place
for navigation, application-owned click effects for click). No OS,
accessibility tree, or browser was touched. A PASS here proves the
round-trip rule holds over that model; it is not evidence about any
live surface.

## Method (the system's rule, exactly)

For each action: (1) snapshot the pre-action state through `observe()`;
(2) execute the action on the live state model (executors return
nothing used as evidence); (3) take a FRESH observation of the
post-action state through `observe()` — never reusing the action's
own report; (4) execute the constructed inverse (derived from the
observation, per harness.id: set → set of the carried prior value,
check → uncheck, uncheck → check, toggle → toggle, navigate → navigate
to the prior place the post-action observation carries, cross-checked
against the pre-action current place); (5) take a fresh observation
again and compare it for exact equality against the pre-action
snapshot. Equality is PASS; any difference is MISMATCH naming the
differing component. For click, inverse derivation refuses by name
(R-NOINVERSE) at qualification, no effect is delivered, and the
verdict is REFUSED-BY-NAME — not a pass.

## Per-action verdict table

Pre-state (all cases, fresh model instance): fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
Pre-state hash (SHA-256, first 16 hex, over the canonical snapshot): 735466e2a7707b9e

| Case | Action | Pre-state hash | Verdict | Differing component |
|---|---|---|---|---|
| set | set name → 'Grace'; inverse set name → 'Ada' (carried prior) | 735466e2a7707b9e | PASS | — |
| check | check newsletter; inverse uncheck newsletter | 735466e2a7707b9e | PASS | — |
| uncheck | uncheck alerts; inverse check alerts | 735466e2a7707b9e | PASS | — |
| toggle | toggle newsletter; inverse toggle newsletter | 735466e2a7707b9e | PASS | — |
| navigate | navigate → https://example.test/two; inverse navigate-back → https://example.test/one (prior place carried by post-action observation) | 735466e2a7707b9e | PASS | — |
| click | click submit; inverse derivation refused | 735466e2a7707b9e | REFUSED-BY-NAME | — (refusal R-NOINVERSE, action=click) |
| negative-set-wrong-prior (negative control) | set name → 'Grace'; deliberately wrong inverse set name → 'NotAda' | 735466e2a7707b9e | MISMATCH | fields.name (pre='Ada' restored='NotAda') |
| negative-toggle-double-from-stale (negative control) | toggle newsletter; deliberately wrong inverse: toggle applied twice | 735466e2a7707b9e | MISMATCH | checkboxes.newsletter (pre='unchecked' restored='checked') |

Negative controls: both deliberately wrong inverses produced MISMATCH
with the differing component named, proving the harness can detect
failure — its PASS verdicts are not vacuous.

## Exact run output

```
reversibility validation harness -- lane 4 first pass
scope: in-memory state model only; NOT a live desktop or browser
rule: snapshot -> execute -> fresh observe -> execute inverse -> fresh observe -> exact equality

case                               action                     pre-state hash   verdict          differing component
set                                set                        735466e2a7707b9e PASS             -
check                              check                      735466e2a7707b9e PASS             -
uncheck                            uncheck                    735466e2a7707b9e PASS             -
toggle                             toggle                     735466e2a7707b9e PASS             -
navigate                           navigate                   735466e2a7707b9e PASS             -
click                              click                      735466e2a7707b9e REFUSED-BY-NAME  -
negative-set-wrong-prior           set (negative control)     735466e2a7707b9e MISMATCH         fields.name (pre='Ada' restored='NotAda')
negative-toggle-double-from-stale  toggle (negative control)  735466e2a7707b9e MISMATCH         checkboxes.newsletter (pre='unchecked' restored='checked')

case set
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: inverse=('set', 'name', 'Ada')
case check
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: inverse=('uncheck', 'newsletter', None)
case uncheck
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: inverse=('check', 'alerts', None)
case toggle
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: inverse=('toggle', 'newsletter', None)
case navigate
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: inverse=('navigate-back', None, 'https://example.test/one')
case click
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: refusal R-NOINVERSE action=click: an activation has no semantic inverse derivable from the observation; its effects belong to the application; action not delivered
case negative-set-wrong-prior
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: deliberately wrong inverse=('set', 'name', 'NotAda')
case negative-toggle-double-from-stale
  pre-state: fields={'name': 'Ada', 'search': 'idol'} checkboxes={'newsletter': 'unchecked', 'alerts': 'checked'} nav.current='https://example.test/one' nav.prior=None nav.history=['https://example.test/one'] clicks={'submit': 0}
  note: deliberately wrong inverse: toggle applied twice

harness verdict: OK -- derivable actions PASS, click REFUSED-BY-NAME (R-NOINVERSE), both negative controls detected as MISMATCH
```
