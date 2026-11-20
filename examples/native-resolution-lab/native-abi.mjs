const expectedImports=new Set(['fd_write','proc_exit','fd_read','args_sizes_get','args_get']);
export async function nativeModule(kind,pins,dependencies={}){
  const fetcher=dependencies.fetcher??fetch;
  const resp=await fetcher(new URL('./wasm/'+kind+'.wasm',import.meta.url));
  if(!resp.ok)throw new Error('Native module unavailable: '+kind);
  return instantiateBytes(await resp.arrayBuffer(),pins[kind]);
}
export async function instantiateBytes(bytes,pin){
  if(!pin||typeof pin.sha256!=='string')throw new Error('Missing build pin');
  const snapshot=(ArrayBuffer.isView(bytes)?new Uint8Array(bytes.buffer,bytes.byteOffset,bytes.byteLength):new Uint8Array(bytes)).slice();
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',snapshot))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(hash!==pin.sha256)throw new Error('Native module digest mismatch');
  const m=await WebAssembly.compile(snapshot), wasi=Object.create(null);
  for (const item of WebAssembly.Module.imports(m)){
    if(item.module!=='wasi_snapshot_preview1'||item.kind!=='function'||!expectedImports.has(item.name))throw new Error('Unapproved Wasm import');
    wasi[item.name]=()=>{throw new Error('This demo grants no host effects');};
  }
  const inst=await WebAssembly.instantiate(m,{wasi_snapshot_preview1:wasi});
  return inst.exports;
}
export function integral(x,min,max,label){
  if(!Number.isSafeInteger(x)||x<min||x>max)throw new RangeError('Invalid '+label);
  return x;
}
export function bindNumber(exports,name){
  const f=exports[name];if(typeof f!=='function')throw new Error('Missing export: '+name);
  return (...args)=>Number(f(...args.map(x=>typeof x==='bigint'?x:BigInt(integral(x,-2147483648,4294967295,'numeric carrier')))));
}
export function bindExact(exports,name){
  const f=exports[name];if(typeof f!=='function')throw new Error('Missing export: '+name);
  return (...args)=>f(...args.map(x=>typeof x==='bigint'?x:BigInt(integral(x,-2147483648,4294967295,'numeric carrier'))));
}
export function planner(exports, retune = null) {
  const run=bindNumber(exports,'idol_planner__plan');
  const storage=exports.memory;
  if(!(storage instanceof WebAssembly.Memory))throw new Error('Missing Wasm memory');
  // ABI regions are physical transport only. The Idol module decides feasibility,
  // costs, tie-breaking, frontier membership, refusal and winner.
  const start=storage.grow(11)*65536;
  const retained=new WeakMap();
  function rerank(cut,active,weights,profile) {
    if(!retune)throw new Error("Native reranker not admitted");
    const key=JSON.stringify([active,profile]);
    const prior=retained.get(cut)?.get(key);
    if(!prior||JSON.stringify(cut)!==prior.packet)throw new Error("No checked frontier for this exact cut and axis selection; run search first");
    const winnerOrdinal=retune(prior.words,prior.mask,8,weights);
    if(winnerOrdinal<0)return {nativeStatus:winnerOrdinal};
    integral(winnerOrdinal,0,prior.result.frontierCount,"rerank result ordinal");
    return {...prior.result, winnerOrdinal, winner:prior.result.frontier[winnerOrdinal-1]??null, reusedFrontier:true};
  }
  const plan=(cut,active,weights,profile) => {
    const axes=['latency','storage','risk','clarity','compute'];
    if(cut.symbols.length>16||cut.base.length>256||weights.length!==5)throw new Error('Packet exceeds physical demo limits');
    const idMap=new Map(cut.symbols.map((s,i)=>[s,i]));
    if(idMap.size!==cut.symbols.length)throw new Error('Duplicate symbol in the transport dictionary');
    const bits=names=>names.reduce((n,name)=>{
      if(!idMap.has(name))throw new Error('Unknown symbol in transport: '+name);
      return n | (1<<idMap.get(name));},0);
    const ordered=cut.base.slice().sort((a,b)=>(a.stage-b.stage)||(a.id<b.id?-1:a.id>b.id?1:0));
    const names=ordered.map(a=>a.id);
    if(new Set(names).size!==names.length)throw new Error('Duplicate row identity');
    const wire=ordered.flatMap(a=>[a.stage,bits(a.requires),bits(a.provides),a.flag,...a.costs]);
    if(wire.length!==9*ordered.length)throw new Error('Wrong physical record width');
    const maxPlans=4096,data=start,weight=data+8*wire.length,work=weight+40,out=work+8*9*maxPlans,end=out+8*(3+9*maxPlans);
    const extra=Math.max(0,Math.ceil((end-storage.buffer.byteLength)/65536));
    if(extra)storage.grow(extra);
    const v=new DataView(storage.buffer);
    const write=(at,words)=>words.forEach((val,i)=>v.setBigInt64(at+8*i,BigInt(integral(val,-2147483648,2147483647,'packet word')),true));
    const read=(at,count)=>Array.from({length:count},(_,i)=>Number(v.getBigInt64(at+8*i,true)));
    write(data,wire);write(weight,weights);
    const mask=active.reduce((n,name)=>n|(1<<integral(axes.indexOf(name),0,4,'axis slot')),0);
    const result=run(data,ordered.length,bits(cut.initial),bits(cut.required),profile,mask,8,weight,work,maxPlans,out,maxPlans);
    if(result<0)return {nativeStatus:result};
    const [resolvedCount,n,winnerOrdinal]=read(out,3);
    integral(n,0,maxPlans,'native frontier extent');
    integral(resolvedCount,n,maxPlans,'native resolved count');
    if(n!==result)throw new Error('Returned frontier extent disagrees with the native header');
    integral(winnerOrdinal,0,n,'native winner extent');
    const rows=[];
    for(let i=0;i<n;i++){
      const [a,b,c,d,...metrics]=read(out+8*(3+9*i),9);
      metrics.forEach(x=>integral(x,0,4000000,'native metric'));
      rows.push({actions:[a,b,c,d].map(j=>names[integral(j,1,names.length,'native row index')-1]),metrics});
    }
    const frontier=Object.freeze(rows.map(x=>Object.freeze({actions:Object.freeze(x.actions),metrics:Object.freeze(x.metrics)})));
    const snapshot=Object.freeze({nativeStatus:result,resolvedCount,frontierCount:n,winnerOrdinal,winner:frontier[winnerOrdinal-1]??null,frontier});
    if(!retained.has(cut))retained.set(cut,new Map());
    retained.get(cut).set(JSON.stringify([active,profile]),{result:snapshot,mask,packet:JSON.stringify(cut),words:read(out,3+9*n)});
    return snapshot;
  };
  return Object.assign(plan,{rerank});
}

