"""
Export functionality for manual assignments.

Separate from ranking export to maintain clean separation of concerns.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import numpy as np

from src.controller.assignments import Assignment


def export_assignments_to_csv(
    assignments: List[Assignment],
    esn_df: Optional[pd.DataFrame] = None,
    erasmus_df: Optional[pd.DataFrame] = None,
    question_columns: Optional[List[str]] = None,
    esn_vectors: Optional[np.ndarray] = None,
    erasmus_vectors: Optional[np.ndarray] = None
) -> bytes:
    """
    Export assignments to CSV format with all columns except question columns.

    Args:
        assignments: List of Assignment objects
        esn_df: ESN dataframe (optional, for full export)
        erasmus_df: Erasmus dataframe (optional, for full export)
        question_columns: List of question column names to exclude (optional)
        esn_vectors: ESN vectors for matching count (optional)
        erasmus_vectors: Erasmus vectors for matching count (optional)

    Returns:
        CSV data as bytes
    """
    if not assignments:
        # Return empty CSV with headers
        df = pd.DataFrame(columns=[
            "ESN_Name",
            "ESN_Surname",
            "Erasmus_Name",
            "Erasmus_Surname",
            "Assignment_Timestamp"
        ])
        return df.to_csv(index=False).encode('utf-8')

    # If no dataframes provided, use basic export
    if esn_df is None or erasmus_df is None:
        rows = []
        for assignment in assignments:
            rows.append({
                "ESN_Name": assignment.esn_name,
                "ESN_Surname": assignment.esn_surname,
                "Erasmus_Name": assignment.erasmus_name,
                "Erasmus_Surname": assignment.erasmus_surname,
                "Assignment_Timestamp": assignment.timestamp
            })
        df = pd.DataFrame(rows)
        return df.to_csv(index=False).encode('utf-8')

    # Universal export with all columns
    question_cols = set(question_columns) if question_columns else set()
    rows = []

    for assignment in assignments:
        esn_row = esn_df.iloc[assignment.esn_index]
        erasmus_row = erasmus_df.iloc[assignment.erasmus_index]

        row = {}

        # Add ESN columns - ALL columns except questions
        for col in esn_df.columns:
            if col not in question_cols:
                col_name = f"ESN_{col}"
                value = esn_row[col]
                if pd.notna(value):
                    row[col_name] = value

        # Add Erasmus columns - ALL columns except questions
        for col in erasmus_df.columns:
            if col not in question_cols:
                col_name = f"Erasmus_{col}"
                value = erasmus_row[col]
                if pd.notna(value):
                    row[col_name] = value

        # Add matching answers count if vectors available
        if esn_vectors is not None and erasmus_vectors is not None:
            esn_vec = esn_vectors[assignment.esn_index]
            erasmus_vec = erasmus_vectors[assignment.erasmus_index]

            matching_count = 0
            compared_count = 0

            for i in range(min(len(esn_vec), len(erasmus_vec))):
                esn_val = esn_vec[i]
                erasmus_val = erasmus_vec[i]

                # Check if both values are valid (not None and not NaN)
                if esn_val is not None and erasmus_val is not None:
                    esn_is_nan = isinstance(esn_val, float) and np.isnan(esn_val)
                    erasmus_is_nan = isinstance(erasmus_val, float) and np.isnan(erasmus_val)

                    if not esn_is_nan and not erasmus_is_nan:
                        compared_count += 1
                        if esn_val == erasmus_val:
                            matching_count += 1

            row["Matching_Answers"] = matching_count
            row["Compared_Questions"] = compared_count

        row["Assignment_Timestamp"] = assignment.timestamp
        rows.append(row)

    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode('utf-8')


def export_assignments_to_xlsx(
    assignments: List[Assignment],
    output_path: Path,
    esn_df: Optional[pd.DataFrame] = None,
    erasmus_df: Optional[pd.DataFrame] = None,
    question_columns: Optional[List[str]] = None,
    esn_vectors: Optional[np.ndarray] = None,
    erasmus_vectors: Optional[np.ndarray] = None
) -> Path:
    """
    Export assignments to Excel format with all columns except question columns.

    Args:
        assignments: List of Assignment objects
        output_path: Path where to save the Excel file
        esn_df: ESN dataframe (optional, for full export)
        erasmus_df: Erasmus dataframe (optional, for full export)
        question_columns: List of question column names to exclude (optional)
        esn_vectors: ESN vectors for matching count (optional)
        erasmus_vectors: Erasmus vectors for matching count (optional)

    Returns:
        Path to the created file
    """
    if not assignments:
        # Create empty dataframe with headers
        df = pd.DataFrame(columns=[
            "ESN_Name",
            "ESN_Surname",
            "Erasmus_Name",
            "Erasmus_Surname",
            "Assignment_Timestamp"
        ])
    elif esn_df is None or erasmus_df is None:
        # Basic export without extra columns
        rows = []
        for assignment in assignments:
            rows.append({
                "ESN_Name": assignment.esn_name,
                "ESN_Surname": assignment.esn_surname,
                "Erasmus_Name": assignment.erasmus_name,
                "Erasmus_Surname": assignment.erasmus_surname,
                "Assignment_Timestamp": assignment.timestamp
            })
        df = pd.DataFrame(rows)
    else:
        # Universal export with all columns
        question_cols = set(question_columns) if question_columns else set()
        rows = []

        for assignment in assignments:
            esn_row = esn_df.iloc[assignment.esn_index]
            erasmus_row = erasmus_df.iloc[assignment.erasmus_index]

            row = {}

            # Add ESN columns - ALL columns except questions
            for col in esn_df.columns:
                if col not in question_cols:
                    col_name = f"ESN_{col}"
                    value = esn_row[col]
                    if pd.notna(value):
                        row[col_name] = value

            # Add Erasmus columns - ALL columns except questions
            for col in erasmus_df.columns:
                if col not in question_cols:
                    col_name = f"Erasmus_{col}"
                    value = erasmus_row[col]
                    if pd.notna(value):
                        row[col_name] = value

            # Add matching answers count if vectors available
            if esn_vectors is not None and erasmus_vectors is not None:
                esn_vec = esn_vectors[assignment.esn_index]
                erasmus_vec = erasmus_vectors[assignment.erasmus_index]

                matching_count = 0
                compared_count = 0

                for i in range(min(len(esn_vec), len(erasmus_vec))):
                    esn_val = esn_vec[i]
                    erasmus_val = erasmus_vec[i]

                    # Check if both values are valid (not None and not NaN)
                    if esn_val is not None and erasmus_val is not None:
                        esn_is_nan = isinstance(esn_val, float) and np.isnan(esn_val)
                        erasmus_is_nan = isinstance(erasmus_val, float) and np.isnan(erasmus_val)

                        if not esn_is_nan and not erasmus_is_nan:
                            compared_count += 1
                            if esn_val == erasmus_val:
                                matching_count += 1

                row["Matching_Answers"] = matching_count
                row["Compared_Questions"] = compared_count

            row["Assignment_Timestamp"] = assignment.timestamp
            rows.append(row)

        df = pd.DataFrame(rows)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to Excel
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Assignments", index=False)

    return output_path


def generate_assignment_filename(prefix: str = "assignments") -> str:
    """
    Generate a timestamped filename for assignment export.

    Args:
        prefix: Filename prefix

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"
