/* Browser-compatible, offline JS reference. No Wasm or production benchmark claim. */
export const AXES = Object.freeze(['latency','storage','risk','clarity','compute']);
export const DIRECTIONS = Object.freeze({latency:1,storage:1,risk:1,clarity:-1,compute:1});
export const STAGES = Object.freeze(['retrieve','plan','verify','record']);
export const EVIDENCE = 'synthetic-model-costs/not-runtime-measurements';
const lex = (a,b) => a < b ? -1 : a > b ? 1 : 0;
const demand = (test, message) => { if (!test) throw new Error(message); };
const plain = x => x !== null && typeof x==='object' && !Array.isArray(x)
  && Object.getPrototypeOf(x) === Object.prototype;
const unique = xs => [...new Set(xs)].sort(lex);
const validKey = x => typeof x === 'string' && /^[a-z][a-z0-9-]*$/.test(x);
const immutable = x => {
  if (x && typeof x==='object' && !Object.isFrozen(x)) {
    for (const v of Object.values(x)) immutable(v);
    Object.freeze(x);
  }
  return x;
};

export function canonicalJSON(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return JSON.stringify(value);
  if (typeof value === 'number' && Number.isSafeInteger(value)) return String(value);
  if (Array.isArray(value)) {
    demand(Object.keys(value).length===value.length && Object.keys(value).every((key,i)=>key===String(i)),
      'invalid sparse archive array');
    return '['+value.map(canonicalJSON).join(',')+']';
  }
  demand(plain(value),'unsupported canonical data');
  return '{'+Object.keys(value).sort(lex).map(k=>JSON.stringify(k)+':'+canonicalJSON(value[k])).join(',')+'}';
}

// SHA-256 with 32-bit words so graph identity agrees in a browser and Node.
const K = [
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
];
const rotr = (x,n) => (x>>>n)|(x<<(32-n));
export function sha256(text) {
  const input = new TextEncoder().encode(text);
  const padded = new Uint8Array(Math.ceil((input.length+9)/64)*64);
  padded.set(input); padded[input.length]=128;
  const view = new DataView(padded.buffer);
  const bits = BigInt(input.length)*8n;
  view.setBigUint64(padded.length-8,bits);
  const h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const w = new Int32Array(64);
  for (let i=0;i<padded.length;i+=64) {
    for (let j=0;j<16;j++) w[j]=view.getInt32(i+4*j);
    for (let j=16;j<64;j++) {
      const x=w[j-15], y=w[j-2];
      w[j]=w[j-16]+(rotr(x,7)^rotr(x,18)^(x>>>3))+w[j-7]+(rotr(y,17)^rotr(y,19)^(y>>>10));
    }
    let [a,b,c,d,e,f,g,z]=h;
    for (let j=0;j<64;j++) {
      const t1=(z+(rotr(e,6)^rotr(e,11)^rotr(e,25))+((e&f)^(~e&g))+K[j]+w[j])|0;
      const t2=((rotr(a,2)^rotr(a,13)^rotr(a,22))+((a&b)^(a&c)^(b&c)))|0;
      [a,b,c,d,e,f,g,z]=[(t1+t2)|0,a,b,c,(d+t1)|0,e,f,g];
    }
    [a,b,c,d,e,f,g,z].forEach((x,j)=>h[j]=(h[j]+x)|0);
  }
  return h.map(x=>(x>>>0).toString(16).padStart(8,'0')).join('');
}
const id = value => sha256(canonicalJSON(value));

const option = (phase,key,requires,provides,values,holdout=false,admission='qualified-fixture') =>
  ({kind:'action',phase,key,requires,provides,metrics:Object.fromEntries(AXES.map((a,i)=>[a,values[i]])),
    holdout,admission,evidence:EVIDENCE});
const zero = Object.fromEntries(AXES.map(a=>[a,0]));

