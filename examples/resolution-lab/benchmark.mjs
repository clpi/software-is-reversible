import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {cpus,platform,arch} from 'node:os';
import {performance} from 'node:perf_hooks';
import {AXES,canonicalGraph,demoEvents,searchLab,canonicalJSON} from './search.mjs';
import {loadKernel} from './kernel.mjs';
const kernel=await loadKernel(readFileSync(new URL('./native/kernel.wasm',import.meta.url)));
const alternatives=[
  ['exhaustive-reference',{mode:'exhaustive'}],
  ['factored-reference',{mode:'factored'}],
  ['factored-idol-comparator',{mode:'factored',cmpScalar:kernel.compare}]
];
const profiles=[
  ['full/5 axes',demoEvents(),AXES,'full'],
  ['full/3 axes',demoEvents(),['latency','risk','clarity'],'full'],
  ['before append/5 axes',demoEvents().filter(e=>e.key!=='full-receipt'),AXES,'full'],
  ['narrow control/5 axes',demoEvents(),AXES,'narrow']
];
let rows=[];
for(const [profile,source,axes,p] of profiles) {
  const expected=searchLab(canonicalGraph(source),{axes,profile:p,mode:'exhaustive'}).frontier;
  const data=alternatives.map(([name])=>({architecture:name,samplesMs:[]}));
  for(const phase of ['warmup','measure']) for(let i=0;i<(phase==='warmup'?6:15);i++){
    const order=[0,1,2].map(j=>(j+i)%3);
    for(const j of order) {
      // Graph construction and input seed are identical and outside the timed region.
      const graph=canonicalGraph(source);
      const start=performance.now();
      const result=searchLab(graph,{...alternatives[j][1],axes,profile:p});
      const ms=performance.now()-start;
      assert(result.certificate.exact);
      assert.equal(canonicalJSON(result.frontier),canonicalJSON(expected));
      if(phase==='measure') data[j].samplesMs.push(ms);
    }
  }
  for(const x of data) {
    const ordered=x.samplesMs.slice().sort((a,b)=>a-b);
    x.medianMs=ordered[7];x.p90Ms=ordered[13];
  }
  rows.push({profile,cut:canonicalGraph(source).digest,frontier:expected.length,data});
}
console.log(JSON.stringify({node:process.version,v8:process.versions.v8,cpu:cpus()[0]?.model,platform:platform(),arch:arch(),
  scope:'Cold memo; solver, rank and independent certificate timed together; cut parse excluded. Local Node fixture timings, not browser production benchmarks.',
  rows},null,2));
