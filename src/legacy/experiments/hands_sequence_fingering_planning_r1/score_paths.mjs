import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {performance} from 'node:perf_hooks';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const old=path.join(here,'..','hands_fingering_inference_poc_r1');
const req=createRequire(path.join(old,'package.json'));
const ort=req('onnxruntime-node');
const {predictFingerings}=req('@lumikey/piano-fingering-model');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(n,v)=>fs.writeFileSync(path.join(here,n),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const bindings=read(path.join(here,'SOURCE_EVENT_BINDINGS.json'));
const pp=read(path.join(here,'PIANOPLAYER_RAW_OUTPUT.json'));
const source=bindings.bindings;
const baseline=read(path.join(old,'OUTPUT_VALIDATION_AND_FEASIBILITY.json'));
const paths={old_design:Object.fromEntries(source.map(x=>[x.note_id,x.source_timeline_note.finger])),lumikey_greedy:Object.fromEntries(baseline.rows.map(x=>[x.note_id,x.ai_finger])),pianoplayer_sequence:Object.fromEntries(Object.values(pp.hands).flat().map(x=>[x.note_id,x.finger]))};
const started=performance.now();const models={};
for(const h of ['left','right'])models[h]=await ort.InferenceSession.create(path.join(old,'node_modules','@lumikey','piano-fingering-model','models',`fingering_transformer_${h}.onnx`),{executionProviders:['cpu'],enableProfiling:true,profileFilePrefix:path.join(here,'score_cpu_'+h)});
const results=[];
try{
 for(const [name,fingers] of Object.entries(paths)){
  const notes=source.map(x=>({...x.model_input}));
  const byHand={left:source.filter(x=>x.model_input.left).sort((a,b)=>a.model_input.time-b.model_input.time||a.model_input.note-b.model_input.note),right:source.filter(x=>!x.model_input.left).sort((a,b)=>a.model_input.time-b.model_input.time||a.model_input.note-b.model_input.note)};
  const indices={left:0,right:0};const traces=[];const nll={left:0,right:0};const wrapped={};
  for(const h of ['left','right']){
   wrapped[h]={run:async input=>{
    const index=indices[h]++;const item=byHand[h][index];
    if(!item)throw Error('Extra inference note');
    const tokens=Array.from(input.tokens.data);
    if(tokens.some((v,i)=>i%5===4&&v!==-1))throw Error('Unexpected future finger hint');
    const target=notes[item.model_input_index];
    if(Object.hasOwn(target,'finger'))throw Error('Premature forced finger');
    const output=await models[h].run(input);const logits=Array.from(output.logits.data);
    if(logits.length!==5||logits.some(v=>!Number.isFinite(v)))throw Error('Invalid logits');
    const maximum=Math.max(...logits);const logZ=maximum+Math.log(logits.reduce((s,v)=>s+Math.exp(v-maximum),0));
    const finger=fingers[item.note_id];const logProbability=logits[finger-1]-logZ;nll[h]-=logProbability;
    // Official API reads current note.finger AFTER awaiting run(). Set only this note now.
    // Earlier assignments rebuild the official per-finger state; all FUTURE hints remain absent.
    target.finger=finger;
    traces.push({note_id:item.note_id,hand:h,hand_index:index,chosen_finger:finger,input_tokens:tokens,logits,probabilities:logits.map(v=>Math.exp(v-logZ)),chosen_log_probability:logProbability,prefix_fingers:byHand[h].slice(0,index).map(x=>fingers[x.note_id])});
    return output;
   }};
  }
  const t=performance.now();const replay=await predictFingerings(notes,wrapped);
  if(replay.length!==23||traces.length!==23)throw Error('Incomplete scoring');
  for(const x of source){const matches=replay.filter(n=>['left','note','time','duration','velocity'].every(k=>n[k]===x.model_input[k]));if(matches.length!==1||matches[0].finger!==fingers[x.note_id])throw Error('Replay binding failed');}
  results.push({path_name:name,fingers,conditional_nll:nll.left+nll.right,conditional_nll_by_hand:nll,mean_nll:(nll.left+nll.right)/23,scoring_ms:performance.now()-t,traces});
 }
 const oldTraces=read(path.join(old,'RAW_ONNX_LOGITS_AND_TOKENS.json'));const greedy=results.find(r=>r.path_name==='lumikey_greedy');
 let maxLogitDifference=0;
 for(const t of greedy.traces){const previous=oldTraces.find(x=>x.hand===t.hand&&x.hand_note_index===t.hand_index);if(JSON.stringify(t.input_tokens)!==JSON.stringify(previous.input_tokens))throw Error('Official greedy tokens not reproduced');for(let i=0;i<5;i++)maxLogitDifference=Math.max(maxLogitDifference,Math.abs(t.logits[i]-previous.logits[i]));if(t.chosen_finger!==t.logits.indexOf(Math.max(...t.logits))+1)throw Error('Greedy output not reproduced');}
 if(maxLogitDifference>1e-5)throw Error('Greedy logits not reproduced');
 const candidate=results.find(r=>r.path_name==='pianoplayer_sequence');const conditionalDifferences=[];
 for(const t of candidate.traces){const g=greedy.traces.find(x=>x.note_id===t.note_id);const changed=JSON.stringify(t.input_tokens)!==JSON.stringify(g.input_tokens);if(changed)conditionalDifferences.push({note_id:t.note_id,prefix_fingers:t.prefix_fingers,greedy_prefix_fingers:g.prefix_fingers,max_logit_difference:Math.max(...t.logits.map((v,i)=>Math.abs(v-g.logits[i])))});}
 if(!conditionalDifferences.some(x=>x.max_logit_difference>1e-5))throw Error('No history-dependence evidence');
 write('CONDITIONAL_MODEL_PATH_SCORES.json',{task:'PIANO_SEQUENCE_FINGERING_PLANNING_R1',formula:'sum_i -log softmax(logits_i(path-specific previous assignments, unknown future fingers))[chosen finger]',model:'@lumikey/piano-fingering-model 0.3.0',executionProviders:['cpu'],test_notes:23,context_policy:'Future pitch/timing within four-bar test sequence only; adjacent source context analysed separately',paths:results,validation:{all_future_finger_hints_unknown:true,official_state_update_reused:true,official_greedy_tokens_exact:true,max_previous_greedy_logit_difference:maxLogitDifference,path_dependent_changed_inputs_and_logits:conditionalDifferences},runtime_ms:performance.now()-started});
 console.log(JSON.stringify({scores:results.map(({traces,...r})=>r),max_previous_greedy_logit_difference:maxLogitDifference,history_dependent_notes:conditionalDifferences.map(x=>x.note_id),runtime_ms:performance.now()-started}));
}finally{for(const s of Object.values(models)){await s.endProfiling();await s.release();}}

