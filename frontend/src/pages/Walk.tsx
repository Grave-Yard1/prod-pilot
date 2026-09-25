import { Link } from "react-router-dom";
import { useApi } from "../api";
import { Failure, Lamp, Loading } from "../components/State";
import { callWord, sentence } from "../format";
import type { Incident, MachineSummary } from "../types";

export function Walk() {
  const incidents = useApi<Incident[]>("/api/incidents?status=open");
  const machines = useApi<MachineSummary[]>("/api/machines");
  const open = incidents.data ?? [];
  const openCodes = new Set(open.map((item) => item.machine.code));
  const glance = (machines.data ?? []).filter(
    (machine) => (machine.status === "alarm" || machine.status === "watch") && !openCodes.has(machine.code),
  );

  return (
    <div className="page">
      <p className="kicker">Walk</p>
      <h1>On the floor</h1>
      <p className="lede">What needs a call before you move on.</p>
      {incidents.loading && <Loading />}
      {incidents.error && <Failure message={incidents.error} />}
      {!incidents.loading && open.length === 0 && (
        <p className="empty">Nothing is waiting. Glance at the stations below and keep walking.</p>
      )}
      <div className="stack">
        {open.map((incident) => {
          const analysis = incident.analysis;
          return (
            <Link
              key={incident.number}
              to={`/call/${incident.number}`}
              className="call-plate"
              data-testid={`open-call-${incident.number}`}
            >
              <span className="plate-top">
                <Lamp status={incident.machine.status} />
                <span>
                  {incident.machine.code} · {incident.machine.name}
                </span>
                <span className="plate-id">{incident.label}</span>
              </span>
              <strong className="plate-title">{sentence(incident.symptom)}</strong>
              <span className="plate-meta">
                {incident.observations[0]?.note ? `“${sentence(incident.observations[0].note)}”` : "No note yet"}
                {analysis
                  ? ` · ${analysis.similarity_percent}% like ${analysis.matched_label} · Suggested ${callWord(analysis.recommendation)}`
                  : ""}
              </span>
            </Link>
          );
        })}
      </div>
      <section className="section">
        <h2>Glance at these</h2>
        {machines.loading && <Loading label="Checking stations…" />}
        {machines.error && <Failure message={machines.error} />}
        {!machines.loading && glance.length === 0 && <p className="empty">No other station is in watch or alarm.</p>}
        <ul className="glance">
          {glance.map((machine) => (
            <li key={machine.code}>
              <Link to={`/machine/${machine.code}`}>
                <Lamp status={machine.status} />
                <span>
                  <strong>{machine.code}</strong> {machine.name}
                </span>
                <em>{machine.zone}</em>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
