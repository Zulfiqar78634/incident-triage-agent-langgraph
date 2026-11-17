interface Props {
  run: {
    run_id: string;
    status: string;
    incident: { service: string; environment: string; severity: string };
    diagnosis?: Record<string, unknown> | null;
    context_usage?: Record<string, unknown> | null;
  };
  apiConnected: boolean;
}

export default function RunHeader({ run, apiConnected }: Props) {
  const confidence = run.diagnosis?.confidence as number | undefined;

  return (
    <div className="run-header">
      <div>
        <h2>Run {run.run_id}</h2>
        <div className="meta">
          <span className={`badge ${run.status}`}>{run.status}</span>
          <span>{run.incident.service}</span>
          <span>{run.incident.environment}</span>
          <span>Severity: {run.incident.severity}</span>
          {confidence !== undefined && <span>Confidence: {Math.round(confidence * 100)}%</span>}
          <span className={apiConnected ? "connected" : "disconnected"}>
            {apiConnected ? "API connected" : "API unavailable"}
          </span>
        </div>
      </div>
    </div>
  );
}
