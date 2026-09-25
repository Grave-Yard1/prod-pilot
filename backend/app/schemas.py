from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    machine_code: str = Field(min_length=1, max_length=16)
    symptom: str = Field(min_length=1, max_length=200)
    observation: str = Field(min_length=1, max_length=2000)
    error_code: str | None = Field(default=None, max_length=32)
    worker_name: str = Field(min_length=1, max_length=80)


class DecisionCreate(BaseModel):
    supervisor_name: str = Field(min_length=1, max_length=80)
    action: str = Field(pattern="^(continue|slow|stop)$")
    note: str = Field(default="", max_length=2000)


class RepairCreate(BaseModel):
    engineer_name: str = Field(min_length=1, max_length=80)
    diagnosis: str = Field(min_length=1, max_length=200)
    action: str = Field(min_length=1, max_length=200)
    downtime_minutes: int = Field(ge=0, le=10000)
    outcome: str = Field(min_length=1, max_length=200)
