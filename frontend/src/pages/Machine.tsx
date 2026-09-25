import { Link, useParams } from "react-router-dom";
import { useApi } from "../api";
import { Sparkline } from "../components/Sparkline";
import { Failure, Lamp, Loading } from "../components/State";
import { formatWhen, metricLabel, sentence, statusLabel } from "../format";
import type { MachineDetail } from "../types";

export function Machine() {
  const params = useParams();
  const code = params.code ?? "";
  const machine = useApi<MachineDetail>(code ? `/api/machines/${code}` : null);

  if (machine.loading) {
    return (
      <div className="page">
        <Loading />
      </div>
    );
  }
  if (machine.error || !machine.data) {
    return (
      <div className="page">
        <Failure message={machine.error ?? "Station not found"} />
      </div>
    );
  }

  const data = machine.data;
  return (
    <div className="page">
      <Link className="back" to="/floor">
        Back to the floor
      </Link>
      <article className="job dark-job">
        <p className="job-machine">
          <Lamp status={data.status} />
          <span>
            {data.code}
            <small>
              {data.name} · {data.zone}
            </small>
          </span>
        </p>
        <h1>{statusLabel(data.status)}</h1>
        <p className="who-name">{data.contact_name}</p>
        <p>{data.trade}</p>
        <div className="meters">
          {data.series.map((series) => {
            const latest = series.points[series.points.length - 1];
            return (
              <div key={series.metric} className="meter">
                <div className="meter-label">
                  <span>{metricLabel(series.metric)}</span>
                  <strong className={latest > series.limit_value ? "over" : ""}>
                    {latest} {series.unit}
                  </strong>
                  <span>limit {series.limit_value}</span>
                </div>
                <Sparkline points={series.points} limit={series.limit_value} />
              </div>
            );
          })}
        </div>
        <h2>Incidents on this station</h2>
        {data.incidents.length === 0 && <p className="empty">No incidents on this station.</p>}
        <ul className="history">
          {data.incidents.map((item) => (
            <li key={item.number}>
              <Link to={`/call/${item.number}`}>
                <strong>{item.label}</strong>
                <span>{sentence(item.symptom)}</span>
                <em>
                  {statusLabel(item.status)} · {formatWhen(item.created_at)}
                </em>
              </Link>
            </li>
          ))}
        </ul>
      </article>
    </div>
  );
}
