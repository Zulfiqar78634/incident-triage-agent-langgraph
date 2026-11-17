import { useEffect, useState } from "react";
import ApprovalPanel from "./components/ApprovalPanel";
import EvidencePanel from "./components/EvidencePanel";
import IncidentForm from "./components/IncidentForm";
import RunHeader from "./components/RunHeader";
import TracePanel from "./components/TracePanel";
import WorkflowTimeline from "./components/WorkflowTimeline";
import { checkHealth, startRun, submitApproval } from "./api/client";
import { useRunState } from "./hooks/useRunState";
import type { IncidentInput } from "./types/agent";

export default function App() {
  const [runId, setRunId] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState(false);
  const { run, error } = useRunState(runId);

  useEffect(() => {
    checkHealth().then(setApiConnected);
  }, []);

  const handleStart = async (incident: IncidentInput) => {
    const created = await startRun(incident);
    setRunId(created.run_id);
  };

  const handleApproval = async (decision: "approved" | "rejected") => {
    if (!runId) return;
    await submitApproval(runId, decision);
  };

  return (
    <div className="app">
      <header>
        <div>
          <h1>Incident Triage & Safe Remediation Agent</h1>
          <p>Investigate incidents, explain decisions, and require approval before risky actions.</p>
        </div>
      </header>

      <main>
        <IncidentForm onStart={handleStart} />

        {error && <div className="error">{error}</div>}

        {run && (
          <>
            <RunHeader run={run} apiConnected={apiConnected} />
            <WorkflowTimeline status={run.status} />

            <section className="card">
              <h3>Agent reasoning</h3>
              <p>{String(run.diagnosis?.rationale ?? "The agent is collecting evidence.")}</p>
            </section>

            <EvidencePanel evidence={run.evidence} toolCalls={run.tool_calls} />
            <ApprovalPanel run={run} onApprove={handleApproval} />

            {run.verification && (
              <section className="card">
                <h3>Verification</h3>
                <pre>{JSON.stringify(run.verification, null, 2)}</pre>
              </section>
            )}

            <TracePanel events={run.events} />
          </>
        )}
      </main>
    </div>
  );
}
