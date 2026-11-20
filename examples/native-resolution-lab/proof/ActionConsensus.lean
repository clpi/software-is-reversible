import Lean

namespace ActionConsensus

universe u v w x

def Fiber {C : Type u} {Q : Type v} {R : Type w} (initial : C → Prop)
    (answer : Q → C → R) (history : List (Q × R)) (c : C) : Prop :=
  initial c ∧ ∀ qr ∈ history, answer qr.1 c = qr.2

def Includes {C : Type u} (a b : C → Prop) : Prop := ∀ c, a c → b c

def Live {C : Type u} (f : C → Prop) : Prop := ∃ c, f c

/-- A safe early stop needs a nonempty fiber, but not a singleton fiber.
    Legality can include membership in each interpretation's measured Pareto set. -/
def Certified {C : Type u} {A : Type x} (lawful : C → A → Prop)
    (f : C → Prop) (a : A) : Prop :=
  Live f ∧ ∀ c, f c → lawful c a

def Countermodel {C : Type u} {A : Type x} (lawful : C → A → Prop)
    (f : C → Prop) (a : A) : Prop :=
  ∃ c, f c ∧ ¬ lawful c a

theorem fiber_append_exact {C : Type u} {Q : Type v} {R : Type w}
    (initial : C → Prop) (answer : Q → C → R) (old extra : List (Q × R)) (c : C) :
    Fiber initial answer (old ++ extra) c ↔
      Fiber initial answer old c ∧ (∀ qr ∈ extra, answer qr.1 c = qr.2) := by
  constructor
  · rintro ⟨hc, hh⟩
    exact ⟨⟨hc, fun qr h => hh qr (List.mem_append_left _ h)⟩,
      fun qr h => hh qr (List.mem_append_right _ h)⟩
  · rintro ⟨⟨hc, hl⟩, hr⟩
    exact ⟨hc, fun qr h => (List.mem_append.mp h).elim (hl qr) (hr qr)⟩

/-- More evidence means fewer admissible interpretations, not more assumptions. -/
theorem append_refines {C : Type u} {Q : Type v} {R : Type w}
    (initial : C → Prop) (answer : Q → C → R) (old extra : List (Q × R)) :
    Includes (Fiber initial answer (old ++ extra)) (Fiber initial answer old) :=
  fun c h => ((fiber_append_exact initial answer old extra c).mp h).1

/-- Refinement contravariantly enlarges the set of unanimous actions,
    provided the refined evidence is jointly realizable. -/
theorem preserve_certified {C : Type u} {A : Type x} {lawful : C → A → Prop}
    {broad narrow : C → Prop} (h : Includes narrow broad) (live : Live narrow)
    {a : A} (ha : Certified lawful broad a) : Certified lawful narrow a :=
  ⟨live, fun c hc => ha.2 c (h c hc)⟩

theorem preserved_on_append {C : Type u} {Q : Type v} {R : Type w} {A : Type x}
    (initial : C → Prop) (answer : Q → C → R) (lawful : C → A → Prop)
    (old extra : List (Q × R)) (a : A)
    (live : Live (Fiber initial answer (old ++ extra)))
    (h : Certified lawful (Fiber initial answer old) a) :
    Certified lawful (Fiber initial answer (old ++ extra)) a :=
  preserve_certified (append_refines initial answer old extra) live h

theorem stop_has_no_countermodel {C : Type u} {A : Type x} {lawful : C → A → Prop}
    {f : C → Prop} {a : A} (h : Certified lawful f a) :
    ¬ Countermodel lawful f a := by
  rintro ⟨c, hc, hn⟩
  exact hn (h.2 c hc)

theorem nonempty_no_countermodel_exact {C : Type u} {A : Type x}
    (lawful : C → A → Prop) (f : C → Prop) (a : A)
    (d : ∀ c, Decidable (lawful c a)) :
    Certified lawful f a ↔ Live f ∧ ¬ Countermodel lawful f a := by
  constructor
  · exact fun h => ⟨h.1, stop_has_no_countermodel h⟩
  · rintro ⟨live, hc⟩
    refine ⟨live, fun c hf => ?_⟩
    cases d c with
    | isTrue h => exact h
    | isFalse h => exact False.elim (hc ⟨c, hf, h⟩)

def SameAnswers {C : Type u} {Q : Type v} {R : Type w} (answer : Q → C → R)
    (available : Q → Prop) (c d : C) : Prop := ∀ q, available q → answer q c = answer q d

theorem indivisible_fiber {C : Type u} {Q : Type v} {R : Type w}
    {initial : C → Prop} {answer : Q → C → R} {available : Q → Prop}
    {c d : C} (initialD : initial d) (same : SameAnswers answer available c d)
    (hist : List (Q × R)) (usesOnly : ∀ qr ∈ hist, available qr.1)
    (hc : Fiber initial answer hist c) : Fiber initial answer hist d :=
  ⟨initialD, fun qr h => (same qr.1 (usesOnly qr h)).symm.trans (hc.2 qr h)⟩

/-- No history using these queries can decide the action when one surviving
    interpretation has an indistinguishable mate and their lawful sets conflict. -/
theorem incompatible_alias_obstructs_stop
    {C : Type u} {Q : Type v} {R : Type w} {A : Type x}
    {initial : C → Prop} {answer : Q → C → R} {available : Q → Prop}
    {lawful : C → A → Prop} {c d : C} (initialD : initial d)
    (same : SameAnswers answer available c d)
    (disjoint : ∀ a, lawful c a → lawful d a → False)
    (hist : List (Q × R)) (usesOnly : ∀ qr ∈ hist, available qr.1)
    (hc : Fiber initial answer hist c) :
    ¬ ∃ a, Certified lawful (Fiber initial answer hist) a := by
  rintro ⟨a, h⟩
  exact disjoint a (h.2 c hc) (h.2 d (indivisible_fiber initialD same hist usesOnly hc))

/-- Concrete positive control: unresolved second coordinate does not block
    a decision that depends solely on the already established first coordinate. -/
theorem whole_intent_not_required :
    let f : Bool × Bool → Prop := fun x => x.1 = true
    (∃ c d, f c ∧ f d ∧ c ≠ d) ∧ Certified (fun c a : Bool × Bool => c.1 = a.1) f (true,false) := by
  exact ⟨⟨(true,false), (true,true), rfl, rfl, by decide⟩,
    ⟨⟨(true,false), rfl⟩, fun _ h => h⟩⟩

#print axioms fiber_append_exact
#print axioms append_refines
#print axioms preserve_certified
#print axioms preserved_on_append
#print axioms stop_has_no_countermodel
#print axioms nonempty_no_countermodel_exact
#print axioms indivisible_fiber
#print axioms incompatible_alias_obstructs_stop
#print axioms whole_intent_not_required

end ActionConsensus
