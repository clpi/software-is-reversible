import {AXES,appendEvents,canonicalGraph,compareArchitectures,demoEvents,weightCandidates} from './search.mjs';
import {analyzeInference,fixture} from './inference.mjs';
import {apply,reverse} from './reversal.mjs';
import {loadKernel} from './kernel.mjs';
import {incidence} from './incidence.mjs';
const $=id=>document.getElementById(id);
const text=(id,s)=>{$(id).textContent=s};
const show=(id,x)=>text(id,JSON.stringify(x,null,2));
const stableFacts=demoEvents(), finalReceipt=stableFacts.find(e=>e.key==='full-receipt');
let graph=canonicalGraph(stableFacts.filter(e=>e!==finalReceipt)), appended=false;
let current=5, actions=[], kernel=null;
function line(parent,tag,content) {
  const e=document.createElement(tag); e.textContent=content; parent.append(e); return e;
}
function axes() { return AXES.filter(a=>a!=='storage'||$('storage').checked); }
function solve() {
  const d=axes(), weights=Object.fromEntries(d.map(a=>[a,a==='latency'||a==='clarity'?Number($(a).value):1]));
  const profile=$('profile').value;
  const result=compareArchitectures(graph,{axes:d,weights,profile,...(kernel?{cmpScalar:kernel.compare}:{})});
  const {factored,exhaustive,agree}=result, score=factored.selected?.metrics;
  text('graph-state', `${graph.events.length} append-set events · cut ${graph.digest.slice(0,16)} · synthetic costs`);
  const out=$('search-result');out.replaceChildren();
  line(out,'p', `Oracle agreement: ${agree&&factored.certificate.exact?'exact':'FAILED'} · ${factored.frontier.length} frontier vectors · ${weightCandidates(d).length} generated weight vectors`);
  line(out,'p',`Candidate extensions this cut: exhaustive ${exhaustive.stats.extensions}, factored ${factored.stats.extensions}. Factored reused ${factored.stats.reusedStages} stages; ${factored.stats.actualCoordinateComparisons} new ${kernel?'Idol Wasm':'reference'} coordinate comparisons; rank reuses the stored frontier: ${factored.stats.reusedFrontier?'yes':'no'}.`);
  if(score) {
    const picked=line(out,'p','Selected: '+factored.selected.actions.join(' → '));picked.className='picked';
    line(out,'p', d.map(k=>`${k} ${score[k]}`).join(' · '));
  }
  if(factored.heldOut) line(out,'p',`Held-out check: ${factored.heldOut.dominatedNarrowPoints}/${factored.heldOut.narrowedFrontierPoints} narrowed points dominated by an excluded plan.`).className='error';
  const detail=document.createElement('details');out.append(detail);line(detail,'summary','Inspect the entire frontier and independent oracle');
  line(detail,'pre',JSON.stringify({frontier:factored.frontier.map(p=>({actions:p.actions,metrics:p.metrics})),certificate:factored.certificate,heldOut:factored.heldOut},null,2));
  show('graph-data',{graph,incidence:{order:graph.nodes.map(n=>n.key),0:'absent',1:'premise',2:'conclusion',3:'both',rows:incidence(graph)},weightCandidates:weightCandidates(d)});
}
function reportUndo(note='Ready. No action outside this page is available.') {
  show('undo-result',{freshState:current,history:actions,note});
}
function dispatch(kind) {
  const rec=apply(kind,current);
  const next=kernel ? kernel[kind](current) : rec.after;
  if(next!==rec.after) throw new Error('Native result disagrees with the action contract');
  actions.push(rec); current=next; reportUndo(kernel?'Executed by Idol-generated WebAssembly.':'Reference action; native not admitted.');
}
const commands=new Set([...document.querySelectorAll('[data-prompt]')].map(x=>x.dataset.prompt.toLowerCase()));
const clean=s=>s.trim().toLowerCase().replace(/\s+/g,' ');
function inputInt(id,min,max){const raw=$(id).valueAsNumber;if(!Number.isInteger(raw)||raw<min||raw>max)throw new Error(`Choose ${id} in ${min}–${max}.`);return raw;}
function chat() {
  const prompt=$('query').value.trim();
  if(!prompt)return;
  const pane=$('transcript');line(pane,'li',prompt);
  const respond=s=>{line(pane,'li',s).className='answer';pane.scrollTop=pane.scrollHeight};
  try {
    const cmd=clean(prompt);
    if(!commands.has(cmd)){show('token-result',{status:'refused',reason:'Unregistered typed command'});respond('No registered command matched. I didn’t take an action.');return;}
    const horizon=inputInt('horizon',1,fixture.horizon),tilt=inputInt('tilt',1,12);
    const common={horizon,reweight:{'':[tilt,...fixture.vocabulary.slice(1).map(()=>1)]},
      threshold:cmd==='require stronger evidence'?'3/4':$('threshold').value,
      budget:inputInt('budget',0,4096),...(kernel?{compareI32:kernel.compare}:{})};
    const requestedResolution=Math.min(horizon,inputInt('resolution',0,fixture.horizon));
    const start=analyzeInference({...common,resolution:requestedResolution});
    const obscurityLimit=inputInt('obscurity-limit',1,64);
    const auto=$('refine').checked;
    const steps=[start.obscurity.compatibilityCount];
    let result=start;
    let resolution=requestedResolution;
    while(auto&&result.map.certified&&steps.at(-1)>obscurityLimit&&resolution<horizon) {
      result=analyzeInference({...common,resolution:++resolution});
      steps.push(result.obscurity.compatibilityCount);
    }
    const resolved=result.qualification.status==='qualified'&&steps.at(-1)<=obscurityLimit;
    const first=result.map.tokens?.[0];
    const route=first===0?'clear':first===1?'flip':null;
    const plan={source:resolution>requestedResolution?'explicit command + structural refinement':'explicit command + gate',
      config:{horizon,threshold:common.threshold,tilt,requestedResolution,resolution,obscurityLimit,automaticRefinement:auto},
      action:resolved?route:null,pending:!resolved,
      stopVector:{certified:result.map.certified,remainingUpper:result.map.remainingUpper,reason:result.map.stopReason,minimumMass:common.threshold},
      actionEffects:'sandbox only', resolutionTrajectory:steps};
    show('token-result',{plan,result});
    let summary=result.map.tokens? `Exact candidate [${result.map.tokens.join(', ')}] at ${result.map.probability}. `:'No terminating candidate in this scope. ';
    if(!result.map.certified)summary=summary.replace('Exact candidate','Uncertified candidate');
    summary+=`Greedy: [${result.greedy.tokens.join(', ')}] at ${result.greedy.probability}${result.greedy.valid?'':' (not terminal)'}. `;
    summary+=`Projection fiber: ${steps.join(' → ')}. `;
    summary+=route&&resolved ? `Qualified sandbox action: ${route}.` : `No action: ${result.qualification.status==='qualified'?'projection ambiguous or no registered terminal action':result.qualification.reason}.`;
    if(route&&resolved&&$('apply').checked) { dispatch(route);summary+=' Executed locally with a reversal receipt.'; }
    respond(summary);
  } catch(e){show('token-result',{status:'refused',reason:e.message});respond('Refused: '+e.message);}
}
for (let x=0;x<8;x++){const opt=line($('seed'),'option',x.toString(2).padStart(3,'0'));opt.value=String(x);}
$('seed').value='5';
$('horizon').max=fixture.horizon;$('horizon').value=fixture.horizon;
$('resolution').max=fixture.horizon;
for (const el of document.querySelectorAll('[data-prompt]')) el.addEventListener('click',()=>{$('query').value=el.dataset.prompt;chat()});
$('prompt').addEventListener('submit',e=>{e.preventDefault();chat()});
$('rerank').addEventListener('click',solve);
for (const id of ['latency','clarity','storage','profile']) $(id).addEventListener('change',solve);
$('append').addEventListener('click',()=>{ if(appended)return;graph=appendEvents(graph,[finalReceipt]);appended=true;$('append').disabled=true;solve();});
$('flip').addEventListener('click',()=>dispatch('flip'));$('clear').addEventListener('click',()=>dispatch('clear'));
$('undo-one').addEventListener('click',()=>{
  const rec=actions.at(-1);
  if(!rec){reportUndo('No admitted action to reverse.');return;}
  const r=reverse(rec,current); if(!r.ok){reportUndo('Refused: '+r.reason);return;}
  if(rec.kind==='flip'&&kernel&&kernel.flip(current)!==r.prior) {reportUndo('Refused: native inverse disagrees.');return;}
  actions.pop();current=r.prior;reportUndo('Restored the exactly observed pre-state.');
});
$('change').addEventListener('click',()=>{current^=4;reportUndo('Outside edit simulated; history remains intact.');});
$('reset').addEventListener('click',()=>{current=Number($('seed').value);actions=[];reportUndo();});
try {
  kernel=await loadKernel();
  text('runtime','Idol Wasm + exact reference solvers');
  text('native-evidence','Three action/comparison exports compiled twice identically with retained Idol 5efca0e. Host supplies no WASI authority. Exact reference code builds the search and verifies it independently; the active view reports comparator counts. This is not a fully native port.');
} catch (e) {text('runtime','Reference only · '+e.message);}
reportUndo();solve();
