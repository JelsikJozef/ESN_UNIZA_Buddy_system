"""
Session state management for Streamlit GUI.
"""
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.controller.pipeline import PipelineArtifacts


@dataclass
class InputState:
    """State for uploaded and parsed input data."""
    mode: str = "xlsx"  # "xlsx" or "csv"

    # Raw uploaded files (bytes)
    xlsx_file: Optional[bytes] = None
    erasmus_csv_file: Optional[bytes] = None
    esn_csv_file: Optional[bytes] = None

    # Parsed dataframes
    erasmus_df: Optional[pd.DataFrame] = None
    esn_df: Optional[pd.DataFrame] = None

    # Metadata
    xlsx_sheet_names: List[str] = field(default_factory=list)
    erasmus_sheet: Optional[str] = None
    esn_sheet: Optional[str] = None
    csv_separator: str = ","

    # File names
    xlsx_filename: str = ""
    erasmus_csv_filename: str = ""
    esn_csv_filename: str = ""


@dataclass
class ConfigState:
    """State for pipeline configuration."""
    # Filters
    buddy_filter_enabled: bool = True
    buddy_filter_column: Optional[str] = None
    buddy_filter_value: str = "Yes"

    timestamp_filter_enabled: bool = False
    timestamp_filter_column: Optional[str] = None
    timestamp_filter_min: str = ""
    timestamp_filter_format: str = ""

    # Schema
    required_columns: List[str] = field(default_factory=list)
    identifier_column: Optional[str] = None
    question_columns: List[str] = field(default_factory=list)

    # Matching
    top_k: int = 10

    # Output
    per_esner_sheets: bool = True
    include_extra_fields: bool = True
    output_prefix: str = "matching_"


@dataclass
class ResultsState:
    """State for pipeline results."""
    artifacts: Optional[PipelineArtifacts] = None
    selected_esn_index: int = 0

    # For quick access
    esn_names: List[str] = field(default_factory=list)


def init_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    if "input" not in st.session_state:
        st.session_state.input = InputState()

    if "config" not in st.session_state:
        st.session_state.config = ConfigState()

    if "results" not in st.session_state:
        st.session_state.results = ResultsState()

    if "autodetected_questions" not in st.session_state:
        st.session_state.autodetected_questions = []

    if "autodetected_timestamp" not in st.session_state:
        st.session_state.autodetected_timestamp = None

    if "autodetected_contact" not in st.session_state:
        st.session_state.autodetected_contact = None

    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "Input"

    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False

    if "run_logs" not in st.session_state:
        st.session_state.run_logs = []

    if "run_history" not in st.session_state:
        st.session_state.run_history = []


def reset_results() -> None:
    """Clear results state."""
    st.session_state.results = ResultsState()


def get_input_state() -> InputState:
    """Get input state."""
    return st.session_state.input


def get_config_state() -> ConfigState:
    """Get config state."""
    return st.session_state.config


def get_results_state() -> ResultsState:
    """Get results state."""
    return st.session_state.results


def log_message(message: str, level: str = "INFO") -> None:
    """Add a log message to the run logs."""
    st.session_state.run_logs.append({"level": level, "message": message})
