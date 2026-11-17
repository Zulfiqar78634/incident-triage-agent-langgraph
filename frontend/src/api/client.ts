import type { AgentRun, IncidentInput } from "../types/agent";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function startRun(incident: IncidentInput): Promise<AgentRun> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(incident),
  });

  if (!response.ok) throw new Error("Failed to start agent run");
  return response.json();
}

export async function getRun(runId: string): Promise<AgentRun> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}`);

  if (!response.ok) throw new Error("Failed to load agent run");
  return response.json();
}

export async function submitApproval(
  runId: string,
  decision: "approved" | "rejected"
): Promise<AgentRun> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reason:
        decision === "approved"
          ? "Evidence supports the proposed remediation."
          : "Do not execute this action.",
      operator_id: "web-operator",
    }),
  });

  if (!response.ok) throw new Error("Failed to submit approval");
  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
