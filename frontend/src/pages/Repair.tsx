import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api, useApi } from "../api";
import { Failure, Loading } from "../components/State";
import { formatWhen } from "../format";
import { usePersona } from "../persona";
import type { Incident } from "../types";

export function Repair() {
  const params = useParams();
  const number = params.number ?? "";
  const incident = useApi<Incident>(number ? `/api/incidents/${number}` : null);
  const persona = usePersona();
  const [engineer, setEngineer] = useState("");
  const [engineerEdited, setEngineerEdited] = useState(false);
  const [diagnosis, setDiagnosis] = useState("");
  const [action, setAction] = useState("");
  const [downtime, setDowntime] = useState("");
  const [outcome, setOutcome] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const engineerValue = engineerEdited
    ? engineer
    : persona.role === "engineer"
      ? persona.name
      : (incident.data?.machine.contact_name ?? "");

  if (incident.loading && !incident.data) {
    return (
      <div className="page">
        <Loading label="Opening the repair…" />
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

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      await api(`/api/incidents/${data.number}/repair`, {
        method: "POST",
        body: JSON.stringify({
          engineer_name: engineerValue.trim() || data.machine.contact_name,
          diagnosis: diagnosis.trim(),
          action: action.trim(),
          downtime_minutes: Number(downtime),
          outcome: outcome.trim(),
        }),
      });
      incident.reload();
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "The repair was not recorded");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <Link className="back" to={`/call/${data.number}`}>
        Back to the call
      </Link>
      <p className="kicker">{data.label}</p>
      <h1>Record the repair</h1>
      <p className="lede">
        {data.machine.code} · {data.machine.name}. This becomes the history the next walk can retrieve.
      </p>
      {!data.decision && (
        <p className="empty">
          A supervisor call has to be recorded first. <Link to={`/call/${data.number}`}>Open the call</Link>.
        </p>
      )}
      {data.repair ? (
        <section className="recorded" data-testid="repair-recorded">
          <h2>Closed into history</h2>
          <p>
            {data.repair.engineer_name} · {formatWhen(data.repair.repaired_at)}
          </p>
          <p>{data.repair.diagnosis}</p>
          <p>{data.repair.action}</p>
          <p>{data.repair.downtime_minutes} minutes</p>
          <p>{data.repair.outcome}</p>
        </section>
      ) : (
        data.decision && (
          <form className="sheet" onSubmit={submit}>
            <label htmlFor="engineer-name">Engineer</label>
            <input
              id="engineer-name"
              value={engineerValue}
              onChange={(event) => {
                setEngineerEdited(true);
                setEngineer(event.target.value);
              }}
            />
            <label htmlFor="diagnosis">Diagnosis</label>
            <input id="diagnosis" value={diagnosis} onChange={(event) => setDiagnosis(event.target.value)} required />
            <label htmlFor="action-taken">Action taken</label>
            <input id="action-taken" value={action} onChange={(event) => setAction(event.target.value)} required />
            <label htmlFor="downtime">Downtime (minutes)</label>
            <input
              id="downtime"
              type="number"
              min={0}
              value={downtime}
              onChange={(event) => setDowntime(event.target.value)}
              required
            />
            <label htmlFor="outcome">Outcome</label>
            <input
              id="outcome"
              value={outcome}
              onChange={(event) => setOutcome(event.target.value)}
              placeholder="Machine returned to normal"
              required
            />
            {formError && <Failure message={formError} />}
            <button type="submit" className="submit" data-testid="save-repair" disabled={saving}>
              {saving ? "Saving…" : "Save the repair"}
            </button>
          </form>
        )
      )}
    </div>
  );
}
