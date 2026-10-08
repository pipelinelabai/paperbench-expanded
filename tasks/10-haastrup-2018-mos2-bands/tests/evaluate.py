import sys
from pathlib import Path


TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK.parents[1]))

from scripts.native_verifier_runner import main


if __name__ == '__main__':
    raise SystemExit(main(TASK))
