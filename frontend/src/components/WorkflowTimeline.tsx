interface Props {
  status: string;
}

const STEPS = [
  { key: "triage", label: "Triage" },
  { key: "investigate", label: "Investigate" },
  { key: "diagnose", label: "Diagnose" },
  { key: "plan", label: "Plan remediation" },
  { key: "approval", label: "Approval" },
  { key: "execute", label: "Execute" },
  { key: "verify", label: "Verify recovery" },
];

function stepState(step: string, status: string): string {
  const order = ["created", "investigating", "awaiting_approval", "executing", "verifying", "completed", "escalated", "cancelled", "failed"];
  const currentIndex = order.indexOf(status);
  const stepIndex = STEPS.findIndex((item) => item.key === step);

  if (status === "awaiting_approval" && step === "approval") return "waiting";
  if (stepIndex < currentIndex) return "completed";
  if (stepIndex === currentIndex) return "running";
  return "pending";
}

export default function WorkflowTimeline({ status }: Props) {
  return (
    <div className="timeline">
      {STEPS.map((step) => (
        <div key={step.key} className={`timeline-step ${stepState(step.key, status)}`}>
          <span>{step.label}</span>
          <small>{stepState(step.key, status)}</small>
        </div>
      ))}
    </div>
  );
}
