from __future__ import annotations

from pathlib import Path

from .state import SearchState
from ..utils import atomic_write_json, read_json


class Checkpoint:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, state: SearchState, policy_state: dict, signature: str) -> None:
        atomic_write_json(
            self.path,
            {
                "signature": signature,
                "state": state.to_dict(),
                "policy_state": policy_state,
            },
        )

    def load(self, signature: str):
        payload = read_json(self.path, default=None)
        if payload is None:
            return None
        if payload.get("signature") != signature:
            raise ValueError("checkpoint signature does not match current public configuration")
        return SearchState.from_dict(payload.get("state", {})), dict(payload.get("policy_state", {}))
