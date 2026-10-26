"""Compatibility CLI; the optimizer implementation lives in optilab.optimizer."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from optilab.__main__ import main

if __name__ == "__main__":
    arguments = sys.argv[1:] or [str(ROOT / "examples" / "constant_pipeline.c")]
    raise SystemExit(main(["analyze"] + arguments))
