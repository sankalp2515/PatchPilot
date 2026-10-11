export type Case = { name: string; input: unknown; expected: unknown };
export type Incident = {
  title: string;
  vendor: "stripe" | "github" | "slack" | "shopify";
  target_version: string;
  mode: "live" | "replay";
  source_code: string;
  entrypoint: string;
  cases: Case[];
  symptom: string;
  search_hint: string;
  max_attempts: number;
  replay_scenario: "repair" | "recovery" | "no_evidence" | "auth";
};
export type Metrics = {
  search_calls: number;
  model_calls: number;
  tokens: number;
  elapsed_seconds: number;
};
export type Summary = {
  id: string;
  title: string;
  vendor: string;
  mode: string;
  status: string;
  created_at: string;
  metrics: Metrics;
};
export type Result = {
  name: string;
  passed: boolean;
  actual: unknown;
  expected: unknown;
  error: string;
};
export type Source = {
  id: string;
  title: string;
  url: string;
  text: string;
  provenance: string;
  version: string;
  sha256: string;
  query: string;
};
export type Run = {
  id: string;
  status: string;
  phase: string;
  input: Incident;
  created_at: string;
  plan: { area: string; task: string }[];
  events: { at: string; kind: string; title: string; detail: string }[];
  sources: Source[];
  attempts: {
    number: number;
    code: string;
    error: string;
    results: Result[];
  }[];
  baseline: Result[];
  verification: Result[];
  proposed_code: string;
  diff: string;
  diagnosis: string;
  citations: { source_id: string; quote: string }[];
  limitations: string[];
  metrics: Metrics;
};
export type Config = {
  live_ready: boolean;
  search_ready: boolean;
  model_ready: boolean;
  provider: string;
  model: string;
  partners: Record<string, string>;
};
export const terminal = new Set([
  "verified",
  "no_change",
  "needs_human",
  "unverified",
  "failed",
  "cancelled",
  "interrupted",
]);
