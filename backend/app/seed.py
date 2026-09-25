"""Berlin-style simulated production data. Fictional people, machines, and shifts."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.cases import INCIDENT_001, INCIDENT_007, INCIDENT_014
from app.clock import utcnow
from app.models import EngineerRepair, IncidentRecord, MachineRecord, MachineSignal, SupervisorDecision, WorkerObservation
from app.services.analysis import create_analysis
from app.services.retrieval import IncidentFeatures

INCIDENT_003 = IncidentFeatures(
    machine_code="M-44",
    symptom="guard open",
    observation="light curtain broken during the weld",
    error_code="E900",
)

INCIDENT_009 = IncidentFeatures(
    machine_code="M-31",
    symptom="torque fault",
    observation="rundown stopped short of angle",
    error_code="E552",
)

MACHINES = [
    {
        "code": "M-17",
        "name": "Drive unit spindle",
        "zone": "Drive Unit",
        "status": "alarm",
        "trade": "Drive unit maintenance",
        "contact_name": "Lea Hoffmann",
        "vibration": [2.1, 2.4, 2.9, 3.6, 4.4, 5.2, 6.3, 7.4],
        "vibration_limit": 4.5,
        "temperature": [58, 59, 59, 60, 60, 61, 61, 61],
        "temperature_limit": 75,
    },
    {
        "code": "M-19",
        "name": "Rotor press",
        "zone": "Drive Unit",
        "status": "watch",
        "trade": "Drive unit maintenance",
        "contact_name": "Lea Hoffmann",
        "vibration": [2.8, 3.1, 3.4, 3.6, 3.9, 4.1],
        "vibration_limit": 4.5,
        "temperature": [55, 56, 57, 57, 58, 58],
        "temperature_limit": 75,
    },
    {
        "code": "M-12",
        "name": "Framing robot",
        "zone": "Body",
        "status": "running",
        "trade": "Body maintenance",
        "contact_name": "Jonas Weber",
        "vibration": [1.1, 1.2, 1.1, 1.3, 1.2, 1.2],
        "vibration_limit": 4.5,
        "temperature": [40, 41, 41, 42, 42, 42],
        "temperature_limit": 70,
    },
    {
        "code": "M-44",
        "name": "Weld cell",
        "zone": "Body",
        "status": "running",
        "trade": "Body maintenance",
        "contact_name": "Jonas Weber",
        "vibration": [1.4, 1.5, 1.4, 1.6, 1.5, 1.5],
        "vibration_limit": 4.5,
        "temperature": [46, 47, 48, 48, 49, 48],
        "temperature_limit": 80,
    },
    {
        "code": "M-22",
        "name": "Paint circulation",
        "zone": "Paint",
        "status": "watch",
        "trade": "Paint maintenance",
        "contact_name": "Mara Vogel",
        "vibration": [0.8, 0.8, 0.9, 0.9, 0.8, 0.9],
        "vibration_limit": 3.0,
        "temperature": [66, 67, 68, 69, 70, 71],
        "temperature_limit": 70,
    },
    {
        "code": "M-08",
        "name": "Paint oven",
        "zone": "Paint",
        "status": "running",
        "trade": "Paint maintenance",
        "contact_name": "Mara Vogel",
        "vibration": [0.6, 0.6, 0.7, 0.6, 0.6, 0.6],
        "vibration_limit": 3.0,
        "temperature": [180, 182, 181, 183, 182, 182],
        "temperature_limit": 190,
    },
    {
        "code": "M-31",
        "name": "Torque spindle",
        "zone": "General Assembly",
        "status": "running",
        "trade": "Fastening maintenance",
        "contact_name": "Erik Lang",
        "vibration": [1.0, 1.1, 1.0, 1.2, 1.1, 1.1],
        "vibration_limit": 4.0,
        "temperature": [36, 37, 37, 38, 38, 38],
        "temperature_limit": 60,
    },
    {
        "code": "M-52",
        "name": "Seat deck lifter",
        "zone": "General Assembly",
        "status": "running",
        "trade": "Assembly maintenance",
        "contact_name": "Erik Lang",
        "vibration": [0.9, 1.0, 0.9, 1.0, 1.0, 0.9],
        "vibration_limit": 4.0,
        "temperature": [34, 34, 35, 35, 35, 35],
        "temperature_limit": 60,
    },
]

CLOSED = [
    {
        "number": 1,
        "features": INCIDENT_001,
        "worker": "Sam Keller",
        "supervisor": "Alex Novak",
        "decision": "slow",
        "decision_note": "Held the station and called drive unit maintenance.",
        "engineer": "Lea Hoffmann",
        "diagnosis": "Bearing degradation",
        "action": "Bearing replaced",
        "downtime": 27,
        "outcome": "Machine returned to normal",
        "age": timedelta(days=6, hours=2),
    },
    {
        "number": 3,
        "features": INCIDENT_003,
        "worker": "Sam Keller",
        "supervisor": "Alex Novak",
        "decision": "stop",
        "decision_note": "Stopped the cell until the curtain was checked.",
        "engineer": "Jonas Weber",
        "diagnosis": "Curtain reflector misaligned",
        "action": "Reflector reseated",
        "downtime": 18,
        "outcome": "Machine returned to normal",
        "age": timedelta(days=11),
    },
    {
        "number": 7,
        "features": INCIDENT_007,
        "worker": "Ines Bauer",
        "supervisor": "Alex Novak",
        "decision": "slow",
        "decision_note": "Slowed the booth and called paint maintenance.",
        "engineer": "Mara Vogel",
        "diagnosis": "Hose clamp loose",
        "action": "Clamp replaced",
        "downtime": 14,
        "outcome": "Machine returned to normal",
        "age": timedelta(days=3, hours=4),
    },
    {
        "number": 9,
        "features": INCIDENT_009,
        "worker": "Omar Haddad",
        "supervisor": "Alex Novak",
        "decision": "continue",
        "decision_note": "Finished the current car, then released the tool.",
        "engineer": "Erik Lang",
        "diagnosis": "Socket wear",
        "action": "Socket replaced",
        "downtime": 11,
        "outcome": "Machine returned to normal",
        "age": timedelta(days=9),
    },
]


def _signals(session: Session, machine: MachineRecord, spec: dict, end) -> None:
    series = (
        ("vibration", "mm/s", spec["vibration"], spec["vibration_limit"]),
        ("temperature", "C", spec["temperature"], spec["temperature_limit"]),
    )
    for metric, unit, values, limit_value in series:
        span = len(values) - 1
        for index, value in enumerate(values):
            session.add(
                MachineSignal(
                    machine_id=machine.id,
                    metric=metric,
                    value=value,
                    unit=unit,
                    limit_value=limit_value,
                    recorded_at=end - timedelta(minutes=5 * (span - index)),
                )
            )


def seed(session: Session) -> None:
    now = utcnow()
    machines: dict[str, MachineRecord] = {}
    for spec in MACHINES:
        machine = MachineRecord(
            code=spec["code"],
            name=spec["name"],
            zone=spec["zone"],
            status=spec["status"],
            trade=spec["trade"],
            contact_name=spec["contact_name"],
        )
        session.add(machine)
        machines[spec["code"]] = machine
    session.flush()
    for spec in MACHINES:
        _signals(session, machines[spec["code"]], spec, now)

    for spec in CLOSED:
        features: IncidentFeatures = spec["features"]
        opened = now - spec["age"]
        incident = IncidentRecord(
            number=spec["number"],
            machine_id=machines[features.machine_code].id,
            symptom=features.symptom,
            error_code=features.error_code,
            status="repaired",
            opened_by=spec["worker"],
            created_at=opened,
        )
        session.add(incident)
        session.flush()
        session.add(
            WorkerObservation(
                incident_id=incident.id,
                worker_name=spec["worker"],
                note=features.observation,
                observed_at=opened - timedelta(minutes=2),
            )
        )
        session.add(
            SupervisorDecision(
                incident_id=incident.id,
                supervisor_name=spec["supervisor"],
                action=spec["decision"],
                note=spec["decision_note"],
                decided_at=opened + timedelta(minutes=3),
            )
        )
        session.add(
            EngineerRepair(
                incident_id=incident.id,
                engineer_name=spec["engineer"],
                diagnosis=spec["diagnosis"],
                action=spec["action"],
                downtime_minutes=spec["downtime"],
                outcome=spec["outcome"],
                repaired_at=opened + timedelta(minutes=spec["downtime"]),
            )
        )

    opened = now - timedelta(minutes=10)
    current = IncidentRecord(
        number=14,
        machine_id=machines[INCIDENT_014.machine_code].id,
        symptom=INCIDENT_014.symptom,
        error_code=INCIDENT_014.error_code,
        status="open",
        opened_by="Sam Keller",
        created_at=opened,
    )
    session.add(current)
    session.flush()
    session.add(
        WorkerObservation(
            incident_id=current.id,
            worker_name="Sam Keller",
            note=INCIDENT_014.observation,
            observed_at=opened,
        )
    )
    session.flush()
    session.refresh(current)
    create_analysis(session, current)
