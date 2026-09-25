"""Deterministic retrieval over closed incident history.

The score is an integer number of thousandths so a pair can be asserted exactly.
Weights:

  machine       400  same machine code
  symptom       320  token Jaccard of the symptom
  family        150  shared symptom family (vibration, fluid, fastening, thermal, safety)
  error_code     80  both codes present and equal
  observation    50  token Jaccard of the worker note

Incident #014 against incident #001 is the fixture:
same machine (400) + same symptom (320) + shared vibration family (150) = 870,
which is 0.87. The new note does not repeat the old wording, and #014 has no error code,
so those parts stay at 0. Nothing in this module special-cases those incident numbers.
"""

from dataclasses import dataclass


WEIGHTS = {
    "machine": 400,
    "symptom": 320,
    "family": 150,
    "error_code": 80,
    "observation": 50,
}

STOPWORDS = {
    "a",
    "an",
    "the",
    "before",
    "after",
    "started",
    "of",
    "to",
    "and",
    "on",
    "for",
    "with",
    "from",
    "in",
    "at",
    "is",
    "was",
    "were",
    "it",
    "this",
    "that",
    "minutes",
    "minute",
    "during",
}

FAMILIES = {
    "vibration": {
        "vibration",
        "vibrations",
        "noise",
        "noisy",
        "bearing",
        "grind",
        "grinding",
        "hum",
        "whine",
        "rattle",
    },
    "fluid": {"coolant", "leak", "leaking", "drip", "dripping", "viscosity", "oil", "puddle"},
    "fastening": {"torque", "angle", "fastener", "bolt", "rundown", "socket"},
    "thermal": {"temperature", "overheat", "overheating", "hot", "thermal"},
    "safety": {"guard", "estop", "interlock", "curtain"},
}


@dataclass(frozen=True)
class IncidentFeatures:
    machine_code: str
    symptom: str
    observation: str
    error_code: str | None = None


@dataclass(frozen=True)
class Comparison:
    points: int
    parts: dict[str, int]
    shared_families: tuple[str, ...]

    @property
    def score(self) -> float:
        return self.points / 1000


def tokens(text: str) -> set[str]:
    found: set[str] = set()
    for raw in text.lower().replace("-", " ").split():
        word = "".join(ch for ch in raw if ch.isalnum())
        if word and not word.isdigit() and word not in STOPWORDS:
            found.add(word)
    return found


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def families_in(*texts: str) -> set[str]:
    words: set[str] = set()
    for text in texts:
        words |= tokens(text)
    return {name for name, vocab in FAMILIES.items() if words & vocab}


def compare(current: IncidentFeatures, past: IncidentFeatures) -> Comparison:
    symptom_points = round(WEIGHTS["symptom"] * jaccard(tokens(current.symptom), tokens(past.symptom)))
    shared = families_in(current.symptom, current.observation) & families_in(past.symptom, past.observation)
    current_code = (current.error_code or "").strip().upper()
    past_code = (past.error_code or "").strip().upper()
    observation_points = round(
        WEIGHTS["observation"] * jaccard(tokens(current.observation), tokens(past.observation))
    )
    parts = {
        "machine": WEIGHTS["machine"] if current.machine_code == past.machine_code else 0,
        "symptom": symptom_points,
        "family": WEIGHTS["family"] if shared else 0,
        "error_code": WEIGHTS["error_code"] if current_code and past_code and current_code == past_code else 0,
        "observation": observation_points,
    }
    return Comparison(
        points=sum(parts.values()),
        parts=parts,
        shared_families=tuple(sorted(shared)),
    )


def similarity_points(current: IncidentFeatures, past: IncidentFeatures) -> int:
    return compare(current, past).points


def similarity(current: IncidentFeatures, past: IncidentFeatures) -> float:
    return compare(current, past).score
