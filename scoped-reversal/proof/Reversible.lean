import Std

namespace SoftwareIsReversible
universe u v w

def Left {A : Type u} {B : Type v} (D : A → Prop) (f : A → B)
    (g : B → Option A) : Prop := ∀ a, D a → g (f a) = some a

def InjectiveOn {A : Type u} {B : Type v} (D : A → Prop) (f : A → B) : Prop :=
  ∀ a b, D a → D b → f a = f b → a = b

theorem inverse_injective {A : Type u} {B : Type v} (D : A → Prop) (f : A → B)
    (g : B → Option A) (h : Left D f g) : InjectiveOn D f := by
  intro a b ha hb eq
  have h₁ := h a ha
  rw [eq, h b hb] at h₁
  exact (Option.some.inj h₁).symm

theorem collision_impossible {A : Type u} {B : Type v} (D : A → Prop) (f : A → B)
    (a b : A) (ha : D a) (hb : D b) (eq : f a = f b) (ne : a ≠ b) :
    ¬ ∃ g, Left D f g := by
  intro ⟨g, inv⟩
  exact ne (inverse_injective D f g inv a b ha hb eq)

def finiteInverse {A : Type u} {B : Type v} [DecidableEq B]
    (f : A → B) (domain : List A) (b : B) : Option A :=
  match domain with
  | [] => none
  | a :: rest => if f a = b then some a else finiteInverse f rest b

theorem finite_inverse_sound {A : Type u} {B : Type v} [DecidableEq B]
    (D : A → Prop) (f : A → B) (injective : InjectiveOn D f) (domain : List A)
    (members : ∀ a ∈ domain, D a) (x : A) (hx : x ∈ domain) :
    finiteInverse f domain (f x) = some x := by
  induction domain with
  | nil => simp at hx
  | cons a rest ih =>
    by_cases eq : f a = f x
    · have a_eq := injective a x (members a (by simp)) (members x hx) eq
      simp [finiteInverse, eq, a_eq]
    · have tail : x ∈ rest := (List.mem_cons.mp hx).resolve_left (fun e => eq (by rw [e]))
      simpa [finiteInverse, eq] using ih
        (fun t ht => members t (List.mem_cons_of_mem _ ht)) tail

/-- The finite declaration need not have decidable membership in D; exact
enumeration and decidable output equality suffice for a computable inverse. -/
theorem inverse_iff_injective_finite {A : Type u} {B : Type v} [DecidableEq B]
    (D : A → Prop) (f : A → B) (domain : List A) (exactly : ∀ a, a ∈ domain ↔ D a) :
    (∃ g, Left D f g) ↔ InjectiveOn D f := by
  constructor
  · intro ⟨g, inv⟩
    exact inverse_injective D f g inv
  · intro inj
    exact ⟨finiteInverse f domain, fun a ha => finite_inverse_sound D f inj domain
      (fun x hx => (exactly x).mp hx) a ((exactly a).mpr ha)⟩

theorem compose_inverse {A : Type u} {B : Type v} {C : Type w}
    (D : A → Prop) (E : B → Prop) (f : A → B) (g : B → C)
    (fInv : B → Option A) (gInv : C → Option B)
    (maps : ∀ a, D a → E (f a)) (lf : Left D f fInv) (lg : Left E g gInv) :
    Left D (fun a => g (f a)) (fun c => (gInv c).bind fInv) := by
  intro a ha
  change (gInv (g (f a))).bind fInv = some a
  rw [lg (f a) (maps a ha)]
  exact lf a ha

/-- Explicit residual construction needs no finite search: if a decoder
can consume output and residual, the paired encoding is reversible. -/
theorem residual_inverse {A : Type u} {B : Type v} {R : Type w}
    (D : A → Prop) (f : A → B) (residual : A → R) (recover : B → R → Option A)
    (valid : ∀ a, D a → recover (f a) (residual a) = some a) :
    Left D (fun a => (f a, residual a)) (fun v => recover v.1 v.2) := valid

private def removeOne {A : Type u} [DecidableEq A] (a : A) : List A → List A
  | [] => []
  | x :: xs => if x = a then xs else x :: removeOne a xs

private theorem removeOne_length {A : Type u} [DecidableEq A] (a : A) (xs : List A)
    (h : a ∈ xs) : (removeOne a xs).length + 1 = xs.length := by
  induction xs with
  | nil => simp at h
  | cons x xs ih =>
    by_cases e : x = a
    · simp [removeOne, e]
    · have ht := (List.mem_cons.mp h).resolve_left (fun j => e j.symm)
      simp only [removeOne, e, if_false, List.length_cons]
      rw [ih ht]

