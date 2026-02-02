from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from src.model.rank import ESNRanking


def _safe_sheet_name(name: str) -> str:
    safe = "".join(c for c in name if c not in '[]:*?/\\')
    return safe[:31] if safe else "Sheet"


def _build_summary(stats: Dict, config: Dict, esn_count: int, erasmus_count: int) -> pd.DataFrame:
    schema_cfg = config.get("schema", {})
    matching_cfg = config.get("matching", {})
    question_cols = schema_cfg.get("question_columns", [])
    rows = [
        {"Metric": "Run Timestamp", "Value": datetime.now(timezone.utc).isoformat()},
        {"Metric": "Number of ESN members", "Value": esn_count},
        {"Metric": "Number of Erasmus students (filtered)", "Value": stats.get("erasmus_after_filter", erasmus_count)},
        {"Metric": "Question Count", "Value": len(question_cols)},
        {"Metric": "Matching Metric", "Value": matching_cfg.get("metric", "hamming")},
        {"Metric": "Top K", "Value": matching_cfg.get("top_k")},
    ]
    return pd.DataFrame(rows)


def _find_contact_column(columns: List[str]) -> str | None:
    """Locate the whatsapp/contact column by keyword, case-insensitive."""
    for col in columns:
        if isinstance(col, str) and "whatsapp" in col.lower():
            return col
    return None


def _candidate_rows(
    ranking: ESNRanking,
    erasmus_df: pd.DataFrame,
    question_cols: List[str],
    esn_vector: np.ndarray,
    erasmus_vectors: np.ndarray
) -> pd.DataFrame:
    """
    Build rows for candidate matches with accurate NaN-aware comparison stats.

    Args:
        ranking: ESNRanking for one ESN member
        erasmus_df: Erasmus dataframe
        question_cols: List of question columns
        esn_vector: Vector for this ESN member
        erasmus_vectors: Matrix of all Erasmus vectors
    """
    contact_col = _find_contact_column(list(erasmus_df.columns))
    contact_header = contact_col or "Whatsapp contact"
    rows = []

    for rank_num, candidate in enumerate(ranking.candidates, start=1):
        student = erasmus_df.iloc[candidate.erasmus_index]
        student_vector = erasmus_vectors[candidate.erasmus_index]

        # Compute accurate comparison stats accounting for NaN values
        valid_mask = ~np.isnan(esn_vector) & ~np.isnan(student_vector)
        compared_questions_count = int(np.sum(valid_mask))

        if compared_questions_count > 0:
            different_answers_count = int(candidate.distance)
            same_answers_count = compared_questions_count - different_answers_count

            # Clamp to valid ranges
            if same_answers_count < 0:
                same_answers_count = 0
            if different_answers_count > compared_questions_count:
                different_answers_count = compared_questions_count
                same_answers_count = 0
        else:
            compared_questions_count = 0
            same_answers_count = 0
            different_answers_count = 0

        row = {
            "Rank": rank_num,
            "Student Name": student.get("Name", ""),
            "Student Surname": student.get("Surname", ""),
            contact_header: student.get(contact_col, "") if contact_col else "",
            "Compared questions": compared_questions_count,
            "Number of same answers": same_answers_count,
            "Number of different answers": different_answers_count,
        }

        # Append all answered non-question fields (excluding already included keys)
        base_keys = set(row.keys())
        for col in erasmus_df.columns:
            if col in question_cols or col in base_keys:
                continue
            value = student.get(col, "")
            if pd.notna(value) and str(value).strip():
                row[col] = value
        rows.append(row)

    return pd.DataFrame(rows)


def export_results(
    rankings: List[ESNRanking],
    esn_df: pd.DataFrame,
    erasmus_df: pd.DataFrame,
    stats: Dict,
    config: Dict,
    esn_vectors: np.ndarray = None,
    erasmus_vectors: np.ndarray = None
) -> Path:
    """
    Export matching results to Excel workbook.

    Args:
        rankings: List of ESNRanking objects
        esn_df: ESN dataframe
        erasmus_df: Erasmus dataframe
        stats: Statistics dictionary
        config: Configuration dictionary
        esn_vectors: Optional ESN vectors for accurate comparison stats
        erasmus_vectors: Optional Erasmus vectors for accurate comparison stats

    Returns:
        Path to the generated Excel file
    """
    output_cfg = config.get("output", {})
    out_dir = Path(output_cfg.get("out_dir", "outputs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"matching_{timestamp}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary_df = _build_summary(stats, config, len(esn_df), len(erasmus_df))
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if output_cfg.get("per_esner_sheets", True):
            schema_cfg = config.get("schema", {})
            question_cols = schema_cfg.get("question_columns", [])

            for ranking in rankings:
                esn_row = esn_df.iloc[ranking.esn_index]
                sheet_name = _safe_sheet_name(f"{esn_row.get('Name', '')} {esn_row.get('Surname', '')}")

                # Get ESN vector if available
                esn_vector = esn_vectors[ranking.esn_index] if esn_vectors is not None else None

                # Build candidate rows with accurate stats if vectors available
                if esn_vector is not None and erasmus_vectors is not None:
                    candidates_df = _candidate_rows(
                        ranking, erasmus_df, question_cols, esn_vector, erasmus_vectors
                    )
                else:
                    # Fallback to old behavior (for backwards compatibility)
                    candidates_df = _candidate_rows_legacy(ranking, erasmus_df, question_cols)

                candidates_df.to_excel(writer, sheet_name=sheet_name or "ESN", index=False)

    return out_path


def _candidate_rows_legacy(ranking: ESNRanking, erasmus_df: pd.DataFrame, question_cols: List[str]) -> pd.DataFrame:
    """Legacy version without NaN-aware counts (for backwards compatibility)."""
    contact_col = _find_contact_column(list(erasmus_df.columns))
    contact_header = contact_col or "Whatsapp contact"
    rows = []
    for rank_num, candidate in enumerate(ranking.candidates, start=1):
        student = erasmus_df.iloc[candidate.erasmus_index]
        diff_answers = int(candidate.distance)
        same_answers = len(question_cols) - diff_answers
        if same_answers < 0:
            same_answers = 0
        row = {
            "Rank": rank_num,
            "Student Name": student.get("Name", ""),
            "Student Surname": student.get("Surname", ""),
            contact_header: student.get(contact_col, "") if contact_col else "",
            "Number of same answers": same_answers,
            "Number of different answers": diff_answers,
        }
        base_keys = set(row.keys())
        for col in erasmus_df.columns:
            if col in question_cols or col in base_keys:
                continue
            value = student.get(col, "")
            if pd.notna(value) and str(value).strip():
                row[col] = value
        rows.append(row)
    return pd.DataFrame(rows)


