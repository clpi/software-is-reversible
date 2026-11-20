import {bindNumber,bindExact,integral,nativeModule,nativePage,nativeRerank,planner} from './native-abi.mjs';
const $=id=>document.getElementById(id);
const content=(id,x)=>{$(id).textContent=x;};
const dump=(id,x)=>content(id,JSON.stringify(x,null,2));
const element=(tag,value)=>{const e=document.createElement(tag);e.textContent=value;return e;};
const number=(id,min,max)=>integral($(id).valueAsNumber,min,max,id);
const loadJson=async file=>{const x=await fetch(new URL(file,import.meta.url));if(!x.ok)throw new Error('Missing '+file);return await x.json();};
function enable(ids){for(const id of ids)$(id).disabled=false;}
function installPlanner(ex,fixture,retune) {
  const run=planner(ex,retune);let cut=structuredClone(fixture);
  const printPacket=()=>{$('packet').value=JSON.stringify(cut,null,2)};
  const render=(reuse=false)=>{
    try {
      const active=cut.axis.filter(name=>name!=='storage'||$('storage').checked);
      const weights=[number('latency',0,99),1,1,number('clarity',0,99),1];
      const result=(reuse?run.rerank:run)(cut,active,weights,Number($('profile').value));
      content('winner',result.nativeStatus<0?'Native refusal '+result.nativeStatus:result.winner?.actions.join(' / ')??'No qualifying plan.');
      $('metrics').replaceChildren();$('frontier').replaceChildren();
      for(const [name,val] of Object.entries({Edges:cut.base.length,Qualifying:result.resolvedCount,Pareto:result.frontierCount,'Native verdict':result.nativeStatus,'Frontier reuse':result.reusedFrontier?'yes':'no'})){
        const e=document.createElement('div');e.append(element('strong',val??'—'),element('span',name));$('metrics').append(e);
      }
      if(!result.frontier)return;
      const table=document.createElement('table'), head=table.createTHead().insertRow();
      for(const k of ['Plan',...cut.axis])head.append(element('th',k));
      const body=table.createTBody();
      for(const row of result.frontier){
        const tr=body.insertRow();
        for(const value of [row.actions.join(' / '),...row.metrics])tr.append(element('td',value));
      }
      $('frontier').append(table);
    } catch(e){$('frontier').replaceChildren();$('metrics').replaceChildren();content('winner','Transport refusal: '+e.message);}
  };
  const sync=()=>{printPacket();$('append').disabled=!(cut.append&&!cut.base.some(x=>x.id===cut.append.id));render();};
  $('solve').onclick=()=>render();
  $('rerank').onclick=()=>render(true);
  $('append').onclick=()=>{cut={...cut,base:[...cut.base,cut.append]};sync();};
  $('reset').onclick=()=>{cut=structuredClone(fixture);sync();};
  $('packetRun').onclick=()=>{
    try {
      if($('packet').value.length>80000)throw new Error('Packet is too large');
      const next=JSON.parse($('packet').value);
      if(next?.schema!==fixture.schema||JSON.stringify(next.axis)!==JSON.stringify(fixture.axis))throw new Error('Unsupported packet schema or axes');
      cut=next;sync();
    }catch(e){content('winner','Transport refusal: '+e.message);$('metrics').replaceChildren();$('frontier').replaceChildren();}
  };
  enable(['solve','rerank','reset','packetRun']);sync();
}
function installChat(ex) {
  const run=bindExact(ex,'idol_chat__decision');
  const fields=['rootRow','zeroRow','oneRow','minStop','horizon'];
  const labels=['Unresolved; no admissible result yet','Unresolved; an incumbent exists','Exact probability; canonical answer still unresolved','Exact canonical answer','No terminal result possible in this scope'];
  const answer=()=>{
    try{
      const args=fields.map((x,i)=>number(x,i<3?-1:1,i<3?63:4));
      const packed=run(...args,8);
      if(packed<0n){dump('chatResult',{status:Number(packed),nativeVerdict:'Native refusal'});return;}
      const [status,path,n,d,N,D,work,unknown]=[[0,3],[3,4],[7,7],[14,13],[27,7],[34,13],[47,4],[51,4]].map(([offset,width])=>Number((packed>>BigInt(offset))&((1n<<BigInt(width))-1n)));
      dump('chatResult',{status,nativeVerdict:labels[status]??'Native refusal',pathCode:path,
        tokenIds:path>0?[...path.toString(2).slice(1)].map(Number).concat(2):[],
        lower:[n,d],upper:[N,D],expanded:work,unknownPrefixes:unknown});
    }catch(e){content('chatResult',e.message);}
  };
  enable(['answer']);$('answer').onclick=answer;
  for(const p of document.querySelectorAll('.chatPreset')){
    p.disabled=false;p.onclick=()=>{p.dataset.values.split(',').forEach((val,i)=>{$(fields[i]).value=val});answer();};
  }
  answer();
}
function installReversal(ex) {
  const prepare=bindExact(ex,'idol_reversal__prepare'), advance=bindNumber(ex,'idol_reversal__advance'),
    verify=bindNumber(ex,'idol_reversal__verify'), inverse=bindNumber(ex,'idol_reversal__inverse'),
    undoVerify=bindNumber(ex,'idol_reversal__undoverify');
  let observed=5, snapshot=5, receipt=null;
  const caps=()=>7+($('restorePerm').checked?8:0);
  const display= (stage,x)=>dump('undoResult',{stage,observedFrame:observed,retainedReceipt:receipt?.toString()??null,native:x});
  $('apply').onclick=()=>{
    if(receipt!==null){display('transport: rewind or reset before another transaction',null);return;}
    const proposed=prepare(snapshot,observed,Number($('plan').value),caps());
    if(proposed<0n){display('Native prepare refusal',String(proposed));return;}
    receipt=proposed;
    const next=advance(proposed,receipt,observed,caps());
    if(next<0){display('Native advance refusal',next);return;}
    observed=next;snapshot=observed;
    display('Native verification checked the sandbox post-state',verify(proposed,receipt,observed));
  };
  $('rewind').onclick=()=>{
    if(receipt===null){display('No retained receipt',null);return;}
    const prior=observed,next=inverse(receipt,receipt,prior,caps());
    if(next<0){display('Native rewind refusal',next);return;}
    observed=next;
    const verdict=undoVerify(receipt,receipt,prior,observed,caps());
    if(verdict>=0){receipt=null;snapshot=observed;}
    display(verdict>=0?'Native rewind verified':'Native rewind verification refused',verdict);
  };
  $('outside').onclick=()=>{observed+=8;display('Sandbox supplied a newer generation at the same value',null);};
  $('undoReset').onclick=()=>{observed=5;snapshot=5;receipt=null;display('New sandbox experiment',null);};
  enable(['apply','rewind','outside','undoReset']);display('New sandbox experiment',null);
}
function installSuffix(ex,fixtures){
  const run=nativePage(ex);
  const page=()=>{
    try{
      const cut=fixtures[$('suffixCase').value];
      const result=run(cut,number('rank',0,1073741823),number('limit',0,32));
      dump('witnessResult',{fixture:cut.label,...result,verdict:result.status>=0?'Native page':result.status===-2?'Native refusal: unknown paths can change ranks':'Native refusal: malformed or outside support',
        witnesses:result.codes?.map(code=>[...code.toString(2).slice(1)].map(Number).concat(2))});
    }catch(e){content('witnessResult',e.message);}
  };
  enable(['page']);$('page').onclick=page;page();
}
try{
  const [pin,fixture,suffixes]=await Promise.all([loadJson('pins.json'),loadJson('fixture.json'),loadJson('suffix-fixtures.json')]);
  const modules=await Promise.all(['planner','chat','reversal','rerank','suffix'].map(k=>nativeModule(k,pin)));
  installPlanner(modules[0],fixture,nativeRerank(modules[3]));installChat(modules[1]);installReversal(modules[2]);installSuffix(modules[4],suffixes);content('status','Native Idol engines · no solver fallback');
}catch(e){content('status','Native admission failed: '+e.message);}
