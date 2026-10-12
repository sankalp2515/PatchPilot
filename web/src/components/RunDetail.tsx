import { useState } from "react";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Code2,
  Download,
  ExternalLink,
  FileSearch,
  FlaskConical,
  GitBranch,
  Layers3,
  LoaderCircle,
  RotateCcw,
  ShieldCheck,
  Square,
  XCircle,
} from "lucide-react";
import { downloadText } from "../api";
import { terminal, type Run, type Result } from "../types";

export const label = (status: string) =>
  ({
    verified: "Verified in tested scope",
    needs_human: "Needs investigation",
    no_change: "No repair needed",
    unverified: "Not verified",
    failed: "Run stopped",
    cancelled: "Cancelled",
    interrupted: "Ready to resume",
  })[status] || status.replaceAll("_", " ");
const focus = [
  ["Planning", GitBranch],
  ["Tool use", Code2],
  ["State", Layers3],
  ["Context", FileSearch],
  ["Execution", Activity],
  ["Recovery", RotateCcw],
  ["Verification", ShieldCheck],
  ["Iteration", GitBranch],
] as const;

function CaseResults({ results }: { results: Result[] }) {
  if (!results.length)
    return (
      <div className="empty-panel">Test results appear after execution.</div>
    );
  return (
    <div className="case-results">
      {results.map((result) => (
        <details
          key={result.name}
          className={result.passed ? "case-pass" : "case-fail"}
        >
          <summary>
            {result.passed ? <CheckCircle2 size={17} /> : <XCircle size={17} />}
            <span>{result.name}</span>
            <b>{result.passed ? "Passed" : "Failed"}</b>
            <ChevronRight size={15} />
          </summary>
          <div className="case-body">
            {result.error && <p className="case-error">{result.error}</p>}
            <div>
              <section>
                <span>Expected</span>
                <pre>{JSON.stringify(result.expected, null, 2)}</pre>
              </section>
              <section>
                <span>Observed</span>
                <pre>{JSON.stringify(result.actual, null, 2)}</pre>
              </section>
            </div>
          </div>
        </details>
      ))}
    </div>
  );
}

