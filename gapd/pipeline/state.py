from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchState:
    evaluated: dict[str, float] = field(default_factory=dict)
    step: int = 0
    status: str = "ready"

    def to_dict(self) -> dict:
        return {
            "evaluated": dict(self.evaluated),
            "step": int(self.step),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, values: dict) -> "SearchState":
        return cls(
            evaluated={str(k): float(v) for k, v in values.get("evaluated", {}).items()},
            step=int(values.get("step", 0)),
            status=str(values.get("status", "ready")),
        )