export function demoEvents() {
  return immutable([
    {kind:'scope',name:'finite-append-set-demo-v1',evidence:EVIDENCE},
    option('retrieve','scan',['query'],['complete'],[12,0,0,6,9]),
    option('retrieve','index',['query'],['complete','indexed'],[4,6,1,7,4]),
    option('retrieve','scope',['query'],['sparse'],[2,2,1,8,3]),
    option('retrieve','join',['query'],['complete','indexed'],[4,4,0,8,3]),
    option('retrieve','witness-index',['query'],['complete','indexed'],[1,3,0,10,2],true),
    option('plan','enumerate',['complete'],['exact'],[10,1,0,5,10]),
    option('plan','factor',['complete','indexed'],['exact'],[3,4,0,7,3]),
    option('plan','interval',['sparse'],['bounds'],[2,1,1,7,2]),
    option('plan','refine',['sparse'],['exact'],[8,2,1,8,6]),
    option('plan','guess',['query'],['exact'],[0,0,0,12,0],false,'unverified-proposal'),
    option('verify','pairwise',['exact'],['checked'],[5,1,0,7,6]),
    option('verify','certificate',['exact'],['checked'],[3,3,0,9,3]),
    option('verify','replay',['exact','indexed'],['checked'],[2,5,0,10,5]),
    option('verify','publish-bound',['bounds'],['bounded-checked'],[2,0,1,8,2]),
    option('record','minimal',['checked'],['resolved'],[2,1,0,5,2]),
    option('record','full-receipt',['checked'],['resolved'],[3,4,0,9,2]),
    option('record','shared-receipt',['checked','indexed'],['resolved'],[2,3,0,9,1]),
    option('record','partial-receipt',['bounded-checked'],['partial'],[1,0,0,8,1]),
  ]);
}
function normalizeEvent(e) {
  demand(plain(e) && (e.kind==='scope' || e.kind==='action'),'invalid event');
  if (e.kind==='scope') {
    demand(Object.keys(e).length===3 && validKey(e.name) && e.evidence===EVIDENCE,'unknown scope evidence');
    return {kind:e.kind,name:e.name,evidence:e.evidence};
  }
  demand(Object.keys(e).length===9 && STAGES.includes(e.phase) && validKey(e.key),'invalid action key or phase');
  demand(Array.isArray(e.requires) && e.requires.every(validKey) &&
    Array.isArray(e.provides) && e.provides.length>0 && e.provides.every(validKey),'invalid directed hyperedge');
  demand(plain(e.metrics) && Object.keys(e.metrics).length===AXES.length &&
    AXES.every(a=>Number.isSafeInteger(e.metrics[a]) && e.metrics[a]>=0 && e.metrics[a]<=1e6),'invalid modeled metrics');
  demand(e.evidence===EVIDENCE && ['qualified-fixture','unverified-proposal'].includes(e.admission)
    && typeof e.holdout==='boolean','invalid evidence lane');
  if (e.admission==='qualified-fixture') {
    if (e.provides.includes('resolved'))
      demand(e.phase==='record' && e.requires.includes('checked'),'missing resolved evidence premise');
    if (e.provides.includes('partial'))
      demand(e.phase==='record' && e.requires.includes('bounded-checked'),'missing partial evidence premise');
    if (e.provides.includes('checked'))
      demand(e.phase==='verify' && e.requires.includes('exact'),'missing exact evidence premise');
    if (e.provides.includes('bounded-checked'))
      demand(e.phase==='verify' && e.requires.includes('bounds'),'missing bounded evidence premise');
  }
  return {kind:e.kind,phase:e.phase,key:e.key,requires:unique(e.requires),provides:unique(e.provides),
    metrics:Object.fromEntries(AXES.map(a=>[a,e.metrics[a]])),holdout:e.holdout,admission:e.admission,evidence:e.evidence};
}
const graphs = new WeakSet();
const predecessors = new WeakMap();

export function canonicalGraph(events) {
  demand(Array.isArray(events),'expected event array');
  const content=new Map(), keys=new Map();
  for (const input of events) {
    const event=normalizeEvent(input), digest=id(event);
    const prior=content.get(digest);
    demand(!prior || canonicalJSON(event)===canonicalJSON(prior),'content-address collision');
    if (event.kind==='action') {
      demand(!keys.has(event.key) || keys.get(event.key)===digest,'conflicting immutable action key');
      keys.set(event.key,digest);
    }
    content.set(digest,event);
  }
  const ids=[...content.keys()].sort(lex);
  const records=ids.map(digest=>({digest,...content.get(digest)}));
  demand(records.filter(e=>e.kind==='scope').length===1,'expected unique graph scope');
  const {name}=records.find(e=>e.kind==='scope');
  const makeNode = (kind,key) => ({kind,key,digest:id([name,kind,key])});
  const nodesByDigest=new Map();
  const addNode=(kind,key)=>{
    const n=makeNode(kind,key); nodesByDigest.set(n.digest,n); return n.digest;
  };
  const edges=records.filter(a=>a.kind==='action').map(a=>{
    const stage=STAGES.indexOf(a.phase);
    const premises=unique([addNode('phase',String(stage)),addNode('evidence',a.digest),
      ...a.requires.map(x=>addNode('capability',x))]);
    const conclusions=unique([addNode('phase',String(stage+1)),...a.provides.map(x=>addNode('capability',x))]);
    return {digest:id([name,premises,conclusions]),action:a.key,premises,conclusions};
  }).sort((a,b)=>lex(a.digest,b.digest));
  const scope=Object.freeze({name,evidence:EVIDENCE});
  const graph=immutable({digest:id([name,ids]),scope,records,events:ids.map(k=>content.get(k)),
    nodes:[...nodesByDigest.values()].sort((a,b)=>lex(a.digest,b.digest)),edges});
  graphs.add(graph);
  return graph;
}
export function appendEvents(graph, events) {
  demand(graphs.has(graph) && Array.isArray(events),'invalid append');
  const next=canonicalGraph([...graph.events,...events]);
  predecessors.set(next,graph);
  return next;
}

