import { test, expect } from "@playwright/test";

test("recovery example completes with protected tests, evidence, diff and report", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await page.getByRole("button", { name: /Recorded replay Recovery/ }).click();
  await expect(page.getByLabel("Execution mode")).toHaveValue("replay");
  await page
    .getByRole("button", { name: "Start investigation", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Verified in tested scope",
  );
  await expect(page.getByRole("status")).toContainText("5/5");
  await expect(page.getByText("2/5 cases pass on attempt 1.")).toBeVisible();
  await page.getByRole("tab", { name: "Evidence (1)" }).click();
  await expect(page.getByText("Recorded historical excerpt")).toBeVisible();
  await page.getByRole("tab", { name: "Proposed repair" }).click();
  await expect(page.getByText("Minimal proposed change")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Download adapter" }),
  ).toBeVisible();
  await page.getByRole("tab", { name: "Acceptance tests" }).click();
  await expect(
    page.getByText("After proposed repair", { exact: true }),
  ).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: "Report", exact: true }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/patchpilot.*\.md/);
  await expect(page.locator(".case-pass")).toHaveCount(5);
  expect(errors).toEqual([]);
});

test("mobile workbench and editor remain usable without horizontal overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Examples", exact: true }).click();
  await expect(page.getByText("Bring your own integration")).toBeVisible();
  await page.getByRole("button", { name: /No authoritative evidence/ }).click();
  await page
    .getByRole("button", { name: "Start investigation", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Needs investigation");
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
  await page.screenshot({
    path: "../docs/assets/mobile-workbench.png",
    fullPage: true,
  });
});

test("invalid JSON remains editable and credential input is rejected", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "New investigation", exact: true })
    .click();
  await page.getByLabel("Protected acceptance cases").fill("{invalid json");
  await page
    .getByRole("button", { name: "Start investigation", exact: true })
    .click();
  await expect(page.getByRole("alert")).toBeVisible();
  await page
    .getByLabel("Protected acceptance cases")
    .fill(
      JSON.stringify([
        {
          name: "Secret rejection",
          input: { api_key: "private-example" },
          expected: {},
        },
      ]),
    );
  await page
    .getByRole("button", { name: "Start investigation", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "Check the incident fields",
  );
  await expect(page.getByRole("dialog")).toBeVisible();
});
