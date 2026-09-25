import { Link } from "react-router-dom";
import { useApi } from "../api";
import { Failure, Lamp, Loading } from "../components/State";
import { callWord, formatWhen, sentence, statusLabel } from "../format";
import type { Handoff as HandoffReport } from "../types";

export function Handoff() {
  const report = useApi<HandoffReport>("/api/handoff");

  return (
    <div className="page" data-testid="handoff">
      <p className="kicker">Handoff</p>
      <h1>For the next supervisor</h1>
      <p className="lede">What this shift decided, what got closed into history, and what is still carrying.</p>
      {report.loading && <Loading label="Gathering the shift…" />}
      {report.error && <Failure message={report.error} />}
      {report.data && (
        <>
          <p className="shift-meta">
            {report.data.shift_label} · {formatWhen(report.data.generated_at)}
          </p>
          <section className="section">
            <h2>Still waiting</h2>
            {report.data.waiting.length === 0 && <p className="empty">No open call is waiting.</p>}
            <ul className="handoff-list">
              {report.data.waiting.map((item) => (
                <li key={item.number}>
                  <Link to={`/call/${item.number}`}>
                    <strong>
                      {item.label} · {item.machine_code}
                    </strong>
                    <span>{sentence(item.symptom)}</span>
                    {item.recommendation && (
                      <em>
                        Suggested {callWord(item.recommendation)}
                        {item.similarity_percent !== null ? ` · ${item.similarity_percent}%` : ""}
                      </em>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
          <section className="section">
            <h2>Calls this shift</h2>
            {report.data.decisions.length === 0 && <p className="empty">No call has been recorded this shift.</p>}
            <ul className="handoff-list">
              {report.data.decisions.map((item) => (
                <li key={item.incident_number}>
                  <Link to={`/call/${item.incident_number}`}>
                    <strong>
                      {item.label} · {item.machine_code} · {callWord(item.action)}
                    </strong>
                    <span>
                      {item.supervisor_name} · {formatWhen(item.decided_at)}
                    </span>
                    {item.note && <em>{item.note}</em>}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
          <section className="section">
            <h2>Closed into history</h2>
            {report.data.repairs.length === 0 && <p className="empty">Nothing has been closed into history this shift.</p>}
            <ul className="handoff-list">
              {report.data.repairs.map((item) => (
                <li key={item.incident_number}>
                  <Link to={`/call/${item.incident_number}`}>
                    <strong>
                      {item.label} · {item.machine_code} · {item.action}
                    </strong>
                    <span>
                      {item.engineer_name} · {item.downtime_minutes} minutes
                    </span>
                    <em>{item.outcome}</em>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
          <section className="section">
            <h2>Still carrying</h2>
            {report.data.carry.length === 0 && <p className="empty">No station is left in watch or alarm.</p>}
            <ul className="glance">
              {report.data.carry.map((machine) => (
                <li key={machine.code}>
                  <Link to={`/machine/${machine.code}`}>
                    <Lamp status={machine.status} />
                    <span>
                      <strong>{machine.code}</strong> {machine.name}
                    </span>
                    <em>
                      {statusLabel(machine.status)} · {machine.zone}
                    </em>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}
