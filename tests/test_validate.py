import pandas as pd
import pytest

from src.model import validate


def test_validate_missing_required_column_raises():
    esn_df = pd.DataFrame({"Name": ["A"], "Q01": ["A"]})
    erasmus_df = pd.DataFrame({"Name": ["B"], "Q01": ["B"]})
    config = {
        "schema": {
            "required_columns": ["Name", "Surname"],
            "question_columns": ["Q01"],
            "answer_encoding": "AB",
        }
    }
    with pytest.raises(ValueError):
        validate.validate_tables(esn_df, erasmus_df, config)
