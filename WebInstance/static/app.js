"use strict";
const $ = (id) => document.getElementById(id);
const passLabels = {propagation:"Constant propagation",folding:"Constant folding",dce:"Dead-code elimination",unused:"Unused assignments"};
const state = {analysis:null, selected:0, examples:[], busy:false};
const defaultSource = "int main(void)\n{\n    int a = 5;\n    int b = a + 10;\n    if (0) {\n        b = 999;\n    }\n    return b;\n}\n";
const statusLabels = {tested_equal:"Tested equal",counterexample:"Counterexample",inconclusive:"Inconclusive",compile_error:"Compile error",unavailable:"Compiler unavailable",ok:"Complete",unsupported:"Unsupported"};
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}
function notice(message, type="") {
  const node = $("notice");
  node.textContent = message || "";
  node.className = message ? "notice " + type : "notice hidden";
}
function setBusy(busy, action) {
  state.busy = busy;
  $("analyzeButton").disabled = busy;
  $("experimentButton").disabled = busy;
  ["exampleSelect","copyOriginal","compilerSelect","optimization","repetitions","timeout"].forEach(id=>$(id).disabled=busy);
  document.querySelectorAll(".pass-options input").forEach(node=>node.disabled=busy);
  ["originalCode","candidateCode","inputCases"].forEach(id=>$(id).readOnly=busy);
  $("analyzeButton").querySelector("span").textContent = busy && action === "analyze" ? "Tracing…" : "Trace optimizations";
  $("experimentButton").querySelector("span").textContent = busy && action === "experiment" ? "Compiling and comparing…" : "Run behavioral comparison";
  document.body.setAttribute("aria-busy", String(busy));
}
async function api(path, options={}) {
  const response = await fetch(path, {headers:{"Content-Type":"application/json"}, ...options});
  let data;
  try { data = await response.json(); } catch { throw new Error("The local server returned an unreadable response."); }
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}
function selectTab(name) {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    const active = button.dataset.tab === name;
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    $(button.dataset.tab + "Panel").classList.toggle("hidden", !active);
  });
}
function renderDiagnostics(result) {
  const messages = (result.diagnostics || []).map((item) => {
    if (typeof item === "string") return item;
    return (item.line ? "Line " + item.line + ": " : "") + (item.message || String(item));
  });
  if (result.status === "ok") {
    if (messages.length) notice(messages.join("\n"));
    else notice("Trace complete. The candidate is ready to inspect or edit before an experiment.", "success");
  } else {
    notice(messages.join("\n") || "This source is outside the optimizer's supported subset. You can still investigate it with a compiler experiment.", "error");
  }
}
function setMetrics(result) {
  const metrics=result.metrics || {};
  $("originalNodes").textContent=metrics.original_ast_nodes ?? "—";
  $("candidateNodes").textContent=metrics.optimized_ast_nodes ?? "—";
  $("passesRun").textContent=metrics.passes_run ?? (result.trace || []).length;
  $("changedPasses").textContent=metrics.changed_passes ?? (result.trace || []).filter(x=>x.changed).length;
}
function renderTrace() {
  const trace = state.analysis?.trace || [];
  $("traceList").replaceChildren();
  $("traceEmpty").classList.toggle("hidden", trace.length > 0);
  $("traceContent").classList.toggle("hidden", !trace.length);
  trace.forEach((step,index) => {
    const button=element("button",null,"trace-item"+(step.changed?" changed":"")+(index===state.selected?" active":""));
    button.append(element("span",String(index+1).padStart(2,"0"),"trace-index"));
    const label=element("span",passLabels[step.pass_name] || step.pass_name || "Pass");
    label.append(element("small","Iteration "+(step.iteration ?? 1)));
    button.append(label,element("span",null,"trace-dot"));
    button.setAttribute("aria-pressed",String(index===state.selected));
    button.addEventListener("click",()=>{state.selected=index;renderTrace();});
    $("traceList").append(button);
  });
  if (!trace.length) return;
  const step=trace[state.selected] || trace[0];
  $("traceTitle").textContent=passLabels[step.pass_name] || step.pass_name || "Transformation";
  $("traceStatus").textContent=step.changed ? "Changed" : "No change";
  $("traceStatus").className="status-pill"+(step.changed?"":" neutral");
  $("beforeCode").textContent=typeof step.before==="string" ? step.before : JSON.stringify(step.before,null,2);
  $("afterCode").textContent=typeof step.after==="string" ? step.after : JSON.stringify(step.after,null,2);
  $("traceReasons").replaceChildren();
  const changes=step.changes || [];
  if (!changes.length) $("traceReasons").append(element("p",step.reason || "No supported rewrite changed this pass's input."));
  changes.forEach((change)=>{
    const line=change.line ? "Line "+change.line+" · " : "";
    const text=change.reason || change.message || "Transformation recorded.";
    $("traceReasons").append(element("p",line+text));
  });
}
async function analyze() {
  if (state.busy) return;
  setBusy(true,"analyze"); notice("");
  try {
    const passes=Array.from(document.querySelectorAll(".pass-options input:checked")).map(node=>node.value);
    const result=await api("/api/analyze",{method:"POST",body:JSON.stringify({source:$("originalCode").value,passes})});
    state.analysis=result; state.selected=0;
    if (result.status==="ok" && typeof result.optimized_code==="string") $("candidateCode").value=result.optimized_code;
    setMetrics(result); renderTrace(); renderDiagnostics(result); populateFunctions(); selectTab("trace");
  } catch(error) { notice(error.message,"error"); }
  finally { setBusy(false); }
}
function graphFunctions() {
  const graph=state.analysis?.graphs?.[$("cfgVersion").value];
  return graph?.functions || [];
}
function populateFunctions() {
  const functions=graphFunctions();
  $("cfgFunction").replaceChildren(...functions.map((fn,index)=>{
    const option=element("option",fn.name || "Function "+(index+1)); option.value=String(index); return option;
  }));
  drawGraph();
}
function svgElement(name, attributes={}, text) {
  const node=document.createElementNS("http://www.w3.org/2000/svg",name);
  Object.entries(attributes).forEach(([key,value])=>node.setAttribute(key,String(value)));
  if (text !== undefined) node.textContent=String(text);
  return node;
}
function drawGraph() {
  const fn=graphFunctions()[Number($("cfgFunction").value) || 0];
  const container=$("cfgCanvas"); container.replaceChildren();
  if (!fn || !fn.nodes?.length) {
    container.append(element("p",state.analysis ? "No supported function graph is available for this version." : "Trace a supported program to inspect its control flow.","muted"));
    return;
  }
  const nodes=fn.nodes, width=780, gap=90, height=nodes.length*gap+65;
  const svg=svgElement("svg",{viewBox:"0 0 "+width+" "+height,width,height,role:"img","aria-label":"Control flow of "+fn.name});
  const defs=svgElement("defs"), marker=svgElement("marker",{id:"arrowhead",markerWidth:8,markerHeight:8,refX:7,refY:3,orient:"auto",markerUnits:"strokeWidth"});
  marker.append(svgElement("path",{d:"M0,0 L0,6 L8,3 z",fill:"#65829b"})); defs.append(marker); svg.append(defs);
  const positions=new Map(nodes.map((node,index)=>[String(node.id),{x:width/2,y:30+index*gap}]));
  (fn.edges || []).forEach((edge,index)=>{
    const start=positions.get(String(edge.source)), end=positions.get(String(edge.target));
    if (!start || !end) return;
    const adjacent=end.y-start.y===gap;
    let d;
    if (adjacent) d="M"+start.x+","+(start.y+42)+" L"+end.x+","+end.y;
    else {
      const offset=(index%2?1:-1)*(185+Math.min(65,Math.abs(end.y-start.y)*.05));
      const x=start.x+offset;
      d="M"+(start.x+(offset>0?160:-160))+","+(start.y+21)+" C"+x+","+(start.y+21)+" "+x+","+(end.y+21)+" "+(end.x+(offset>0?160:-160))+","+(end.y+21);
    }
    svg.append(svgElement("path",{d,fill:"none",stroke:"#58718b","stroke-width":1.5,"marker-end":"url(#arrowhead)"}));
    if(edge.label) {
      const x=adjacent?start.x+12:start.x+(index%2?1:-1)*205;
      svg.append(svgElement("text",{x,y:(start.y+end.y)/2+15,fill:"#a9c4fa","font-size":10,"font-family":"Consolas,monospace"},edge.label));
    }
  });
  nodes.forEach((node)=>{
    const p=positions.get(String(node.id)),kind=String(node.kind || "");
    const terminal=/entry|exit|return/.test(kind);
    const group=svgElement("g");
    group.append(svgElement("rect",{x:p.x-160,y:p.y,width:320,height:42,rx:terminal?20:7,fill:terminal?"#19352c":"#1c2b3b",stroke:terminal?"#457462":"#3d566e"}));
    const fullLabel=String(node.label ?? node.kind ?? node.id),label=fullLabel.length>45?fullLabel.slice(0,42)+"…":fullLabel;
    group.append(svgElement("text",{x:p.x,y:p.y+26,"text-anchor":"middle",fill:"#d4e3f3","font-family":"Consolas,monospace","font-size":11},label));
    group.append(svgElement("title",{},fullLabel+(node.line?" · line "+node.line:"")));
    svg.append(group);
  });
  container.append(svg);
}
function outcomeClass(status) {
  return status==="counterexample" || status==="compile_error" ? " error" : status==="tested_equal" ? "" : " warning";
}
function firstExecution(runs) {
  if (!Array.isArray(runs) || !runs.length) return "Not executed";
  const run=runs[0];
  if(run.timed_out) return "Execution timed out";
  if(run.error) return String(run.error);
  return "Exit: "+run.returncode+"\nstdout: "+(run.stdout || "(empty)")+"\nstderr: "+(run.stderr || "(empty)");
}
function renderExperiment(result) {
  $("experimentResults").classList.remove("hidden");
  $("resultTitle").textContent=statusLabels[result.status] || result.status || "Experiment complete";
  $("resultStatus").textContent=result.compiler?.name || "Local compiler";
  $("resultStatus").className="status-pill"+outcomeClass(result.status);
  $("resultSummary").textContent=result.summary || (result.status==="tested_equal" ? "Both variants produced matching observable results for the recorded cases." : "Inspect the recorded cases and build output.");
  $("caseResults").replaceChildren();
  (result.cases || []).forEach((entry)=>{
    const row=element("section",null,"case-row"),heading=element("div",null,"case-row-heading");
    heading.append(element("strong",entry.label || "Input case"),element("span",statusLabels[entry.status] || entry.status || (entry.comparison?.equal?"Matched":"Inspect"),"status-pill"+outcomeClass(entry.status)));
    const details=element("div",null,"case-row-details");
    ["original","candidate"].forEach((variant)=>{
      const part=element("div"); part.append(element("h4",variant.toUpperCase()),element("pre",firstExecution(entry[variant]))); details.append(part);
    });
    row.append(heading,details); $("caseResults").append(row);
  });
  $("timingResults").replaceChildren();
  const timings=result.measurements?.by_case || [];
  if(timings.length) {
    const table=element("table",null,"timing-table"),head=element("thead"),headRow=element("tr");
    ["Case","Original median","Candidate median","Original / candidate"].forEach(label=>headRow.append(element("th",label)));
    head.append(headRow);table.append(head);
    const body=element("tbody");
    timings.forEach(entry=>{
      const row=element("tr"),ratio=entry.median_ratio_original_over_candidate;
      [entry.label,formatTime(entry.original?.median_seconds),formatTime(entry.candidate?.median_seconds),Number.isFinite(ratio)?ratio.toFixed(3)+"×":"—"].forEach(text=>row.append(element("td",text)));
      body.append(row);
    });table.append(body);$("timingResults").append(table);
  }
  $("buildResults").replaceChildren();
  Object.entries(result.builds || {}).forEach(([name,build])=>{
    const details=element("details"),summary=element("summary",name[0].toUpperCase()+name.slice(1)+" build · "+(build.success?"compiled":"inspect diagnostics"));
    const compile=build.compile || {};
    const command=Array.isArray(compile.command)?compile.command.join(" "):String(compile.command || "");
    const text=command+"\n\n"+(compile.stdout || "")+(compile.stderr || "")+(compile.timed_out?"\nCompilation timed out":"");
    details.append(summary,element("pre",text || "No compiler output."));$("buildResults").append(details);
  });
  $("artifactLinks").replaceChildren();
  (result.artifact_links || []).forEach(artifact=>{
    const a=element("a",artifact.name);
    if (typeof artifact.url==="string" && artifact.url.startsWith("/api/runs/")) {a.href=artifact.url;a.setAttribute("download","");$("artifactLinks").append(a);}
  });
  $("rawEvidence").textContent=JSON.stringify(result,null,2);
}
function formatTime(seconds) { return Number.isFinite(seconds) ? (seconds*1000).toFixed(3)+" ms" : "—"; }
async function experiment() {
  if (state.busy) return;
  let cases;
  try {cases=JSON.parse($("inputCases").value);}catch{notice("Input cases must be valid JSON.","error");return;}
  if (!Array.isArray(cases)) {notice("Input cases must be a JSON array.","error");return;}
  setBusy(true,"experiment");notice("");selectTab("experiment");
  try {
    const result=await api("/api/experiment",{method:"POST",body:JSON.stringify({
      original:$("originalCode").value,candidate:$("candidateCode").value,
      compiler:$("compilerSelect").value || null,optimization:$("optimization").value,cases,
      repetitions:Number($("repetitions").value),timeout:Number($("timeout").value)
    })});
    renderExperiment(result);
  } catch(error){notice(error.message,"error");}
  finally{setBusy(false);}
}
async function loadToolchains() {
  try {
    const data=await api("/api/toolchains"),available=(data.toolchains || []).filter(tool=>tool.available);
    for (const tool of available) {
      const option=element("option",tool.name+" · "+(tool.version || "").split("\n")[0]);
      option.value=tool.path || tool.name;$("compilerSelect").append(option);
    }
    $("toolchainNote").textContent=available.length ? available.map(tool=>tool.name).join(" / ")+" available · settings apply equally to both editors" : "No compiler detected. Install GCC or Clang and add it to PATH.";
  } catch(error){$("toolchainNote").textContent=error.message;}
}
async function loadExamples() {
  try {
    const data=await api("/api/examples");state.examples=data.examples || [];
    state.examples.forEach(example=>{
      const option=element("option",example.name);option.value=example.id;$("exampleSelect").append(option);
    });
  } catch { /* The editor remains fully usable without examples. */ }
}
$("originalCode").value=defaultSource;
$("analyzeButton").addEventListener("click",analyze);
$("experimentButton").addEventListener("click",experiment);
$("copyOriginal").addEventListener("click",()=>{$("candidateCode").value=$("originalCode").value;notice("Original copied into the candidate editor. Make one change to investigate.");});
$("exampleSelect").addEventListener("change",()=>{
  const example=state.examples.find(item=>item.id===$("exampleSelect").value);
  if(!example)return;
  $("originalCode").value=example.code;$("candidateCode").value=example.candidate_code || "";$("exampleDescription").textContent=example.description || "";
  if(Array.isArray(example.cases)) $("inputCases").value=JSON.stringify(example.cases,null,2);
  state.analysis=null;state.selected=0;setMetrics({});renderTrace();populateFunctions();notice("");$("experimentResults").classList.add("hidden");
  if(example.candidate_code) {
    selectTab("experiment");
    notice("Original and candidate loaded together. Review the intervention and input cases, then run the comparison.");
  }
});
document.querySelectorAll("[data-tab]").forEach(button=>{
  button.addEventListener("click",()=>selectTab(button.dataset.tab));
  button.addEventListener("keydown",(event)=>{
    if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;
    event.preventDefault();
    const buttons=Array.from(document.querySelectorAll("[data-tab]")),index=buttons.indexOf(button);
    const next=event.key==="Home"?0:event.key==="End"?buttons.length-1:(index+(event.key==="ArrowRight"?1:-1)+buttons.length)%buttons.length;
    selectTab(buttons[next].dataset.tab);buttons[next].focus();
  });
});
$("cfgVersion").addEventListener("change",populateFunctions);
$("cfgFunction").addEventListener("change",drawGraph);
for(const id of ["originalCode","candidateCode"]){
  $(id).addEventListener("keydown",(event)=>{
    if(event.key==="Tab" && !event.currentTarget.readOnly){
      event.preventDefault();const node=event.currentTarget,start=node.selectionStart,end=node.selectionEnd;
      node.setRangeText("    ",start,end,"end");
    }
  });
}
$("originalCode").addEventListener("input",()=>{
  $("experimentResults").classList.add("hidden");
  if(state.analysis) {
    state.analysis=null;state.selected=0;setMetrics({});renderTrace();populateFunctions();
    notice("Original source changed. Trace again to refresh the transformation evidence.");
  }
});
$("candidateCode").addEventListener("input",()=>$("experimentResults").classList.add("hidden"));
["inputCases","compilerSelect","optimization","repetitions","timeout"].forEach(id=>{
  $(id).addEventListener("input",()=>$("experimentResults").classList.add("hidden"));
});
void Promise.all([loadToolchains(),loadExamples()]);
