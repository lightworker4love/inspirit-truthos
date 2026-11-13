import { expect, test } from "@playwright/test";

const origin = "http://127.0.0.1:13100";
const truthApi = "http://127.0.0.1:18180";
const hermes = "http://127.0.0.1:18181";

test("student flow uses the real isolated backend and preserves branding", async ({ page, context, request }, info) => {
  const unexpectedRequests: string[] = [];
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await context.route("**/*", async route => {
    const url = new URL(route.request().url());
    if (!["127.0.0.1", "localhost"].includes(url.hostname)) {
      unexpectedRequests.push(url.origin);
      await route.abort();
    } else await route.continue();
  });
  await page.goto("/chat");
  await expect(page).toHaveURL(/reason=missing-user/);
  await expect(page.getByText("請先告訴我你的名字", { exact: true })).toBeVisible();
  const user = `security-${info.project.name}-${Date.now()}`;
  await page.getByLabel("名字或代號").fill(user);
  await page.getByRole("button", { name: "開始對話" }).click();
  await expect(page.getByText("你好。我是 Hermes，你的生命藍圖陪伴者。", { exact: false })).toBeVisible();
  const message = "I always give up before finishing what I start";
  const reply = page.waitForResponse(r => r.url() === `${hermes}/chat` && r.request().method() === "POST");
  await page.getByPlaceholder("慢慢說，從現在最真實的一句話開始...").fill(message);
  await page.getByRole("button", { name: "送出訊息" }).click();
  const response = await reply;
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.session_id).toBeTruthy();
  expect(body.response).toContain(message);
  await expect(page.getByText(body.response, { exact: true })).toBeVisible();
  // Poll the real API because writeback can finish after the Hermes response.
  await expect.poll(async () => {
    const map = await request.get(`${truthApi}/api/soul-map/${user}`);
    return map.ok() ? (await map.json()).status : "";
  }).toBe("active");
  await page.goto("/soul-map");
  await expect(page.getByRole("heading", { name: "靈魂藍圖", exact: true })).toBeVisible();
  await expect(page.getByText("active", { exact: true })).toBeVisible();
  const map = await (await request.get(`${truthApi}/api/soul-map/${user}`)).json();
  expect(map.updated_at).toBeTruthy();
  await page.goto("/history");
  await expect(page).toHaveTitle("iN SPiRiT 生命藍圖 Life Blueprint");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: info.outputPath("student-flow.png"), fullPage: true });
  expect(unexpectedRequests).toEqual([]);
  expect(errors).toEqual([]);
});

test("backend CORS is exact-origin and invalid payloads are rejected", async ({ request }) => {
  for (const service of [truthApi, hermes]) {
    const accepted = await request.fetch(`${service}/health`, {
      method: "OPTIONS",
      headers: { Origin: origin, "Access-Control-Request-Method": "GET" },
    });
    expect(accepted.headers()["access-control-allow-origin"]).toBe(origin);
    const rejected = await request.fetch(`${service}/health`, {
      method: "OPTIONS",
      headers: { Origin: "https://untrusted.invalid", "Access-Control-Request-Method": "GET" },
    });
    expect(rejected.headers()["access-control-allow-origin"]).toBeUndefined();
    expect(rejected.status()).toBe(400);
  }
  const invalid = await request.post(`${hermes}/chat`, { data: { message: "missing-user" } });
  expect(invalid.status()).toBe(422);
});
