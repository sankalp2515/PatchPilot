import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import RunDetail from "./components/RunDetail";
import type { Run } from "./types";
const base = {
  id: "test",
  status: "verified",
  phase: "verified",
  input: {
    title: "Test incident",
    vendor: "stripe",
    target_version: "basil",
    entrypoint: "normalize",
    mode: "replay",
    max_attempts: 3,
    symptom: "Missing pointer",
  },
  created_at: "2026-10-12",
  plan: [],
  events: [],
  sources: [],
  attempts: [],
  baseline: [],
  verification: [],
  proposed_code: "",
  diff: "",
  diagnosis: "",
  citations: [],
  limitations: [],
  metrics: { elapsed_seconds: 0, search_calls: 0, model_calls: 0, tokens: 0 },
} as unknown as Run;
const callbacks = {
  onBack: () => {},
  onRerun: () => {},
  onCancel: () => {},
  onResume: () => {},
};
test("shows proof hashes and separate independent coverage when present", () => {
  const run = {
    ...base,
    proof: {
      contract_hash: "contract123",
      evidence_hashes: [{ source_id: "s1", sha256: "evidence123" }],
      patch_hash: "patch123",
      acceptance_passed: 5,
      total: 5,
      audit: { applicable: true, passed: 8, total: 8, results: [] },
      verified_scope:
        "Only the supplied contract and audited invoice pointers.",
    },
  };
  render(<RunDetail run={run} {...callbacks} />);
  expect(
    screen.getByRole("heading", { name: "Repair proof" }),
  ).toBeInTheDocument();
  expect(screen.getByText("contract123")).toBeInTheDocument();
  expect(screen.getByText("8/8 independent audit cases")).toBeInTheDocument();
  expect(
    screen.getByText(
      "Only the supplied contract and audited invoice pointers.",
    ),
  ).toBeInTheDocument();
});
test("historical runs without a proof remain readable and disclose absent proof", () => {
  render(<RunDetail run={base} {...callbacks} />);
  expect(
    screen.getByText("This historical run has no bound repair proof."),
  ).toBeInTheDocument();
});
