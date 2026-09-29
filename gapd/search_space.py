from __future__ import annotations

import itertools
import random


class PeptideSpace:
    def __init__(self, alphabet: str, length: int):
        self.alphabet = alphabet
        self.length = int(length)
        self._allowed = set(alphabet)

    def validate(self, sequence: str) -> None:
        if len(sequence) != self.length:
            raise ValueError(f"sequence length must equal {self.length}")
        invalid = set(sequence) - self._allowed
        if invalid:
            raise ValueError(f"invalid symbols: {sorted(invalid)}")

    def random_sequence(self, rng: random.Random) -> str:
        return "".join(rng.choice(self.alphabet) for _ in range(self.length))

    def mutate(self, sequence: str, position: int, symbol: str) -> str:
        self.validate(sequence)
        if symbol not in self._allowed:
            raise ValueError(f"invalid symbol: {symbol}")
        chars = list(sequence)
        chars[position] = symbol
        return "".join(chars)

    def iter_sequences(self):
        for chars in itertools.product(self.alphabet, repeat=self.length):
            yield "".join(chars)
