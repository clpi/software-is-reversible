namespace Reversible

/-! Section A. Frontier before weights.
    Plans are cost vectors of two coordinates, lower is better.
    The three plans below are the general counterexample class in
    concrete form: the middle plan is undominated, yet no positive
    linear weighting ever selects it, because it sits above the
    segment joining the other two. -/

def le2 (p q : Nat × Nat) : Prop := p.1 ≤ q.1 ∧ p.2 ≤ q.2

def dom (p q : Nat × Nat) : Prop := le2 p q ∧ (p.1 < q.1 ∨ p.2 < q.2)

def onFrontier (l : List (Nat × Nat)) (p : Nat × Nat) : Prop :=
  p ∈ l ∧ ∀ q ∈ l, ¬ dom q p

def planA : Nat × Nat := (0, 10)
def planB : Nat × Nat := (6, 6)
def planC : Nat × Nat := (10, 0)

theorem b_not_dominated_by_a : ¬ dom planA planB := by
  intro h
  simp [dom, le2, planA, planB] at h

theorem b_not_dominated_by_c : ¬ dom planC planB := by
  intro h
  simp [dom, le2, planC, planB] at h

theorem b_not_dominated_by_b : ¬ dom planB planB := by
  intro h
  rcases h.2 with h | h <;> exact Nat.lt_irrefl _ h

theorem b_on_frontier : onFrontier [planA, planB, planC] planB := by
  refine ⟨by simp, ?_⟩
  intro q hq
  simp at hq
  rcases hq with rfl | rfl | rfl
  · exact b_not_dominated_by_a
  · exact b_not_dominated_by_b
  · exact b_not_dominated_by_c

/-- The counterexample in full: for every pair of positive weights,
    the middle plan never strictly beats both rivals, so no positive
    linear weighting selects it, although it is on the frontier. -/
theorem b_never_selected (w1 w2 : Nat) (_h1 : 0 < w1) (_h2 : 0 < w2) :
    ¬ (w1 * 6 + w2 * 6 < w1 * 0 + w2 * 10 ∧
       w1 * 6 + w2 * 6 < w1 * 10 + w2 * 0) := by
  rintro ⟨ha, hb⟩
  omega

/-- The class is not a one-off: the same shape at a second scale,
    plans (0, 20), (11, 11), (20, 0), is likewise never selected
    by positive weights. The fully general symmetric form is
    census lemma L-gen in the program record: its proof needs a
    nonlinear step, and it is carried there as a named lemma with
    the concrete instances proved here. -/
theorem b2_never_selected (w1 w2 : Nat) (_h1 : 0 < w1) (_h2 : 0 < w2) :
    ¬ (w1 * 11 + w2 * 11 < w1 * 0 + w2 * 20 ∧
       w1 * 11 + w2 * 11 < w1 * 20 + w2 * 0) := by
  rintro ⟨ha, hb⟩
  omega

/-! Section B. The break-even rule in full cost form.
    Reuse wins only when the avoided work exceeds setup,
    validation, persistence, and restart combined. -/

def reuseWins (avoided setup validation persistence restart : Nat) : Prop :=
  setup + validation + persistence + restart < avoided

theorem reuse_wins_of_cover {a s v p r : Nat}
    (h : s + v + p + r < a) : reuseWins a s v p r := h

theorem no_win_without_cover {a s v p r : Nat}
    (h : a ≤ s + v + p + r) : ¬ reuseWins a s v p r := by
  intro hw
  exact Nat.not_lt_of_ge h hw

