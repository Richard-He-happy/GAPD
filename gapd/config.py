from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass
class Config:
    work_dir: str
    alphabet: str
    length: int
    budget: int
    batch_size: int
    seed: int
    policy: dict[str, Any]
    evaluator: dict[str, Any]

    @property
    def search_space_size(self) -> int:
        return len(self.alphabet) ** self.length

    def public_signature_payload(self) -> dict[str, Any]:
        return {
            "alphabet": self.alphabet,
            "length": self.length,
            "policy": self.policy,
            "evaluator_name": self.evaluator.get("name"),
        }


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return dict(value)


def load_config(path: str | Path) -> Config:
    source = Path(path)
    if not source.exists():
        raise ConfigError(f"config does not exist: {source}")
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ConfigError("top-level config must be a mapping")

    alphabet = str(data.get("alphabet", "ACDEFGHIKLMNPQRSTVWY")).strip().upper()
    if not alphabet or len(set(alphabet)) != len(alphabet):
        raise ConfigError("alphabet must contain unique symbols")

    length = int(data.get("length", 4))
    budget = int(data.get("budget", 24))
    batch_size = int(data.get("batch_size", 4))
    seed = int(data.get("seed", 17))
    if min(length, budget, batch_size) <= 0:
        raise ConfigError("length, budget, and batch_size must be positive")

    policy = _require_mapping(data.get("policy", {"name": "simple_genetic"}), "policy")
    evaluator = _require_mapping(data.get("evaluator", {"name": "toy"}), "evaluator")
    work_dir = str(data.get("work_dir", "./work/gapd"))

    return Config(
        work_dir=work_dir,
        alphabet=alphabet,
        length=length,
        budget=min(budget, len(alphabet) ** length),
        batch_size=batch_size,
        seed=seed,
        policy=policy,
        evaluator=evaluator,
    )
