from __future__ import annotations

import subprocess
from pathlib import Path

from .base import Evaluator
from .dlg_parser import parse_binding_energy
from ..utils import ensure_dir


class AutoDockGPUEvaluator(Evaluator):
    """Generic adapter for externally prepared ligands; larger returned scores are better."""

    def __init__(
        self,
        executable: str,
        receptor_fld: str,
        ligand_dir: str,
        dlg_dir: str,
        extra_args: list[str] | None = None,
    ):
        self.executable = executable
        self.receptor_fld = Path(receptor_fld)
        self.ligand_dir = Path(ligand_dir)
        self.dlg_dir = ensure_dir(dlg_dir)
        self.extra_args = list(extra_args or [])

    def _paths(self, sequence: str) -> tuple[Path, Path]:
        ligand = self.ligand_dir / f"{sequence}.pdbqt"
        dlg = self.dlg_dir / f"{sequence}.dlg"
        return ligand, dlg

    def evaluate(self, sequences: list[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for sequence in sequences:
            ligand, dlg = self._paths(sequence)
            if not ligand.exists():
                raise FileNotFoundError(f"prepared ligand not found: {ligand}")
            if dlg.exists():
                dlg.unlink()
            cmd = [
                self.executable,
                "--ffile", str(self.receptor_fld),
                "--lfile", str(ligand),
                "--dlgoutput", "1",
                *self.extra_args,
            ]
            completed = subprocess.run(cmd, cwd=self.dlg_dir, text=True, capture_output=True)
            if completed.returncode != 0:
                raise RuntimeError(f"external evaluator failed for {sequence}: {completed.stderr.strip()}")
            produced = self.dlg_dir / f"{ligand.stem}.dlg"
            if produced != dlg and produced.exists():
                produced.replace(dlg)
            if not dlg.exists():
                raise RuntimeError(f"DLG was not produced for {sequence}")
            energy = parse_binding_energy(dlg)
            scores[sequence] = -float(energy)
        return scores
