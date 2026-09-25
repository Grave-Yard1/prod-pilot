from app.cases import INCIDENT_001, INCIDENT_007, INCIDENT_014
from app.services.retrieval import IncidentFeatures, compare, similarity


def test_seed_pair_scores_87():
    assert similarity(INCIDENT_014, INCIDENT_001) == 0.87
    comparison = compare(INCIDENT_014, INCIDENT_001)
    assert comparison.points == 870
    assert comparison.parts == {
        "machine": 400,
        "symptom": 320,
        "family": 150,
        "error_code": 0,
        "observation": 0,
    }
    assert comparison.shared_families == ("vibration",)


def test_different_machine_scores_lower():
    assert similarity(INCIDENT_014, INCIDENT_007) < similarity(INCIDENT_014, INCIDENT_001)
    other_machine = IncidentFeatures(
        machine_code="M-22",
        symptom="abnormal vibration",
        observation="unusual noise",
        error_code=None,
    )
    assert compare(other_machine, INCIDENT_001).points == 470
    assert similarity(other_machine, INCIDENT_001) < 0.87