private theorem removeOne_keeps {A : Type u} [DecidableEq A] (a b : A) (xs : List A)
    (ne : b ≠ a) (h : b ∈ xs) : b ∈ removeOne a xs := by
  induction xs with
  | nil => simp at h
  | cons x xs ih =>
    by_cases e : x = a
    · subst x
      simp only [removeOne, if_true]
      exact (List.mem_cons.mp h).resolve_left ne
    · simp only [removeOne, e, if_false]
      exact List.mem_cons.mpr ((List.mem_cons.mp h).imp_right ih)

theorem nodup_subset_length {A : Type u} [DecidableEq A] (xs ys : List A)
    (unique : xs.Nodup) (incl : ∀ a ∈ xs, a ∈ ys) : xs.length ≤ ys.length := by
  induction xs generalizing ys with
  | nil => simp
  | cons x xs ih =>
    obtain ⟨hnot,hx⟩ := List.nodup_cons.mp unique
    have inY := incl x (by simp)
    have rem := ih (removeOne x ys) hx (fun t h => removeOne_keeps x t ys (by
      intro eq
      exact hnot (eq ▸ h)) (incl t (by simp [h])))
    change xs.length + 1 ≤ ys.length
    calc
      _ ≤ (removeOne x ys).length + 1 := Nat.add_le_add_right rem 1
      _ = _ := removeOne_length x ys inY

theorem map_nodup_of_injective {A : Type u} {R : Type v}
    (f : A → R) (xs : List A) (unique : xs.Nodup)
    (inj : ∀ a ∈ xs, ∀ b ∈ xs, f a = f b → a = b) : (xs.map f).Nodup := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
    obtain ⟨notTail, tail⟩ := List.nodup_cons.mp unique
    apply List.nodup_cons.mpr
    constructor
    · intro hx
      obtain ⟨a, ha, eq⟩ := List.mem_map.mp hx
      exact notTail ((inj a (by simp [ha]) x (by simp) eq) ▸ ha)
    · exact ih tail (fun a ha b hb => inj a (by simp [ha]) b (by simp [hb]))

/-- Within a fixed output fiber, reversibility injects each distinct
possible original into residuals. No coding algorithm can avoid this bound. -/
theorem fiber_lower_bound {A : Type u} {B : Type v} {R : Type w} [DecidableEq R]
    (D : A → Prop) (f : A → B) (r : A → R) (recover : B → R → Option A)
    (valid : ∀ a, D a → recover (f a) (r a) = some a)
    (out : B) (fiber : List A) (codes : List R) (unique : fiber.Nodup)
    (scope : ∀ a ∈ fiber, D a ∧ f a = out)
    (bounded : ∀ a ∈ fiber, r a ∈ codes) : fiber.length ≤ codes.length := by
  have mapUnique := map_nodup_of_injective r fiber unique (by
    intro a ha b hb eq
    have ea := valid a (scope a ha).1
    have eb := valid b (scope b hb).1
    rw [(scope a ha).2, eq, ← (scope b hb).2, eb] at ea
    exact (Option.some.inj ea).symm)
  have len := nodup_subset_length (fiber.map r) codes mapUnique (by
    intro code hc
    obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hc
    exact bounded a ha)
  simpa using len

theorem fin_mem_range (n : Nat) (i : Fin n) : i ∈ List.finRange n := by
  have hi : i.val < (List.finRange n).length := by simp
  have same : (List.finRange n)[i.val] = i := by
    rw [List.getElem_finRange]
    apply Fin.ext
    rfl
  rw [← same]
  exact List.getElem_mem hi

/-- In particular, there must be at least as many fixed-width codes as
fiber members. Setting n = 2^bits gives the usual bit-width lower bound. -/
theorem fin_fiber_lower_bound {A : Type u} {B : Type v} (n : Nat)
    (D : A → Prop) (f : A → B) (r : A → Fin n) (recover : B → Fin n → Option A)
    (valid : ∀ a, D a → recover (f a) (r a) = some a)
    (out : B) (fiber : List A) (unique : fiber.Nodup)
    (scope : ∀ a ∈ fiber, D a ∧ f a = out) : fiber.length ≤ n := by
  have h := fiber_lower_bound D f r recover valid out fiber (List.finRange n) unique scope
    (fun a _ => fin_mem_range n (r a))
  simpa using h


