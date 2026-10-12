import {
  ArrowUpRight,
  Check,
  Code2,
  FileSearch,
  GitBranch,
  ShieldCheck,
  Terminal,
  Workflow,
} from "lucide-react";

export default function Landing() {
  return (
    <div className="landing">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="landing-nav">
        <a className="landing-brand" href="/" aria-label="PatchPilot home">
          <span className="pilot-mark">
            <Workflow size={23} />
          </span>
          PatchPilot<span className="brand-period">.</span>
        </a>
        <nav aria-label="Site navigation">
          <a href="#workflow">How it works</a>
          <a href="/app/showcase">Product walkthrough</a>
          <a href="#proof">The proof</a>
          <a href="#pricing">Pricing</a>
        </nav>
        <a className="nav-workspace" href="/app">
          Open workspace <ArrowUpRight size={17} />
        </a>
      </header>
      <main id="main-content">
        <section className="landing-hero">
          <div className="hero-copy">
            <div className="release-note">
              <span /> Built for the moment an integration breaks
            </div>
            <h1>
              API changes.
              <br />
              Your contract stays.
            </h1>
            <p>
              Turn a broken Python adapter into a small, evidence-backed repair.
              Find the right documentation, protect your expected outputs, and
              review exactly what passed.
            </p>
            <div className="hero-actions">
              <a className="button primary" href="/app">
                Try the repair workspace <ArrowUpRight size={19} />
              </a>
              <a className="install-link" href="#install">
                Install locally
              </a>
            </div>
            <div className="hero-assurance">
              <ShieldCheck size={16} /> Local execution. Protected tests. Your
              final decision.
            </div>
          </div>
          <div
            className="repair-dossier"
            aria-label="Illustrated Stripe replay repair dossier"
          >
            <div className="dossier-head">
              <span>
                <span className="dossier-dot" /> Repair dossier
              </span>
              <span>Stripe / Basil</span>
            </div>
            <div className="dossier-body">
              <div className="dossier-meta">
                Recorded demonstration <span>Python adapter</span>
              </div>
              <h2>
                A missing payment pointer.
                <br />A traceable way forward.
              </h2>
              <div className="contract-line">
                <span>Contract</span>
                <code>invoice → payment_intent_ids</code>
                <span className="contract-lock">
                  <ShieldCheck size={13} /> protected
                </span>
              </div>
              <div className="code-window">
                <div className="code-window-title">
                  <Code2 size={14} /> adapter.py <span>proposed change</span>
                </div>
                <pre>
                  <span className="code-muted">
                    # Invoice payment references changed
                  </span>
                  {"\n"}
                  <span className="code-remove">
                    − invoice["payment_intent"]
                  </span>
                  {"\n"}
                  <span className="code-add">
                    + invoice["payments"]["data"]
                  </span>
                </pre>
              </div>
              <div className="proof-chain">
                <div>
                  <FileSearch size={19} />
                  <strong>Version evidence</strong>
                  <small>Official source excerpt</small>
                </div>
                <span />
                <div>
                  <GitBranch size={19} />
                  <strong>Minimal repair</strong>
                  <small>Reviewable Python diff</small>
                </div>
                <span />
                <div>
                  <ShieldCheck size={19} />
                  <strong>Tested scope</strong>
                  <small>Acceptance + audit</small>
                </div>
              </div>
              <div className="dossier-footer">
                <Check size={17} />
                <span>Evidence travels with the patch.</span>
                <span className="proof-stamp">Review ready</span>
              </div>
            </div>
            <div className="dossier-caption">
              A product illustration. Run the replay to inspect the actual
              evidence.
            </div>
          </div>
        </section>
        <section className="trust-strip">
          <p>Made for engineers who own the integration.</p>
          <div>
            <span>
              Search with <b>SerpApi</b>
            </span>
            <span>
              Trace with <b>neatlogs</b>
            </span>
            <span>
              Context with <b>Entire</b>
            </span>
            <span>
              Scenarios with <b>cfo.ai</b>
            </span>
          </div>
          <small>
            Tool roles, not customer endorsements. Connection status appears in
            the workspace.
          </small>
        </section>
        <section id="workflow" className="landing-section">
          <div className="section-intro">
            <span className="section-kicker">From incident to evidence</span>
            <h2>
              Fix the break.
              <br />
              Keep the reasoning.
            </h2>
            <p>
              An API migration is a research problem before it is a code
              problem. PatchPilot keeps both sides in one investigation.
            </p>
          </div>
          <ol className="workflow-story">
            <li>
              <span>1</span>
              <div>
                <FileSearch />
                <h3>Start with the failure.</h3>
                <p>
                  Bring a sanitized response, the adapter, and the output your
                  application needs. Acceptance cases stay protected.
                </p>
              </div>
            </li>
            <li>
              <span>2</span>
              <div>
                <GitBranch />
                <h3>Follow the version evidence.</h3>
                <p>
                  SerpApi discovers vendor documentation. Fetched,
                  version-specific passages support a bounded repair proposal.
                </p>
              </div>
            </li>
            <li>
              <span>3</span>
              <div>
                <ShieldCheck />
                <h3>Leave with a reviewable proof.</h3>
                <p>
                  Compare the baseline and repaired cases. Inspect citations,
                  the diff, independent audit results, and a portable report.
                </p>
              </div>
            </li>
          </ol>
        </section>
        <section id="proof" className="proof-section">
          <div className="proof-section-copy">
            <span className="section-kicker">
              Inside the sample investigation
            </span>
            <h2>
              “Passed” needs
              <br />a paper trail.
            </h2>
            <p>
              The historical Stripe Basil invoice migration removes the direct
              payment pointer. The replay shows the failure, an incomplete
              attempt, and recovery using the invoice payment list.
            </p>
            <a href="/app" className="text-action">
              Inspect the recorded investigation <ArrowUpRight size={18} />
            </a>
          </div>
          <div className="proof-ledger">
            <div>
              <span>Before</span>
              <h3>A protected case fails.</h3>
              <p>
                The original adapter expects a field the target response no
                longer provides.
              </p>
            </div>
            <div>
              <span>Research</span>
              <h3>The version matters.</h3>
              <p>
                Captured official documentation and literal citations explain
                the schema change.
              </p>
            </div>
            <div>
              <span>After</span>
              <h3>The patch has boundaries.</h3>
              <p>
                Acceptance coverage and deterministic counterexamples are
                reported separately. Hashes bind the contract, evidence, and
                proposed code.
              </p>
            </div>
          </div>
        </section>
        <section className="landing-section benefits-section">
          <div className="section-intro">
            <span className="section-kicker">
              Less guesswork in the handoff
            </span>
            <h2>
              Built to earn
              <br />a code review.
            </h2>
          </div>
          <div className="benefit-grid">
            <article>
              <h3>Documentation beside the diff.</h3>
              <p>
                No disconnected tabs or unsupported explanation. Inspect the
                source passage that informed a proposed change.
              </p>
            </article>
            <article>
              <h3>Failure is a useful outcome.</h3>
              <p>
                Missing evidence, authentication problems, and exhausted
                attempts surface clearly. The agent can stop without inventing a
                repair.
              </p>
            </article>
            <article>
              <h3>A record you can take with you.</h3>
              <p>
                Export the adapter and investigation report. Durable checkpoints
                preserve progress when a local run is interrupted.
              </p>
            </article>
            <article>
              <h3>A deliberately narrow scope.</h3>
              <p>
                Restricted Python adapter execution. Sanitized inputs. Bounded
                attempts. Review the proposal before applying it yourself.
              </p>
            </article>
          </div>
        </section>
        <section id="pricing" className="pricing-section">
          <div>
            <span className="section-kicker">
              An experiment with transparent economics
            </span>
            <h2>
              Start local.
              <br />
              Know the cost.
            </h2>
            <p>Illustrative pricing, not a paid offering.</p>
            <p>
              Live usage depends on your search and model providers. The
              business scenario uses editable assumptions, not measured customer
              demand.
            </p>
          </div>
          <article className="price-card">
            <span>Local prototype</span>
            <h3>
              $0 <small>project fee</small>
            </h3>
            <p>Replay the sample and run the workspace on your machine.</p>
            <ul>
              <li>
                <Check size={16} /> Recorded investigations
              </li>
              <li>
                <Check size={16} /> Evidence and report exports
              </li>
              <li>
                <Check size={16} /> Bring your own provider keys
              </li>
            </ul>
            <a href="#install" className="button secondary">
              Get the local prototype <ArrowUpRight size={17} />
            </a>
          </article>
          <article className="price-card concept">
            <span>Team concept</span>
            <h3>
              $79 <small>/ month</small>
            </h3>
            <p>
              A planning assumption for a future shared review workflow.
              Individual concept: $19/month.
            </p>
            <ul>
              <li>
                <Check size={16} /> Proposed recurring subscription
              </li>
              <li>
                <Check size={16} /> Provider costs modeled separately
              </li>
              <li>
                <Check size={16} /> No billing or checkout today
              </li>
            </ul>
            <a href="/app" className="text-action">
              Explore the current workspace <ArrowUpRight size={17} />
            </a>
          </article>
        </section>
        <section className="landing-section faq-section">
          <div className="section-intro">
            <span className="section-kicker">Before you run it</span>
            <h2>
              A few good
              <br />
              questions.
            </h2>
          </div>
          <div className="faq-list">
            {[
              [
                "Does PatchPilot change my production code?",
                "It proposes an adapter and a diff for your review. You download and apply any change yourself. It does not deploy or mutate production systems.",
              ],
              [
                "What does verified mean?",
                "The proposed adapter passed the protected acceptance cases and any applicable independent audit. This establishes the reported tested scope, not correctness for every possible response.",
              ],
              [
                "Can I try it without API keys?",
                "Yes. Recorded replay uses sanitized historical fixtures and captured documentation. Live research requires server-side SerpApi and supported model credentials.",
              ],
              [
                "Can it repair an arbitrary repository?",
                "The current scope is a restricted Python response adapter with a named entrypoint. It is not a general repository repair or execution agent.",
              ],
              [
                "Where do credentials and incident data go?",
                "Provider keys stay in the local server environment. Live runs send research queries and sanitized incident context to configured providers. Remove secrets and personal data before creating an incident.",
              ],
            ].map(([q, a]) => (
              <details key={q}>
                <summary>
                  {q}
                  <span aria-hidden="true">+</span>
                </summary>
                <p>{a}</p>
              </details>
            ))}
          </div>
        </section>
        <section id="install" className="install-section">
          <div>
            <Terminal size={28} />
            <h2>
              Your next migration
              <br />
              deserves better evidence.
            </h2>
            <p>
              Run locally with Python 3.12 and Node.js, or use Docker Compose.
              The quick-start command sets up and starts the app.
            </p>
            <a className="button primary" href="/app">
              Open the repair workspace <ArrowUpRight size={18} />
            </a>
          </div>
          <div className="install-terminal">
            <div>
              <span /> Local quick start
            </div>
            <pre>
              git clone https://github.com/sankalp2515/PatchPilot.git{"\n"}cd
              PatchPilot{"\n"}
              <span># Windows PowerShell: setup + start</span>
              {"\n"}.\scripts\run.ps1{"\n"}
              <span># Or with Docker Desktop</span>
              {"\n"}docker compose up --build -d
            </pre>
            <p>
              See the repository README for supported environments and live
              credentials.
            </p>
            <a
              href="https://github.com/sankalp2515/PatchPilot"
              target="_blank"
              rel="noreferrer"
            >
              Read installation guide <ArrowUpRight size={16} />
            </a>
          </div>
        </section>
      </main>
      <footer className="landing-footer">
        <a className="landing-brand" href="/">
          PatchPilot<span className="brand-period">.</span>
        </a>
        <p>Repair the adapter. Preserve the contract.</p>
        <a href="/app">
          Engineering workspace <ArrowUpRight size={16} />
        </a>
      </footer>
    </div>
  );
}
