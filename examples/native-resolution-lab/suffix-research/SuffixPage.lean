import Lean

namespace SuffixPage

/-- An ordered transition table for a fixed observation scope. A positive
    stop flag places the empty suffix after every nonempty suffix. -/
structure Machine (State : Type u) (Label : Type v) where
  stop : State → Bool
  next : State → List (Label × State)

def enumBlocks {α : Type w} {B : Type x} (sem : B → List α) (bs : List B) : List α :=
  (bs.map sem).flatten

def chooseBlock {α : Type w} {B : Type x} (size : B → Nat) (select : B → Nat → Option α) :
    List B → Nat → Option α
  | [], _ => none
  | b :: bs, n => if n < size b then select b n else chooseBlock size select bs (n - size b)

theorem enumBlocks_count {α : Type w} {B : Type x} (sem : B → List α) (size : B → Nat)
    (h : ∀ b, (sem b).length = size b) (bs : List B) :
    (enumBlocks sem bs).length = (bs.map size).sum := by
  induction bs with
  | nil => rfl
  | cons b bs ih => simp [enumBlocks] at ih ⊢; rw [h, ih]

theorem chooseBlock_exact {α : Type w} {B : Type x} (sem : B → List α)
    (size : B → Nat) (select : B → Nat → Option α)
    (hc : ∀ b, (sem b).length = size b) (hs : ∀ b n, select b n = (sem b)[n]?)
    (bs : List B) (n : Nat) :
    chooseBlock size select bs n = (enumBlocks sem bs)[n]? := by
  induction bs generalizing n with
  | nil => simp [chooseBlock, enumBlocks]
  | cons b bs ih =>
    have he : enumBlocks sem (b :: bs) = sem b ++ enumBlocks sem bs := rfl
    rw [he]
    by_cases hn : n < size b
    · rw [List.getElem?_append_left (by simpa [hc] using hn)]
      simp [chooseBlock, hn, hs]
    · rw [List.getElem?_append_right (by rw [hc]; omega)]
      simp [chooseBlock, hn, hc, ih]

def eos {Label : Type v} (b : Bool) : List (List Label) := if b then [[]] else []

def one (b : Bool) : Nat := if b then 1 else 0

theorem eos_count {Label : Type v} (b : Bool) : (eos (Label := Label) b).length = one b := by
  cases b <;> rfl

/-- Slow reference: lists all realized suffix occurrences. -/
def reference {State : Type u} {Label : Type v} (m : Machine State Label) :
    Nat → State → List (List Label)
  | 0, s => eos (m.stop s)
  | fuel + 1, s =>
    enumBlocks (fun (l,t) => (reference m fuel t).map (l :: ·)) (m.next s) ++ eos (m.stop s)

/-- Computes subtree masses; the recursion may be memoized at (fuel,state)
    without constructing a list of suffix witnesses. -/
def mass {State : Type u} {Label : Type v} (m : Machine State Label) : Nat → State → Nat
  | 0, s => one (m.stop s)
  | fuel + 1, s =>
    ((m.next s).map (fun (_,t) => mass m fuel t)).sum + one (m.stop s)

def select {State : Type u} {Label : Type v} (m : Machine State Label) :
    Nat → State → Nat → Option (List Label)
  | 0, s, n => if n < one (m.stop s) then some [] else none
  | fuel + 1, s, n =>
    let children := ((m.next s).map (fun (_,t) => mass m fuel t)).sum
    if n < children then
      chooseBlock
        (fun (_,t) => mass m fuel t)
        (fun (l,t) k => (select m fuel t k).map (l :: ·))
        (m.next s) n
    else if n - children < one (m.stop s) then some [] else none

theorem mass_exact {State : Type u} {Label : Type v} (m : Machine State Label)
    (fuel : Nat) (s : State) : mass m fuel s = (reference m fuel s).length := by
  induction fuel generalizing s with
  | zero => exact (eos_count _).symm
  | succ fuel ih =>
    rw [mass, reference, List.length_append, eos_count, enumBlocks_count]
    intro b
    exact (List.length_map ..).trans (ih b.2).symm

theorem eos_in_range {Label : Type v} {b : Bool} {n : Nat} (h : n < one b) :
    (eos (Label := Label) b)[n]? = some [] := by
  cases b
  · simp [one] at h
  · have : n = 0 := by simp [one] at h; omega
    subst n
    rfl

