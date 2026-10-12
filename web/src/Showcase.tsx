import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, Download, FileSearch, GitBranch, ShieldCheck, Workflow } from "lucide-react";
import { api } from "./api";
import type { Run } from "./types";
import "./showcase.css";

type Span = { name: string; type: string; id: string; parent: string | null; metrics: Record<string, unknown> };
type Trace = { trace_id: string; span_count: number; spans: Span[] };
type ComparisonRun = { audit_passed: number; audit_total: number; trace_id: string; readback: { spans: Span[] } };
type FinancialValue = number | null | { value: number | null; formula: string };
type Snapshot = {
  kind: string; captured_at: string; disclosure: string; run: Run; live_trace: Trace;
  comparison: { before: ComparisonRun; after: ComparisonRun; experiment: string };
  entire: { checkpoint_id: string; session_count: number; has_review: boolean; sessions: { agent: string; kind: string }[] };
  business: { scenario: string; cases: string[]; rows: { name: string; values: FinancialValue[]; formula: { timeless: string } }[] };
};
const chapters = ["The problem", "Find evidence", "Review repair", "Verify outcome", "Tools and business"];
const getValue = (value: FinancialValue) => typeof value === "object" && value !== null ? value.value : value;
function money(value: FinancialValue) {
  const number = getValue(value);
  return number === null ? "—" : `$${number.toLocaleString("en-US", {maximumFractionDigits:2})}`;
}

