import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, useApi } from "../api";
import { Failure, Loading } from "../components/State";
import { ZONES } from "../format";
import { usePersona } from "../persona";
import type { Incident, MachineSummary } from "../types";

const SYMPTOMS = [
  "abnormal vibration",
  "unusual noise",
  "coolant leak",
  "torque fault",
  "guard open",
  "overheating",
];

export function Report() {
  const machines = useApi<MachineSummary[]>("/api/machines");
  const persona = usePersona();
  const navigate = useNavigate();
  const [machineCode, setMachineCode] = useState("M-17");
  const [symptom, setSymptom] = useState("");
  const [observation, setObservation] = useState("");
  const [errorCode, setErrorCode] = useState("");
  const [worker, setWorker] = useState(persona.role === "worker" ? persona.name : "Sam Keller");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!symptom.trim() || !observation.trim()) {
      setFormError("A symptom and what you saw are both required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      const created = await api<Incident>("/api/incidents", {
        method: "POST",
        body: JSON.stringify({
          machine_code: machineCode,
          symptom: symptom.trim(),
          observation: observation.trim(),
          error_code: errorCode.trim() || null,
          worker_name: worker.trim() || "Sam Keller",
        }),
      });
      navigate(`/call/${created.number}`);
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "The incident was not created");
      setSaving(false);
    }
  }

  const rows = machines.data ?? [];

  return (
    <div className="page">
      <p className="kicker">Report</p>
      <h1>Something is off</h1>
      <p className="lede">Say what you saw. The match against closed repairs comes back on the next screen.</p>
      {machines.loading && <Loading />}
      {machines.error && <Failure message={machines.error} />}
      <form className="sheet" onSubmit={submit}>
        <label htmlFor="machine">Machine</label>
        <select id="machine" value={machineCode} onChange={(event) => setMachineCode(event.target.value)}>
          {ZONES.map((zone) => {
            const group = rows.filter((machine) => machine.zone === zone);
            if (!group.length) return null;
            return (
              <optgroup key={zone} label={zone}>
                {group.map((machine) => (
                  <option key={machine.code} value={machine.code}>
                    {machine.code} · {machine.name}
                  </option>
                ))}
              </optgroup>
            );
          })}
        </select>
        <fieldset>
          <legend>Symptom</legend>
          <div className="chips">
            {SYMPTOMS.map((item) => (
              <button
                key={item}
                type="button"
                className={symptom === item ? "chip active" : "chip"}
                aria-pressed={symptom === item}
                onClick={() => setSymptom(item)}
              >
                {item.charAt(0).toUpperCase() + item.slice(1)}
              </button>
            ))}
          </div>
          <label htmlFor="symptom" className="sr">
            Symptom
          </label>
          <input id="symptom" value={symptom} onChange={(event) => setSymptom(event.target.value)} />
        </fieldset>
        <label htmlFor="observation">What did you see or hear?</label>
        <textarea
          id="observation"
          value={observation}
          onChange={(event) => setObservation(event.target.value)}
          placeholder="Where it started, and how long ago"
        />
        <label htmlFor="error-code">Error code</label>
        <input
          id="error-code"
          value={errorCode}
          onChange={(event) => setErrorCode(event.target.value)}
          placeholder="Optional"
        />
        <label htmlFor="worker-name">Worker</label>
        <input id="worker-name" value={worker} onChange={(event) => setWorker(event.target.value)} />
        {formError && <Failure message={formError} />}
        <button type="submit" className="submit" data-testid="create-incident" disabled={saving}>
          {saving ? "Creating the incident…" : "Create the incident"}
        </button>
      </form>
    </div>
  );
}
