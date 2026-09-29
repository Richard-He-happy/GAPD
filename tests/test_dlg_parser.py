from pathlib import Path

from gapd.evaluators.dlg_parser import parse_binding_energy


def test_parse_binding_energy(tmp_path: Path):
    dlg = tmp_path / "x.dlg"
    dlg.write_text("Lowest Binding Energy = -7.25 kcal/mol\n", encoding="utf-8")
    assert parse_binding_energy(dlg) == -7.25
