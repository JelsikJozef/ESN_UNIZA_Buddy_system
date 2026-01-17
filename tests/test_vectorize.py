import numpy as np
import pandas as pd

from src.model import vectorize


def test_vectorize_respects_configured_order_and_ignores_invalid():
    esn_df = pd.DataFrame([
        {"Name": "A", "Q02": "B", "Q01": "A", "Q03": "C"},
    ])
    erasmus_df = pd.DataFrame([
        {"Name": "B", "Q02": "A", "Q01": "B", "Q03": "A"},
    ])
    config = {"schema": {"question_columns": ["Q03", "Q01", "Q02"], "answer_encoding": "AB"}}

    esn_vec, erasmus_vec = vectorize.vectorize_tables(esn_df, erasmus_df, config)

    assert esn_vec.question_columns == ["Q03", "Q01", "Q02"]
    # Q03 invalid -> nan, Q01 A -> 0, Q02 B ->1
    assert np.isnan(esn_vec.vectors[0, 0])
    assert esn_vec.vectors[0, 1] == 0
    assert esn_vec.vectors[0, 2] == 1
    # Erasmus Q03 A ->0, Q01 B ->1, Q02 A ->0
    assert erasmus_vec.vectors[0].tolist() == [0.0, 1.0, 0.0]
