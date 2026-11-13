import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const service = process.argv[2];
const { RAILWAY_PROJECT_ID: project, RAILWAY_ENVIRONMENT: environment, DEPLOY_SHA: sha } = process.env;
assert.ok(service && project && environment && sha, "Missing deployment verification target");
let lastStatus;
for (let attempt = 0; attempt < 36; attempt++) {
  const raw = execFileSync("railway", ["deployment", "list", "--project", project, "--environment", environment, "--service", service, "--limit", "5", "--json"], { encoding: "utf8", timeout: 30000 });
  const result = JSON.parse(raw);
  const deployments = Array.isArray(result) ? result : result.deployments;
  assert.ok(Array.isArray(deployments), "Unexpected Railway deployment-list response");
  const deployment = deployments.find(d => JSON.stringify(d.meta ?? {}).includes(sha) || (d.message ?? "").includes(sha));
  if (deployment) {
    if (deployment.status !== lastStatus) console.log(JSON.stringify({ service, deploymentId: deployment.id, status: deployment.status, sha }));
    lastStatus = deployment.status;
    if (deployment.status === "SUCCESS") process.exit(0);
    assert.ok(!["FAILED", "CRASHED", "REMOVED", "SKIPPED"].includes(deployment.status), `${service} deployment failed`);
  } else if (attempt === 0) {
    console.log(JSON.stringify({ service, expectedSha: sha, observation: "waiting for a deployment with matching commit/message", responseKeys: deployments.map(d => ({ id: d.id, status: d.status, metaKeys: Object.keys(d.meta ?? {}) })) }));
  }
  await delay(10000);
}
throw new Error(`No successful ${service} deployment for ${sha} within the verification window`);
