import subprocess
import sys


def test_version():
    result = subprocess.run([sys.executable, "-m", "gapd", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "gapd 0.1.0" in result.stdout
