"""Start OptiLab using the optional project-local dependency folder."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
runtime = ROOT / ".runtime"
if runtime.is_dir():
    sys.path.insert(0, str(runtime))
sys.path.insert(0, str(ROOT))

def main():
    try:
        import flask
        import pycparser
    except ImportError:
        print("Install project dependencies first:")
        print(f'  "{sys.executable}" -m pip install -r "{ROOT / "requirements.txt"}"')
        return 2
    from optilab.__main__ import main as cli
    return cli(["serve"] + sys.argv[1:])

if __name__ == "__main__":
    raise SystemExit(main())
