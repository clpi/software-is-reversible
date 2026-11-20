import Lean

namespace CompositionalPruning

universe u v w

abbrev Cost (Axis : Type u) := Axis → Nat

def Weak {Axis : Type u} (x y : Cost Axis) : Prop := ∀ i, x i ≤ y i

def Dominates {Axis : Type u} (x y : Cost Axis) : Prop :=
  Weak x y ∧ ∃ i, x i < y i

theorem weak_refl {Axis : Type u} (x : Cost Axis) : Weak x x :=
  fun _ => Nat.le_refl _

theorem weak_dominates {Axis : Type u} {x y z : Cost Axis}
    (h₁ : Weak x y) (h₂ : Dominates y z) : Dominates x z := by
  obtain ⟨hy, i, hi⟩ := h₂
  exact ⟨fun k => Nat.le_trans (h₁ k) (hy k), i, Nat.lt_of_le_of_lt (h₁ i) hi⟩

theorem dominates_weak {Axis : Type u} {x y z : Cost Axis}
    (h₁ : Dominates x y) (h₂ : Weak y z) : Dominates x z := by
  obtain ⟨hx, i, hi⟩ := h₁
  exact ⟨fun k => Nat.le_trans (hx k) (h₂ k), i, Nat.lt_of_lt_of_le hi (h₂ i)⟩

theorem strict_compose {Axis : Type u} {x y z : Cost Axis}
    (h₁ : Dominates x y) (h₂ : Dominates y z) : Dominates x z :=
  weak_dominates h₁.1 h₂

def addCost {Axis : Type u} (x delta : Cost Axis) : Cost Axis :=
  fun i => x i + delta i

/-- The same additive continuation preserves all axis comparisons exactly.
    Valid substitution still requires that the continuation be lawful for both plans. -/
theorem common_additive {Axis : Type u} {x y : Cost Axis} (delta : Cost Axis) :
    Dominates x y ↔ Dominates (addCost x delta) (addCost y delta) := by
  unfold Dominates Weak addCost
  constructor <;> rintro ⟨hw, i, hs⟩
  · exact ⟨fun j => Nat.add_le_add_right (hw j) _, i, Nat.add_lt_add_right hs _⟩
  · exact ⟨fun j => Nat.le_of_add_le_add_right (hw j), i, Nat.lt_of_add_lt_add_right hs⟩

/-- A lawful continuation arena may have cross-component feasibility constraints.
    This data makes applicability a separate gate, not an objective score. -/
structure Arena (Plan : Type v) (Ctx : Type w) (Axis : Type u) where
  lawful : Ctx → Plan → Prop
  final : Ctx → Plan → Cost Axis

def Front {Plan : Type v} {Ctx : Type w} {Axis : Type u}
    (m : Arena Plan Ctx Axis) (pool : Plan → Prop) (ctx : Ctx) (x : Plan) : Prop :=
  pool x ∧ m.lawful ctx x ∧ ¬ ∃ y, pool y ∧ m.lawful ctx y ∧
    Dominates (m.final ctx y) (m.final ctx x)

def Covers {Plan : Type v} {Ctx : Type w} {Axis : Type u}
    (m : Arena Plan Ctx Axis) (pool kept : Plan → Prop) (ctx : Ctx) : Prop :=
  ∀ x, pool x → m.lawful ctx x →
    ∃ y, kept y ∧ m.lawful ctx y ∧ Weak (m.final ctx y) (m.final ctx x)

/-- For each context, the replacement may differ. A replacement must be lawful
    in that context and preserve every axis, not merely a weighted total. -/
theorem retained_front_exact {Plan : Type v} {Ctx : Type w} {Axis : Type u}
    {m : Arena Plan Ctx Axis} {pool kept : Plan → Prop} {ctx : Ctx}
    (sub : ∀ x, kept x → pool x) (cover : Covers m pool kept ctx)
    {x : Plan} (hx : kept x) :
    Front m kept ctx x ↔ Front m pool ctx x := by
  constructor
  · rintro ⟨hk, hl, hn⟩
    refine ⟨sub x hk, hl, ?_⟩
    rintro ⟨y, hy, hly, hdy⟩
    obtain ⟨z, hz, hlz, hw⟩ := cover y hy hly
    exact hn ⟨z, hz, hlz, weak_dominates hw hdy⟩
  · rintro ⟨_, hl, hn⟩
    refine ⟨hx, hl, ?_⟩
    rintro ⟨y, hy, hly, hdy⟩
    exact hn ⟨y, sub y hy, hly, hdy⟩

