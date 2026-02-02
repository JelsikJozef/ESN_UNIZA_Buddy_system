"""
Reusable pipeline for ESN Buddy Matching System.
Can be called from both CLI and GUI.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.model import ingest, match, rank, validate, vectorize
from src.view import export_xlsx


@dataclass
class PipelineArtifacts:
    """Container for all pipeline outputs and intermediate data."""

    # Final output
    output_path: Path

    # Statistics
    stats: Dict[str, int]

    # DataFrames (after filtering)
    esn_df: pd.DataFrame
    erasmus_df: pd.DataFrame

    # Vectorization outputs
    esn_vectors: np.ndarray
    erasmus_vectors: np.ndarray
    question_columns: List[str]

    # Matching outputs
    distances: np.ndarray
    rankings: List[rank.ESNRanking]

    # Config used
    config: Dict


def compute_comparison_stats(
    esn_vector: np.ndarray,
    erasmus_vector: np.ndarray,
    distance: float
) -> Tuple[int, int, int]:
    """
    Compute accurate comparison statistics accounting for NaN values.

    Returns:
        (compared_questions_count, same_answers_count, different_answers_count)
    """
    valid_mask = ~np.isnan(esn_vector) & ~np.isnan(erasmus_vector)
    compared_questions_count = int(np.sum(valid_mask))

    if compared_questions_count == 0:
        return 0, 0, 0

    different_answers_count = int(distance)
    same_answers_count = compared_questions_count - different_answers_count

    # Clamp to valid ranges
    if same_answers_count < 0:
        same_answers_count = 0
    if different_answers_count > compared_questions_count:
        different_answers_count = compared_questions_count
        same_answers_count = 0

    return compared_questions_count, same_answers_count, different_answers_count


def run_pipeline_from_config(
    config: Dict,
    debug: bool = False,
    input_override: Optional[Tuple[pd.DataFrame, pd.DataFrame]] = None
) -> PipelineArtifacts:
    """
    Run the complete matching pipeline.

    Args:
        config: Configuration dictionary (same structure as config.yml)
        debug: Enable debug mode
        input_override: Optional (erasmus_df, esn_df) tuple to bypass file loading

    Returns:
        PipelineArtifacts containing all outputs and intermediate data

    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If input files not found
    """
    # Validate matching metric
    matching_cfg = config.get("matching", {})
    if matching_cfg.get("metric", "hamming") != "hamming":
        raise ValueError(f"Unsupported matching metric: {matching_cfg.get('metric')}")

    # Step 1: Ingest
    if input_override:
        erasmus_df, esn_df = input_override
        stats = {
            "esn_loaded": len(esn_df),
            "erasmus_loaded": len(erasmus_df),
            "esn_after_filter": len(esn_df),
            "erasmus_after_filter": len(erasmus_df),
        }
    else:
        erasmus_df, esn_df, stats = ingest.load_tables(config, debug=debug)

    # Step 2: Validate
    erasmus_df, esn_df = validate.validate_tables(erasmus_df, esn_df, config)

    # Step 3: Vectorize
    esn_vec, erasmus_vec = vectorize.vectorize_tables(esn_df, erasmus_df, config)

    # Step 4: Match
    distances = match.compute_distance_matrix(esn_vec.vectors, erasmus_vec.vectors)

    # Step 5: Rank
    top_k = matching_cfg.get("top_k")
    if top_k is None:
        top_k = len(erasmus_df)
    identifier_column = config.get("schema", {}).get("identifier_column")
    rankings = rank.rank_candidates(distances, erasmus_df, top_k, identifier_column)

    # Step 6: Export
    out_path = export_xlsx.export_results(
        rankings, esn_df, erasmus_df, stats, config,
        esn_vectors=esn_vec.vectors,
        erasmus_vectors=erasmus_vec.vectors
    )

    # Package all artifacts
    artifacts = PipelineArtifacts(
        output_path=out_path,
        stats=stats,
        esn_df=esn_df,
        erasmus_df=erasmus_df,
        esn_vectors=esn_vec.vectors,
        erasmus_vectors=erasmus_vec.vectors,
        question_columns=esn_vec.question_columns,
        distances=distances,
        rankings=rankings,
        config=config,
    )

    return artifacts
