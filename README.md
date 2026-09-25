# Linewalk

A floor companion for a production supervisor. You are walking a wide line, several things can be wrong at once, and the call in front of you is continue, slow, or stop. Linewalk puts the last successful repair next to what the worker just saw, and it leaves the call with you.

This is a hackathon prototype. The stations, people, and incidents are **Berlin-style simulated production data**. It is not a Tesla system, and it does not claim to be one. The suggestion never changes the line.

## The walk

1. Open the floor. M-17, a drive unit spindle, is in alarm.
2. Incident **#014** is abnormal vibration. The worker heard unusual noise.
3. The retriever scores it **87%** against incident **#001**: same machine, same symptom, shared vibration family. Last time, the bearing was replaced, downtime was 27 minutes, and the machine returned to normal.
4. The suggested call is **slow**. You tap Continue, Slow, or Stop. That tap is the only record of the call.
5. An engineer records the diagnosis, the action, the downtime, and the outcome.
6. The repair becomes history. The next similar report can retrieve it.
7. Handoff lists what this shift decided and what the next supervisor still has to carry.

## How the 87% is produced

The score is a fixed weighted sum, in thousandths:

| Part | Weight | #014 against #001 |
| --- | --- | --- |
| Same machine | 400 | 400 |
| Symptom match | 320 | 320 |
| Shared symptom family | 150 | 150 |
| Error code, both present and equal | 80 | 0 |
| Worker-note overlap | 50 | 0 |

400 + 320 + 150 = 870, which is 0.87. Pytest asserts `similarity(incident_014, incident_001) == 0.87`. There is no branch that returns 87 for that incident number.

The suggested call is a separate policy:

- A safety-class code or a guard / curtain / e-stop report recommends **stop**.
- A match of 80% or more to a repair that returned the machine to normal recommends **slow**.
- Anything weaker recommends **continue**.

An optional language model can phrase the brief when `LLM_API_KEY` and `LLM_BASE_URL` are set (OpenAI-compatible `/chat/completions`). It does not choose the call and it does not write machine, observation, decision, or repair records. With no key, the brief is written from the same evidence.

## Records

These stay in separate tables. A decision does not overwrite an analysis. A repair does not overwrite a decision. Each row stores who wrote it and when.

- `MachineRecord` and `machine_signals`
- `IncidentRecord`
- `WorkerObservation`
- `AIAnalysis`
- `SupervisorDecision`
- `EngineerRepair`

Recording a decision does not change machine status. When an engineer records that the machine returned to normal, that repair write is what marks the station running again.

## Run it locally

API on port 8741, UI on port 8742.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8741
```

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:8742

One process, for a single deployable container:

```bash
docker build -t linewalk .
docker run --rm -p 8741:8741 -v linewalk-data:/data linewalk
```

The image serves the built UI and the API on port 8741.

Optional narrator:

```bash
export LLM_API_KEY=...
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4o-mini
```

## Tests

```bash
cd backend && .venv/bin/pytest
cd frontend && npx playwright install chromium && npm run e2e
```

Pytest covers the 87% fixture, the call policy, and the split between analysis, decision, and repair. Playwright walks the supervisor path: open #014, record Slow, record the repair, and see it on the handoff. A second browser test files a new vibration and checks that the bearing history comes back.
