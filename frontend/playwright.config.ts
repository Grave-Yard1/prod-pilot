import { defineConfig, devices } from "@playwright/test";

const backend = "../backend";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: "http://127.0.0.1:8742",
    ...devices["Desktop Chrome"],
  },
  webServer: [
    {
      command: "mkdir -p data && rm -f data/e2e.db && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8741",
      cwd: backend,
      env: {
        PATH: process.env.PATH ?? "",
        HOME: process.env.HOME ?? "",
        DATABASE_URL: "sqlite:///./data/e2e.db",
      },
      url: "http://127.0.0.1:8741/api/health",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 8742",
      url: "http://127.0.0.1:8742",
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
