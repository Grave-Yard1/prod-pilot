import json

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AIAnalysis, IncidentRecord, MachineRecord
from app.services.analysis import label_for
from app.services.recommendation import SAFETY_LINE


def iso(value) -> str:
    return value.isoformat()


def latest_analysis(incident: IncidentRecord) -> AIAnalysis | None:
    if not incident.analyses:
        return None
    return max(incident.analyses, key=lambda item: (item.created_at, item.id))


def signal_payload(signal) -> dict:
    return {
        "metric": signal.metric,
        "value": signal.value,
        "unit": signal.unit,
        "limit_value": signal.limit_value,
        "recorded_at": iso(signal.recorded_at),
    }


def latest_by_metric(machine: MachineRecord) -> list[dict]:
    chosen = {}
    for signal in sorted(machine.signals, key=lambda item: item.recorded_at):
        chosen[signal.metric] = signal
    return [signal_payload(signal) for signal in chosen.values()]


def series_by_metric(machine: MachineRecord) -> list[dict]:
    grouped: dict[str, list] = {}
    for signal in sorted(machine.signals, key=lambda item: item.recorded_at):
        grouped.setdefault(signal.metric, []).append(signal)
    series = []
    for metric, signals in grouped.items():
        series.append(
            {
                "metric": metric,
                "unit": signals[-1].unit,
                "limit_value": signals[-1].limit_value,
                "points": [signal.value for signal in signals],
                "recorded_at": [iso(signal.recorded_at) for signal in signals],
            }
        )
    return series


def machine_summary(machine: MachineRecord, open_numbers: list[int]) -> dict:
    return {
        "code": machine.code,
        "name": machine.name,
        "zone": machine.zone,
        "status": machine.status,
        "trade": machine.trade,
        "contact_name": machine.contact_name,
        "signals": latest_by_metric(machine),
        "open_incident_numbers": open_numbers,
    }


def machine_detail(machine: MachineRecord, incidents: list[IncidentRecord]) -> dict:
    open_numbers = [item.number for item in incidents if item.status != "repaired"]
    payload = machine_summary(machine, open_numbers)
    payload["series"] = series_by_metric(machine)
    payload["incidents"] = [
        {
            "number": item.number,
            "label": label_for(item.number),
            "symptom": item.symptom,
            "status": item.status,
            "created_at": iso(item.created_at),
        }
        for item in sorted(incidents, key=lambda row: row.number, reverse=True)
    ]
    return payload


def analysis_payload(analysis: AIAnalysis | None) -> dict | None:
    if analysis is None:
        return None
    evidence = json.loads(analysis.evidence_json)
    return {
        "id": analysis.id,
        "recommendation": analysis.recommendation,
        "similarity_points": analysis.similarity_points,
        "similarity_percent": analysis.similarity_points // 10,
        "matched_incident_number": analysis.matched_incident_number,
        "matched_label": label_for(analysis.matched_incident_number) if analysis.matched_incident_number else None,
        "evidence": evidence,
        "rationale": analysis.rationale,
        "model_id": analysis.model_id,
        "narrative_source": analysis.narrative_source,
        "safety_line": SAFETY_LINE,
        "created_at": iso(analysis.created_at),
    }


def incident_payload(incident: IncidentRecord) -> dict:
    analysis = latest_analysis(incident)
    return {
        "number": incident.number,
        "label": label_for(incident.number),
        "status": incident.status,
        "symptom": incident.symptom,
        "error_code": incident.error_code,
        "opened_by": incident.opened_by,
        "created_at": iso(incident.created_at),
        "machine": {
            "code": incident.machine.code,
            "name": incident.machine.name,
            "zone": incident.machine.zone,
            "status": incident.machine.status,
            "trade": incident.machine.trade,
            "contact_name": incident.machine.contact_name,
        },
        "observations": [
            {
                "id": item.id,
                "worker_name": item.worker_name,
                "note": item.note,
                "observed_at": iso(item.observed_at),
            }
            for item in sorted(incident.observations, key=lambda row: row.observed_at)
        ],
        "analysis": analysis_payload(analysis),
        "decision": None
        if incident.decision is None
        else {
            "id": incident.decision.id,
            "supervisor_name": incident.decision.supervisor_name,
            "action": incident.decision.action,
            "note": incident.decision.note,
            "decided_at": iso(incident.decision.decided_at),
        },
        "repair": None
        if incident.repair is None
        else {
            "id": incident.repair.id,
            "engineer_name": incident.repair.engineer_name,
            "diagnosis": incident.repair.diagnosis,
            "action": incident.repair.action,
            "downtime_minutes": incident.repair.downtime_minutes,
            "outcome": incident.repair.outcome,
            "repaired_at": iso(incident.repair.repaired_at),
        },
    }


def load_incident(session: Session, number: int) -> IncidentRecord | None:
    return session.execute(
        select(IncidentRecord)
        .where(IncidentRecord.number == number)
        .options(
            joinedload(IncidentRecord.machine),
            joinedload(IncidentRecord.observations),
            joinedload(IncidentRecord.analyses),
            joinedload(IncidentRecord.decision),
            joinedload(IncidentRecord.repair),
        )
    ).unique().scalar_one_or_none()