structure Action (S : Type u) (R : Type v) where
  permit : S → Prop
  step : S → S × R
  unstep : S → R → S
  undo_valid : ∀ s, permit s → unstep (step s).1 (step s).2 = s

def Admitted {S : Type u} {R : Type v} : List (Action S R) → S → Prop
  | [], _ => True
  | a :: tail, s => a.permit s ∧ Admitted tail (a.step s).1

def execute {S : Type u} {R : Type v} : List (Action S R) → S → S × List R
  | [], s => (s, [])
  | a :: tail, s =>
    let (next, stamp) := a.step s
    let (final, stamps) := execute tail next
    (final, stamp :: stamps)

def undo {S : Type u} {R : Type v} : List (Action S R) → S → List R → Option S
  | [], s, [] => some s
  | a :: tail, s, stamp :: stamps => (undo tail s stamps).map (fun p => a.unstep p stamp)
  | _, _, _ => none

theorem scoped_trace_inverse {S : Type u} {R : Type v} (actions : List (Action S R))
    (s : S) (valid : Admitted actions s) :
    undo actions (execute actions s).1 (execute actions s).2 = some s := by
  induction actions generalizing s with
  | nil => rfl
  | cons a tail ih =>
    change a.permit s ∧ Admitted tail (a.step s).1 at valid
    change (undo tail (execute tail (a.step s).1).1 (execute tail (a.step s).1).2).map
      (fun p => a.unstep p (a.step s).2) = some s
    rw [ih _ valid.2]
    simp [a.undo_valid s valid.1]

/-- A rank within a declared fiber uses a common residual alphabet; no
    global table of disjoint labels is necessary. -/
def rankIn {A : Type u} [DecidableEq A] (a : A) : List A → Nat
  | [] => 0
  | x :: xs => if x = a then 0 else 1 + rankIn a xs

theorem rank_recovers {A : Type u} [DecidableEq A] (a : A) (xs : List A)
    (h : a ∈ xs) : xs[rankIn a xs]? = some a := by
  induction xs with
  | nil => simp at h
  | cons x xs ih =>
    by_cases eq : x = a
    · subst x
      simp [rankIn]
    · have ha : a ∈ xs := (List.mem_cons.mp h).resolve_left (Ne.symm eq)
      simp [rankIn, eq, Nat.add_comm 1, ih ha]

theorem rank_lt_length {A : Type u} [DecidableEq A] (a : A) (xs : List A)
    (h : a ∈ xs) : rankIn a xs < xs.length := by
  induction xs with
  | nil => simp at h
  | cons x xs ih =>
    by_cases eq : x = a
    · simp [rankIn, eq]
    · have ha : a ∈ xs := (List.mem_cons.mp h).resolve_left (Ne.symm eq)
      have hh := ih ha
      simp only [rankIn, eq, if_false, List.length_cons]
      omega

def sourceFiber {A : Type u} {B : Type v} [DecidableEq B]
    (f : A → B) (domain : List A) (out : B) : List A :=
  domain.filter (fun a => decide (f a = out))

theorem rank_fiber_attainable
    {A : Type u} {B : Type v} [DecidableEq A] [DecidableEq B]
    (f : A → B) (domain : List A) (n : Nat)
    (cap : ∀ b, (sourceFiber f domain b).length ≤ n) :
    ∃ encode : (a : { a // a ∈ domain }) → Fin n,
      ∃ decode : B → Fin n → Option A,
        ∀ a : {a // a ∈ domain}, decode (f a.val) (encode a) = some a.val := by
  have member (a : { a // a ∈ domain }) : a.val ∈ sourceFiber f domain (f a.val) := by
    simp [sourceFiber, a.property]
  let enc (a : { a // a ∈ domain }) : Fin n :=
    ⟨rankIn a.val (sourceFiber f domain (f a.val)),
      Nat.lt_of_lt_of_le (rank_lt_length _ _ (member a)) (cap (f a.val))⟩
  refine ⟨enc, fun b j => (sourceFiber f domain b)[j.val]?, ?_⟩
  intro a
  exact rank_recovers _ _ (member a)

#print axioms rank_recovers
#print axioms rank_lt_length
#print axioms rank_fiber_attainable

#print axioms inverse_injective
#print axioms collision_impossible
#print axioms finite_inverse_sound
#print axioms inverse_iff_injective_finite
#print axioms compose_inverse
#print axioms residual_inverse
#print axioms fiber_lower_bound
#print axioms fin_fiber_lower_bound
#print axioms scoped_trace_inverse
end SoftwareIsReversible
