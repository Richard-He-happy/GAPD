from pathlib import Path

import yaml

from gapd.config import load_config
from gapd.pipeline import run_search


def test_run_and_resume(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    work = tmp_path / "work"
    config_path.write_text(yaml.safe_dump({
        "work_dir": str(work),
        "alphabet": "ACD",
        "length": 3,
        "budget": 10,
        "batch_size": 3,
        "seed": 2,
        "policy": {"name": "simple_genetic", "mutation_rate": 0.2},
        "evaluator": {"name": "toy", "seed": 9},
    }), encoding="utf-8")
    config = load_config(config_path)
    first = run_search(config)
    second = run_search(config)
    assert first["evaluated_count"] == 10
    assert second["evaluated_count"] == 10
    assert (work / "cache.json").exists()
    assert (work / "checkpoint.json").exists()
