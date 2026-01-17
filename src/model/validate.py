from typing import Dict, Iterable, Tuple

import pandas as pd


def _ensure_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{label} missing columns: {', '.join(missing)}")


def validate_tables(erasmus_df: pd.DataFrame, esn_df: pd.DataFrame, config: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    schema_cfg = config.get("schema", {})
    input_cfg = config.get("input", {})
    required_cols = schema_cfg.get("required_columns", [])
    question_cols = schema_cfg.get("question_columns", [])
    identifier_col = schema_cfg.get("identifier_column")
    answer_encoding = schema_cfg.get("answer_encoding")
    buddy_column = input_cfg.get("buddy_interest_column")

    if answer_encoding != "AB":
        raise ValueError(f"Unsupported answer encoding: {answer_encoding}")

    erasmus_required = list(required_cols)
    esn_required = list(required_cols)
    if identifier_col:
        erasmus_required.append(identifier_col)
        esn_required.append(identifier_col)
    if buddy_column:
        erasmus_required.append(buddy_column)

    _ensure_columns(erasmus_df, erasmus_required, "Erasmus dataset")
    _ensure_columns(esn_df, esn_required, "ESN dataset")
    _ensure_columns(erasmus_df, question_cols, "Erasmus dataset")
    _ensure_columns(esn_df, question_cols, "ESN dataset")

    return erasmus_df, esn_df