/-- A removed nondominated plan needs an equal-vector witness. Hence the
    entire frontier image survives; preserving plan identities is stronger. -/
theorem frontier_image_exact {Plan : Type v} {Ctx : Type w} {Axis : Type u}
    {m : Arena Plan Ctx Axis} {pool kept : Plan → Prop} {ctx : Ctx}
    (sub : ∀ x, kept x → pool x) (cover : Covers m pool kept ctx) (z : Cost Axis) :
    (∃ x, Front m kept ctx x ∧ m.final ctx x = z) ↔
    (∃ x, Front m pool ctx x ∧ m.final ctx x = z) := by
  constructor
  · rintro ⟨x, h, hx⟩
    exact ⟨x, (retained_front_exact sub cover h.1).mp h, hx⟩
  · rintro ⟨x, h, hx⟩
    obtain ⟨y, hk, hl, hw⟩ := cover x h.1 h.2.1
    have heq : m.final ctx y = m.final ctx x := by
      funext i
      have hle := hw i
      by_cases hlt : m.final ctx y i < m.final ctx x i
      · exact False.elim (h.2.2 ⟨y, sub y hk, hl, hw, i, hlt⟩)
      · omega
    refine ⟨y, (retained_front_exact sub cover hk).mpr ⟨sub y hk, hl, ?_⟩, heq.trans hx⟩
    rintro ⟨w, hp, hlw, hdw⟩
    rw [heq] at hdw
    exact h.2.2 ⟨w, hp, hlw, hdw⟩

theorem piecewise_frontier_image {Plan : Type v} {Ctx : Type w} {Axis : Type u}
    {m : Arena Plan Ctx Axis} {pool kept : Plan → Prop} {target : Ctx → Prop}
    (sub : ∀ x, kept x → pool x)
    (cover : ∀ ctx, target ctx → Covers m pool kept ctx) :
    ∀ ctx, target ctx → ∀ z,
      (∃ x, Front m kept ctx x ∧ m.final ctx x = z) ↔
      (∃ x, Front m pool ctx x ∧ m.final ctx x = z) :=
  fun ctx h z => frontier_image_exact sub (cover ctx h) z

/-- Finite conjunctive closure control: two enabling atoms are individually
    worthless for this goal but jointly complete one dependency rule. -/
def jointGain (a b : Bool) : Nat := if a && b then 1 else 0

theorem complementarity_control :
    jointGain false false = 0 ∧ jointGain true false = 0 ∧
    jointGain false true = 0 ∧ jointGain true true > 0 := by decide

/-- A closed finite inventory lets us distinguish known, covered-new, and
    unsearched. Nothing absent from the searched space counts as new by default. -/
inductive Status where
  | known | coveredNew | unsearched
  deriving DecidableEq

def status {Key : Type u} [DecidableEq Key] (known covered : List Key) (x : Key) : Status :=
  if x ∈ known then .known else if x ∈ covered then .coveredNew else .unsearched

theorem covered_new_exact {Key : Type u} [DecidableEq Key]
    (known covered : List Key) (x : Key) :
    status known covered x = .coveredNew ↔ x ∉ known ∧ x ∈ covered := by
  by_cases hk : x ∈ known <;> by_cases hc : x ∈ covered <;> simp [status, hk, hc]

theorem unsearched_exact {Key : Type u} [DecidableEq Key]
    (known covered : List Key) (x : Key) :
    status known covered x = .unsearched ↔ x ∉ known ∧ x ∉ covered := by
  by_cases hk : x ∈ known <;> by_cases hc : x ∈ covered <;> simp [status, hk, hc]

#print axioms common_additive
#print axioms retained_front_exact
#print axioms frontier_image_exact
#print axioms piecewise_frontier_image
#print axioms complementarity_control
#print axioms covered_new_exact
#print axioms unsearched_exact

end CompositionalPruning
