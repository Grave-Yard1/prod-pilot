import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, useApi } from "../api";
import { Sparkline } from "../components/Sparkline";
import { Failure, Lamp, Loading } from "../components/State";
import {
  PART_ORDER,
  callDetail,
  callWord,
  formatWhen,
  metricLabel,
  partLabel,
  pointsLabel,
  sentence,
  statusLabel,
} from "../format";
import { usePersona } from "../persona";
import type { CallAction, Incident, MachineDetail } from "../types";

export function Call() {
  const params = useParams();
  const number = params.number ?? "";
  const incident = useApi<Incident>(number ? `/api/incidents/${number}` : null);
  const machineCode = incident.data?.machine.code ?? null;
  const machine = useApi<MachineDetail>(machineCode ? `/api/machines/${machineCode}` : null);
  const persona = usePersona();
  const [note, setNote] = useState("");
  const [supervisor, setSupervisor] = useState(persona.role === "supervisor" ? persona.name : "Alex Novak");
  const [stopArmed, setStopArmed] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  if (incident.loading) {
    return (
      <div className="page">
        <Loading label="Opening the call…" />
      </div>
    );
  }
  if (incident.error || !incident.data) {
    return (
      <div className="page">
        <Failure message={incident.error ?? "Incident not found"} />
      </div>
    );
  }

  const data = incident.data;
  const analysis = data.analysis;
  const evidence = analysis?.evidence[0];
  const recommendation = analysis?.recommendation ?? "continue";

  async function choose(action: CallAction) {
    if (action === "stop" && !stopArmed) {
      setStopArmed(true);
      return;
    }
    setStopArmed(false);
    setSaving(true);
    setFormError(null);
    try {
      await api(`/api/incidents/${data.number}/decision`, {
        method: "POST",
        body: JSON.stringify({ supervisor_name: supervisor.trim() || "Alex Novak", action, note }),
      });
      incident.reload();
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "The call was not recorded");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <Link className="back" to="/">
        Back to the walk
      </Link>
      <article className="job">
        <header className="job-head">
          <p className="job-id">{data.label}</p>
          <p className="job-machine">
            <Lamp status={data.machine.status} />
            <span>
              {data.machine.code}
              <small>
                {data.machine.name} · {data.machine.zone}
              </small>
            </span>
          </p>
          <p className="job-status">{statusLabel(data.machine.status)}</p>
        </header>

        <h1>{sentence(data.symptom)}</h1>
        {data.observations.map((item) => (
          <blockquote key={item.id} className="quote">
            <p>“{sentence(item.note)}”</p>
            <footer>
              {item.worker_name} · {formatWhen(item.observed_at)}
            </footer>
          </blockquote>
        ))}
        <p className="code-line">
          Error code <strong>{data.error_code ?? "none yet"}</strong>
        </p>

        {analysis && (
          <section className={`stamp-block ${recommendation}`}>
            <p className="stamp-kicker">Suggested call</p>
            <p className={`stamp ${recommendation}`} data-testid="recommendation">
              {callWord(recommendation)}
            </p>
            <p>{callDetail(recommendation)}</p>
            <p className="match-line">
              <span data-testid="similarity">{analysis.similarity_percent}%</span>
              {analysis.matched_label ? ` like incident ${analysis.matched_label}` : " · no closed match"}
            </p>
          </section>
        )}

        {evidence && (
          <section className="evidence">
            <h2>Last time this looked like this</h2>
            <p className="evidence-title">
              <Link to={`/call/${evidence.incident_number}`}>{evidence.label}</Link>
              <span>{evidence.similarity_percent}%</span>
            </p>
            <dl className="facts">
              <div>
                <dt>Diagnosis</dt>
                <dd>{evidence.diagnosis}</dd>
              </div>
              <div>
                <dt>What fixed it</dt>
                <dd data-testid="prior-action">{evidence.action}</dd>
              </div>
              <div>
                <dt>Downtime</dt>
                <dd>{evidence.downtime_minutes} minutes</dd>
              </div>
              <div>
                <dt>Outcome</dt>
                <dd>{evidence.outcome}</dd>
              </div>
              <div>
                <dt>Recorded by</dt>
                <dd>{evidence.engineer_name}</dd>
              </div>
              <div>
                <dt>Error on that case</dt>
                <dd>{evidence.error_code ?? "None"}</dd>
              </div>
            </dl>
            <blockquote className="quote quiet">
              <p>“{sentence(evidence.observation)}”</p>
            </blockquote>
            <h3>Why {analysis?.similarity_percent}%</h3>
            <ul className="parts">
              {PART_ORDER.map((key) => (
                <li key={key}>
                  <span>{partLabel(key, evidence.shared_families)}</span>
                  <strong>{pointsLabel(evidence.parts[key] ?? 0)}</strong>
                </li>
              ))}
            </ul>
            <p className="parts-note">Matched against closed repairs. The number is the sum of those parts.</p>
          </section>
        )}

        <section className="who">
          <h2>Who to reach</h2>
          <p className="who-name">{data.machine.contact_name}</p>
          <p>{data.machine.trade}</p>
        </section>

        {machine.data && (
          <section className="meters">
            <h2>What the station is showing</h2>
            {machine.data.series.map((series) => {
              const latest = series.points[series.points.length - 1];
              const over = latest > series.limit_value;
              return (
                <div key={series.metric} className="meter">
                  <div className="meter-label">
                    <span>{metricLabel(series.metric)}</span>
                    <strong className={over ? "over" : ""}>
                      {latest} {series.unit}
                    </strong>
                    <span>limit {series.limit_value}</span>
                  </div>
                  <Sparkline points={series.points} limit={series.limit_value} />
                </div>
              );
            })}
          </section>
        )}

        {analysis && <p className="rationale">{analysis.rationale}</p>}

        {data.decision ? (
          <section className="recorded" data-testid="decision-recorded">
            <h2>You called {callWord(data.decision.action)}</h2>
            <p>
              {data.decision.supervisor_name} · {formatWhen(data.decision.decided_at)}
            </p>
            {data.decision.note && <p className="note-copy">{data.decision.note}</p>}
            <p>The line was not changed by this app.</p>
          </section>
        ) : (
          <section className="decide">
            <h2>Your call</h2>
            <label htmlFor="supervisor-name">Supervisor</label>
            <input id="supervisor-name" value={supervisor} onChange={(event) => setSupervisor(event.target.value)} />
            <label htmlFor="shift-note">Note for the next shift</label>
            <textarea
              id="shift-note"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="What you saw, and who you told"
            />
            {formError && <Failure message={formError} />}
            <div className="calls">
              <button type="button" className="call continue" data-testid="decide-continue" disabled={saving} onClick={() => choose("continue")}>
                <span>Continue</span>
                <small>Keep the station running</small>
                {recommendation === "continue" && <em>Suggested</em>}
              </button>
              <button type="button" className="call slow" data-testid="decide-slow" disabled={saving} onClick={() => choose("slow")}>
                <span>Slow the station</span>
                <small>Hold it and call the trade</small>
                {recommendation === "slow" && <em>Suggested</em>}
              </button>
              <button type="button" className="call stop" data-testid="decide-stop" disabled={saving} onClick={() => choose("stop")}>
                <span>{stopArmed ? "Confirm stop" : "Stop the station"}</span>
                <small>{stopArmed ? "Tap again to record the stop" : "Stop the station"}</small>
                {recommendation === "stop" && <em>Suggested</em>}
              </button>
            </div>
            <p className="decide-note">Recording a call does not change the line.</p>
          </section>
        )}

        {data.repair ? (
          <section className="recorded" data-testid="repair-recorded">
            <h2>Closed into history</h2>
            <p>
              {data.repair.engineer_name} · {formatWhen(data.repair.repaired_at)}
            </p>
            <p>
              {data.repair.diagnosis}. {data.repair.action}. {data.repair.downtime_minutes} minutes. {data.repair.outcome}.
            </p>
          </section>
        ) : (
          data.decision && (
            <Link className="text-action" data-testid="record-repair" to={`/repair/${data.number}`}>
              Record the repair
            </Link>
          )
        )}
      </article>
    </div>
  );
}