export default function Showcase() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const [step, setStep] = useState(0);
  const [partner, setPartner] = useState("neatlogs");
  useEffect(() => { api<Snapshot>("/showcase").then(setSnapshot).catch((e: Error) => setError(e.message)); }, []);
  const run = snapshot?.run;
  const next = () => { setStep(Math.min(step + 1, 4)); window.scrollTo(0, 0); };
  const row = (name: string) => snapshot!.business.rows.find(r => r.name === `PP ${name}`)!;
  return <div className="showcase-shell">
    <header className="showcase-header">
      <a className="showcase-brand" href="/"><Workflow size={24}/> PatchPilot</a>
      <span className="showcase-saved">Saved live investigation</span>
      <a href="/app">Open workspace <ArrowRight size={16}/></a>
    </header>
    <div className="showcase-layout">
      <aside className="showcase-nav">
        <span className="small-label">Product walkthrough</span>
        <h1>From a broken adapter<br/>to a defensible repair.</h1>
        <nav aria-label="Walkthrough chapters">{chapters.map((chapter, i) => <button key={chapter} aria-label={chapter} aria-current={step === i ? "step" : undefined} onClick={() => {setStep(i); window.scrollTo(0, 0);}}><span>0{i+1}</span>{chapter}<ArrowRight size={15}/></button>)}</nav>
        <p>A real search and model run, preserved for inspection. No new provider calls are made in this walkthrough.</p>
        {run && <small>Captured {new Date(run.created_at).toLocaleString("en-IN", {timeZone:"Asia/Kolkata"})} IST<br/>Run {run.id.slice(0,8)} · Synthetic historical fixtures</small>}
      </aside>
      <main className="showcase-main">
        {error ? <div role="alert" className="panel"><h2>Saved investigation unavailable</h2><p>{error}</p><a href="/app">Continue in the workspace</a></div> : !snapshot || !run ? <p role="status">Loading saved investigation…</p> : <>
          <div className="showcase-eyebrow"><span className="small-label">0{step+1} / {chapters[step]}</span><span>Stripe · {run.input.target_version}</span></div>
          {step === 0 && <>
            <h2>One moved field.<br/>A broken integration.</h2>
            <p className="showcase-lead">Your application expects invoice payment IDs. The vendor changes where they live. PatchPilot investigates the change while protecting the output your application relies on.</p>
            <div className="showcase-split"><section className="panel"><h3>The adapter before repair</h3><pre>{run.input.source_code}</pre></section><section className="panel"><h3>The failure we reproduced</h3><strong className="showcase-failure">{run.baseline.filter(r => !r.passed).length}/{run.baseline.length} acceptance cases failed</strong><pre>{run.baseline[0]?.error}</pre><p>Same input fixtures. Same expected outputs throughout the investigation.</p></section></div>
            <section className="panel"><h3>The application’s contract</h3><div className="showcase-split"><div><span className="small-label">Sanitized invoice response</span><pre>{JSON.stringify(run.input.cases[0].input, null, 2)}</pre></div><div><span className="small-label">Expected normalized output</span><pre>{JSON.stringify(run.input.cases[0].expected, null, 2)}</pre></div></div></section>
          </>}
          {step === 1 && <>
            <h2>Find the change.<br/>Keep the evidence.</h2>
            <p className="showcase-lead">SerpApi discovers version-specific vendor documentation. PatchPilot fetches the official page and grounds the proposal in a literal source passage.</p>
            {run.sources.map(source => <section className="panel" key={source.id}><h3><FileSearch size={20}/> {source.title}</h3><span className="small-label">Actual SerpApi query</span><pre>{source.query}</pre><div className="showcase-source-url">{source.url}</div><span className="showcase-provenance">{source.provenance}</span>{run.citations.filter(c => c.source_id === source.id).map((citation,i) => <blockquote key={i}>{citation.quote}</blockquote>)}<details><summary>Inspect captured source text and hash</summary><small>{source.sha256}</small><pre>{source.text}</pre></details></section>)}
            <section className="panel"><h3>The saved investigation plan</h3><ol className="showcase-plan">{run.plan.map(item => <li key={item.area}><b>{item.area}</b><span>{item.task}</span></li>)}</ol></section>
          </>}
          {step === 2 && <>
            <h2>A focused change. An unchanged contract.</h2>
            <p className="showcase-lead">The agent proposes a bounded JSON adapter function. Your original acceptance cases stay intact; imports, shell access and network execution are prohibited.</p>
            <section className="panel"><h3>Proposed change</h3><pre className="showcase-diff">{run.diff}</pre></section>
            <details className="panel"><summary>Inspect complete repaired adapter</summary><pre>{run.proposed_code}</pre></details>
            <section className="panel"><h3>Recorded proposal attempts</h3>{run.attempts.map(attempt => <p key={attempt.number}>Attempt {attempt.number}: {attempt.results.filter(r => r.passed).length}/{attempt.results.length} supplied cases passed. {attempt.error}</p>)}</section>
          </>}
          {step === 3 && <>
            <h2>Proof you can inspect.<br/>Scope you can understand.</h2>
            <p className="showcase-lead">This repair passed the protected contract and the applicable local Stripe audit. The result is a proposal for human review; no production system was changed.</p>
            <div className="showcase-stats"><section><strong>{run.proof?.acceptance_passed}/{run.proof?.total}</strong><span>Protected acceptance cases</span></section><section><strong>{run.proof?.audit.passed}/{run.proof?.audit.total}</strong><span>Scoped independent audit</span></section><section><strong>{run.metrics.elapsed_seconds}s</strong><span>Measured live run duration</span></section></div>
            <section className="panel"><h3><ShieldCheck size={20}/> Acceptance results</h3>{run.verification.map(result => <details key={result.name} className="showcase-case"><summary><CheckCircle2 size={16}/> {result.name}<span>{result.passed ? "Passed" : "Failed"}</span></summary><div className="showcase-split"><pre>Expected{ "\n" }{JSON.stringify(result.expected,null,2)}</pre><pre>Observed{ "\n" }{JSON.stringify(result.actual,null,2)}</pre></div></details>)}</section>
            <section className="panel"><h3>Bound repair proof</h3><p>{run.proof?.verified_scope}</p><dl className="showcase-hashes"><dt>Contract</dt><dd>{run.proof?.contract_hash}</dd><dt>Patch</dt><dd>{run.proof?.patch_hash}</dd></dl><p>Checksums bind the artifacts for comparison; they are not signatures or a universal correctness guarantee.</p></section>
          </>}
          {step === 4 && <>
            <h2>Observe the work.<br/>Build the business.</h2>
            <p className="showcase-lead">Inspect authenticated tool readbacks inside PatchPilot. These are saved integration records, not embedded vendor dashboards or new account connections.</p>
            <div className="tabs" role="tablist" aria-label="Integration evidence">{["neatlogs","Entire","cfo.ai"].map(name => <button role="tab" aria-selected={partner===name} key={name} onClick={() => setPartner(name)}>{name}</button>)}</div>
            <div role="tabpanel">
              {partner === "neatlogs" && <>
                <section className="panel"><h3>neatlogs · Trace the actual live investigation</h3><p>{snapshot.live_trace.span_count} persisted spans · {run.metrics.tokens.toLocaleString()} reported model tokens · content capture disabled</p><small className="showcase-id">Trace {snapshot.live_trace.trace_id}</small><ul className="showcase-spans">{snapshot.live_trace.spans.map(span => <li key={span.id}><span>{span.parent ? "↳ " : ""}{span.name}</span><small>{span.type}</small></li>)}</ul></section>
                <section className="panel"><h3>A separate controlled improvement comparison</h3><div className="showcase-stats"><section><strong>{snapshot.comparison.before.audit_passed}/{snapshot.comparison.before.audit_total}</strong><span>Preserved adapter · audit</span></section><section><strong>{snapshot.comparison.after.audit_passed}/{snapshot.comparison.after.audit_total}</strong><span>Improved replay · audit</span></section></div><p>Both adapters pass 5/5 supplied cases. The improved replay recovers after an incomplete proposal. This comparison uses synthetic fixtures; it does not measure general model accuracy.</p><details><summary>Inspect recorded recovery and trace IDs</summary><small className="showcase-id">Before {snapshot.comparison.before.trace_id}<br/>After {snapshot.comparison.after.trace_id}</small>{snapshot.comparison.after.readback.spans.filter(s => ["tools.propose","verification.acceptance","verification.audit"].includes(s.name)).map(s => <pre key={s.id}>{s.name}{"\n"}{JSON.stringify(s.metrics,null,2)}</pre>)}</details></section>
              </>}
              {partner === "Entire" && <section className="panel"><h3><GitBranch size={20}/> Entire · Retain the decision behind a change</h3><p>A real read-only Codex design review was attached to its development commit. It identified interpreter-version reproducibility as a risk; setup and Docker select Python 3.12.</p><div className="showcase-checkpoint"><span className="small-label">Checkpoint</span><strong>{snapshot.entire.checkpoint_id}</strong><span>{snapshot.entire.session_count} recorded session · {snapshot.entire.sessions[0]?.agent} · {snapshot.entire.sessions[0]?.kind}</span><span>Associated commit: 791e5a4</span></div><p>This review was attached retrospectively after hook setup. It does not establish continuous capture of earlier development.</p></section>}
              {partner === "cfo.ai" && <>
                <section className="panel"><h3>cfo.ai · Test a business hypothesis</h3><p>Saved scenario: {snapshot.business.scenario}. Every value below is an illustrative USD planning assumption. Paid subscriptions and billing are not implemented.</p><div className="showcase-table-wrap"><table><thead><tr><th>Monthly model</th>{snapshot.business.cases.map(c => <th key={c}>{c}</th>)}</tr></thead><tbody>{["Paying customers","Monthly price USD","Revenue USD","Direct costs USD","Gross margin","Static runway months"].map(name => <tr key={name}><th>{name}</th>{row(name).values.map((value,i) => <td key={i}>{name.includes("USD") ? money(value) : name === "Gross margin" ? `${(Number(getValue(value))*100).toFixed(1)}%` : getValue(value) === null ? "No positive burn" : Number(getValue(value)).toFixed(name.includes("runway") ? 2 : 0)}</td>)}</tr>)}</tbody></table></div><details><summary>Inspect all model inputs and formulas</summary>{snapshot.business.rows.map(r => <div className="showcase-formula" key={r.name}><b>{r.name.replace("PP ","")}</b><code>{r.formula.timeless}</code><span>{r.values.map(v => getValue(v) ?? "No positive burn").join(" · ")}</span></div>)}</details></section>
                <section className="panel"><h3>The decision: validate review effort before charging</h3><p>In the base case, human review costs $480 versus $64 in provider and compute assumptions. The conservative case has only 1.6% gross margin. The next milestone is a reviewed pilot measuring useful repairs, reviewer time and repeat use.</p></section>
              </>}
            </div>
          </>}
          <footer className="showcase-actions"><a className="button secondary" href="/api/showcase/report"><Download size={16}/> Download repair report</a>{step < 4 ? <button className="button primary" onClick={next}>Continue to {chapters[step+1].toLowerCase()} <ArrowRight size={16}/></button> : <a className="button primary" href="/app">Try your own investigation <ArrowRight size={16}/></a>}</footer>
        </>}
      </main>
    </div>
  </div>;
}
