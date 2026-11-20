import test from 'node:test';
import assert from 'node:assert/strict';
import { apply, reverse } from './reversal.mjs';
test('all finite states, inverse traces, and fresh-state refusals', () => {
  for(let x=0; x<8; x++) for(let trace=0;trace<16;trace++) {
    const receipts=[];
    let s=x;
    for(let i=0;i<4;i++){const r=apply(trace&(1<<i)?'flip':'clear', s); receipts.push(r);s=r.after}
    for(const r of receipts.reverse()){
      for(let o=0;o<8;o++) if(o!==s) assert.equal(reverse(r,o).ok,false);
      s=reverse(r,s).prior;
    }
    assert.equal(s,x);
  }
  assert.equal(reverse({...apply('clear',3),residual:null},0).ok,false);
});
