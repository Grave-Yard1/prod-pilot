def test_open_call_matches_bearing_history_at_87(client):
    incident = client.get("/api/incidents/14")
    assert incident.status_code == 200
    body = incident.json()
    assert body["symptom"] == "abnormal vibration"
    assert body["observations"][0]["worker_name"] == "Sam Keller"
    assert body["observations"][0]["note"] == "unusual noise"
    assert body["observations"][0]["observed_at"]
    assert body["decision"] is None
    assert body["repair"] is None
    analysis = body["analysis"]
    assert analysis["similarity_percent"] == 87
    assert analysis["similarity_points"] == 870
    assert analysis["recommendation"] == "slow"
    assert analysis["matched_incident_number"] == 1
    assert analysis["narrative_source"] == "deterministic"
    assert analysis["model_id"] == "local-retriever"
    assert "authorized person" in analysis["rationale"].lower()
    assert "does not change the line" in analysis["rationale"].lower()
    evidence = analysis["evidence"][0]
    assert evidence["action"] == "Bearing replaced"
    assert evidence["diagnosis"] == "Bearing degradation"
    assert evidence["downtime_minutes"] == 27
    assert evidence["parts"]["machine"] == 400
    assert evidence["parts"]["symptom"] == 320
    assert evidence["parts"]["family"] == 150


def test_decision_does_not_change_machine_status_or_analysis(client):
    before_machine = client.get("/api/machines/M-17").json()
    before = client.get("/api/incidents/14").json()
    assert before_machine["status"] == "alarm"

    response = client.post(
        "/api/incidents/14/decision",
        json={
            "supervisor_name": "Alex Novak",
            "action": "slow",
            "note": "Held the station and called Lea Hoffmann.",
        },
    )
    assert response.status_code == 200
    after = response.json()
    after_machine = client.get("/api/machines/M-17").json()

    assert after_machine["status"] == before_machine["status"] == "alarm"
    assert after["analysis"]["id"] == before["analysis"]["id"]
    assert after["analysis"]["similarity_points"] == before["analysis"]["similarity_points"]
    assert after["analysis"]["rationale"] == before["analysis"]["rationale"]
    assert after["analysis"]["recommendation"] == "slow"
    assert after["decision"]["supervisor_name"] == "Alex Novak"
    assert after["decision"]["action"] == "slow"
    assert after["decision"]["decided_at"]
    assert after["decision"]["id"] != after["analysis"]["id"]
    assert after["status"] == "decided"
    assert after["repair"] is None


def test_repair_is_a_separate_record_and_can_return_the_machine(client):
    decided = client.post(
        "/api/incidents/14/decision",
        json={"supervisor_name": "Alex Novak", "action": "slow", "note": "Holding M-17."},
    ).json()
    blocked = client.post(
        "/api/incidents/9/repair",
        json={
            "engineer_name": "Lea Hoffmann",
            "diagnosis": "Already closed",
            "action": "None",
            "downtime_minutes": 1,
            "outcome": "Machine returned to normal",
        },
    )
    assert blocked.status_code == 409

    response = client.post(
        "/api/incidents/14/repair",
        json={
            "engineer_name": "Lea Hoffmann",
            "diagnosis": "Bearing degradation",
            "action": "Bearing replaced",
            "downtime_minutes": 27,
            "outcome": "Machine returned to normal",
        },
    )
    assert response.status_code == 200
    closed = response.json()
    assert closed["repair"]["engineer_name"] == "Lea Hoffmann"
    assert closed["repair"]["action"] == "Bearing replaced"
    assert closed["repair"]["repaired_at"]
    assert closed["decision"]["id"] == decided["decision"]["id"]
    assert closed["decision"]["note"] == decided["decision"]["note"]
    assert closed["analysis"]["id"] == decided["analysis"]["id"]
    assert closed["status"] == "repaired"
    assert client.get("/api/machines/M-17").json()["status"] == "running"


