# Design notes

## Policy / evaluator separation

The public runner knows only the `SearchPolicy` and `Evaluator` contracts. This permits deterministic local tests without exposing research-specific search logic.

## Cache and checkpoint

The score cache and checkpoint are bound to a public configuration signature. They are ordinary software-engineering components and contain no special research search rules.

## Demonstration genetic policy

The included genetic policy intentionally uses only textbook operations: sampled parents, one-point crossover, optional random mutation, duplicate filtering, and deterministic enumeration fallback. It is an independent demonstration policy and does not reproduce unpublished research-specific search logic.

## External molecular evaluation

The AutoDock-GPU adapter assumes ligand PDBQT files already exist. Research-specific molecular preparation, evaluation settings, and experimental configurations remain outside this repository.
