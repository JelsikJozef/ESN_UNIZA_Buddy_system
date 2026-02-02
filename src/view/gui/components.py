"""
Reusable UI components for the Streamlit GUI.
"""
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def autodetect_question_columns(columns: List[str]) -> List[str]:
    """
    Detect likely question columns using heuristics.

    Heuristics:
    - Contains "A)" and "B)"
    - Contains newline characters
    """
    detected = []
    for col in columns:
        if not isinstance(col, str):
            continue
        col_lower = col.lower()
        if ("a)" in col_lower and "b)" in col_lower) or "\n" in col:
            detected.append(col)
    return detected


def autodetect_timestamp_column(columns: List[str]) -> Optional[str]:
    """Detect likely timestamp column."""
    for col in columns:
        if not isinstance(col, str):
            continue
        if "timestamp" in col.lower():
            return col
    return None


def autodetect_contact_column(columns: List[str]) -> Optional[str]:
    """Detect likely contact column (whatsapp, phone, etc.)."""
    keywords = ["whatsapp", "phone", "tel", "contact", "email"]
    for col in columns:
        if not isinstance(col, str):
            continue
        col_lower = col.lower()
        for keyword in keywords:
            if keyword in col_lower:
                return col
    return None


def show_dataframe_summary(df: pd.DataFrame, label: str) -> None:
    """Display a summary card for a dataframe."""
    st.subheader(f"{label} Dataset")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))


def show_dataset_preview(df: pd.DataFrame, label: str, max_rows: int = 10) -> None:
    """Show a preview table for a dataset."""
    st.write(f"**Preview (first {max_rows} rows):**")
    st.dataframe(df.head(max_rows), use_container_width=True)


def show_column_list(columns: List[str], label: str) -> None:
    """Show a searchable list of column names."""
    st.write(f"**{label} Columns ({len(columns)}):**")
    search = st.text_input(f"Search {label} columns", key=f"search_{label}")

    if search:
        filtered = [col for col in columns if search.lower() in str(col).lower()]
    else:
        filtered = columns

    if filtered:
        # Show in expander to save space
        with st.expander(f"View columns ({len(filtered)} shown)", expanded=False):
            for i, col in enumerate(filtered, 1):
                st.text(f"{i}. {col}")
    else:
        st.info("No columns match the search.")


def show_question_health_report(
    erasmus_df: pd.DataFrame,
    esn_df: pd.DataFrame,
    question_columns: List[str]
) -> None:
    """Show health report for question columns."""
    if not question_columns:
        st.info("No question columns selected.")
        return

    st.subheader("Question Health Report")

    health_data = []
    for col in question_columns:
        # Calculate validity percentages
        erasmus_valid = 0
        esn_valid = 0

        if col in erasmus_df.columns:
            erasmus_values = erasmus_df[col].dropna().astype(str).str.strip().str.upper()
            erasmus_valid = (erasmus_values.isin(["A", "B"])).sum() / len(erasmus_df) * 100

        if col in esn_df.columns:
            esn_values = esn_df[col].dropna().astype(str).str.strip().str.upper()
            esn_valid = (esn_values.isin(["A", "B"])).sum() / len(esn_df) * 100

        health_data.append({
            "Question": col[:50] + "..." if len(col) > 50 else col,
            "Erasmus Valid %": round(erasmus_valid, 1),
            "ESN Valid %": round(esn_valid, 1),
            "Min Valid %": round(min(erasmus_valid, esn_valid), 1),
        })

    health_df = pd.DataFrame(health_data)

    # Highlight low validity
    def highlight_low_validity(val):
        if isinstance(val, (int, float)) and val < 70:
            return "background-color: #ffcccc"
        return ""

    try:
        # Try pandas >= 2.1 style.map
        styled_df = health_df.style.map(
            highlight_low_validity,
            subset=["Erasmus Valid %", "ESN Valid %", "Min Valid %"]
        )
    except AttributeError:
        # Fallback to older applymap for pandas < 2.1
        styled_df = health_df.style.applymap(
            highlight_low_validity,
            subset=["Erasmus Valid %", "ESN Valid %", "Min Valid %"]
        )

    st.dataframe(styled_df, use_container_width=True)
    st.caption("Warning: Questions with <70% validity (highlighted) may have data quality issues.")


