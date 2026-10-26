"""Compatibility entrypoint: use the shared, tested optimizer core."""
from pathlib import Path
import sys
from optilab.__main__ import main

if __name__ == "__main__":
    arguments = sys.argv[1:] or [str(Path(__file__).resolve().parent / "examples" / "constant_pipeline.c")]
    raise SystemExit(main(["analyze"] + arguments))