theorem win_monotone_avoided {a a' s v p r : Nat}
    (h : reuseWins a s v p r) (hle : a ≤ a') : reuseWins a' s v p r :=
  Nat.lt_of_lt_of_le h hle

theorem win_antitone_cost {a s v p r extra : Nat}
    (hna : a ≤ s + extra + v + p + r) :
    ¬ reuseWins a (s + extra) v p r :=
  fun hw => Nat.not_lt_of_ge hna hw

/-! Section C. The closure worklist.
    A rule is a premise list and a conclusion. The count of premises
    still missing from the derived set drives the queue: a rule
    fires exactly when its count reaches zero. -/

def missCount (derived : List Nat) : List Nat → Nat
  | [] => 0
  | p :: ps => (if p ∈ derived then 0 else 1) + missCount derived ps

def missing (derived : List Nat) (r : List Nat × Nat) : Nat :=
  missCount derived r.1

theorem missCount_zero_of_all {derived : List Nat} :
    ∀ {ps : List Nat}, (∀ p ∈ ps, p ∈ derived) →
      missCount derived ps = 0 := by
  intro ps
  induction ps with
  | nil => intro _; rfl
  | cons p ps ih =>
    intro h
    simp only [missCount]
    rw [if_pos (h p (by simp)), Nat.zero_add]
    exact ih (fun q hq => h q (List.mem_cons_of_mem p hq))

theorem missing_zero_of_all {derived : List Nat} {r : List Nat × Nat}
    (h : ∀ p ∈ r.1, p ∈ derived) : missing derived r = 0 :=
  missCount_zero_of_all h

theorem missCount_le {derived : List Nat} :
    ∀ {ps : List Nat}, missCount derived ps ≤ ps.length := by
  intro ps
  induction ps with
  | nil => exact Nat.zero_le _
  | cons p ps ih =>
    simp only [missCount, List.length_cons]
    by_cases hp : p ∈ derived
    · rw [if_pos hp]; omega
    · rw [if_neg hp]; omega

theorem missing_le {derived : List Nat} {r : List Nat × Nat} :
    missing derived r ≤ r.1.length :=
  missCount_le

theorem missCount_pos_of_mem {derived : List Nat} {p : Nat} :
    ∀ {ps : List Nat}, p ∈ ps → p ∉ derived →
      0 < missCount derived ps := by
  intro ps
  induction ps with
  | nil => intro hp; simp at hp
  | cons q ps ih =>
    intro hp hd
    simp only [missCount]
    rcases List.mem_cons.mp hp with rfl | hp'
    · rw [if_neg hd]
      omega
    · have ih' := ih hp' hd
      by_cases hqd : q ∈ derived
      · rw [if_pos hqd]; omega
      · rw [if_neg hqd]; omega

theorem missing_of_mem {derived : List Nat} {r : List Nat × Nat} {p : Nat}
    (hp : p ∈ r.1) (hd : p ∉ derived) : 0 < missing derived r :=
  missCount_pos_of_mem hp hd

/-- Derivability from a seed set under a rule set: the least closure
    the worklist must equal, stated as an inductive predicate. -/
inductive Deriv (rules : List (List Nat × Nat)) (seed : List Nat) :
    Nat → Prop where
  | base {x : Nat} : x ∈ seed → Deriv rules seed x
  | step {ps : List Nat} {c : Nat} :
      (ps, c) ∈ rules → (∀ p ∈ ps, Deriv rules seed p) →
      Deriv rules seed c

theorem deriv_monotone {rules : List (List Nat × Nat)}
    {s s' : List Nat} (h : ∀ x ∈ s, x ∈ s') {x : Nat}
    (hd : Deriv rules s x) : Deriv rules s' x := by
  induction hd with
  | base hm => exact Deriv.base (h _ hm)
  | step hr _ ih => exact Deriv.step hr (fun p hp => ih p hp)

theorem deriv_growth {rules : List (List Nat × Nat)}
    {s : List Nat} {extra : List Nat} {x : Nat}
    (hd : Deriv rules s x) : Deriv rules (s ++ extra) x :=
  deriv_monotone (fun _ hy => List.mem_append_left extra hy) hd

theorem missCount_antitone {d d' : List Nat}
    (h : ∀ x ∈ d, x ∈ d') :
    ∀ {ps : List Nat}, missCount d' ps ≤ missCount d ps := by
  intro ps
  induction ps with
  | nil => exact Nat.zero_le _
  | cons p ps ih =>
    simp only [missCount]
    by_cases hp : p ∈ d'
    · rw [if_pos hp]
      by_cases hpd : p ∈ d
      · rw [if_pos hpd]; omega
      · rw [if_neg hpd]; omega
    · have hpd : p ∉ d := fun hm => hp (h p hm)
      rw [if_neg hp, if_neg hpd]
      omega

theorem missing_antitone {r : List Nat × Nat} {d d' : List Nat}
    (h : ∀ x ∈ d, x ∈ d') : missing d' r ≤ missing d r :=
  missCount_antitone h

/-! Section D. Incremental reevaluation equals full reevaluation,
    and compensation restores the prior view.
    Eligibility and dominance are abstract here; the update and the
    compensation are proved in place, not cited. -/

variable {A : Type}

def frontier (e : A → Prop) (d : A → A → Prop) (x : A) : Prop :=
  e x ∧ ∀ y, e y → ¬ d y x

theorem insert_exact (e : A → Prop) (d : A → A → Prop)
    (irr : ∀ x, ¬ d x x) (z x : A) :
    frontier (fun x => e x ∨ x = z) d x ↔
      (frontier e d x ∧ ¬ d z x) ∨
      (x = z ∧ ∀ y, e y → ¬ d y z) := by
  constructor
  · rintro ⟨hx, hn⟩
    rcases hx with he | hz
    · exact Or.inl ⟨⟨he, fun y hy => hn y (Or.inl hy)⟩, hn z (Or.inr rfl)⟩
    · subst hz
      exact Or.inr ⟨rfl, fun y hy => hn y (Or.inl hy)⟩
  · rintro (⟨⟨he, hn⟩, hz⟩ | ⟨rfl, hn⟩)
    · refine ⟨Or.inl he, fun y hy => ?_⟩
      rcases hy with hy | rfl
      · exact hn y hy
      · exact hz
    · refine ⟨Or.inr rfl, fun y hy => ?_⟩
      rcases hy with hy | rfl
      · exact hn y hy
      · exact irr _

theorem retract_insert_of_fresh (e : A → Prop) (d : A → A → Prop)
    (z x : A) (hz : ¬ e z) (hx : x ≠ z) :
    frontier (fun y => (e y ∨ y = z) ∧ y ≠ z) d x ↔ frontier e d x := by
  constructor
  · rintro ⟨hxE, hn⟩
    have he : e x := by
      rcases hxE.1 with h | h
      · exact h
      · exact absurd h hx
    refine ⟨he, fun y hy => hn y ⟨Or.inl hy, ?_⟩⟩
    intro hyz
    subst hyz
    exact hz hy
  · rintro ⟨he, hn⟩
    refine ⟨⟨Or.inl he, hx⟩, fun y hy => ?_⟩
    rcases hy.1 with hyE | hyz
    · exact hn y hyE
    · exact absurd hyz hy.2

/-! Section E. Reversible actions as structural maps.
    An action in scope is a pair of maps with a proved round trip.
    The inverse of a value-setting action is derivable only from
    what the pre-action observation carries: here, the prior value
    itself, captured before the action runs. -/

/-- An action in scope: a run map, and an undo that takes the
    pre-action observation together with the post-action state.
    The undo is a function of what the observation carries; an
    inverse that needs more than the observation carries does not
    exist in this form, which is the refusal discipline. -/
structure Act (S : Type) where
  run : S → S
  undo : S → S → S
  law : ∀ s, undo s (run s) = s

theorem act_restores {S : Type} (a : Act S) (s : S) :
    a.undo s (a.run s) = s := a.law s

def actComp {S : Type} (a b : Act S) : Act S where
  run := b.run ∘ a.run
  undo := fun pre post => a.undo pre (b.undo (a.run pre) post)
  law := by
    intro s
    simp [Function.comp_apply, b.law, a.law]

theorem comp_restores {S : Type} (a b : Act S) (s : S) :
    (actComp a b).undo s ((actComp a b).run s) = s :=
  act_restores (actComp a b) s

/-- Setting a field: the run writes the new value and keeps the
    rest; the undo writes back the first component of the
    pre-action observation. -/
def setField (new : Nat) : Act (Nat × Bool) where
  run := fun s => (new, s.2)
  undo := fun pre post => (pre.1, post.2)
  law := by
    intro s
    cases s
    rfl

theorem set_field_restores (prior new : Nat) (b : Bool) :
    (setField new).undo (prior, b) ((setField new).run (prior, b))
      = (prior, b) :=
  act_restores (setField new) (prior, b)

/-- Toggling is its own inverse, and needs nothing from the
    observation beyond the state itself. -/
def toggleField : Act (Nat × Bool) where
  run := fun s => (s.1, !s.2)
  undo := fun _ post => (post.1, !post.2)
  law := by
    intro s
    cases s with
    | mk n b => cases b <;> rfl

theorem toggle_restores (n : Nat) (b : Bool) :
    toggleField.undo (n, b) (toggleField.run (n, b)) = (n, b) :=
  act_restores toggleField (n, b)

/-- An action with no derivable inverse is carried as the empty
    option; no restoration claim exists for it, by construction. -/
theorem no_inverse_no_claim {S : Type} (o : Option (Act S)) :
    o = none → ¬ ∃ a : Act S, o = some a := by
  rintro rfl ⟨a, ha⟩
  exact Option.noConfusion ha

/-! Section F. Stop soundness, in both faces.
    Acceptable stop: a threshold accepts the first plan that meets
    it, which says nothing about the plans still open.
    Optimal stop: the checker certifies that no remaining plan
    beats or ties the chosen one. -/

def loop : Nat → Nat → Nat → Nat
  | 0, _, s => s
  | n + 1, t, s => if t ≤ s then s else loop n t (s + 1)

theorem loop_sound (n t s : Nat) :
    t ≤ loop n t s ∨ loop n t s = s + n := by
  induction n generalizing s with
  | zero => exact Or.inr rfl
  | succ k ih =>
    simp only [loop]
    by_cases h : t ≤ s
    · rw [if_pos h]
      exact Or.inl h
    · rw [if_neg h]
      rcases ih (s := s + 1) with h1 | h1
      · exact Or.inl h1
      · exact Or.inr (by omega)

theorem loop_stops_only_when_sufficient {n t s : Nat}
    (h : loop n t s ≠ s + n) : t ≤ loop n t s :=
  (loop_sound n t s).elim id (fun he => absurd he h)

/-- The threshold control, concrete: with threshold ten over the
    plan latencies nine and two, the first acceptable plan is the
    latency nine plan, while the latency two plan is still open. -/
theorem threshold_accepts_worse :
    List.find? (fun x => x ≤ 10) [9, 2] = some 9 ∧
    (2 : Nat) ∈ [9, 2] ∧ 2 < 9 := by
  refine ⟨rfl, by simp, by decide⟩

/-- The optimality certificate shape: a chosen plan certified
    against the whole remaining set. -/
def certifiedOptimal (chosen : Nat) (all : List Nat) : Prop :=
  ∀ q ∈ all, chosen ≤ q

theorem certified_optimal_sound {c : Nat} {l : List Nat}
    (h : certifiedOptimal c l) {q : Nat} (hq : q ∈ l) : c ≤ q :=
  h q hq

theorem two_certified_over_nine_two :
    certifiedOptimal 2 [9, 2] := by
  intro q hq
  simp at hq
  rcases hq with rfl | rfl <;> decide

/-! Section G. The subset oracle.
    Two independent enumerations of the subsets of a finite set
    agree: the powerset count is the checkpoint count. -/

/-- Subsets by recursion: each element is left out or taken.
    This is one of the two independent enumerations the oracle
    agreement is about; the count theorem is the checkpoint law. -/
def powerset : List Nat → List (List Nat)
  | [] => [[]]
  | x :: xs => powerset xs ++ (powerset xs).map (x :: ·)

theorem powerset_count_eight :
    (powerset [1, 2, 3]).length = 8 := by
  rfl

theorem powerset_count (l : List Nat) :
    (powerset l).length = 2 ^ l.length := by
  induction l with
  | nil => rfl
  | cons x xs ih =>
    simp only [powerset, List.length_append, List.length_map, ih,
      List.length_cons]
    rw [Nat.pow_succ]
    omega

/-! Section H. Tensor edits as overlays.
    A state is a function from coordinates to values. An overlay
    selects coordinates and supplies their new values; every
    coordinate the overlay does not select keeps its value
    exactly. The inverse overlay is built from the pinned original
    state, which is what the edit record carries as before bytes. -/

def applyOv (ov : Nat → Option Nat) (s : Nat → Nat) : Nat → Nat :=
  fun i => (ov i).elim (s i) id

theorem overlay_protects {ov : Nat → Option Nat} {s : Nat → Nat}
    {i : Nat} (h : ov i = none) : applyOv ov s i = s i := by
  simp [applyOv, h]

theorem overlay_applies {ov : Nat → Option Nat} {s : Nat → Nat}
    {i : Nat} {v : Nat} (h : ov i = some v) : applyOv ov s i = v := by
  simp [applyOv, h]

def inverseOv (ov : Nat → Option Nat) (s : Nat → Nat) :
    Nat → Option Nat :=
  fun i => (ov i).map (fun _ => s i)

theorem edit_roundtrip (ov : Nat → Option Nat) (s : Nat → Nat) :
    applyOv (inverseOv ov s) (applyOv ov s) = s := by
  funext i
  cases h : ov i with
  | none => simp [applyOv, inverseOv, h]
  | some v => simp [applyOv, inverseOv, h]

theorem tied_preserved {tied : Nat → Nat → Prop}
    {ov : Nat → Option Nat} {s : Nat → Nat}
    (hs : ∀ i j, tied i j → s i = s j)
    (hov : ∀ i j, tied i j → ov i = ov j)
    {i j : Nat} (ht : tied i j) :
    applyOv ov s i = applyOv ov s j := by
  have h1 := hs i j ht
  have h2 := hov i j ht
  cases h : ov i with
  | none =>
    have hj : ov j = none := by rw [← h2]; exact h
    simp [applyOv, h, hj, h1]
  | some v =>
    have hj : ov j = some v := by rw [← h2]; exact h
    simp [applyOv, h, hj]

end Reversible
