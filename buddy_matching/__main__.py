from pathlib import Path
import sys

from src.controller.cli import main


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parent))
    main()
