import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AXES,canonicalGraph,demoEvents,searchLab,appendEvents} from './search.mjs';
import {loadKernel} from './kernel.mjs';
import {incidence} from './incidence.mjs';
test('admitted Wasm comparator preserves every graph axis/profile frontier and rejects altered binary', async () => {
  const bytes=readFileSync(new URL('./native/kernel.wasm',import.meta.url));
  const wasm=await loadKernel(bytes);
  const full=demoEvents(), edge=full.find(x=>x.key==='full-receipt');
  const base=canonicalGraph(full.filter(x=>x!==edge));
  const extended=appendEvents(base,[edge]);
  for(const profile of ['full','narrow']) for(let mask=1;mask<32;mask++) {
    const axes=AXES.filter((_,i)=>mask&(1<<i));
    for(const graph of [base,extended]) {
      const native=searchLab(graph,{profile,axes,cmpScalar:wasm.compare});
      const ref=searchLab(graph,{profile,axes,mode:'exhaustive'});
      assert(native.certificate.exact);
      assert.deepEqual(native.frontier,ref.frontier);
    }
  }
  const damaged=Buffer.from(bytes);damaged[12]^=1;
  await assert.rejects(loadKernel(damaged),/digest mismatch/);
});
test('derived view reconstructs premise and conclusion memberships, including dual role', () => {
  const graph=canonicalGraph(demoEvents());
  for (const [i,{bits}] of incidence(graph).entries()) {
    const e=graph.edges[i];const r=flag=>graph.nodes.filter((_,j)=>bits[j]&flag).map(n=>n.digest).sort();
    assert.deepEqual(r(1),e.premises); assert.deepEqual(r(2),e.conclusions);
  }
  assert.deepEqual(incidence({nodes:[{digest:'x'}],edges:[{action:'both',premises:['x'],conclusions:['x']}]}),
    [{action:'both',bits:[3]}]);
});
