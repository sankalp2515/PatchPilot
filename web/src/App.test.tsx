import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, test, expect, beforeEach } from "vitest";
import App from "./App";

const example = {
  title: "Stripe invoice migration",
  vendor: "stripe",
  target_version: "2025-03-31.basil",
  mode: "live",
  source_code: "def normalize_invoice(x):\n    return []",
  entrypoint: "normalize_invoice",
  cases: [{ name: "Empty", input: {}, expected: [] }],
  symptom: "Missing field",
  search_hint: "invoice",
  max_attempts: 3,
  replay_scenario: "repair",
};
beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const body = url.includes("/config")
        ? {
            live_ready: true,
            search_ready: true,
            model_ready: true,
            provider: "groq",
            model: "test",
            partners: {
              neatlogs: "pending",
              entire: "pending",
              cfo_ai: "pending",
            },
          }
        : url.includes("/examples")
          ? [example]
          : [];
      return { ok: true, json: async () => body };
    }),
  );
});

test("loads example into editable intake and labels live mode", async () => {
  render(<App />);
  await screen.findByText("Stripe invoice migration");
  fireEvent.click(screen.getByRole("button", { name: /New investigation/i }));
  expect(screen.getByLabelText("Incident title")).toHaveValue(
    "Stripe invoice migration",
  );
  expect(screen.getByLabelText("Execution mode")).toHaveValue("live");
  expect(screen.getByLabelText("Adapter function")).toHaveValue(
    example.source_code,
  );
});

test("shows partner integrations as pending rather than compliant", async () => {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Integrations" }));
  await waitFor(() =>
    expect(screen.getByText("Morning setup")).toBeInTheDocument(),
  );
  expect(screen.getAllByText("Pending").length).toBe(3);
});

test("network error produces a readable recovery action", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => {
      throw new Error("offline");
    }),
  );
  render(<App />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/backend/i);
  expect(
    screen.getByRole("button", { name: "Retry connection" }),
  ).toBeInTheDocument();
});

test("retry connection restarts selected investigation polling", async () => {
  let failed = false;
  const finished = {
    id: "retry-run",
    status: "needs_human",
    phase: "needs_human",
    input: example,
    created_at: new Date().toISOString(),
    plan: [],
    events: [],
    sources: [],
    attempts: [],
    baseline: [],
    verification: [],
    proposed_code: "",
    diff: "",
    diagnosis: "Recovered detail",
    citations: [],
    limitations: [],
    metrics: { search_calls: 0, model_calls: 0, tokens: 0, elapsed_seconds: 0 },
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      if (url === "/api/runs/retry-run") {
        if (!failed) {
          failed = true;
          throw new Error("temporary outage");
        }
        return { ok: true, json: async () => finished };
      }
      const data = url.includes("/config")
        ? { live_ready: true, partners: {} }
        : url.includes("/examples")
          ? [example]
          : [
              {
                id: "retry-run",
                title: "Recoverable incident",
                vendor: "stripe",
                mode: "replay",
                status: "needs_human",
                created_at: new Date().toISOString(),
                metrics: finished.metrics,
              },
            ];
      return { ok: true, json: async () => data };
    }),
  );
  render(<App />);
  fireEvent.click(
    await screen.findByRole("button", { name: /Recoverable incident/ }),
  );
  await screen.findByRole("alert");
  fireEvent.click(screen.getByRole("button", { name: "Retry connection" }));
  expect(await screen.findByText("Recovered detail")).toBeInTheDocument();
});
