from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class VectorizedTable:
    dataframe: pd.DataFrame
    vectors: np.ndarray
    question_columns: List[str]


def _encode_value(value) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip().upper()
    if text == "A":
        return 0.0
    if text == "B":
        return 1.0
    return np.nan


def _vectorize_single(df: pd.DataFrame, question_columns: List[str]) -> np.ndarray:
    rows = len(df)
    cols = len(question_columns)
    matrix = np.empty((rows, cols), dtype=float)
    for row_idx, (_, row) in enumerate(df.iterrows()):
        for col_idx, column in enumerate(question_columns):
            matrix[row_idx, col_idx] = _encode_value(row[column])
    return matrix


def vectorize_tables(esn_df: pd.DataFrame, erasmus_df: pd.DataFrame, config: Dict) -> Tuple[VectorizedTable, VectorizedTable]:
    question_columns = config.get("schema", {}).get("question_columns", [])
    esn_vectors = _vectorize_single(esn_df, question_columns)
    erasmus_vectors = _vectorize_single(erasmus_df, question_columns)
    return VectorizedTable(esn_df, esn_vectors, question_columns), VectorizedTable(erasmus_df, erasmus_vectors, question_columns)
