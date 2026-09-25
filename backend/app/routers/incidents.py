from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.clock import utcnow
from app.deps import get_session
from app.models import EngineerRepair, IncidentRecord, MachineRecord, SupervisorDecision, WorkerObservation
from app.schemas import DecisionCreate, IncidentCreate, RepairCreate
from app.serialize import incident_payload, load_incident
from app.services.analysis import create_analysis
from app.services.recommendation import repair_successful

router = APIRouter()


def _require(session: Session, number: int) -> IncidentRecord:
    incident = load_incident(session, number)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("")
def list_incidents(status: str | None = None, session: Session = Depends(get_session)) -> list[dict]:
    statement = (
        select(IncidentRecord)
        .options(
            joinedload(IncidentRecord.machine),
            joinedload(IncidentRecord.observations),
            joinedload(IncidentRecord.analyses),
            joinedload(IncidentRecord.decision),
            joinedload(IncidentRecord.repair),
        )
        .order_by(IncidentRecord.number.desc())
    )
    if status:
        statement = statement.where(IncidentRecord.status == status)
    rows = session.execute(statement).unique().scalars().all()
    return [incident_payload(row) for row in rows]


@router.get("/{number}")
def get_incident(number: int, session: Session = Depends(get_session)) -> dict:
    return incident_payload(_require(session, number))


@router.post("", status_code=201)
def create_incident(body: IncidentCreate, session: Session = Depends(get_session)) -> dict:
    machine = session.scalar(select(MachineRecord).where(MachineRecord.code == body.machine_code.strip().upper()))
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    error_code = (body.error_code or "").strip().upper() or None
    number = (session.scalar(select(func.max(IncidentRecord.number))) or 0) + 1
    now = utcnow()
    incident = IncidentRecord(
        number=number,
        machine_id=machine.id,
        symptom=body.symptom.strip(),
        error_code=error_code,
        status="open",
        opened_by=body.worker_name.strip(),
        created_at=now,
    )
    session.add(incident)
    session.flush()
    session.add(
        WorkerObservation(
            incident_id=incident.id,
            worker_name=body.worker_name.strip(),
            note=body.observation.strip(),
            observed_at=now,
        )
    )
    if machine.status != "down":
        machine.status = "alarm"
    incident.machine = machine
    session.flush()
    create_analysis(session, incident)
    session.commit()
    session.expire_all()
    return incident_payload(_require(session, number))


@router.post("/{number}/decision")
def record_decision(number: int, body: DecisionCreate, session: Session = Depends(get_session)) -> dict:
    incident = _require(session, number)
    if incident.decision is not None:
        raise HTTPException(status_code=409, detail="A supervisor decision is already recorded")
    if incident.status == "repaired":
        raise HTTPException(status_code=409, detail="This incident is already closed")
    # The decision is its own record. It must not write machine status or the analysis.
    session.add(
        SupervisorDecision(
            incident_id=incident.id,
            supervisor_name=body.supervisor_name.strip(),
            action=body.action,
            note=body.note.strip(),
            decided_at=utcnow(),
        )
    )
    incident.status = "decided"
    session.commit()
    session.expire_all()
    return incident_payload(_require(session, number))


@router.post("/{number}/repair")
def record_repair(number: int, body: RepairCreate, session: Session = Depends(get_session)) -> dict:
    incident = _require(session, number)
    if incident.decision is None:
        raise HTTPException(status_code=409, detail="A supervisor decision is required before a repair is recorded")
    if incident.repair is not None:
        raise HTTPException(status_code=409, detail="A repair is already recorded")
    session.add(
        EngineerRepair(
            incident_id=incident.id,
            engineer_name=body.engineer_name.strip(),
            diagnosis=body.diagnosis.strip(),
            action=body.action.strip(),
            downtime_minutes=body.downtime_minutes,
            outcome=body.outcome.strip(),
            repaired_at=utcnow(),
        )
    )
    incident.status = "repaired"
    # The engineer's recorded outcome is what updates the machine, not the earlier call.
    incident.machine.status = "running" if repair_successful(body.outcome) else "watch"
    session.commit()
    session.expire_all()
    return incident_payload(_require(session, number))


@router.post("/{number}/analyze")
def analyze_again(number: int, session: Session = Depends(get_session)) -> dict:
    incident = _require(session, number)
    create_analysis(session, incident)
    session.commit()
    session.expire_all()
    return incident_payload(_require(session, number))
