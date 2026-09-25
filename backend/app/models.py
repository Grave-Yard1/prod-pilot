from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MachineRecord(Base):
    """Machine identity, zone, and the trade to call. Signals live beside it."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    zone: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(16))
    trade: Mapped[str] = mapped_column(String(80))
    contact_name: Mapped[str] = mapped_column(String(80))

    signals: Mapped[list["MachineSignal"]] = relationship(
        back_populates="machine", cascade="all, delete-orphan"
    )
    incidents: Mapped[list["IncidentRecord"]] = relationship(back_populates="machine")


class MachineSignal(Base):
    __tablename__ = "machine_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    metric: Mapped[str] = mapped_column(String(40))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    limit_value: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    machine: Mapped[MachineRecord] = relationship(back_populates="signals")


class IncidentRecord(Base):
    """The case itself. Observations, analysis, the decision, and the repair are other tables."""

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    symptom: Mapped[str] = mapped_column(String(200))
    error_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open")
    opened_by: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    machine: Mapped[MachineRecord] = relationship(back_populates="incidents")
    observations: Mapped[list["WorkerObservation"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["AIAnalysis"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )
    decision: Mapped["SupervisorDecision | None"] = relationship(
        back_populates="incident", uselist=False, cascade="all, delete-orphan"
    )
    repair: Mapped["EngineerRepair | None"] = relationship(
        back_populates="incident", uselist=False, cascade="all, delete-orphan"
    )


class WorkerObservation(Base):
    __tablename__ = "worker_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    worker_name: Mapped[str] = mapped_column(String(80))
    note: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentRecord] = relationship(back_populates="observations")


class AIAnalysis(Base):
    """Retrieval and the suggested call. Written by the analysis service, never by editing other records."""

    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    recommendation: Mapped[str] = mapped_column(String(16))
    similarity_points: Mapped[int] = mapped_column(Integer)
    matched_incident_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)
    model_id: Mapped[str] = mapped_column(String(80))
    narrative_source: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentRecord] = relationship(back_populates="analyses")


class SupervisorDecision(Base):
    __tablename__ = "supervisor_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), unique=True, index=True)
    supervisor_name: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(Text, default="")
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentRecord] = relationship(back_populates="decision")


class EngineerRepair(Base):
    __tablename__ = "engineer_repairs"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), unique=True, index=True)
    engineer_name: Mapped[str] = mapped_column(String(80))
    diagnosis: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(200))
    downtime_minutes: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[str] = mapped_column(String(200))
    repaired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentRecord] = relationship(back_populates="repair")