function dimensions(axes) {
  demand(Array.isArray(axes)&&axes.length>0&&new Set(axes).size===axes.length &&
    axes.every(a=>AXES.includes(a)),'invalid projection axes');
  return axes.slice();
}

function vector(plan,axes) { return axes.map(a=>plan.metrics[a]); }
export function dominates(a,b,axes=AXES,cmpScalar=lex) {
  let strict=false;
  for (const k of axes) {
    const sign=cmpScalar(DIRECTIONS[k]*a.metrics[k],DIRECTIONS[k]*b.metrics[k]);
    if (sign>0) return false;
    if (sign<0) strict=true;
  }
  return strict;
}
const keyOf = p => p.actions.join('/');
function pareto(choices,axes,cmpScalar=lex) {
  // Duplicate points retain the lexically smallest joint action trace.
  const byVector=new Map();
  for (const p of choices.sort((a,b)=>lex(keyOf(a),keyOf(b)))) {
    const key=vector(p,axes).join(',');
    if (!byVector.has(key)) byVector.set(key,p);
  }
  const options=[...byVector.values()];
  return options.filter(p=>!options.some(q=>q!==p && dominates(q,p,axes,cmpScalar)));
}
function extend(p,a) {
  return {actions:[...p.actions,a.key],eventIds:[...p.eventIds,a.digest],
    caps:unique([...p.caps,...a.provides]),metrics:Object.fromEntries(AXES.map(k=>[k,p.metrics[k]+a.metrics[k]]))};
}
const can=(p,a)=>a.requires.every(r=>p.caps.includes(r));
function choices(graph,profile) {
  return STAGES.map(phase=>graph.records.filter(a=>a.kind==='action' && a.phase===phase &&
    a.admission==='qualified-fixture' && (profile==='full' || !a.holdout)).sort((a,b)=>lex(a.key,b.key)));
}

function explore(graph,mode,profile,axes,previous=null,rawComparator=lex) {
  let comparedCoordinates=0;
  const cmpScalar=(a,b)=>{
    comparedCoordinates++;
    // Modeled path coordinates are at most 4 million in magnitude.
    const r=rawComparator(a,b);
    demand(r===-1 || r===0 || r===1,'comparator must return numeric -1, 0 or 1');
    return r;
  };
  const layers=choices(graph,profile);
  const interfaces=layers.map((layer,i)=>
    unique(layers.slice(i+1).flatMap(l=>l.flatMap(a=>a.requires)).concat('resolved','partial')));
  const signatures=layers.map((layer,i)=>canonicalJSON([layer.map(a=>a.digest),
    mode==='factored'&&i<layers.length-1?interfaces[i]:[]]));
  const stops=[];
  let examined=0, extensions=0, factoredDiscarded=0;
  let plans=[{actions:[],eventIds:[],caps:['query'],metrics:{...zero}}];
  let peak=1, first=0, reusedExtensions=0, reusedExamined=0, reusedDiscarded=0;
  if (previous) {
    while (first<signatures.length && signatures[first]===previous.signatures[first]) {
      const stage=previous.stops[first];
      stops.push(stage);
      plans=stage.plans;
      peak=Math.max(peak,stage.expanded);
      reusedExtensions+=stage.expanded;
      reusedExamined+=stage.examined;
      reusedDiscarded+=stage.expanded-plans.length;
      first++;
    }
  }
  for (let stage=first;stage<layers.length;stage++) {
    const expanded=[];
    const stageExamined=plans.length*layers[stage].length;
    examined+=stageExamined;
    for (const p of plans) for (const a of layers[stage]) {
      if (can(p,a)) { expanded.push(extend(p,a)); extensions++; }
    }
    peak=Math.max(peak,expanded.length);
    if (mode==='factored' && stage<layers.length-1) {
      const grouped=new Map();
      for (const p of expanded) {
        const sig=p.caps.filter(x=>interfaces[stage].includes(x)).join(',');
        if (!grouped.has(sig)) grouped.set(sig,[]);
        grouped.get(sig).push(p);
      }
      plans=[...grouped.values()].flatMap(group=>pareto(group,axes,cmpScalar));
      factoredDiscarded+=expanded.length-plans.length;
    } else plans=expanded;
    stops.push({plans,expanded:expanded.length,examined:stageExamined});
  }
  const resolved=plans.filter(p=>p.caps.includes('resolved'));
  const pending=plans.filter(p=>p.caps.includes('partial')&&!p.caps.includes('resolved'));
  const qualify = p => ({...p,id:id([graph.digest,p.eventIds]),qualification:'modeled-resolved',evidence:EVIDENCE});
  return {frontier:pareto(resolved,axes,cmpScalar).map(qualify),signatures,stops,stats:{
    examined,extensions,factoredDiscarded,comparedCoordinates,peakLiveCandidates:peak,
    stageCounts:Object.fromEntries(stops.map((s,i)=>[STAGES[i],s.plans.length])),
    reusedStages:first,reusedExtensions,reusedExamined,reusedDiscarded,
    logicalExtensions:extensions+reusedExtensions,
    resolvedWitnessesBeforeFinalPareto:resolved.length,provisionalWitnessesNotCertified:pending.length,
    unqualifiedActionsExcluded:graph.records.filter(a=>a.admission==='unverified-proposal').length,
  }};
}

