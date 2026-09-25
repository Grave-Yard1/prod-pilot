"""Optional narrator. It returns prose only, and only when an endpoint is configured.

The suggested call is chosen before this function runs. Nothing here writes a
machine, observation, decision, or repair record.
"""

import os

import httpx


SYSTEM = (
    "You write a two-sentence floor brief for a production supervisor. "
    "Use only the JSON evidence. Repeat the recommendation you are given; do not choose a different one. "
    "Do not invent measurements, people, procedures, or causes. "
    "Do not say the line was changed. "
    "End by stating that an authorized person decides."
)


def narrate(pack: dict) -> tuple[str, str] | None:
    key = os.environ.get("LLM_API_KEY", "").strip()
    base = os.environ.get("LLM_BASE_URL", "").strip().rstrip("/")
    if not key or not base:
        return None
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    try:
        response = httpx.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": _user_content(pack)},
                ],
            },
            timeout=8.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None
    if not isinstance(content, str) or not content.strip():
        return None
    return content.strip(), model


def _user_content(pack: dict) -> str:
    import json

    return json.dumps(pack, ensure_ascii=True)
