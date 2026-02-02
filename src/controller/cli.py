import argparse
from pathlib import Path
from typing import Dict

import yaml

from src.controller.pipeline import run_pipeline_from_config


def _load_config(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def run_pipeline(config_path: Path, debug_csv: bool = False) -> Path:
    """CLI wrapper for the pipeline."""
    config = _load_config(config_path)
    artifacts = run_pipeline_from_config(config, debug=debug_csv)
    return artifacts.output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ESN Buddy Matching CLI")
    parser.add_argument("--config", required=True, help="Path to config.yml")
    parser.add_argument(
        "--debug-csv",
        action="store_true",
        help="Print CSV columns and attempted separators during load",
    )
    args = parser.parse_args()
    try:
        out_path = run_pipeline(Path(args.config), debug_csv=args.debug_csv)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        raise SystemExit(1)
    print(f"Output written to: {out_path}")


if __name__ == "__main__":
    main()