function weightsFor(axes,weights) {
  const w = weights ?? Object.fromEntries(axes.map(a=>[a,1]));
  demand(plain(w) && Object.keys(w).every(k=>axes.includes(k)) &&
    Object.values(w).every(x=>Number.isSafeInteger(x)&&x>=0&&x<=1e6),'invalid weights');
  demand(axes.some(a=>w[a]>0),'all-zero objective');
  return Object.fromEntries(axes.map(a=>[a,w[a]??0]));
}
function chooseWinner(frontier,axes,weights) {
  if (!frontier.length) return null;
  const value = p => axes.reduce((s,a)=>s+weights[a]*p.metrics[a]*DIRECTIONS[a],0);
  return frontier.slice().sort((p,q)=>value(p)-value(q)||lex(keyOf(p),keyOf(q)))[0];
}
const memo = new WeakMap();
const verificationMemo=new WeakMap();
const comparatorIds=new WeakMap([[lex,0]]);
let nextComparatorId=1;
function comparatorNumber(cmp) {
  demand(typeof cmp==='function','invalid scalar comparator');
  if (!comparatorIds.has(cmp)) {
    for (const [a,b] of [[-4000000,4000000],[4000000,-4000000],[0,0],[-1,-2],[1,2]]) {
      demand(cmp(a,b)===lex(a,b),'comparator failed signed scalar control');
    }
    comparatorIds.set(cmp,nextComparatorId++);
  }
  return comparatorIds.get(cmp);
}

export function searchLab(graph,{
  mode='factored',axes=AXES,weights,profile='full',proofBudget='all',cmpScalar=lex,
}={}) {
  demand(graphs.has(graph),'graph was not constructed canonically');
  demand(['factored','exhaustive'].includes(mode),'unsupported search architecture');
  demand(['full','narrow'].includes(profile),'unsupported candidate profile');
  demand(['all','none'].includes(proofBudget),'unsupported proof budget');
  const dims=dimensions(axes), w=weightsFor(dims,weights);
  const tag=canonicalJSON([mode,dims,profile,comparatorNumber(cmpScalar)]);
  if (!memo.has(graph)) memo.set(graph,new Map());
  const cache=memo.get(graph);
  const reusedFrontier=cache.has(tag);
  if (!reusedFrontier) {
    const previous=memo.get(predecessors.get(graph))?.get(tag);
    cache.set(tag,immutable(explore(graph,mode,profile,dims,previous,cmpScalar)));
  }
  const {frontier,stats}=cache.get(tag);
  const selected=chooseWinner(frontier,dims,w);
  const heldOut=profile==='narrow'?heldOutControl(graph,dims):null;
  let checked='not-checked', verificationReused=false;
  if (proofBudget==='all') {
    if (!verificationMemo.has(graph)) verificationMemo.set(graph,new Map());
    const receipts=verificationMemo.get(graph);
    verificationReused=receipts.has(tag);
    if (!verificationReused) receipts.set(tag,immutable(verifyFrontier(graph,frontier,{axes:dims,profile})));
    checked=receipts.get(tag);
  }
  return immutable({frontier,selected,stats:{...stats,reusedFrontier,verificationReused,
    actualCandidateExtensions:reusedFrontier?0:stats.extensions,
    actualCoordinateComparisons:reusedFrontier?0:stats.comparedCoordinates},heldOut,
    projection:{axes:dims,weights:w,profile}, architecture:mode,graphDigest:graph.digest,
    comparison:cmpScalar===lex?'reference-js':'caller-supplied-signed-comparator',
    certificate:checked,
    evidence:EVIDENCE});
}

