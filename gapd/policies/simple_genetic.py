from __future__ import annotations

import random

from ..search_space import PeptideSpace
from .base import SearchPolicy
from .random_search import _as_tuple, _json_safe


class SimpleGeneticPolicy(SearchPolicy):
    """Independent textbook-style GA used only for the public demonstration."""

    def __init__(self, space: PeptideSpace, seed: int = 17, mutation_rate: float = 0.25):
        self.space = space
        self.rng = random.Random(seed)
        self.mutation_rate = float(mutation_rate)
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be between 0 and 1")
        self.seen: set[str] = set()
        self.scores: dict[str, float] = {}

    def _ranked_pool(self) -> list[str]:
        ranked = [seq for seq, _ in sorted(self.scores.items(), key=lambda item: (-item[1], item[0]))]
        if len(ranked) <= 2:
            return ranked
        return ranked[: max(2, (len(ranked) + 1) // 2)]

    def _random_unseen(self) -> str | None:
        for _ in range(100):
            sequence = self.space.random_sequence(self.rng)
            if sequence not in self.seen:
                return sequence
        return None

    def _child(self) -> str | None:
        pool = self._ranked_pool()
        if len(pool) < 2:
            return self._random_unseen()
        parent_a, parent_b = self.rng.sample(pool, 2)
        if self.space.length == 1:
            child = parent_a
        else:
            cut = self.rng.randrange(1, self.space.length)
            child = parent_a[:cut] + parent_b[cut:]
        if self.rng.random() < self.mutation_rate:
            position = self.rng.randrange(self.space.length)
            alternatives = [x for x in self.space.alphabet if x != child[position]]
            if alternatives:
                child = self.space.mutate(child, position, self.rng.choice(alternatives))
        return child if child not in self.seen else None

    def propose(self, count: int) -> list[str]:
        result: list[str] = []
        attempts = 0
        while len(result) < count and attempts < max(100, count * 100):
            attempts += 1
            candidate = self._child()
            if candidate is None or candidate in self.seen:
                continue
            self.seen.add(candidate)
            result.append(candidate)
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
            "mutation_rate": self.mutation_rate,
            "rng_state": _json_safe(self.rng.getstate()),
        }

    def load_state(self, values: dict) -> None:
        self.seen = set(values.get("seen", []))
        self.scores = {str(k): float(v) for k, v in values.get("scores", {}).items()}
        self.mutation_rate = float(values.get("mutation_rate", self.mutation_rate))
        if "rng_state" in values:
            self.rng.setstate(_as_tuple(values["rng_state"]))
