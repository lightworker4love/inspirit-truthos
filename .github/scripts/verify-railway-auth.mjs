import assert from "node:assert/strict";
import { appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const token = process.env.RAILWAY_DEPLOY_CREDENTIAL;
const project = process.env.RAILWAY_PROJECT_ID;
assert.ok(token && project && process.env.GITHUB_ENV, "Missing Railway deployment configuration");
async function query(header, document) {
  const response = await fetch("https://backboard.railway.com/graphql/v2", {
    method: "POST",
    headers: { "Content-Type": "application/json", [header]: header === "Authorization" ? `Bearer ${token}` : token },
    body: JSON.stringify({ query: document }),
    signal: AbortSignal.timeout(15000),
  });
  return response.ok ? await response.json() : {};
}
const scoped = await query("Project-Access-Token", "query { projectToken { projectId environmentId } }");
let authVariable;
if (scoped.data?.projectToken?.projectId === project && scoped.data.projectToken.environmentId) {
  authVariable = "RAILWAY_TOKEN";
  appendFileSync(process.env.GITHUB_ENV, `RAILWAY_TOKEN=${token}\n`);
  console.log("Verified project-scoped Railway access to the expected project");
} else {
  authVariable = "RAILWAY_API_TOKEN";
  const account = await query("Authorization", `query { project(id: "${project}") { id } }`);
  assert.equal(account.data?.project?.id, project, "Existing Railway credential cannot access the expected project; no deployment started");
  appendFileSync(process.env.GITHUB_ENV, `RAILWAY_API_TOKEN=${token}\n`);
  console.log("Verified account/workspace Railway access to the expected project");
}
// Capture safe deployment identifiers before any production write, for recovery.
const environment = { ...process.env };
delete environment.RAILWAY_TOKEN;
delete environment.RAILWAY_API_TOKEN;
environment[authVariable] = token;
for (const service of ["truth-api", "hermes-agent", "truthos-web"]) {
  const raw = execFileSync("railway", ["deployment", "list", "--project", project, "--environment", "production", "--service", service, "--limit", "3", "--json"], { env: environment, encoding: "utf8", timeout: 30000 });
  const result = JSON.parse(raw);
  const deployments = Array.isArray(result) ? result : result.deployments;
  assert.ok(Array.isArray(deployments), "Unexpected deployment baseline response");
  console.log(JSON.stringify({ baselineService: service, deployments: deployments.map(d => ({ id: d.id, status: d.status, commitHash: d.meta?.commitHash ?? null })) }));
}
