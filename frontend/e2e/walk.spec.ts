import { expect, test } from "@playwright/test";

test("a phone can open the waiting call", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "On the floor" })).toBeVisible();
  await expect(page.getByText("Not a Tesla system")).toBeVisible();
  await expect(page.getByText("Recommendation only. You decide. This does not change the line.")).toBeVisible();
  await page.getByTestId("open-call-14").click();
  await expect(page.getByTestId("similarity")).toHaveText("87%");
  await expect(page.getByTestId("decide-slow")).toBeVisible();
});

test("supervisor records a slow call and the repair enters the handoff", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("open-call-14").click();
  await expect(page.getByTestId("similarity")).toHaveText("87%");
  await expect(page.getByTestId("recommendation")).toHaveText("Slow");
  await expect(page.getByTestId("prior-action")).toContainText(/bearing replaced/i);
  await page.getByLabel("Note for the next shift").fill("Held M-17 and called drive unit maintenance.");
  await page.getByTestId("decide-slow").click();
  await expect(page.getByTestId("decision-recorded")).toContainText(/slow/i);
  await expect(page.getByText("The line was not changed by this app.")).toBeVisible();
  await page.getByTestId("record-repair").click();
  await page.getByLabel("Diagnosis").fill("Bearing degradation");
  await page.getByLabel("Action taken").fill("Bearing replaced");
  await page.getByLabel("Downtime (minutes)").fill("27");
  await page.getByLabel("Outcome").fill("Machine returned to normal");
  await page.getByTestId("save-repair").click();
  await expect(page.getByTestId("repair-recorded")).toBeVisible();
  await page.getByRole("link", { name: "Handoff" }).click();
  await expect(page.getByTestId("handoff")).toContainText("M-17");
  await expect(page.getByTestId("handoff")).toContainText(/slow/i);
  await expect(page.getByTestId("handoff")).toContainText("Bearing replaced");
});

test("a new vibration report retrieves the bearing history", async ({ page }) => {
  await page.goto("/report");
  await page.getByLabel("Machine").selectOption("M-17");
  await page.getByRole("button", { name: "Abnormal vibration" }).click();
  await page.getByLabel("What did you see or hear?").fill("unusual noise");
  await page.getByTestId("create-incident").click();
  await expect(page.getByTestId("similarity")).toHaveText(/^(87|92)%$/);
  await expect(page.getByTestId("recommendation")).toHaveText("Slow");
  await expect(page.getByTestId("prior-action")).toContainText(/bearing replaced/i);
});
