"""
Test universal export with all columns except questions.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from src.controller.assignments import Assignment
from src.view.export_assignments import export_assignments_to_csv, export_assignments_to_xlsx


def test_universal_export_all_columns():
    """Test that export includes ALL columns except questions."""
    # Create sample dataframes with various columns
    esn_df = pd.DataFrame({
        "Name": ["John", "Jane"],
        "Surname": ["Doe", "Smith"],
        "Email": ["john@esn.com", "jane@esn.com"],
        "Phone": ["+421123456", "+421654321"],
        "Facebook": ["john.doe", "jane.smith"],
        "Instagram": ["@johndoe", "@janesmith"],
        "University": ["UNIZA", "UNIZA"],
        "Faculty": ["FRI", "FEI"],
        "Hobbies": ["Sports", "Music"],
        "Allergies": ["None", "Lactose"],
        "Q1_What_is_your_favorite_color": ["Red", "Blue"],
        "Q2_Do_you_like_pizza": ["Yes", "No"],
        "Q3_Favorite_sport": ["Football", "Basketball"]
    })

    erasmus_df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Surname": ["Brown", "Green"],
        "Email": ["alice@mail.com", "bob@mail.com"],
        "WhatsApp": ["+34123456", "+34654321"],
        "Telegram": ["@alice", "@bob"],
        "Home_University": ["Madrid University", "Barcelona University"],
        "Country": ["Spain", "Spain"],
        "Arrival_Date": ["2026-09-01", "2026-09-05"],
        "Departure_Date": ["2027-01-31", "2027-02-15"],
        "Dietary_Restrictions": ["Vegetarian", "None"],
        "Allergies": ["Peanuts", "None"],
        "Emergency_Contact": ["+34999888", "+34888777"],
        "Q1_What_is_your_favorite_color": ["Red", "Green"],
        "Q2_Do_you_like_pizza": ["Yes", "Yes"],
        "Q3_Favorite_sport": ["Football", "Tennis"]
    })

    # Question columns to exclude
    question_columns = [
        "Q1_What_is_your_favorite_color",
        "Q2_Do_you_like_pizza",
        "Q3_Favorite_sport"
    ]

    # Create vectors (encoded question answers)
    esn_vectors = np.array([[0, 1, 2], [1, 0, 3]])
    erasmus_vectors = np.array([[0, 1, 2], [2, 1, 4]])

    # Create assignments
    assignments = [
        Assignment(
            esn_index=0,
            erasmus_index=0,
            timestamp="2026-02-03T10:00:00",
            esn_name="John",
            esn_surname="Doe",
            erasmus_name="Alice",
            erasmus_surname="Brown"
        ),
        Assignment(
            esn_index=1,
            erasmus_index=1,
            timestamp="2026-02-03T10:05:00",
            esn_name="Jane",
            esn_surname="Smith",
            erasmus_name="Bob",
            erasmus_surname="Green"
        )
    ]

    # Test CSV export
    csv_bytes = export_assignments_to_csv(
        assignments,
        esn_df=esn_df,
        erasmus_df=erasmus_df,
        question_columns=question_columns,
        esn_vectors=esn_vectors,
        erasmus_vectors=erasmus_vectors
    )

    csv_str = csv_bytes.decode('utf-8')
    print("=" * 80)
    print("CSV Export Preview (first 500 chars):")
    print("=" * 80)
    print(csv_str[:500])
    print("\n")

    # Verify ALL non-question columns are included
    assert "ESN_Name" in csv_str
    assert "ESN_Email" in csv_str
    assert "ESN_Phone" in csv_str
    assert "ESN_Facebook" in csv_str
    assert "ESN_Instagram" in csv_str
    assert "ESN_University" in csv_str
    assert "ESN_Hobbies" in csv_str
    assert "ESN_Allergies" in csv_str

    assert "Erasmus_Name" in csv_str
    assert "Erasmus_Email" in csv_str
    assert "Erasmus_WhatsApp" in csv_str
    assert "Erasmus_Telegram" in csv_str
    assert "Erasmus_Country" in csv_str
    assert "Erasmus_Arrival_Date" in csv_str
    assert "Erasmus_Dietary_Restrictions" in csv_str
    assert "Erasmus_Emergency_Contact" in csv_str

    # Verify question columns are NOT included
    assert "Q1_What_is_your_favorite_color" not in csv_str
    assert "Q2_Do_you_like_pizza" not in csv_str
    assert "Q3_Favorite_sport" not in csv_str

    # Verify matching count columns
    assert "Matching_Answers" in csv_str
    assert "Compared_Questions" in csv_str

    print("✓ CSV Export contains ALL non-question columns")
    print()

    # Test XLSX export
    output_path = Path("outputs/test_universal_export.xlsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result_path = export_assignments_to_xlsx(
        assignments,
        output_path,
        esn_df=esn_df,
        erasmus_df=erasmus_df,
        question_columns=question_columns,
        esn_vectors=esn_vectors,
        erasmus_vectors=erasmus_vectors
    )

    assert result_path.exists()

    # Read and verify Excel content
    df = pd.read_excel(result_path)

    print("=" * 80)
    print("XLSX Export Columns:")
    print("=" * 80)
    for col in sorted(df.columns):
        print(f"  • {col}")
    print()

    print("=" * 80)
    print("Sample Data (first row):")
    print("=" * 80)
    for col in df.columns[:10]:  # Show first 10 columns
        print(f"  {col}: {df.iloc[0][col]}")
    print("  ...")
    print()

    # Count columns
    esn_cols = [col for col in df.columns if col.startswith("ESN_")]
    erasmus_cols = [col for col in df.columns if col.startswith("Erasmus_")]

    print(f"✓ ESN columns exported: {len(esn_cols)}")
    print(f"✓ Erasmus columns exported: {len(erasmus_cols)}")

    # Verify all non-question columns are present
    expected_esn_cols = [col for col in esn_df.columns if col not in question_columns]
    expected_erasmus_cols = [col for col in erasmus_df.columns if col not in question_columns]

    for col in expected_esn_cols:
        assert f"ESN_{col}" in df.columns, f"Missing ESN column: {col}"

    for col in expected_erasmus_cols:
        assert f"Erasmus_{col}" in df.columns, f"Missing Erasmus column: {col}"

    # Verify question columns are NOT present
    for col in question_columns:
        assert f"ESN_{col}" not in df.columns, f"Question column should be excluded: ESN_{col}"
        assert f"Erasmus_{col}" not in df.columns, f"Question column should be excluded: Erasmus_{col}"

    # Verify matching count
    assert "Matching_Answers" in df.columns
    assert "Compared_Questions" in df.columns

    # John-Alice match: vectors [0,1,2] vs [0,1,2] = 3 matches
    assert df.iloc[0]["Matching_Answers"] == 3
    assert df.iloc[0]["Compared_Questions"] == 3

    # Jane-Bob match: vectors [1,0,3] vs [2,1,4] = 0 matches (none equal)
    assert df.iloc[1]["Compared_Questions"] == 3

    # Clean up
    output_path.unlink()

    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("Universal export includes ALL columns except questions ✓")
    print()


if __name__ == "__main__":
    test_universal_export_all_columns()
