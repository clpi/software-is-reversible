import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AXES, EVIDENCE, sha256, canonicalJSON, demoEvents, canonicalGraph, appendEvents,
  compareArchitectures, searchLab, weightCandidates, verifyFrontier, heldOutControl} from './search.mjs';

const scope = demoEvents().find(e=>e.kind==='scope');
const events = demoEvents();
const from = (key,updates={})=>({...events.find(e=>e.key===key),...updates});

test('browser-compatible SHA agrees against independent Node crypto', () => {
  for (const input of ['', 'abc', '🐕', 'z'.repeat(201), 'a'.repeat(65), canonicalJSON(events)]) {
    assert.equal(sha256(input),createHash('sha256').update(input).digest('hex'));
  }
  assert.throws(()=>canonicalJSON([, 2]),/archive array/);
  const sparse=[, 2]; sparse.extra=1;
  assert.throws(()=>canonicalJSON(sparse),/archive array/);
});

test('event append set is order invariant, idempotent, provenance-bearing and conflict checked', ()=> {
  const graph=canonicalGraph(events);
  const permutation=[...events].reverse().concat(events.slice(0,5));
  assert.equal(canonicalGraph(permutation).digest,graph.digest);
  assert.equal(appendEvents(graph,[...events,...events]).digest,graph.digest);
  const shuffledPremise=from('factor',{requires:['indexed','complete','complete']});
  assert.equal(appendEvents(graph,[shuffledPremise]).digest,graph.digest);
  const left=appendEvents(appendEvents(canonicalGraph([scope]),events.filter(e=>e.phase==='plan')),events);
  const right=appendEvents(appendEvents(canonicalGraph([scope]),events.filter(e=>e.phase==='verify')),events);
  assert.equal(left.digest,right.digest);
  assert.throws(()=>appendEvents(graph,[from('factor',{metrics:{...from('factor').metrics,latency:31}})]),/conflict/);
  assert.throws(()=>appendEvents(graph,[{...from('factor'),uninterpreted:'not erased'}]),/invalid action/);
  assert.throws(()=>appendEvents(graph,[from('full-receipt',{key:'fake',requires:['query']})]),/evidence premise/);
  assert.equal(graph.events.length,19);
  assert.equal(graph.edges.length,18);
  assert(graph.edges.every(e=>e.premises.length>=3&&e.conclusions.length>=2));
  assert(Object.isFrozen(graph.edges[0].premises));
});

test('independent complete Cartesian oracle matches both search architectures for every nonempty axis subset', () => {
  const g=canonicalGraph(events);
  for (let mask=1; mask<1<<AXES.length; mask++) {
    const axes=AXES.filter((_,j)=>mask&(1<<j));
    for (const profile of ['full','narrow']) {
      const r=compareArchitectures(g,{axes,profile});
      assert(r.agree);
      assert(r.factored.certificate.exact);
      assert(r.exhaustive.certificate.exact);
      assert(r.factored.frontier.every(p=>p.evidence===EVIDENCE&&!p.actions.includes('guess')
                                      &&!p.actions.includes('partial-receipt')));
    }
  }
});

test('held-out append partitions exact-in-scope from a clean falsification', () => {
  const g=canonicalGraph(events);
  const h=heldOutControl(g);
  assert(h.falsified);
  assert(h.example.challenger.includes('witness-index'));
  assert(!h.allNarrowPointsDominated);
  assert.equal(h.dominatedNarrowPoints,14);
  assert.equal(h.narrowedFrontierPoints,20);
  assert.equal(h.fullFrontierPoints,18);
  assert.equal(verifyFrontier(g,searchLab(g).frontier.slice(1)).exact,false);
});

test('append reuses prefix layers only with equal future requirement interfaces', () => {
  const extra=events.find(e=>e.key==='full-receipt');
  const base=canonicalGraph(events.filter(e=>e!==extra));
  searchLab(base);
  const appended=appendEvents(base,[extra]);
  const warm=searchLab(appended);
  const cold=searchLab(canonicalGraph(events));
  assert.equal(warm.stats.reusedStages,3);
  assert.equal(warm.stats.reusedExtensions,21);
  assert.equal(warm.stats.actualCandidateExtensions,27);
  assert.equal(cold.stats.actualCandidateExtensions,48);
  assert.deepEqual(warm.frontier,cold.frontier);

  // First graph compresses retrievals with the same future requirements.
  // 'insight' was unavailable to downstream continuations before the append.
  const hasInsight=from('index',{provides:['complete','indexed','insight']});
  const basic=canonicalGraph(events.map(e=>e.key==='index'?hasInsight:e));
  searchLab(basic);
  const late=from('full-receipt',{key:'use-insight',requires:['checked','insight'],
    metrics:{latency:0,storage:0,risk:0,clarity:20,compute:0}});
  const changed=searchLab(appendEvents(basic,[late]));
  const changedCold=searchLab(canonicalGraph([...basic.events,late]));
  assert.equal(changed.stats.reusedStages,0);
  assert.deepEqual(changed.frontier,changedCold.frontier);
  assert(changed.frontier.some(p=>p.actions.includes('use-insight')));
});

test('regenerate a weight grid and distinguish reweighting from redimension', ()=>{
  const g=canonicalGraph(events);
  const w=weightCandidates(AXES,4);
  assert.equal(w.length,70);
  assert(new Set(w.map(c=>canonicalJSON(c.weights))).size===70);
  assert(w.every(c=>Object.values(c.weights).reduce((a,b)=>a+b)===4));
  const initial=searchLab(g,{weights:{latency:1}});
  const same=searchLab(g,{weights:{storage:1}});
  assert.deepEqual(same.frontier,initial.frontier);
  assert.notDeepEqual(same.selected,initial.selected);
  assert(same.stats.reusedFrontier && same.stats.verificationReused);
  assert.equal(same.stats.actualCandidateExtensions,0);
  const d=searchLab(g,{axes:['storage','compute']});
  assert(!d.stats.reusedFrontier);
  assert(d.certificate.exact);
  assert(d.frontier.length<same.frontier.length);
  assert.throws(()=>searchLab(g,{axes:['latency','latency']}),/projection/);
  assert.throws(()=>searchLab(g,{weights:{latency:0}}),/all-zero/);
});

test('score comparisons are delegatable without sharing the checker or mixing caches', ()=>{
  let count=0;
  const cmpScalar=(a,b)=>{count++;assert(Number.isSafeInteger(a)&&Number.isSafeInteger(b));
    return a<b?-1:a>b?1:0;};
  const g=canonicalGraph(events);
  const supplied=searchLab(g,{cmpScalar});
  assert(supplied.certificate.exact);
  assert.equal(supplied.comparison,'caller-supplied-signed-comparator');
  assert(supplied.stats.comparedCoordinates>0);
  assert.equal(count,supplied.stats.comparedCoordinates+5);
  const reference=searchLab(g);
  assert.deepEqual(reference.frontier,supplied.frontier);
  assert(!reference.stats.reusedFrontier);
  assert.throws(()=>searchLab(g,{cmpScalar:()=>1}),/signed scalar/);
  const subtle=(a,b)=>a>=3&&a<=25&&b>=3&&b<=25&&a!==b?(a<b?1:-1):a<b?-1:a>b?1:0;
  assert.equal(searchLab(g,{cmpScalar:subtle}).certificate.exact,false);
});
