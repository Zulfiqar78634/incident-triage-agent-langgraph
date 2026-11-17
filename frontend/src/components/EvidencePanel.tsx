import type { Evidence, ToolCall } from "../types/agent";

interface Props {
  evidence: Evidence[];
  toolCalls: ToolCall[];
}

export default function EvidencePanel({ evidence, toolCalls }: Props) {
  return (
    <div className="panel-grid">
      <section className="card">
        <h3>Evidence used</h3>
        {evidence.length === 0 && <p>No evidence collected yet.</p>}

        {evidence.map((item) => (
          <div key={item.id} className="evidence-item">
            <strong>{item.id} · {item.source}</strong>
            <pre>{item.content}</pre>
          </div>
        ))}
      </section>

      <section className="card">
        <h3>Tool calls</h3>
        {toolCalls.length === 0 && <p>No tools called yet.</p>}

        <table>
          <thead>
            <tr>
              <th>Tool</th>
              <th>Status</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody>
            {toolCalls.map((call) => (
              <tr key={call.call_id}>
                <td>{call.tool}</td>
                <td>{call.status}</td>
                <td>{call.latency_ms} ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
