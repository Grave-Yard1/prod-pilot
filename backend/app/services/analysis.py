"""Build one AIAnalysis row from retrieved repairs.

This service inserts an analysis row only. It does not update the machine,
the worker observation, the supervisor decision, or the engineer repair.
"""

import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.clock import utcnow
from app.models import AIAnalysis, EngineerRepair, IncidentRecord
from app.services.llm import narrate
from app.services.recommendation import SAFETY_LINE, is_safety, recommend, repair_successful
from app.services.retrieval import Comparison, IncidentFeatures, compare


@dataclass
class RankedRepair:
    points: int
    incident: IncidentRecord
    repair: EngineerRepair
    comparison: Comparison


def observation_text(incident: IncidentRecord) -> str:
    notes = sorted(incident.observations, key=lambda item: (item.observed_at, item.id))
    return " ".join(item.note for item in notes)


def features_of(incident: IncidentRecord) -> IncidentFeatures:
    return IncidentFeatures(
        machine_code=incident.machine.code,
        symptom=incident.symptom,
        observation=observation_text(incident),
        error_code=incident.error_code,
    )


def label_for(number: int) -> str:
    return f"#{number:03d}"


def deterministic_brief(incident: IncidentRecord, top: dict | None, action: str) -> str:
    machine = incident.machine
    current = label_for(incident.number)
    if top is None:
        lead = f"No closed history to compare with {current} on {machine.code}."
    else:
        lead = (
            f"{current} on {machine.code} ({machine.name}) matches {top['label']} at {top['similarity_percent']}%. "
            f"That case was {top['diagnosis']}. "
            f"The recorded action was {top['action']}, with {top['downtime_minutes']} minutes of downtime, "
            f"and the outcome was {top['outcome']}."
        )
    return (
        f"{lead} Suggested call: {action}. "
        f"Reach {machine.contact_name}, {machine.trade}. {SAFETY_LINE}"
    )


def _evidence(item: RankedRepair) -> dict:
    past = item.incident
    repair = item.repair
    return {
        "incident_number": past.number,
        "label": label_for(past.number),
        "similarity_points": item.points,
        "similarity_percent": item.points // 10,
        "machine_code": past.machine.code,
        "symptom": past.symptom,
        "observation": observation_text(past),
        "error_code": past.error_code,
        "diagnosis": repair.diagnosis,
        "action": repair.action,
        "downtime_minutes": repair.downtime_minutes,
        "outcome": repair.outcome,
        "engineer_name": repair.engineer_name,
        "parts": item.comparison.parts,
        "shared_families": list(item.comparison.shared_families),
    }


def create_analysis(session: Session, incident: IncidentRecord) -> AIAnalysis:
    history = session.scalars(
        select(IncidentRecord)
        .join(EngineerRepair)
        .options(
            joinedload(IncidentRecord.machine),
            joinedload(IncidentRecord.observations),
            joinedload(IncidentRecord.repair),
        )
    ).unique().all()

    current = features_of(incident)
    ranked: list[RankedRepair] = []
    for past in history:
        if past.id == incident.id or past.repair is None:
            continue
        comparison = compare(current, features_of(past))
        ranked.append(RankedRepair(comparison.points, past, past.repair, comparison))
    ranked.sort(key=lambda item: item.points, reverse=True)

    evidence = [_evidence(item) for item in ranked[:3]]
    top = evidence[0] if evidence else None
    note = observation_text(incident)
    action = recommend(
        top_score=(top["similarity_points"] / 1000) if top else None,
        top_successful=bool(top and repair_successful(top["outcome"])),
        safety=is_safety(incident.error_code, incident.symptom, note),
    )
    rationale = deterministic_brief(incident, top, action)
    model_id = "local-retriever"
    narrative_source = "deterministic"

    narrated = narrate(
        {
            "incident": label_for(incident.number),
            "machine": incident.machine.code,
            "symptom": incident.symptom,
            "observation": note,
            "error_code": incident.error_code,
            "recommendation": action,
            "evidence": evidence,
        }
    )
    if narrated is not None:
        prose, model_id = narrated
        rationale = prose if SAFETY_LINE in prose else f"{prose} {SAFETY_LINE}"
        narrative_source = "llm"

    row = AIAnalysis(
        incident_id=incident.id,
        recommendation=action,
        similarity_points=top["similarity_points"] if top else 0,
        matched_incident_number=top["incident_number"] if top else None,
        evidence_json=json.dumps(evidence),
        rationale=rationale,
        model_id=model_id,
        narrative_source=narrative_source,
        created_at=utcnow(),
    )
    session.add(row)
    return row
