from __future__ import annotations

from pathlib import Path

from .. import __version__
from ..cache import EvaluationCache
from ..config import Config
from ..evaluators import AutoDockGPUEvaluator, ToyEvaluator
from ..policies import RandomSearchPolicy, SimpleGeneticPolicy
from ..search_space import PeptideSpace
from ..utils import atomic_write_json, ensure_dir, stable_signature
from .checkpoint import Checkpoint
from .state import SearchState


def build_policy(config: Config, space: PeptideSpace):
    name = str(config.policy.get("name", "simple_genetic")).lower()
    if name == "simple_genetic":
        return SimpleGeneticPolicy(
            space,
            seed=config.seed,
            mutation_rate=float(config.policy.get("mutation_rate", 0.25)),
        )
    if name == "random_search":
        return RandomSearchPolicy(space, seed=config.seed)
    raise ValueError(f"unknown public policy: {name}")


def build_evaluator(config: Config):
    values = config.evaluator
    name = str(values.get("name", "toy")).lower()
    if name == "toy":
        return ToyEvaluator(seed=int(values.get("seed", 101)))
    if name == "autodock_gpu":
        return AutoDockGPUEvaluator(
            executable=str(values.get("executable", "autodock_gpu_128wi")),
            receptor_fld=str(values["receptor_fld"]),
            ligand_dir=str(values["ligand_dir"]),
            dlg_dir=str(values.get("dlg_dir", str(Path(config.work_dir) / "dlg"))),
            extra_args=[str(x) for x in values.get("extra_args", [])],
        )
    raise ValueError(f"unknown evaluator: {name}")


def run_search(config: Config) -> dict:
    work = ensure_dir(config.work_dir)
    signature = stable_signature(config.public_signature_payload())
    space = PeptideSpace(config.alphabet, config.length)
    policy = build_policy(config, space)
    evaluator = build_evaluator(config)
    cache = EvaluationCache(work / "cache.json", signature)
    checkpoint = Checkpoint(work / "checkpoint.json")
    restored = checkpoint.load(signature)
    if restored:
        state, policy_state = restored
        policy.load_state(policy_state)
    else:
        state = SearchState()

    state.status = "running"
    while len(state.evaluated) < config.budget:
        remaining = config.budget - len(state.evaluated)
        requested = min(config.batch_size, remaining)
        candidates = policy.propose(requested)
        if not candidates:
            break

        uncached: list[str] = []
        for sequence in candidates:
            cached = cache.get(sequence)
            if cached is None:
                uncached.append(sequence)
            else:
                policy.update(sequence, cached)
                state.evaluated[sequence] = cached

        if uncached:
            fresh = evaluator.evaluate(uncached)
            for sequence in uncached:
                score = float(fresh[sequence])
                cache.set(sequence, score)
                policy.update(sequence, score)
                state.evaluated[sequence] = score

        state.step += 1
        checkpoint.save(state, policy.state_dict(), signature)

    state.status = "completed" if len(state.evaluated) >= config.budget else "stopped"
    checkpoint.save(state, policy.state_dict(), signature)
    metadata = {
        "tool": "gapd",
        "version": __version__,
        "status": state.status,
        "evaluated_count": len(state.evaluated),
        "step_count": state.step,
        "policy": str(config.policy.get("name", "simple_genetic")),
        "evaluator": str(config.evaluator.get("name", "toy")),
    }
    atomic_write_json(work / "run_metadata.json", metadata)
    return metadata
