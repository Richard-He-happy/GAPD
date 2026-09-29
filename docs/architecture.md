# Public architecture

The public GAPD repository uses explicit interfaces so the demonstration search logic is separated from scoring.

```text
YAML / CLI
   |
   v
 Config ---> PeptideSpace
   |             |
   v             v
SearchPolicy -> candidate batch -> cache/dedup -> Evaluator
     ^                                      |
     |                                      v
     +------------- score update <---------+
                     |
                     v
                 Checkpoint
```

`SimpleGeneticPolicy` is an independent textbook-style demonstration and is not the unpublished research search implementation. `ToyEvaluator` provides deterministic synthetic scores. `AutoDockGPUEvaluator` is a generic adapter for externally prepared ligand inputs.
