import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  Code2,
  FileSearch,
  FlaskConical,
  GitBranch,
  Layers3,
  LoaderCircle,
  Plus,
  Radio,
  Search,
  Settings2,
  ShieldCheck,
  Terminal,
  Workflow,
  X,
} from "lucide-react";
import Landing from "./Landing";
import { api, post } from "./api";
import {
  terminal,
  type Config,
  type Incident,
  type Run,
  type Summary,
} from "./types";
import IncidentEditor from "./components/IncidentEditor";
import RunDetail, { label } from "./components/RunDetail";

function IntegrationPage({ config }: { config: Config | null }) {
  const partners = [
    [
      "neatlogs",
      "Observe and improve",
      "Connect the SDK to model, search and verification spans. Capture a failed run, improve the agent, and compare real traces.",
      "https://github.com/sankalp2515/PatchPilot/blob/main/docs/evidence/neatlogs-improvement.json",
    ],
    [
      "Entire",
      "Preserve development context",
      "A real design-review session is retained in an Entire checkpoint. The session was attached retrospectively after hook setup.",
      "https://github.com/sankalp2515/PatchPilot/blob/main/docs/evidence/entire-checkpoint.json",
    ],
    [
      "cfo.ai",
      "Plan a viable business",
      "Three editable launch scenarios cover pricing, cost, revenue and runway. Customer and financial inputs are clearly labelled hypotheses.",
      "https://github.com/sankalp2515/PatchPilot/blob/main/docs/business-model.md",
    ],
  ];
  return (
    <>
      <header className="page-heading">
        <div>
          <span className="small-label">Integrations</span>
          <h1>Connected tools and validation</h1>
          <p>
            Release validation records describe how these tools were used. Your
            current provider configuration is shown below; a new installation
            needs its own accounts for live use.
          </p>
        </div>
      </header>
      <section className="panel provider-panel">
        <div>
          <Search size={22} />
          <h2>Live research and repair</h2>
        </div>
        <dl>
          <dt>SerpApi discovery</dt>
          <dd>
            {config?.search_ready ? "Server key configured" : "Key needed"}
          </dd>
          <dt>AI provider</dt>
          <dd>
            {config?.model_ready
              ? `${config.provider} · ${config.model}`
              : "Key needed"}
          </dd>
        </dl>
        <p>
          Credentials stay on the server. A configured key does not guarantee
          account access or quota; live runs report actual provider outcomes.
        </p>
      </section>
      <div className="partner-grid">
        {partners.map(([name, title, detail, url]) => (
          <section className="panel partner" key={name}>
            <div className="partner-top">
              <span className="partner-name">{name}</span>
              <span className="pending-tag">
                Project evidence:{" "}
                {config?.partners?.[
                  name === "cfo.ai" ? "cfo_ai" : name.toLowerCase()
                ] || "not configured"}
              </span>
            </div>
            <h2>{title}</h2>
            <p>{detail}</p>
            <a href={url} target="_blank" rel="noreferrer">
              Inspect project evidence
              <ArrowRight size={15} />
            </a>
          </section>
        ))}
      </div>
      <section className="setup-note">
        <ShieldCheck size={22} />
        <div>
          <h3>Configuration and evidence are different</h3>
          <p>
            Configured keys enable attempts. Verified traces, repository
            checkpoints, and saved financial scenarios establish the individual
            tool outcomes. Entire and cfo.ai support development and business
            planning; they do not verify an adapter.
          </p>
        </div>
      </section>{" "}
    </>
  );
}

