"""Canonical texts for the seeded walk. Tests and the database share these strings."""

from app.services.retrieval import IncidentFeatures

INCIDENT_001 = IncidentFeatures(
    machine_code="M-17",
    symptom="abnormal vibration",
    observation="vibration started 8 minutes before alarm",
    error_code="E431",
)

INCIDENT_014 = IncidentFeatures(
    machine_code="M-17",
    symptom="abnormal vibration",
    observation="unusual noise",
    error_code=None,
)

INCIDENT_007 = IncidentFeatures(
    machine_code="M-22",
    symptom="coolant leak",
    observation="puddle under the booth pump",
    error_code="E218",
)
