import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import {performance} from 'node:perf_hooks';
import {pathToFileURL} from 'node:url';
const root=process.argv[2];
const {instantiateBytes,nativePage}=await import(pathToFileURL(root+'/native-abi.mjs'));
const read=p=>fs.readFileSync(root+'/'+p);
const pins=JSON.parse(read('pins.json')), fixtures=JSON.parse(read('suffix-fixtures.json'));
const native=nativePage(await instantiateBytes(read('wasm/suffix.wasm'),pins.suffix));
function exhaustive(cut,rank,limit){
 const list=[];
 function visit(at,code){
   if(at===0)return;
   const [d,x,y,e]=cut.rows[at-1]; if(d>1){visit(x,2*code);visit(y,2*code+1);}
   if(e)list.push(code);
 }
 visit(cut.root,1);
 return {status:Math.min(limit,Math.max(0,list.length-rank)),lower:list.length,upper:list.length,rows:cut.rows.length,codes:list.slice(rank,rank+limit)};
}
const ms=x=>x.reduce((a,b)=>a+b,0);
const summary={};
for(const [name,cut] of Object.entries(fixtures).filter(([_,c])=>c.horizon===12)){
 const expects=exhaustive(cut,0,8), rank=expects.lower-8;
 assert.deepEqual(native(cut,rank,8),exhaustive(cut,rank,8));
 let raw=[];
 for(let i=0;i<26;i++){
   const record={};
   for(const j of [(i%2),(i+1)%2]){
     const run=j===0?exhaustive:native, key=j===0?'exhaustive':'nativePage';
     const start=performance.now();let amount=0;
     for(let k=0;k<100;k++)amount+=run(cut,(k%2)*rank,8).codes.length;
     record[key]=(performance.now()-start)/100;
     assert.equal(amount,800);
   }
   if(i>4)raw.push(record);
 }
 const num=xs=>xs.sort((a,b)=>a-b)[10];
 const trees=(()=>{
  const list=[];
  const f=(at,p)=>{if(at===0)return;const [d,a,b,e]=cut.rows[at-1];list.push([p,d,+(a!==0),+(b!==0),e]);f(a,p+'0');f(b,p+'1');};
  f(cut.root,'');return list;
 })();
 summary[name]={support:expects.lower,suffixRows:cut.rows.length,expandedRows:trees.length,suffixInputBytes:Buffer.byteLength(JSON.stringify(cut.rows)),expandedInputBytes:Buffer.byteLength(JSON.stringify(trees)),
  medianMillis:{exhaustive:num(raw.map(x=>x.exhaustive)),nativePage:num(raw.map(x=>x.nativePage))},samplesMillis:raw};
}
console.log(JSON.stringify({node:process.version,cpu:os.cpus()[0]?.model,scope:'single-host systematic pair order; cold local query, preconstructed inputs; native includes packet writes and outputs; JS performs full enumeration then returns same requested page; excludes interning, input encode and browser DOM',summary},null,2));
