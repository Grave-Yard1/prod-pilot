import { Link } from "react-router-dom";
import { useApi } from "../api";
import { Failure, Lamp, Loading } from "../components/State";
import { ZONES, metricLabel, statusLabel } from "../format";
import type { MachineSummary } from "../types";

export function Floor() {
  const machines = useApi<MachineSummary[]>("/api/machines");
  const rows = machines.data ?? [];

  return (
    <div className="page">
      <p className="kicker">Floor</p>
      <h1>Stations</h1>
      <p className="lede">A standing view of the line. Tap a plate for the trace and the history.</p>
      {machines.loading && <Loading />}
      {machines.error && <Failure message={machines.error} />}
      {ZONES.map((zone) => {
        const group = rows.filter((machine) => machine.zone === zone);
        if (!group.length) return null;
        return (
          <section key={zone} className="section">
            <h2>{zone}</h2>
            <div className="tiles">
              {group.map((machine) => {
                const hot = machine.signals.find((signal) => signal.value > signal.limit_value) ?? machine.signals[0];
                return (
                  <Link key={machine.code} to={`/machine/${machine.code}`} className={`tile ${machine.status}`}>
                    <span className="tile-top">
                      <Lamp status={machine.status} />
                      <strong>{machine.code}</strong>
                      <em>{statusLabel(machine.status)}</em>
                    </span>
                    <span className="tile-name">{machine.name}</span>
                    {hot && (
                      <span className={hot.value > hot.limit_value ? "tile-signal over" : "tile-signal"}>
                        {metricLabel(hot.metric)} {hot.value} {hot.unit}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
