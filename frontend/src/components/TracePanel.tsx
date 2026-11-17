import type { AgentEvent } from "../types/agent";

interface Props {
  events: AgentEvent[];
}

export default function TracePanel({ events }: Props) {
  return (
    <section className="card">
      <h3>Agent decision trace</h3>
      {events.length === 0 && <p>No events recorded yet.</p>}

      <div className="trace">
        {events.map((event) => (
          <div key={`${event.sequence}-${event.created_at}`} className="event">
            <strong>{event.node} · {event.event}</strong>
            <div>{event.message}</div>
            <small>{event.created_at}</small>
          </div>
        ))}
      </div>
    </section>
  );
}