export function verifyFrontier(graph,frontier,{axes=AXES,profile='full'}={}) {
  demand(graphs.has(graph),'invalid graph');
  demand(['full','narrow'].includes(profile),'unsupported candidate profile');
  const d=dimensions(axes);
  // Independent complete Cartesian replay. Enumerate first; evaluate each
  // entire tuple against sequential prerequisites. No explore()/pareto().
  const accepted=[];
  const layers=choices(graph,profile);
  function tuples(i,trace) {
    if (i<layers.length) {
      for (const action of layers[i]) tuples(i+1,[...trace,action]);
      return;
    }
    const caps=new Set(['query']);
    const metrics={...zero};
    for (const action of trace) {
      if (action.requires.some(k=>!caps.has(k))) return;
      action.provides.forEach(k=>caps.add(k));
      for (const a of AXES) metrics[a]+=action.metrics[a];
    }
    if (!caps.has('resolved')) return;
    const actions=trace.map(a=>a.key), eventIds=trace.map(a=>a.digest);
    accepted.push({actions,eventIds,caps:[...caps].sort(lex),metrics,
      id:id([graph.digest,eventIds]),qualification:'modeled-resolved',evidence:EVIDENCE});
  }
  tuples(0,[]);
  const costs = p => d.map(a=>p.metrics[a]*DIRECTIONS[a]);
  const all=accepted.map(p=>[p,costs(p),p.actions.join('/')]);
  const full=all.filter(([p,a,path])=>!all.some(([q,b,other])=>
    q!==p && b.every((x,i)=>x<=a[i]) && (b.some((x,i)=>x<a[i]) || other<path)
  )).map(([p])=>p).sort((a,b)=>lex(keyOf(a),keyOf(b)));
  const exact=canonicalJSON(frontier)===canonicalJSON(full);
  return {exact,boundary:'finite declared fixture actions only',survivors:full.length,
    completedCandidates:accepted.length};
}

export function heldOutControl(graph,axes=AXES) {
  const d=dimensions(axes);
  const narrow=explore(graph,'exhaustive','narrow',d).frontier;
  const full=explore(graph,'exhaustive','full',d).frontier;
  const witnesses=[];
  for (const incumbent of narrow) {
    const challenger=full.find(p=>dominates(p,incumbent,d));
    if (challenger) witnesses.push({incumbent:incumbent.actions,challenger:challenger.actions,
      before:incumbent.metrics,after:challenger.metrics});
  }
  return immutable({falsified:witnesses.length>0 || full.some(p=>!narrow.some(q=>keyOf(q)===keyOf(p))),
    allNarrowPointsDominated: witnesses.length===narrow.length && narrow.length>0,
    narrowedFrontierPoints:narrow.length,fullFrontierPoints:full.length,
    dominatedNarrowPoints:witnesses.length,example:witnesses[0]??null});
}
export function compareArchitectures(graph,options={}) {
  const exhaustive=searchLab(graph,{...options,mode:'exhaustive'});
  const factored=searchLab(graph,{...options,mode:'factored'});
  return immutable({exhaustive,factored,agree:canonicalJSON(exhaustive.frontier)===canonicalJSON(factored.frontier),
    fewerCandidateExtensions:exhaustive.stats.extensions - factored.stats.extensions});
}
export function weightCandidates(axes=AXES,denominator=4) {
  const d=dimensions(axes);
  demand(Number.isSafeInteger(denominator)&&denominator>=1&&denominator<=12,'unsupported weight grid');
  const out=[];
  function visit(index,left,prefix) {
    if (index===d.length-1) {
      out.push({denominator,weights:Object.fromEntries(d.map((k,i)=>[k,i===index?left:prefix[i]]))});
      return;
    }
    for (let w=0;w<=left;w++) visit(index+1,left-w,[...prefix,w]);
  }
  visit(0,denominator,[]);
  return immutable(out);
}
