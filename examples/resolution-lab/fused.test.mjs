import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AXES,DIRECTIONS,canonicalGraph,demoEvents,heldOutControl} from './search.mjs';
import {loadFused} from './fused.mjs';
test('native fused check replays the held-out winner, ties and slot orientation',async()=>{
  const bytes=readFileSync(new URL('./fused/fused.wasm',import.meta.url));
  const run=await loadFused(bytes);
  const {example}=heldOutControl(canonicalGraph(demoEvents()));
  const orient=vector=>AXES.map(x=>DIRECTIONS[x]*vector[x]);
  const a=orient(example.after),b=orient(example.before);
  assert(run(31,a,b));assert(!run(31,b,a));assert(!run(31,a,a));
  assert.throws(()=>run(0,a,b),/Invalid projection/);
  assert.throws(()=>run(31,a.map(x=>-2147483649),b),/Outside signed i32/);
  const corrupt=Buffer.from(bytes);corrupt[7]^=1;
  await assert.rejects(loadFused(corrupt),/digest mismatch/);
});
