import Lean

namespace ProductFrontier

def Weak {ι : Type u} (x y : ι → Nat) : Prop := ∀ i, x i ≤ y i

def Dom {ι : Type u} (x y : ι → Nat) : Prop := Weak x y ∧ ∃ i, x i < y i

def Front {P : Type u} {ι : Type v} (ok : P → Prop) (cost : P → ι → Nat) (p : P) : Prop :=
  ok p ∧ ¬ ∃ q, ok q ∧ Dom (cost q) (cost p)

def independent {A : Type u} {B : Type v} (p : A → Prop) (q : B → Prop) :
    A × B → Prop := fun x => p x.1 ∧ q x.2

def coproduct {A : Type u} {B : Type v} {ι : Type w} {κ : Type x}
    (f : A → ι → Nat) (g : B → κ → Nat) : A × B → Sum ι κ → Nat :=
  fun p i => Sum.elim (f p.1) (g p.2) i

/-- Exact coordinate separation; no sum or rank can hide a strict witness. -/
theorem coordinate_law {A : Type u} {B : Type v} {ι : Type w} {κ : Type x}
    (f : A → ι → Nat) (g : B → κ → Nat) (a a' : A) (b b' : B) :
    Dom (coproduct f g (a,b)) (coproduct f g (a',b')) ↔
      (Dom (f a) (f a') ∧ Weak (g b) (g b')) ∨
      (Weak (f a) (f a') ∧ Dom (g b) (g b')) := by
  constructor
  · rintro ⟨hw, i, hi⟩
    have h₁ : Weak (f a) (f a') := fun k => hw (.inl k)
    have h₂ : Weak (g b) (g b') := fun k => hw (.inr k)
    cases i with
    | inl k => exact Or.inl ⟨⟨h₁, k, hi⟩, h₂⟩
    | inr k => exact Or.inr ⟨h₁, h₂, k, hi⟩
  · rintro (⟨⟨h₁, i, hi⟩, h₂⟩ | ⟨h₁, h₂, i, hi⟩)
    · exact ⟨fun k => Sum.rec h₁ h₂ k, .inl i, hi⟩
    · exact ⟨fun k => Sum.rec h₁ h₂ k, .inr i, hi⟩

/-- If legality factors and the two components own disjoint axes, append can
    reuse the exact old frontier and solve only the new component. This
    preserves plan identities, not merely the observable objective image. -/
theorem frontier_product {A : Type u} {B : Type v} {ι : Type w} {κ : Type x}
    (p : A → Prop) (q : B → Prop) (f : A → ι → Nat) (g : B → κ → Nat) (a : A) (b : B) :
    Front (independent p q) (coproduct f g) (a,b) ↔ Front p f a ∧ Front q g b := by
  constructor
  · rintro ⟨⟨ha, hb⟩, hn⟩
    refine ⟨⟨ha, ?_⟩, ⟨hb, ?_⟩⟩
    · rintro ⟨a', hp, hd⟩
      exact hn ⟨(a', b), ⟨hp,hb⟩,
        (coordinate_law f g a' a b b).mpr (.inl ⟨hd, fun _ => Nat.le_refl _⟩)⟩
    · rintro ⟨b', hp, hd⟩
      exact hn ⟨(a, b'), ⟨ha,hp⟩,
        (coordinate_law f g a a b' b).mpr (.inr ⟨fun _ => Nat.le_refl _, hd⟩)⟩
  · rintro ⟨⟨ha, hna⟩, ⟨hb, hnb⟩⟩
    refine ⟨⟨ha, hb⟩, ?_⟩
    rintro ⟨⟨a',b'⟩, ⟨hp,hq⟩, hd⟩
    rcases (coordinate_law f g a' a b' b).mp hd with h | h
    · exact hna ⟨a', hp, h.1⟩
    · exact hnb ⟨b', hq, h.2⟩

/-- A trusted bridge from the current cut back to the frozen dependency key
    can replay per-row obligations even if the cut tag has changed. -/
structure Frozen {State : Type u} {Label : Type v} {Value : Type w}
    (holds : State → Label → Value → Prop) where
  key : State → Label → Nat
  valid : ∀ s t l v, key s l = key t l → holds s l v → holds t l v

theorem reuse_unchanged_slice {State : Type u} {Label : Type v} {Value : Type w}
    {holds : State → Label → Value → Prop} (bridge : Frozen holds)
    (old new : State) (rows : List (Label × Value))
    (oldReceipt : ∀ row ∈ rows, holds old row.1 row.2)
    (stable : ∀ row ∈ rows, bridge.key old row.1 = bridge.key new row.1) :
    ∀ row ∈ rows, holds new row.1 row.2 :=
  fun row h => bridge.valid _ _ _ _ (stable row h) (oldReceipt row h)

/-- One replay step encloses both the local facts and reused optimum.
    The new component is the only frontier not supplied as input. -/
theorem replay_after_independent_append
    {State : Type u} {Label : Type v} {Value : Type w}
    {A : Type x} {B : Type y} {ι : Type z} {κ : Type t}
    {holds : State → Label → Value → Prop} (bridge : Frozen holds)
    (old new : State) (rows : List (Label × Value))
    (oldReceipt : ∀ row ∈ rows, holds old row.1 row.2)
    (stable : ∀ row ∈ rows, bridge.key old row.1 = bridge.key new row.1)
    (oldLaw currentLaw : A → Prop) (deltaLaw : B → Prop)
    (oldCost currentCost : A → ι → Nat) (deltaCost : B → κ → Nat)
    (sameLaw : oldLaw = currentLaw) (sameCost : oldCost = currentCost)
    (cached : A → Prop) (hc : ∀ a, cached a ↔ Front oldLaw oldCost a) :
    (∀ row ∈ rows, holds new row.1 row.2) ∧
    (∀ a b, Front (independent currentLaw deltaLaw) (coproduct currentCost deltaCost) (a,b)
      ↔ cached a ∧ Front deltaLaw deltaCost b) := by
  refine ⟨reuse_unchanged_slice bridge old new rows oldReceipt stable, ?_⟩
  intro a b
  rw [frontier_product, ← sameLaw, ← sameCost, ← hc a]

/-- The join contract can couple candidates that were independent at their
    respective cuts. Keeping only each old optimum then loses all feasible plans. -/
def bitCost (b : Bool) (_ : Unit) : Nat := if b then 1 else 0

def guardJoin (p : Bool × Bool) : Prop := p.1 = true ∧ p.2 = true

theorem unsafe_product_control :
    Front (fun _ : Bool => True) bitCost false ∧
    ¬ Front (fun _ : Bool => True) bitCost true ∧
    Front guardJoin (coproduct bitCost bitCost) (true,true) ∧
    ¬ guardJoin (false,false) := by
  refine ⟨⟨trivial, ?_⟩, ?_, ⟨⟨rfl,rfl⟩, ?_⟩, by simp [guardJoin]⟩
  · rintro ⟨q, _, _, i, hi⟩
    cases q <;> cases i <;> simp [bitCost] at hi
  · intro h
    exact h.2 ⟨false, trivial, (fun i => by cases i; decide), (), by decide⟩
  · rintro ⟨⟨a,b⟩, ⟨ha,hb⟩, _, i, hi⟩
    change a = true at ha
    change b = true at hb
    subst a
    subst b
    exact Nat.lt_irrefl _ hi

#print axioms coordinate_law
#print axioms frontier_product
#print axioms reuse_unchanged_slice
#print axioms replay_after_independent_append
#print axioms unsafe_product_control
end ProductFrontier
