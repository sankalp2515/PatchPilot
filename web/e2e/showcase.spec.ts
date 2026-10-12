import { test, expect } from "@playwright/test";

test("saved live walkthrough is self-contained and makes no new provider requests", async ({ page }) => {
  const mutations: string[] = [];
  const remote: string[] = [];
  page.on("request", request => {
    if (request.method() !== "GET") mutations.push(request.url());
    if (!request.url().startsWith("http://127.0.0.1:8017")) remote.push(request.url());
  });
  await page.goto("/app/showcase");
  await expect(page.getByText("Saved live investigation", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Find evidence", exact: true }).click();
  await expect(page.getByText("serpapi_live_fetched", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Review repair", exact: true }).click();
  await expect(page.getByRole("heading", { name: "A focused change. An unchanged contract." })).toBeVisible();
  await page.getByRole("button", { name: "Verify outcome", exact: true }).click();
  await expect(page.getByText("20/20", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Tools and business", exact: true }).click();
  await expect(page.getByText("6/20", { exact: true })).toBeVisible();
  await page.getByRole("tab", { name: "Entire", exact: true }).click();
  await expect(page.getByText("01M4QNEWXG1454P3MWJM7EDW0J", { exact: true })).toBeVisible();
  await page.getByRole("tab", { name: "cfo.ai", exact: true }).click();
  await expect(page.getByText("$1,360", { exact: true })).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: "Download repair report" }).click(),
  ]);
  expect(download.suggestedFilename()).toBe("patchpilot-saved-live-report.md");
  expect(mutations).toEqual([]);
  expect(remote).toEqual([]);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});
