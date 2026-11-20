// Closed demonstrator: no browser, desktop, process or network side effects.
function word(x) { if (!Number.isInteger(x) || x < 0 || x > 7) throw new RangeError("expected three-bit state"); return x; }
export function apply(kind, before) {
  word(before);
  if (kind === 'flip') return Object.freeze({ kind, before, after: before ^ 1, residual: null, residualBits: 0 });
  if (kind === 'clear') return Object.freeze({ kind, before, after: 0, residual: before, residualBits: 3 });
  throw new TypeError("unregistered action");
}
export function reverse(receipt, fresh) {
  word(fresh);
  if (receipt.after !== fresh) return { ok: false, reason: 'Fresh state no longer equals the recorded result.' };
  if (receipt.kind !== 'clear' && receipt.kind !== 'flip') return {ok:false, reason:'Unregistered inverse.'};
  const prior = receipt.kind === 'flip' ? fresh ^ 1 : receipt.residual;
  if (!Number.isInteger(prior) || prior < 0 || prior > 7 || prior !== receipt.before || apply(receipt.kind, prior).after !== fresh) {
    return { ok: false, reason: 'Residual or replay is inconsistent with the receipt.' };
  }
  return { ok: true, prior };
}
