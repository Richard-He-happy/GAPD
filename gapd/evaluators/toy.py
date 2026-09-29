from __future__ import annotations

import hashlib

from .base import Evaluator


class ToyEvaluator(Evaluator):
    """Deterministic synthetic evaluator; larger scores are better."""

    def __init__(self, seed: int = 101):
        self.seed = int(seed)

    def _score(self, sequence: str) -> float:
        digest = hashlib.sha256(f"{self.seed}:{sequence}".encode("utf-8")).digest()
        value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
        composition = sum((i + 1) * (ord(ch) % 17) for i, ch in enumerate(sequence)) / 1000.0
        return round(value + composition, 10)

    def evaluate(self, sequences: list[str]) -> dict[str, float]:
        return {sequence: self._score(sequence) for sequence in sequences}