/-- Exact ordered unranking: no extraction of all suffixes is needed. -/
theorem select_exact {State : Type u} {Label : Type v} (m : Machine State Label)
    (fuel : Nat) (s : State) (n : Nat) : select m fuel s n = (reference m fuel s)[n]? := by
  induction fuel generalizing s n with
  | zero =>
    rw [select, reference]
    by_cases hn : n < one (m.stop s)
    · rw [if_pos hn, eos_in_range hn]
    · rw [if_neg hn, List.getElem?_eq_none (by rw [eos_count]; omega)]
  | succ fuel ih =>
    rw [select, reference]
    let sem : Label × State → List (List Label) :=
      fun (l,t) => (reference m fuel t).map (l :: ·)
    let size : Label × State → Nat := fun (_,t) => mass m fuel t
    let child := ((m.next s).map size).sum
    have hc : ∀ b, (sem b).length = size b := by
      intro b
      exact (List.length_map ..).trans (mass_exact m fuel b.2).symm
    have hlen : (enumBlocks sem (m.next s)).length = child :=
      enumBlocks_count sem size hc _
    change (if n < child then chooseBlock size
      (fun (l,t) k => (select m fuel t k).map (l :: ·)) (m.next s) n
      else if n - child < one (m.stop s) then some [] else none) =
      (enumBlocks sem (m.next s) ++ eos (m.stop s))[n]?
    by_cases hn : n < child
    · rw [if_pos hn, List.getElem?_append_left (by rwa [hlen])]
      apply chooseBlock_exact _ _ _ hc
      intro b i
      cases b; simp only [sem, List.getElem?_map, ih]
    · rw [if_neg hn, List.getElem?_append_right (by rw [hlen]; omega), hlen]
      by_cases h : n - child < one (m.stop s)
      · rw [if_pos h, eos_in_range h]
      · rw [if_neg h, List.getElem?_eq_none (by rw [eos_count]; omega)]

def page {State : Type u} {Label : Type v} (m : Machine State Label)
    (fuel : Nat) (s : State) (start size : Nat) : List (Option (List Label)) :=
  (List.range size).map (fun k => select m fuel s (start + k))

theorem page_exact {State : Type u} {Label : Type v} (m : Machine State Label)
    (fuel : Nat) (s : State) (start size : Nat) :
    page m fuel s start size = (List.range size).map (fun k => (reference m fuel s)[start + k]?) := by
  unfold page
  simp [select_exact]

theorem out_of_bounds {State : Type u} {Label : Type v} (m : Machine State Label)
    {fuel : Nat} {s : State} {n : Nat} (h : mass m fuel s ≤ n) :
    select m fuel s n = none := by
  rw [select_exact]
  exact List.getElem?_eq_none (mass_exact m fuel s ▸ h)

private theorem prefixed_blocks_nodup {Label : Type v} {B : Type x}
    (label : B → Label) (suffix : B → List (List Label)) (bs : List B)
    (hk : (bs.map label).Nodup) (hs : ∀ b ∈ bs, (suffix b).Nodup) :
    (enumBlocks (fun b => (suffix b).map (label b :: ·)) bs).Nodup := by
  induction bs with
  | nil => exact List.Pairwise.nil
  | cons b bs ih =>
    change (((suffix b).map (label b :: ·)) ++ enumBlocks
      (fun c => (suffix c).map (label c :: ·)) bs).Nodup
    have hpair := List.nodup_cons.mp hk
    apply List.pairwise_append.mpr
    refine ⟨List.pairwise_map.mpr ((hs b (List.mem_cons_self ..)).imp ?_), ?_, ?_⟩
    · intro x y h hxy
      exact h (List.cons.inj hxy).2
    · exact ih hpair.2 (fun x hx => hs x (List.mem_cons_of_mem _ hx))
    · intro x hx y hy heq
      obtain ⟨xx, _, rfl⟩ := List.mem_map.mp hx
      subst y
      obtain ⟨row, hr, hm⟩ := List.mem_flatten.mp hy
      obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hr
      obtain ⟨yy, _, hy⟩ := List.mem_map.mp hm
      exact hpair.1 (List.mem_map.mpr ⟨c, hc, (List.cons.inj hy).1⟩)

/-- Distinct outgoing labels ensure the occurrence count is truly the
    cardinality of different words, even at shared downstream states. -/
theorem reference_nodup {State : Type u} {Label : Type v} (m : Machine State Label)
    (keys : ∀ s, ((m.next s).map Prod.fst).Nodup) (fuel : Nat) (s : State) :
    (reference m fuel s).Nodup := by
  induction fuel generalizing s with
  | zero => simp only [reference, eos]; split <;> simp
  | succ fuel ih =>
    rw [reference]
    apply List.pairwise_append.mpr
    refine ⟨prefixed_blocks_nodup Prod.fst (fun p => reference m fuel p.2) _
      (keys s) (fun p _ => ih p.2), ?_, ?_⟩
    · unfold eos
      split <;> simp
    · intro x hx y hy heq
      have hy' : y = [] := by unfold eos at hy; split at hy <;> simp_all
      subst y
      subst x
      obtain ⟨row, hr, hm⟩ := List.mem_flatten.mp hx
      obtain ⟨p, _, rfl⟩ := List.mem_map.mp hr
      obtain ⟨word, _, hw⟩ := List.mem_map.mp hm
      exact List.noConfusion hw

#print axioms reference_nodup
#print axioms enumBlocks_count
#print axioms chooseBlock_exact
#print axioms mass_exact
#print axioms select_exact
#print axioms page_exact
#print axioms out_of_bounds

end SuffixPage
