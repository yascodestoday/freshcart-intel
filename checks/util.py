import subprocess
import sys
from pathlib import Path


def sh(cmd):
    """Run a command, return (exit code, output)."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def pytest_ok():
    code, _ = sh([sys.executable, "-m", "pytest", "-q"])
    return code == 0


def csv_rows(path):
    p = Path(path)
    return sum(1 for _ in open(p, encoding="utf-8")) - 1 if p.exists() else -1
