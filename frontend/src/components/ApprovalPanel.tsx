interface Props {
  run: {
    status: string;
    pending_action?: Record<string, unknown> | null;
    plan?: Record<string, unknown> | null;
  };
  onApprove: (decision: "approved" | "rejected") => void;
}

export default function ApprovalPanel({ run, onApprove }: Props) {
  if (run.status !== "awaiting_approval" || !run.pending_action) {
    return null;
  }

  const action = run.pending_action;

  return (
    <section className="card approval">
      <h3>Approval required</h3>
      <p>
        The agent proposes <strong>{String(action.action)}</strong>. This is a high-risk
        production action and requires explicit operator approval.
      </p>

      <pre>{JSON.stringify(action, null, 2)}</pre>

      <div className="actions">
        <button className="primary" onClick={() => onApprove("approved")}>
          Approve remediation
        </button>
        <button onClick={() => onApprove("rejected")}>Reject</button>
      </div>
    </section>
  );
}