function Workspace() {
  const [retryGeneration, setRetryGeneration] = useState(0);
  const [page, setPage] = useState<"runs" | "examples" | "integrations">(
      "runs",
    ),
    [runs, setRuns] = useState<Summary[]>([]),
    [config, setConfig] = useState<Config | null>(null),
    [examples, setExamples] = useState<Incident[]>([]),
    [selected, setSelected] = useState<string | null>(null),
    [run, setRun] = useState<Run | null>(null),
    [draft, setDraft] = useState<Incident | null>(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true),
    [filter, setFilter] = useState("");
  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    setRetryGeneration((value) => value + 1);
    try {
      const [c, e, r] = await Promise.all([
        api<Config>("/config"),
        api<Incident[]>("/examples"),
        api<Summary[]>("/runs"),
      ]);
      setConfig(c);
      setExamples(e);
      setRuns(r);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void load();
  }, [load]);
  useEffect(() => {
    if (!selected) {
      setRun(null);
      return;
    }
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const data = await api<Run>(`/runs/${selected}`);
        if (disposed) return;
        setRun(data);
        if (!terminal.has(data.status)) timer = setTimeout(poll, 1000);
        else {
          const list = await api<Summary[]>("/runs");
          if (!disposed) setRuns(list);
        }
      } catch (err) {
        if (!disposed) setError((err as Error).message);
      }
    }
    void poll();
    return () => {
      disposed = true;
      clearTimeout(timer);
    };
  }, [selected, retryGeneration]);
  const open = (incident?: Incident) => {
    const value = incident || examples[0];
    if (value)
      setDraft({ ...value, mode: config?.live_ready ? value.mode : "replay" });
  };
  async function submit(incident: Incident) {
    const result = await post<Run>("/runs", incident);
    setDraft(null);
    setRun(result);
    setSelected(result.id);
    setPage("runs");
    setRuns(await api<Summary[]>("/runs"));
  }
  async function mutate(action: "cancel" | "resume") {
    if (!run) return;
    try {
      const result = await post<Run>(`/runs/${run.id}/${action}`);
      setRun(result);
      if (action === "resume") {
        const id = selected;
        setSelected(null);
        setTimeout(() => setSelected(id), 0);
      }
      setRuns(await api<Summary[]>("/runs"));
    } catch (err) {
      setError((err as Error).message);
    }
  }
  function navigate(next: typeof page) {
    setPage(next);
    setSelected(null);
    setFilter("");
  }
  const visible = runs.filter((item) =>
    (item.title + " " + item.vendor + " " + item.status)
      .toLowerCase()
      .includes(filter.toLowerCase()),
  );
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button
          className="brand"
          onClick={() => navigate("runs")}
          aria-label="PatchPilot home"
        >
          <span className="brand-mark">
            <Workflow size={22} />
          </span>
          <span>
            PatchPilot<small>Integration repair</small>
          </span>
        </button>
        <nav aria-label="Main navigation">
          <button
            className={page === "runs" ? "active" : ""}
            onClick={() => navigate("runs")}
          >
            <Layers3 size={18} />
            Investigations
            {runs.length > 0 && (
              <span className="nav-count">{runs.length}</span>
            )}
          </button>
          <button
            className={page === "examples" ? "active" : ""}
            onClick={() => navigate("examples")}
          >
            <FlaskConical size={18} />
            Examples
          </button>
          <button
            className={page === "integrations" ? "active" : ""}
            onClick={() => navigate("integrations")}
          >
            <Settings2 size={18} />
            Integrations
          </button>
        </nav>
        <div className="sidebar-flow">
          <span>Your investigation path</span>
          <div>
            <FileSearch size={15} />
            Find the evidence
          </div>
          <div>
            <Code2 size={15} />
            Propose a repair
          </div>
          <div>
            <ShieldCheck size={15} />
            Prove the outcome
          </div>
        </div>
        <div className="sidebar-bottom">
          <div className="local-indicator">
            <span />
            Local workspace
          </div>
          <p>
            Code changes are proposals.
            <br />
            You decide what ships.
          </p>
          <button onClick={() => navigate("integrations")}>
            <Radio size={15} />
            {config?.live_ready
              ? "Live keys configured"
              : "Replay mode available"}
            <ChevronRight size={14} />
          </button>
        </div>
      </aside>
      <main className="main-shell">
        <div className="topbar">
          <div>
            <span className="workspace-icon">
              <Terminal size={15} />
            </span>
            Engineering workspace
            <span className="topbar-separator" />
            Local
          </div>
          <button
            className="button primary small"
            onClick={() => open()}
            disabled={!examples.length}
          >
            <Plus size={16} />
            New investigation
          </button>
        </div>
        <div className="main-body">
          {error && (
            <div className="error-box" role="alert">
              <span>{error}</span>
              <button
                className="button small secondary"
                onClick={() => void load()}
              >
                Retry connection
              </button>
              <button
                className="icon-button"
                aria-label="Dismiss error"
                onClick={() => setError("")}
              >
                <X size={16} />
              </button>
            </div>
          )}
          {page === "integrations" ? (
            <IntegrationPage config={config} />
          ) : selected && run ? (
            <RunDetail
              key={run.id}
              run={run}
              onBack={() => setSelected(null)}
              onRerun={() => open(run.input)}
              onCancel={() => void mutate("cancel")}
              onResume={() => void mutate("resume")}
            />
          ) : selected ? (
            <div className="loading-state">
              <LoaderCircle className="spin" />
              Loading investigation…
            </div>
          ) : (
            <>
              <header className="page-heading">
                <div>
                  <span className="small-label">
                    {page === "examples"
                      ? "Try the workflow"
                      : "Your repair workbench"}
                  </span>
                  <h1>
                    {page === "examples"
                      ? "Start with a reproducible failure"
                      : "Repair integrations with evidence"}
                  </h1>
                  <p>
                    {page === "examples"
                      ? "Explore a documented migration, failed repairs, and the right time to stop."
                      : "From a broken adapter to a minimal, test-verified proposal. Every decision leaves a trail."}
                  </p>
                </div>
              </header>
              <section className="workflow-banner">
                <div className="workflow-copy">
                  <span className="workflow-symbol">
                    <GitBranch size={28} />
                  </span>
                  <div>
                    <h2>One failure. A complete investigation.</h2>
                    <p>
                      Reproduce, research, repair, verify. Keep the evidence
                      beside the code.
                    </p>
                  </div>
                </div>
                <div className="workflow-steps">
                  <span>
                    <FileSearch size={18} />
                    Evidence
                  </span>
                  <ArrowRight size={16} />
                  <span>
                    <Code2 size={18} />
                    Repair
                  </span>
                  <ArrowRight size={16} />
                  <span>
                    <ShieldCheck size={18} />
                    Verification
                  </span>
                </div>
              </section>
              <div className="section-header">
                <h2>
                  {page === "examples"
                    ? "Sample investigations"
                    : "Choose a starting point"}
                </h2>
                <span>Historical migration · sanitized fixtures</span>
              </div>
              <div className="example-grid">
                {examples
                  .slice(0, page === "examples" ? 4 : 2)
                  .map((example, index) => (
                    <button
                      className="example-card"
                      key={example.title}
                      onClick={() => open(example)}
                    >
                      <div className="example-card-top">
                        <span
                          className={
                            "example-icon " + (index === 0 ? "stripe-icon" : "")
                          }
                        >
                          {index === 0 ? (
                            <span>S</span>
                          ) : index === 1 ? (
                            <GitBranch size={22} />
                          ) : index === 2 ? (
                            <FileSearch size={22} />
                          ) : (
                            <ShieldCheck size={22} />
                          )}
                        </span>
                        <span className="example-mode">
                          {example.mode === "live"
                            ? "Live search + AI"
                            : "Recorded replay"}
                        </span>
                      </div>
                      <h3>{example.title}</h3>
                      <p>
                        {index === 0
                          ? "Repair a removed invoice payment pointer using version-specific vendor documentation."
                          : index === 1
                            ? "An incomplete patch fails a protected edge case. Inspect how the next attempt adapts."
                            : index === 2
                              ? "No fetched evidence supports a repair. The agent explains the gap and stops."
                              : "Authentication errors need credential investigation, not a schema patch."}
                      </p>
                      <div className="example-footer">
                        <span>{example.cases.length} acceptance cases</span>
                        <ArrowRight size={17} />
                      </div>
                    </button>
                  ))}
              </div>
              {page === "examples" && (
                <div className="custom-example">
                  <div>
                    <h3>Bring your own integration</h3>
                    <p>
                      Paste a sanitized real response, a failing adapter, and
                      the output you expect.
                    </p>
                  </div>
                  <button
                    className="button secondary"
                    onClick={() =>
                      open({
                        ...examples[0],
                        title: "Custom integration failure",
                        source_code:
                          "def normalize_response(response):\n    return response\n",
                        entrypoint: "normalize_response",
                        symptom: "Describe the observed failure",
                        search_hint: "",
                        cases: [
                          { name: "Real response", input: {}, expected: {} },
                        ],
                      })
                    }
                  >
                    <Plus size={16} />
                    Custom incident
                  </button>
                </div>
              )}
              {page === "runs" && (
                <>
                  <div className="section-header history-heading">
                    <h2>Investigations</h2>
                    <label className="search-field">
                      <Search size={15} />
                      <input
                        aria-label="Filter investigations"
                        placeholder="Filter investigations"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                      />
                    </label>
                  </div>
                  <section className="panel run-library">
                    {loading ? (
                      <div className="loading-state">
                        <LoaderCircle className="spin" size={18} />
                        Connecting to the local agent…
                      </div>
                    ) : visible.length ? (
                      <>
                        <div className="run-table-head">
                          <span>Incident</span>
                          <span>Outcome</span>
                          <span>Mode</span>
                          <span>Created</span>
                          <span />
                        </div>
                        {visible.map((item) => (
                          <button
                            className="run-row"
                            key={item.id}
                            onClick={() => setSelected(item.id)}
                          >
                            <div className="run-row-title">
                              <span className="run-row-icon">
                                <Activity size={18} />
                              </span>
                              <div>
                                <strong>{item.title}</strong>
                                <small>
                                  {item.vendor} · {item.id.slice(0, 8)}
                                </small>
                              </div>
                            </div>
                            <span className={"status-badge " + item.status}>
                              {!terminal.has(item.status) && (
                                <LoaderCircle className="spin" size={12} />
                              )}{" "}
                              {label(item.status)}
                            </span>
                            <span className="table-mode">
                              {item.mode === "live" ? "Live" : "Replay"}
                            </span>
                            <time>
                              {new Date(item.created_at).toLocaleDateString(
                                [],
                                { month: "short", day: "numeric" },
                              )}
                            </time>
                            <ChevronRight size={16} />
                          </button>
                        ))}
                      </>
                    ) : (
                      <div className="library-empty">
                        <span>
                          <Workflow size={29} />
                        </span>
                        <h3>
                          {filter
                            ? "No matching investigations"
                            : "Your first repair starts here"}
                        </h3>
                        <p>
                          {filter
                            ? "Try another title or vendor."
                            : "Open a sample or bring a failing adapter. We’ll keep the sources, proposed code, and results together."}
                        </p>
                        {!filter && (
                          <button
                            className="button secondary"
                            onClick={() => open()}
                          >
                            <Plus size={16} />
                            Create investigation
                          </button>
                        )}
                      </div>
                    )}
                  </section>
                </>
              )}
              <div className="capability-footer">
                <span>
                  <CheckCircle2 size={15} />
                  Protected acceptance cases
                </span>
                <span>
                  <Layers3 size={15} />
                  Durable run history
                </span>
                <span>
                  <ShieldCheck size={15} />
                  Evidence before a verdict
                </span>
              </div>
            </>
          )}
        </div>
      </main>
      {draft && (
        <IncidentEditor
          initial={draft}
          ready={!!config?.live_ready}
          onClose={() => setDraft(null)}
          onSubmit={submit}
        />
      )}
    </div>
  );
}

export default function App() {
  return window.location.pathname === "/app" ||
    window.location.pathname.startsWith("/app/") ? (
    <Workspace />
  ) : (
    <Landing />
  );
}