def test_new_vibration_retrieves_the_same_bearing_fix(client):
    response = client.post(
        "/api/incidents",
        json={
            "machine_code": "M-17",
            "symptom": "abnormal vibration",
            "observation": "unusual noise",
            "worker_name": "Sam Keller",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["number"] != 14
    assert body["analysis"]["similarity_percent"] == 87
    assert body["analysis"]["recommendation"] == "slow"
    assert body["analysis"]["matched_incident_number"] == 1
    assert body["decision"] is None
    assert client.get("/api/machines/M-17").json()["status"] == "alarm"


def test_safety_code_recommends_stop_without_writing_a_decision(client):
    response = client.post(
        "/api/incidents",
        json={
            "machine_code": "M-44",
            "symptom": "guard open",
            "observation": "light curtain broken during the weld",
            "error_code": "E900",
            "worker_name": "Sam Keller",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["analysis"]["recommendation"] == "stop"
    assert body["decision"] is None
    number = body["number"]
    status_before = client.get("/api/machines/M-44").json()["status"]
    decided = client.post(
        f"/api/incidents/{number}/decision",
        json={"supervisor_name": "Alex Novak", "action": "stop", "note": "Cell is stopped until the curtain is checked."},
    )
    assert decided.status_code == 200
    assert client.get("/api/machines/M-44").json()["status"] == status_before


def test_rerun_appends_analysis_and_leaves_the_decision_untouched(client):
    client.post(
        "/api/incidents/14/decision",
        json={"supervisor_name": "Alex Novak", "action": "continue", "note": "Watching one more cycle."},
    )
    before = client.get("/api/incidents/14").json()
    rerun = client.post("/api/incidents/14/analyze")
    assert rerun.status_code == 200
    after = rerun.json()
    assert after["analysis"]["id"] != before["analysis"]["id"]
    assert after["decision"]["id"] == before["decision"]["id"]
    assert after["decision"]["action"] == "continue"
    assert after["analysis"]["recommendation"] == "slow"
    assert client.get("/api/machines/M-17").json()["status"] == "alarm"


def test_closed_repair_is_what_the_next_report_retrieves(client):
    client.post(
        "/api/incidents/14/decision",
        json={"supervisor_name": "Alex Novak", "action": "slow", "note": "Held M-17."},
    )
    client.post(
        "/api/incidents/14/repair",
        json={
            "engineer_name": "Lea Hoffmann",
            "diagnosis": "Bearing degradation",
            "action": "Bearing replaced",
            "downtime_minutes": 27,
            "outcome": "Machine returned to normal",
        },
    )
    created = client.post(
        "/api/incidents",
        json={
            "machine_code": "M-17",
            "symptom": "abnormal vibration",
            "observation": "unusual noise",
            "worker_name": "Sam Keller",
        },
    )
    assert created.status_code == 201
    analysis = created.json()["analysis"]
    assert analysis["similarity_percent"] == 92
    assert analysis["matched_incident_number"] == 14
    assert analysis["recommendation"] == "slow"
    assert analysis["evidence"][0]["action"] == "Bearing replaced"


def test_handoff_shows_this_shift_only(client):
    initial = client.get("/api/handoff").json()
    assert initial["dataset"] == "berlin-style-simulated"
    assert any(item["number"] == 14 for item in initial["waiting"])
    assert initial["decisions"] == []
    assert initial["repairs"] == []

    client.post(
        "/api/incidents/14/decision",
        json={"supervisor_name": "Alex Novak", "action": "slow", "note": "Held M-17."},
    )
    client.post(
        "/api/incidents/14/repair",
        json={
            "engineer_name": "Lea Hoffmann",
            "diagnosis": "Bearing degradation",
            "action": "Bearing replaced",
            "downtime_minutes": 27,
            "outcome": "Machine returned to normal",
        },
    )
    handoff = client.get("/api/handoff").json()
    assert handoff["waiting"] == []
    assert handoff["decisions"][0]["machine_code"] == "M-17"
    assert handoff["decisions"][0]["action"] == "slow"
    assert handoff["decisions"][0]["supervisor_name"] == "Alex Novak"
    assert handoff["repairs"][0]["action"] == "Bearing replaced"
    assert handoff["repairs"][0]["engineer_name"] == "Lea Hoffmann"
    assert all(item["code"] != "M-17" for item in handoff["carry"])
