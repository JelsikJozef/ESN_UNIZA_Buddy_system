import argparse
from pathlib import Path
from typing import Dict

import yaml

from src.model import ingest, match, rank, validate, vectorize
from src.view import export_xlsx


def _load_config(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def run_pipeline(config_path: Path) -> Path:
    config = _load_config(config_path)
    matching_cfg = config.get("matching", {})
    if matching_cfg.get("metric", "hamming") != "hamming":
        raise ValueError(f"Unsupported matching metric: {matching_cfg.get('metric')}")

    erasmus_df, esn_df, stats = ingest.load_tables(config)
    erasmus_df, esn_df = validate.validate_tables(erasmus_df, esn_df, config)
    esn_vec, erasmus_vec = vectorize.vectorize_tables(esn_df, erasmus_df, config)
    distances = match.compute_distance_matrix(esn_vec.vectors, erasmus_vec.vectors)

    top_k = matching_cfg.get("top_k")
    if top_k is None:
        top_k = len(erasmus_df)
    identifier_column = config.get("schema", {}).get("identifier_column")
    rankings = rank.rank_candidates(distances, erasmus_df, top_k, identifier_column)

    out_path = export_xlsx.export_results(rankings, esn_df, erasmus_df, stats, config)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ESN Buddy Matching CLI")
    parser.add_argument("--config", required=True, help="Path to config.yml")
    args = parser.parse_args()
    try:
        out_path = run_pipeline(Path(args.config))
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        raise SystemExit(1)
    print(f"Output written to: {out_path}")


if __name__ == "__main__":
    main()
