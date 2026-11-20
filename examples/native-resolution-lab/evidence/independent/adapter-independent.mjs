import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const base=process.argv[2]?pathToFileURL(process.argv[2].replace(/\/$/,'')+'/'):new URL('../../',import.meta.url);
const read=n=>readFileSync(new URL(n,base));
const {instantiateBytes,nativeModule,planner}=await import(new URL('native-abi.mjs',base));
const pins=JSON.parse(read('pins.json')), g=JSON.parse(read('fixture.json'));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const n=['planner','chat','reversal'];
const original={};
let digestRefusals=0, loaderReadbacks=0;
for(const kind of n){
  const file=read('wasm/'+kind+'.wasm');
  assert.equal(hash(file),pins[kind].sha256);
  original[kind]=await instantiateBytes(file,pins[kind]);
  const b=Buffer.from(file); b[Math.floor(b.length/2)]^=1;
  await assert.rejects(instantiateBytes(b,pins[kind]),/digest mismatch/);digestRefusals++;
  await assert.rejects(instantiateBytes(file,null),/Missing build pin/);digestRefusals++;
  await assert.rejects(instantiateBytes(file,pins[n[(n.indexOf(kind)+1)%3]]),/digest mismatch/);digestRefusals++;
  const loaded=await nativeModule(kind,pins,{fetcher:async url=>{
    assert.equal(url.pathname.split('/').at(-1),kind+'.wasm');
    return {ok:true,arrayBuffer: async()=>file.buffer.slice(file.byteOffset,file.byteOffset+file.byteLength)};
  }});
  assert.deepEqual(Object.keys(loaded),Object.keys(original[kind])); loaderReadbacks++;
}
await assert.rejects(nativeModule('chat',pins,{fetcher:async()=>({ok:false})}),/unavailable/);
const foreign=Buffer.from('0061736d01000000010401600000020701017801790000','hex');
assert(WebAssembly.validate(foreign));
await assert.rejects(instantiateBytes(foreign,{sha256:hash(foreign)}),/Unapproved Wasm import/);
const invoke=planner(original.planner), weights=[1,1,1,1,1], run=(cut=g,active=g.axis,w=weights,profile=1)=>invoke(cut,active,w,profile);
const baseOut=run();
assert.equal(baseOut.nativeStatus,16);
assert.deepEqual(run({...g,base:[...g.base].reverse(),symbols:[...g.symbols].reverse()}),baseOut);
assert.deepEqual(run(g,g.axis,[10,1,1,1,1]).frontier,baseOut.frontier);
assert.equal(run(g,['clarity'],[0,0,0,1000000,0]).winner.metrics[3],Math.max(...baseOut.frontier.map(x=>x.metrics[3])));
const rejectCases=[
  [{...g,symbols:[...g.symbols,g.symbols[0]]}, /Duplicate symbol/],
  [{...g,base:[...g.base,g.base[0]]}, /Duplicate row identity/],
  [{...g,required:['unregistered']}, /Unknown symbol/],
  [{...g,base:g.base.map((a,i)=>i?a:{...a,costs:a.costs.slice(0,4)})}, /Wrong physical record width/],
  [{...g,base:g.base.map((a,i)=>i?a:{...a,costs:['7',...a.costs.slice(1)]})}, /Invalid packet word/],
];
for(const [bad,error] of rejectCases)assert.throws(()=>run(bad),error);
assert.throws(()=>run(g,['unknown']),/Invalid axis slot/);
assert.equal(run(g,g.axis,[1,1,1,-1,1]).nativeStatus,-2);
assert.equal(run(g,g.axis,weights,2).nativeStatus,-1);
assert.equal(run({...g,base:g.base.map((a,i)=>i?a:{...a,flag:4})}).nativeStatus,-2);
assert.deepEqual(run(),baseOut);
assert(!baseOut.frontier.some(r=>r.actions.includes('guess')));
// The transport consumes caller-declared qualified flags; it is intentionally
// not the source of admission. Record the counterexample, do not hide it.
const forgedRun=run({...g,base:g.base.map(a=>a.id==='guess'?{...a,flag:1}:a)});
assert(forgedRun.frontier.some(r=>r.actions.includes('guess')));
assert.notDeepEqual(forgedRun,baseOut);
assert.deepEqual(run(),baseOut);
// A hostile fake export is never admitted by instantiateBytes at the true
// hash. Inject it only here to locate the transport field-check boundary.
function malformedResult(changes){
  const mem=new WebAssembly.Memory({initial:1});
  return planner({memory:mem,idol_planner__plan:(...args)=>{
    const output=Number(args[10]), view=new DataView(mem.buffer);
    const words=[1,1,1,1,2,3,4,0,1,2,3,4];
    for(const [i,v] of Object.entries(changes.words??{}))words[i]=v;
    words.forEach((v,i)=>view.setBigInt64(output+8*i,BigInt(v),true));
    return BigInt(changes.returned??1);
  }});
}
assert.throws(()=>malformedResult({returned:0})(g,g.axis,weights,1),/extent disagrees/);
assert.throws(()=>malformedResult({words:{1:4097}})(g,g.axis,weights,1),/frontier extent/);
assert.throws(()=>malformedResult({words:{2:2}})(g,g.axis,weights,1),/winner extent/);
assert.throws(()=>malformedResult({words:{3:0}})(g,g.axis,weights,1),/row index/);
const runUntrusted=result=>{
  try{return {status:'accepted-by-transport',result:malformedResult({words:result})(g,g.axis,weights,1)};}
  catch(e){return {status:'refused-by-transport',reason:e.message};}
};
const falseCount=runUntrusted({0:-1}), falseMetric=runUntrusted({7:-4});
console.log(JSON.stringify({loaderReadbacks,digestRefusals,foreignImportRefusals:1,
  structuralInputRefusals:9,structuralOutputRefusals:4,
  signedClarityControls:'pass',pristineAfterRefusalAndMutation:'pass',
  forgedFlag:{baselineResolved:baseOut.resolvedCount,forgedResolved:forgedRun.resolvedCount,
    affectedFrontier:forgedRun.frontier.filter(r=>r.actions.includes('guess')).length},
  syntheticUntrustedExport:{invalidResolvedCount:falseCount.status,negativeMetric:falseMetric.status},
  exactTransportDigest:hash(read('native-abi.mjs')),
  scope:'offline transport control; source fixture is trusted input; not a publication or evidence-admission policy'},null,2));
