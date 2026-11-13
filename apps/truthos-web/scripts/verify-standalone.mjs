import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

// Run inside the final image with --network none. No backend calls or browser JS.
const server = spawn(process.execPath, ["server.js"], {
  env: { ...process.env, HOSTNAME: "127.0.0.1", PORT: "3000", NEXT_TELEMETRY_DISABLED: "1" },
  stdio: "inherit",
});
let serverError;
server.on("error", (error) => { serverError = error; });
try {
  let ready = false;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (serverError) throw serverError;
    assert.equal(server.exitCode, null, "standalone server exited early");
    try {
      ready = (await fetch("http://127.0.0.1:3000", { signal: AbortSignal.timeout(1000) })).ok;
    } catch { /* Readiness may race the server startup. */ }
    if (ready) break;
    await delay(200);
  }
  assert.ok(ready, "standalone server did not become ready");
  for (const route of ["/", "/chat", "/history", "/soul-map"]) {
    const response = await fetch(`http://127.0.0.1:3000${route}`, { signal: AbortSignal.timeout(5000) });
    assert.equal(response.status, 200, route);
    const html = await response.text();
    assert.ok(html.includes("iN SPiRiT 生命藍圖 Life Blueprint"), `brand missing: ${route}`);
    if (route === "/") assert.ok(html.includes("生命藍圖陪伴者"), "Hermes role missing");
    const assets = [...new Set([...html.matchAll(/(?:src|href)="([^" ]*\/_next\/static\/[^" ]+)"/g)].map((match) => match[1].replaceAll("&amp;", "&")))];
    assert.ok(assets.length > 0, `static assets missing: ${route}`);
    for (const asset of assets) {
      const result = await fetch(new URL(asset, "http://127.0.0.1:3000"), { signal: AbortSignal.timeout(5000) });
      assert.equal(result.status, 200, asset);
      await result.arrayBuffer();
    }
    console.log(`PASS ${route}: brand and ${assets.length} static assets`);
  }
  console.log(`PASS standalone runtime ${process.version}`);
} finally {
  server.kill("SIGTERM");
}
