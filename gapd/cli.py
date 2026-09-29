from __future__ import annotations

import argparse
import json

from . import __version__
from .config import ConfigError, load_config
from .pipeline import run_search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gapd",
        description="Privacy-preserving public demo of GAPD peptide sequence search.",
    )
    parser.add_argument("--version", action="version", version=f"gapd {__version__}")
    sub = parser.add_subparsers(dest="command")
    for name in ("demo", "run"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--config", required=True)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        config = load_config(args.config)
        if args.command == "demo" and str(config.evaluator.get("name", "toy")).lower() != "toy":
            parser.error("demo requires a ToyEvaluator configuration")
        result = run_search(config)
    except (ConfigError, ValueError, KeyError, FileNotFoundError, RuntimeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
