from __future__ import annotations

from pathlib import Path

from .utils import atomic_write_json, read_json


class EvaluationCache:
    def __init__(self, path: str | Path, signature: str):
        self.path = Path(path)
        self.signature = signature
        payload = read_json(self.path, default=None)
        if payload is None:
            self.scores: dict[str, float] = {}
        else:
            if payload.get("signature") != signature:
                raise ValueError("cache signature does not match current public configuration")
            self.scores = {str(k): float(v) for k, v in payload.get("scores", {}).items()}

    def get(self, sequence: str):
        return self.scores.get(sequence)

    def set(self, sequence: str, score: float) -> None:
        self.scores[str(sequence)] = float(score)
        self.save()

    def save(self) -> None:
        atomic_write_json(self.path, {"signature": self.signature, "scores": self.scores})
