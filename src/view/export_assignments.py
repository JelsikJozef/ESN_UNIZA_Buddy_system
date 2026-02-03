"""
Export functionality for manual assignments.

Separate from ranking export to maintain clean separation of concerns.
"""
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from src.controller.assignments import Assignment


def export_assignments_to_csv(assignments: List[Assignment]) -> bytes:
    """
    Export assignments to CSV format.

    Args:
        assignments: List of Assignment objects

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


def export_assignments_to_xlsx(assignments: List[Assignment], output_path: Path) -> Path:
    """
    Export assignments to Excel format.

    Args:
        assignments: List of Assignment objects
        output_path: Path where to save the Excel file

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
    else:
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