def show_filter_preview(
    df: pd.DataFrame,
    column: str,
    value: str,
    label: str
) -> Tuple[int, int]:
    """
    Show the effect of a filter on a dataframe.

    Returns:
        (original_count, filtered_count)
    """
    original_count = len(df)

    if column not in df.columns:
        st.warning(f"Column '{column}' not found in {label} dataset.")
        return original_count, 0

    filtered_df = df[df[column] == value]
    filtered_count = len(filtered_df)

    st.info(f"{label}: {filtered_count} / {original_count} rows after filter")

    return original_count, filtered_count


def show_timestamp_filter_preview(
    df: pd.DataFrame,
    column: str,
    min_timestamp: str,
    timestamp_format: str,
    label: str
) -> Tuple[int, int]:
    """
    Show the effect of a timestamp filter on a dataframe.

    Returns:
        (original_count, filtered_count)
    """
    original_count = len(df)

    if column not in df.columns:
        st.warning(f"Column '{column}' not found in {label} dataset.")
        return original_count, 0

    try:
        # Parse the cutoff timestamp
        cutoff = pd.to_datetime(
            min_timestamp,
            format=timestamp_format if timestamp_format else None,
            errors='raise'
        )

        # Parse the timestamp column
        timestamp_series = pd.to_datetime(
            df[column],
            format=timestamp_format if timestamp_format else None,
            errors='coerce'
        )

        # Apply filter
        filtered_df = df[timestamp_series >= cutoff]
        filtered_count = len(filtered_df)

        st.info(f"{label}: {filtered_count} / {original_count} rows after timestamp filter (>= {min_timestamp})")

        return original_count, filtered_count
    except Exception as e:
        st.warning(f"Cannot preview timestamp filter: {str(e)}")
        return original_count, 0


def show_error_with_details(error: Exception, title: str = "Error") -> None:
    """Display an error with expandable details."""
    st.error(f"{title}: {str(error)}")

    with st.expander("Show technical details"):
        st.code(str(error))


def build_config_dict(
    input_state,
    config_state,
    erasmus_df: Optional[pd.DataFrame] = None,
    esn_df: Optional[pd.DataFrame] = None
) -> dict:
    """
    Build a config dictionary from GUI state.

    Args:
        input_state: InputState object
        config_state: ConfigState object
        erasmus_df: Optional Erasmus dataframe (for temp file path)
        esn_df: Optional ESN dataframe (for temp file path)

    Returns:
        Configuration dictionary compatible with pipeline
    """
    config = {
        "input": {
            "format": input_state.mode,
            "buddy_interest_column": config_state.buddy_filter_column or "",
            "buddy_interest_value": config_state.buddy_filter_value,
        },
        "schema": {
            "required_columns": config_state.required_columns,
            "identifier_column": config_state.identifier_column,
            "question_columns": config_state.question_columns,
            "answer_encoding": "AB",
        },
        "matching": {
            "metric": "hamming",
            "top_k": config_state.top_k,
        },
        "output": {
            "out_dir": "outputs",
            "per_esner_sheets": config_state.per_esner_sheets,
        },
    }

    # Add timestamp filter if enabled
    if config_state.timestamp_filter_enabled:
        config["input"]["timestamp_min"] = config_state.timestamp_filter_min
        config["input"]["timestamp_column"] = config_state.timestamp_filter_column
        if config_state.timestamp_filter_format:
            config["input"]["timestamp_format"] = config_state.timestamp_filter_format

    return config


def show_validation_identifier_health(
    df: pd.DataFrame,
    column: Optional[str],
    label: str
) -> None:
    """Show health check for identifier column."""
    if not column or column not in df.columns:
        st.warning(f"Identifier column '{column}' not found in {label} dataset.")
        return

    values = df[column]
    is_unique = values.is_unique
    has_missing = values.isna().any()

    col1, col2 = st.columns(2)
    with col1:
        if is_unique:
            st.success("✓ Unique values")
        else:
            st.warning("⚠ Non-unique values (will use row order as fallback)")

    with col2:
        if not has_missing:
            st.success("✓ No missing values")
        else:
            st.warning("⚠ Has missing values (will use row order as fallback)")
