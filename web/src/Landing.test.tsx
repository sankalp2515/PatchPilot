import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import App from "./App";

test("landing introduces scope and offers working workspace navigation without fetching the backend", () => {
  window.history.replaceState({}, "", "/");
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  expect(
    screen.getByRole("heading", { name: "API changes. Your contract stays." }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Try the repair workspace" }),
  ).toHaveAttribute("href", "/app");
  expect(screen.getByRole("link", { name: "Install locally" })).toHaveAttribute(
    "href",
    "#install",
  );
  expect(
    screen.getByText("Illustrative pricing, not a paid offering."),
  ).toBeInTheDocument();
  expect(fetch).not.toHaveBeenCalled();
});
