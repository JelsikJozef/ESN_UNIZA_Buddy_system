"""
Test suite for assignment export functionality.
"""
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.controller.assignments import Assignment, AssignmentState
from src.view.export_assignments import (
    export_assignments_to_csv,
    export_assignments_to_xlsx,
    generate_assignment_filename,
)


class TestExportAssignments:
    """Test assignment export functionality."""

    def test_export_empty_assignments_csv(self):
        """Test exporting empty assignment list to CSV."""
        csv_bytes = export_assignments_to_csv([])

        # Should return CSV with headers only
        csv_str = csv_bytes.decode('utf-8')
        assert "ESN_Name" in csv_str
        assert "Erasmus_Name" in csv_str
        assert "Assignment_Timestamp" in csv_str

    def test_export_assignments_csv(self):
        """Test exporting assignments to CSV."""
        assignments = [
            Assignment(
                esn_index=0,
                erasmus_index=10,
                timestamp="2026-02-03T10:00:00",
                esn_name="Alice",
                esn_surname="Brown",
                erasmus_name="Bob",
                erasmus_surname="Green"
            ),
            Assignment(
                esn_index=1,
                erasmus_index=20,
                timestamp="2026-02-03T11:00:00",
                esn_name="Carol",
                esn_surname="White",
                erasmus_name="Dave",
                erasmus_surname="Black"
            )
        ]

        csv_bytes = export_assignments_to_csv(assignments)
        csv_str = csv_bytes.decode('utf-8')

        # Check headers
        assert "ESN_Name,ESN_Surname,Erasmus_Name,Erasmus_Surname,Assignment_Timestamp" in csv_str

        # Check data
        assert "Alice" in csv_str
        assert "Brown" in csv_str
        assert "Bob" in csv_str
        assert "Green" in csv_str
        assert "2026-02-03T10:00:00" in csv_str

        assert "Carol" in csv_str
        assert "Dave" in csv_str

    def test_export_assignments_xlsx(self):
        """Test exporting assignments to Excel."""
        assignments = [
            Assignment(
                esn_index=0,
                erasmus_index=10,
                timestamp="2026-02-03T10:00:00",
                esn_name="Alice",
                esn_surname="Brown",
                erasmus_name="Bob",
                erasmus_surname="Green"
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_assignments.xlsx"
            result_path = export_assignments_to_xlsx(assignments, output_path)

            assert result_path == output_path
            assert output_path.exists()

            # Read back and verify
            df = pd.read_excel(output_path, sheet_name="Assignments")

            assert len(df) == 1
            assert df.iloc[0]["ESN_Name"] == "Alice"
            assert df.iloc[0]["ESN_Surname"] == "Brown"
            assert df.iloc[0]["Erasmus_Name"] == "Bob"
            assert df.iloc[0]["Erasmus_Surname"] == "Green"

    def test_export_empty_assignments_xlsx(self):
        """Test exporting empty assignment list to Excel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_empty.xlsx"
            result_path = export_assignments_to_xlsx([], output_path)

            assert result_path.exists()

            # Should have headers but no data
            df = pd.read_excel(output_path, sheet_name="Assignments")
            assert len(df) == 0
            assert "ESN_Name" in df.columns
            assert "Erasmus_Name" in df.columns

    def test_generate_assignment_filename(self):
        """Test filename generation."""
        filename = generate_assignment_filename()

        assert filename.startswith("assignments_")
        assert len(filename) > len("assignments_")

        # Test with custom prefix
        filename_custom = generate_assignment_filename("buddy_pairs")
        assert filename_custom.startswith("buddy_pairs_")

    def test_csv_export_with_state(self):
        """Test CSV export from AssignmentState."""
        state = AssignmentState()

        state.add_assignment(
            esn_index=0,
            erasmus_index=10,
            esn_name="Alice",
            esn_surname="Brown",
            erasmus_name="Bob",
            erasmus_surname="Green"
        )

        state.add_assignment(
            esn_index=1,
            erasmus_index=20,
            esn_name="Carol",
            esn_surname="White",
            erasmus_name="Dave",
            erasmus_surname="Black"
        )

        csv_bytes = export_assignments_to_csv(state.assignments)
        csv_str = csv_bytes.decode('utf-8')

        # Should have 2 data rows plus header
        lines = csv_str.strip().split('\n')
        assert len(lines) == 3  # header + 2 data rows

    def test_xlsx_export_with_multiple_assignments(self):
        """Test Excel export with multiple assignments."""
        state = AssignmentState()

        for i in range(5):
            state.add_assignment(
                esn_index=i,
                erasmus_index=i * 10,
                esn_name=f"ESN_{i}",
                esn_surname=f"Surname_{i}",
                erasmus_name=f"Erasmus_{i}",
                erasmus_surname=f"Student_{i}"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_multiple.xlsx"
            export_assignments_to_xlsx(state.assignments, output_path)

            df = pd.read_excel(output_path, sheet_name="Assignments")

            assert len(df) == 5
            assert df.iloc[0]["ESN_Name"] == "ESN_0"
            assert df.iloc[4]["ESN_Name"] == "ESN_4"
