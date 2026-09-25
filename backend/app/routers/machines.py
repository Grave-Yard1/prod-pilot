from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.deps import get_session
from app.models import IncidentRecord, MachineRecord
from app.serialize import load_incident, machine_detail, machine_summary

router = APIRouter()


@router.get("")
def list_machines(session: Session = Depends(get_session)) -> list[dict]:
    machines = session.scalars(
        select(MachineRecord).options(joinedload(MachineRecord.signals)).order_by(MachineRecord.code)
    ).unique().all()
    open_rows = session.scalars(select(IncidentRecord).where(IncidentRecord.status != "repaired")).all()
    open_by_machine: dict[int, list[int]] = {}
    for incident in open_rows:
        open_by_machine.setdefault(incident.machine_id, []).append(incident.number)
    return [machine_summary(machine, sorted(open_by_machine.get(machine.id, []))) for machine in machines]


@router.get("/{code}")
def get_machine(code: str, session: Session = Depends(get_session)) -> dict:
    machine = session.execute(
        select(MachineRecord)
        .where(MachineRecord.code == code.upper())
        .options(joinedload(MachineRecord.signals))
    ).unique().scalar_one_or_none()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    incidents = session.scalars(select(IncidentRecord).where(IncidentRecord.machine_id == machine.id)).all()
    return machine_detail(machine, list(incidents))
