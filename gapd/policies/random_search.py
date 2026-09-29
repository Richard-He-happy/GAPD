from __future__ import annotations

import random

from ..search_space import PeptideSpace
from .base import SearchPolicy


def _json_safe(value):
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _as_tuple(value):
    if isinstance(value, list):
        return tuple(_as_tuple(v) for v in value)
    return value


class RandomSearchPolicy(SearchPolicy):
    def __init__(self, space: PeptideSpace, seed: int = 17):
        self.space = space
        self.rng = random.Random(seed)
        self.seen: set[str] = set()
        self.scores: dict[str, float] = {}

    def propose(self, count: int) -> list[str]:
        result: list[str] = []
        attempts = 0
        while len(result) < count and attempts < max(100, count * 100):
            attempts += 1
            sequence = self.space.random_sequence(self.rng)
            if sequence in self.seen:
                continue
            self.seen.add(sequence)
            result.append(sequence)
        if len(result) < count:
            for sequence in self.space.iter_sequences():
                if sequence not in self.seen:
                    self.seen.add(sequence)
                    result.append(sequence)
                    if len(result) >= count:
                        break
        return result

    def update(self, sequence: str, score: float) -> None:
        self.space.validate(sequence)
        self.seen.add(sequence)
        self.scores[sequence] = float(score)

    def state_dict(self) -> dict:
        return {
            "seen": sorted(self.seen),
            "scores": dict(self.scores),
            "rng_state": _json_safe(self.rng.getstate()),
        }

    def load_state(self, values: dict) -> None:
        self.seen = set(values.get("seen", []))
        self.scores = {str(k): float(v) for k, v in values.get("scores", {}).items()}
        if "rng_state" in values:
            self.rng.setstate(_as_tuple(values["rng_state"]))