export function nativeRerank(exports){
  const call=bindNumber(exports,'idol_rerank__winner');
  const m=exports.memory;
  if(!(m instanceof WebAssembly.Memory))throw new Error('Missing native rerank memory');
  const begin=m.grow(6)*65536;
  return (words,mask,maximum,weights)=>{
    if(words.length<3||(words.length-3)%9!==0||words.length>3+9*4096||weights.length!==5)
      throw new Error('Invalid physical rerank extent');
    const w=begin+8*words.length;
    const data=new DataView(m.buffer);
    for(let i=0;i<words.length;i++)data.setBigInt64(begin+8*i,BigInt(words[i]),true);
    for(let i=0;i<weights.length;i++)data.setBigInt64(w+8*i,BigInt(weights[i]),true);
    return call(begin,(words.length-3)/9,mask,maximum,w);
  };
}

export function nativePage(exports){
  const readPage=bindNumber(exports,'idol_suffix__page'),memory=exports.memory;
  if(!(memory instanceof WebAssembly.Memory))throw new Error('Missing native paging memory');
  const start=memory.grow(1)*65536;
  return (cut,rank,limit)=>{
    const len=integral(cut.rows.length,1,128,'suffix state extent');
    integral(limit,0,32,'page length');
    const view=new DataView(memory.buffer);
    for(let i=0;i<len;i++){
      if(cut.rows[i]?.length!==4)throw new Error('Wrong suffix record width');
      cut.rows[i].forEach((val,j)=>view.setBigInt64(start+8*(4*i+j),BigInt(val),true));
    }
    const status=readPage(start,len,cut.root,cut.horizon,rank,limit);
    if(status===-1)return {status};
    const lower=Number(view.getBigInt64(start+8*6*len,true));
    const upper=Number(view.getBigInt64(start+8*(6*len+1),true));
    integral(Math.max(0,status),0,limit,'native page extent');
    return {status,lower,upper,rows:len,codes:Array.from({length:Math.max(0,status)},
      (_,i)=>Number(view.getBigInt64(start+8*(6*len+2+i),true)))};
  };
}
