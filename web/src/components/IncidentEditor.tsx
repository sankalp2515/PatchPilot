import { useEffect, useRef, useState } from "react";
import { ArrowRight, X, Code2, FlaskConical, Search } from "lucide-react";
import type { Incident } from "../types";

export default function IncidentEditor({
  initial,
  ready,
  onClose,
  onSubmit,
}: {
  initial: Incident;
  ready: boolean;
  onClose: () => void;
  onSubmit: (incident: Incident) => Promise<void>;
}) {
  const [value, setValue] = useState(initial),
    [cases, setCases] = useState(JSON.stringify(initial.cases, null, 2)),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const panel = dialog.current;
    panel?.querySelector<HTMLInputElement>("input")?.focus();
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function keydown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
      if (event.key === "Tab" && panel) {
        const controls = Array.from(
          panel.querySelectorAll<HTMLElement>(
            "button:not(:disabled),input,select,textarea,a[href]",
          ),
        );
        const first = controls[0],
          last = controls.at(-1);
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    }
    document.addEventListener("keydown", keydown);
    return () => {
      document.removeEventListener("keydown", keydown);
      document.body.style.overflow = before;
      previous?.focus();
    };
  }, [onClose]);
  const set = <K extends keyof Incident>(key: K, next: Incident[K]) =>
    setValue({ ...value, [key]: next });
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const parsed: unknown = JSON.parse(cases);
      if (!Array.isArray(parsed) || !parsed.length)
        throw new Error("Acceptance cases must be a nonempty JSON array.");
      await onSubmit({ ...value, cases: parsed });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Check your input.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="modal-backdrop">
      <section
        ref={dialog}
        className="editor-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="editor-title"
      >
        <header className="modal-header">
          <div>
            <span className="small-label">New investigation</span>
            <h2 id="editor-title">Define the failure. Protect the outcome.</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close incident editor"
          >
            <X size={20} />
          </button>
        </header>
        <form onSubmit={submit}>
          <div className="editor-fields">
            <label>
              Incident title
              <input
                aria-label="Incident title"
                required
                minLength={3}
                maxLength={160}
                value={value.title}
                onChange={(e) => set("title", e.target.value)}
              />
            </label>
            <div className="field-row">
              <label>
                Vendor
                <select
                  value={value.vendor}
                  onChange={(e) =>
                    set("vendor", e.target.value as Incident["vendor"])
                  }
                >
                  <option value="stripe">Stripe</option>
                  <option value="github">GitHub</option>
                  <option value="slack">Slack</option>
                  <option value="shopify">Shopify</option>
                </select>
              </label>
              <label>
                Target API version
                <input
                  required
                  maxLength={100}
                  value={value.target_version}
                  onChange={(e) => set("target_version", e.target.value)}
                />
              </label>
              <label>
                Execution mode
                <select
                  aria-label="Execution mode"
                  value={value.mode}
                  onChange={(e) =>
                    set("mode", e.target.value as Incident["mode"])
                  }
                >
                  <option value="replay">Recorded replay</option>
                  <option value="live" disabled={!ready}>
                    Live search + AI{!ready ? " (keys needed)" : ""}
                  </option>
                </select>
              </label>
            </div>
            <label>
              Observed failure
              <textarea
                className="symptom"
                value={value.symptom}
                maxLength={2000}
                onChange={(e) => set("symptom", e.target.value)}
              />
            </label>
            <div className="field-row">
              <label>
                Search hints
                <input
                  value={value.search_hint}
                  maxLength={200}
                  onChange={(e) => set("search_hint", e.target.value)}
                />
              </label>
              <label>
                Function entrypoint
                <input
                  required
                  value={value.entrypoint}
                  onChange={(e) => set("entrypoint", e.target.value)}
                />
              </label>
            </div>
            <p className="mode-note">
              <Search size={15} />
              {value.mode === "live"
                ? "Uses SerpApi for public vendor research. Your adapter, sanitized cases and selected sources are sent to the configured AI provider; verification runs locally."
                : "Uses labeled recorded evidence and a deterministic repair policy. No live AI or search requests."}
            </p>
          </div>
          <div className="editor-code-grid">
            <label className="code-label">
              <span>
                <Code2 size={16} /> Adapter function
              </span>
              <textarea
                aria-label="Adapter function"
                className="code-input"
                spellCheck={false}
                value={value.source_code}
                required
                maxLength={12000}
                onChange={(e) => set("source_code", e.target.value)}
              />
            </label>
            <label className="code-label">
              <span>
                <FlaskConical size={16} /> Protected acceptance cases
              </span>
              <textarea
                aria-label="Protected acceptance cases"
                className="code-input"
                spellCheck={false}
                value={cases}
                required
                onChange={(e) => setCases(e.target.value)}
              />
            </label>
          </div>
          <p className="editor-help">
            Paste sanitized JSON only. Each case needs a name, input and
            expected output. The agent can propose code; it cannot change these
            cases.
          </p>
          {error && (
            <div role="alert" className="error-box">
              {error}
            </div>
          )}
          <footer className="modal-footer">
            <span>
              3 repair attempts · 4 minute budget · proposed changes only
            </span>
            <button
              type="button"
              className="button secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button className="button primary" disabled={busy}>
              {busy ? "Starting…" : "Start investigation"}
              <ArrowRight size={16} />
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}
