from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.clock import utcnow
from app.deps import get_session
from app.models import EngineerRepair, IncidentRecord, MachineRecord, SupervisorDecision
from app.serialize import iso, latest_analysis
from app.services.analysis import label_for
from app.services.recommendation import SAFETY_LINE

router = APIRouter()

SHIFT = timedelta(hours=12)


@router.get("")
def handoff(session: Session = Depends(get_session)) -> dict:
    now = utcnow()
    cutoff = now - SHIFT
    waiting = session.execute(
        select(IncidentRecord)
        .where(IncidentRecord.status == "open")
        .options(
            joinedload(IncidentRecord.machine),
            joinedload(IncidentRecord.analyses),
        )
        .order_by(IncidentRecord.number.desc())
    ).unique().scalars().all()
    decisions = session.execute(
        select(SupervisorDecision)
        .where(SupervisorDecision.decided_at >= cutoff)
        .options(joinedload(SupervisorDecision.incident).joinedload(IncidentRecord.machine))
        .order_by(SupervisorDecision.decided_at.desc())
    ).unique().scalars().all()
    repairs = session.execute(
        select(EngineerRepair)
        .where(EngineerRepair.repaired_at >= cutoff)
        .options(joinedload(EngineerRepair.incident).joinedload(IncidentRecord.machine))
        .order_by(EngineerRepair.repaired_at.desc())
    ).unique().scalars().all()
    carry = session.scalars(
        select(MachineRecord).where(MachineRecord.status.in_(("alarm", "watch"))).order_by(MachineRecord.code)
    ).all()

    waiting_payload = []
    for incident in waiting:
        analysis = latest_analysis(incident)
        waiting_payload.append(
            {
                "number": incident.number,
                "label": label_for(incident.number),
                "machine_code": incident.machine.code,
                "machine_name": incident.machine.name,
                "symptom": incident.symptom,
                "recommendation": analysis.recommendation if analysis else None,
                "similarity_percent": (analysis.similarity_points // 10) if analysis else None,
            }
        )

    return {
        "shift_label": "Shift A",
        "dataset": "berlin-style-simulated",
        "generated_at": iso(now),
        "safety_line": SAFETY_LINE,
        "waiting": waiting_payload,
        "decisions": [
            {
                "incident_number": item.incident.number,
                "label": label_for(item.incident.number),
                "machine_code": item.incident.machine.code,
                "machine_name": item.incident.machine.name,
                "symptom": item.incident.symptom,
                "action": item.action,
                "note": item.note,
                "supervisor_name": item.supervisor_name,
                "decided_at": iso(item.decided_at),
            }
            for item in decisions
        ],
        "repairs": [
            {
                "incident_number": item.incident.number,
                "label": label_for(item.incident.number),
                "machine_code": item.incident.machine.code,
                "machine_name": item.incident.machine.name,
                "diagnosis": item.diagnosis,
                "action": item.action,
                "downtime_minutes": item.downtime_minutes,
                "outcome": item.outcome,
                "engineer_name": item.engineer_name,
                "repaired_at": iso(item.repaired_at),
            }
            for item in repairs
        ],
        "carry": [
            {"code": machine.code, "name": machine.name, "zone": machine.zone, "status": machine.status}
            for machine in carry
        ],
    }
