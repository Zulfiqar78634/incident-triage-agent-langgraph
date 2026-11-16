const form = document.getElementById("incident-form");
const runPanel = document.getElementById("run-panel");
const approvalActions = document.getElementById("approval-actions");
let currentRunId = null;

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    service: document.getElementById("service").value,
    environment: document.getElementById("environment").value,
    severity: document.getElementById("severity").value,
    operator_id: "web-operator"
  };

  const response = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const run = await response.json();
  currentRunId = run.run_id;
  runPanel.classList.remove("hidden");
  renderRun(run);
});

async function refreshRun() {
  if (!currentRunId) return;
  const response = await fetch(`/api/runs/${currentRunId}`);
  if (response.ok) renderRun(await response.json());
}

function renderRun(run) {
  document.getElementById("run-id").textContent = run.run_id;
  const status = document.getElementById("run-status");
  status.textContent = run.status;
  status.className = `badge ${run.status}`;

  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";

  (run.events || []).forEach((event) => {
    const item = document.createElement("div");
    item.className = "event";
    item.innerHTML = `
      <strong>${event.node} · ${event.event}</strong>
      <div>${event.message}</div>
      <small>${event.created_at}</small>
    `;
    timeline.appendChild(item);
  });

  document.getElementById("plan-output").textContent = JSON.stringify({
    classification: run.classification,
    diagnosis: run.diagnosis,
    plan: run.plan,
    pending_action: run.pending_action,
    execution: run.execution,
    verification: run.verification,
    context_usage: run.context_usage
  }, null, 2);

  const evidence = document.getElementById("evidence");
  evidence.innerHTML = "";
  (run.evidence || []).forEach((item) => {
    const element = document.createElement("div");
    element.className = "evidence-item";
    element.innerHTML = `<strong>${item.id} · ${item.source}</strong><div>${escapeHtml(item.content)}</div>`;
    evidence.appendChild(element);
  });

  approvalActions.classList.toggle("hidden", run.status !== "awaiting_approval");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

document.getElementById("approve-button").addEventListener("click", () => submitApproval("approved"));
document.getElementById("reject-button").addEventListener("click", () => submitApproval("rejected"));

async function submitApproval(decision) {
  const response = await fetch(`/api/runs/${currentRunId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reason: decision === "approved" ? "Evidence supports rollback." : "Do not execute this action.",
      operator_id: "web-operator"
    })
  });

  const run = await response.json();
  renderRun(run);
}

setInterval(refreshRun, 2000);

fetch("/api/health")
  .then(() => {
    document.getElementById("connection-status").textContent = "API connected";
  })
  .catch(() => {
    document.getElementById("connection-status").textContent = "API unavailable";
  });
