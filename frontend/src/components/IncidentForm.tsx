import { useState } from "react";
import type { IncidentInput } from "../types/agent";

interface Props {
  onStart: (incident: IncidentInput) => void;
}

const SAMPLE: IncidentInput = {
  title: "Checkout service 5xx spike",
  description:
    "Checkout is returning 5xx errors after the latest deployment. Database connections appear saturated.",
  service: "checkout-service",
  environment: "production",
  severity: "high",
  operator_id: "web-operator",
};

export default function IncidentForm({ onStart }: Props) {
  const [incident, setIncident] = useState<IncidentInput>(SAMPLE);

  return (
    <section className="card">
      <h2>Report an incident</h2>
      <p>Start an agent run to investigate and propose safe remediation.</p>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          onStart(incident);
        }}
      >
        <label>
          Title
          <input
            value={incident.title}
            onChange={(event) => setIncident({ ...incident, title: event.target.value })}
            required
          />
        </label>

        <label>
          Description
          <textarea
            value={incident.description}
            onChange={(event) => setIncident({ ...incident, description: event.target.value })}
            required
          />
        </label>

        <div className="grid">
          <label>
            Service
            <input
              value={incident.service}
              onChange={(event) => setIncident({ ...incident, service: event.target.value })}
            />
          </label>

          <label>
            Environment
            <select
              value={incident.environment}
              onChange={(event) => setIncident({ ...incident, environment: event.target.value })}
            >
              <option value="production">production</option>
              <option value="staging">staging</option>
              <option value="development">development</option>
            </select>
          </label>

          <label>
            Severity
            <select
              value={incident.severity}
              onChange={(event) => setIncident({ ...incident, severity: event.target.value })}
            >
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
              <option value="critical">critical</option>
            </select>
          </label>
        </div>

        <div className="actions">
          <button type="button" onClick={() => setIncident(SAMPLE)}>
            Load sample incident
          </button>
          <button type="submit" className="primary">
            Start agent run
          </button>
        </div>
      </form>
    </section>
  );
}