export default function RunDetail({
  run,
  onBack,
  onRerun,
  onCancel,
  onResume,
}: {
  run: Run;
  onBack: () => void;
  onRerun: () => void;
  onCancel: () => void;
  onResume: () => void;
}) {
  const [tab, setTab] = useState("overview");
  const active = !terminal.has(run.status);
  const passed = run.verification.filter((r) => r.passed).length;
  const reached = (area: string) =>
    ({
      Planning: run.plan.length > 0,
      "Tool use": run.events.some((e) =>
        ["search", "model", "tool"].includes(e.kind),
      ),
      State: run.events.length > 0,
      Context: run.sources.length > 0,
      Execution: run.attempts.length > 0,
      Recovery: run.events.some((e) => e.kind === "recovery"),
      Verification: run.baseline.length > 0,
      Iteration: run.attempts.length > 1,
    })[area] || false;
  const tabs = [
    ["overview", "Overview"],
    ["evidence", `Evidence (${run.sources.length})`],
    ["repair", "Proposed repair"],
    ["tests", "Acceptance tests"],
    ["activity", "Activity"],
  ];
  return (
    <>
      <div className="breadcrumb">
        <button onClick={onBack}>
          <ArrowLeft size={14} />
          Investigations
        </button>
        <ChevronRight size={14} />
        <span>{run.id.slice(0, 8)}</span>
      </div>
      <header className="run-header">
        <div>
          <div className="run-meta">
            <span className="vendor-symbol">
              {run.input.vendor[0].toUpperCase()}
            </span>
            {run.input.vendor}
            <span className="meta-dot" />
            {run.input.target_version}
            <span className={"mode-tag " + run.input.mode}>
              {run.input.mode === "live" ? "Live research" : "Recorded replay"}
            </span>
          </div>
          <h1>{run.input.title}</h1>
          <p>{run.input.symptom}</p>
        </div>
        <div className="run-actions">
          {active ? (
            <button className="button secondary" onClick={onCancel}>
              <Square size={14} />
              Cancel run
            </button>
          ) : run.status === "interrupted" ? (
            <button className="button primary" onClick={onResume}>
              <RotateCcw size={16} />
              Resume
            </button>
          ) : (
            <button className="button secondary" onClick={onRerun}>
              <RotateCcw size={16} />
              Run again
            </button>
          )}
          <a
            className="button secondary"
            href={`/api/runs/${run.id}/export?format=markdown`}
          >
            <Download size={16} />
            Report
          </a>
        </div>
      </header>
      <div
        className={
          "outcome " +
          (run.status === "verified"
            ? "success"
            : active
              ? "running"
              : "neutral")
        }
        role="status"
        aria-live="polite"
      >
        <div className="outcome-icon">
          {active ? (
            <LoaderCircle className="spin" size={23} />
          ) : run.status === "verified" ? (
            <ShieldCheck size={24} />
          ) : (
            <FileSearch size={24} />
          )}
        </div>
        <div>
          <strong>
            {active ? `Investigating · ${label(run.phase)}` : label(run.status)}
          </strong>
          <p>
            {active
              ? run.events.at(-1)?.title || "Preparing bounded investigation"
              : run.diagnosis || "Saved results remain available."}
          </p>
        </div>
        {run.status === "verified" && (
          <span className="outcome-score">
            {passed}/{run.verification.length}
            <small>cases passed</small>
          </span>
        )}
      </div>
      <section className="proof-record" aria-label="Bound repair proof">
        <h2>
          <ShieldCheck size={19} />
          Repair proof
        </h2>
        {run.proof ? (
          <>
            <div className="proof-counts">
              <strong className="proof-acceptance">
                {run.proof.acceptance_passed}/{run.proof.total} protected
                acceptance cases
              </strong>
              <strong className="proof-audit">
                {run.proof.audit.applicable
                  ? `${run.proof.audit.passed}/${run.proof.audit.total} independent audit cases`
                  : "Independent audit not applicable"}
              </strong>
            </div>
            <dl>
              <dt>Contract hash</dt>
              <dd>{run.proof.contract_hash}</dd>
              <dt>Evidence hashes</dt>
              <dd>
                {run.proof.evidence_hashes
                  .map((item) => `${item.source_id}: ${item.sha256}`)
                  .join(" · ") || "No captured evidence"}
              </dd>
              <dt>Patch hash</dt>
              <dd>{run.proof.patch_hash || "No proposed patch"}</dd>
            </dl>
            <p>{run.proof.verified_scope}</p>
          </>
        ) : (
          <p>
            {active
              ? "Proof appears when verification finishes."
              : "This historical run has no bound repair proof."}
          </p>
        )}
      </section>
      <div className="focus-strip" aria-label="Agent focus areas">
        {focus.map(([name, Icon]) => (
          <div
            key={name}
            aria-label={`${name}: ${reached(name) ? "observed in this run" : "not reached"}`}
            title={run.plan.find((p) => p.area === name)?.task || name}
          >
            <Icon size={15} />
            <span>{name}</span>
            {reached(name) && <Check size={11} />}
          </div>
        ))}
      </div>
      <div className="tabs" role="tablist">
        {tabs.map(([key, text]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={tab === key ? "selected" : ""}
            onClick={() => setTab(key)}
          >
            {text}
          </button>
        ))}
      </div>
      <div className="run-layout">
        <div className="run-content" role="tabpanel">
          {tab === "overview" && (
            <>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Investigation trail</h2>
                  <span>{run.events.length} recorded actions</span>
                </div>
                <div className="timeline">
                  {run.events.length ? (
                    run.events.map((event, index) => (
                      <div className="timeline-step" key={index}>
                        <div className={"timeline-marker " + event.kind}>
                          {event.kind === "verification" ? (
                            <FlaskConical size={15} />
                          ) : event.kind === "search" ? (
                            <SearchIcon />
                          ) : event.kind === "recovery" ? (
                            <RotateCcw size={15} />
                          ) : (
                            <Check size={14} />
                          )}
                        </div>
                        <div>
                          <strong>{event.title}</strong>
                          <p>{event.detail}</p>
                          <time>
                            {new Date(event.at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                              second: "2-digit",
                            })}
                          </time>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="empty-panel">Preparing the first task…</div>
                  )}
                </div>
              </section>
              {run.limitations.length > 0 && (
                <section className="scope-note">
                  <ShieldCheck size={20} />
                  <div>
                    <h3>What this result establishes</h3>
                    {run.limitations.map((item) => (
                      <p key={item}>{item}</p>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
          {tab === "evidence" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>Evidence behind the repair</h2>
                <span>Fetched passages, never snippets</span>
              </div>
              {run.sources.length ? (
                run.sources.map((source) => (
                  <article className="source-record" key={source.id}>
                    <div className="source-top">
                      <span className="source-id">{source.id}</span>
                      <span className="source-origin">
                        {source.provenance === "recorded_replay"
                          ? "Recorded historical excerpt"
                          : "Discovered with SerpApi · fetched official source"}
                      </span>
                    </div>
                    <a href={source.url} target="_blank" rel="noreferrer">
                      <h3>
                        {source.title}
                        <ExternalLink size={14} />
                      </h3>
                    </a>
                    <div className="source-url">{source.url}</div>
                    <div className="source-version">
                      Target version: {source.version}
                    </div>
                    {run.citations
                      .filter((c) => c.source_id === source.id)
                      .map((citation, i) => (
                        <blockquote key={i}>{citation.quote}</blockquote>
                      ))}
                    <details>
                      <summary>Read captured source context</summary>
                      <pre className="source-text">{source.text}</pre>
                    </details>
                    <p className="hash">SHA256 {source.sha256}</p>
                  </article>
                ))
              ) : (
                <div className="empty-panel">
                  <FileSearch size={27} />
                  <h3>No accepted evidence yet</h3>
                  <p>
                    Only acquired official documentation applicable to the
                    target version can support a live repair.
                  </p>
                </div>
              )}
            </section>
          )}
          {tab === "repair" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>Minimal proposed change</h2>
                {run.proposed_code && (
                  <button
                    className="button small secondary"
                    onClick={() =>
                      downloadText(run.proposed_code, "adapter.proposed.py")
                    }
                  >
                    <Download size={14} />
                    Download adapter
                  </button>
                )}
              </div>
              {run.diff ? (
                <pre className="diff">
                  {run.diff.split("\n").map((line, i) => (
                    <div
                      key={i}
                      className={
                        line.startsWith("+") && !line.startsWith("+++")
                          ? "added"
                          : line.startsWith("-") && !line.startsWith("---")
                            ? "removed"
                            : ""
                      }
                    >
                      <span className="line-number">{i + 1}</span>
                      {line || " "}
                    </div>
                  ))}
                </pre>
              ) : (
                <div className="empty-panel">
                  <Code2 size={27} />
                  <h3>No patch proposed</h3>
                  <p>
                    A patch appears after sufficient evidence and model
                    generation. Refused investigations leave code untouched.
                  </p>
                </div>
              )}
              {run.attempts.length > 0 && (
                <div className="attempt-ledger">
                  <h3>Repair attempts</h3>
                  {run.attempts.map((attempt) => (
                    <div key={attempt.number}>
                      <span>Attempt {attempt.number}</span>
                      <span>
                        {attempt.error ||
                          `${attempt.results.filter((r) => r.passed).length}/${attempt.results.length} cases passed`}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}
          {tab === "tests" && (
            <>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Before repair</h2>
                  <span>
                    {run.baseline.filter((r) => r.passed).length}/
                    {run.baseline.length} passed
                  </span>
                </div>
                <CaseResults results={run.baseline} />
              </section>
              <section className="panel">
                <div className="panel-heading">
                  <h2>After proposed repair</h2>
                  <span>
                    {passed}/{run.verification.length} passed
                  </span>
                </div>
                <CaseResults results={run.verification} />
              </section>
              <p className="muted">
                The same acceptance cases are used before and after. The agent
                cannot edit their expected outputs.
              </p>
            </>
          )}
          {tab === "activity" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>Run trace</h2>
                <a
                  className="button small secondary"
                  href={`/api/runs/${run.id}/export`}
                >
                  <Download size={14} />
                  Export JSON
                </a>
              </div>
              <div className="activity-list">
                {run.events.map((event, i) => (
                  <div key={i}>
                    <span className="activity-kind">{event.kind}</span>
                    <div>
                      <strong>{event.title}</strong>
                      <p>{event.detail}</p>
                    </div>
                    <time>{new Date(event.at).toLocaleTimeString()}</time>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
        <aside className="inspector">
          <section className="panel">
            <h3>Run context</h3>
            <dl>
              <dt>Integration</dt>
              <dd>{run.input.vendor}</dd>
              <dt>Target version</dt>
              <dd className="mono">{run.input.target_version}</dd>
              <dt>Entrypoint</dt>
              <dd className="mono">{run.input.entrypoint}</dd>
              <dt>Execution</dt>
              <dd>
                {run.input.mode === "live"
                  ? "Live search + model"
                  : "Recorded demonstration"}
              </dd>
              <dt>Telemetry</dt>
              <dd>
                {run.telemetry?.status || "not recorded"}
                {run.telemetry?.trace_id ? ` · ${run.telemetry.trace_id}` : ""}
              </dd>
              <dt>Repair budget</dt>
              <dd>
                {run.attempts.length} / {run.input.max_attempts} attempts
              </dd>
            </dl>
          </section>
          <section className="panel">
            <h3>Measured work</h3>
            <div className="metric">
              <Clock3 size={16} />
              <span>Elapsed</span>
              <strong>{run.metrics.elapsed_seconds.toFixed(1)}s</strong>
            </div>
            <div className="metric">
              <FileSearch size={16} />
              <span>Search queries</span>
              <strong>{run.metrics.search_calls}</strong>
            </div>
            <div className="metric">
              <Layers3 size={16} />
              <span>Model calls</span>
              <strong>{run.metrics.model_calls}</strong>
            </div>
            <div className="metric">
              <Code2 size={16} />
              <span>Total tokens</span>
              <strong>{run.metrics.tokens.toLocaleString()}</strong>
            </div>
          </section>
          <div className="inspector-note">
            <ShieldCheck size={20} />
            <h3>Review before applying</h3>
            <p>
              PatchPilot proposes a repair. Your repository and production
              systems remain under your control.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}
function SearchIcon() {
  return <FileSearch size={15} />;
}
