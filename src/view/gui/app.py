"""
ESN UNIZA Buddy Matching System - Streamlit GUI
Main application entry point.
"""
import io
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
import yaml

# Add project root to path if running standalone
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try absolute imports first (when run as module), fall back to relative
try:
    from src.view.gui import components, state
    from src.controller.pipeline import PipelineArtifacts, compute_comparison_stats, run_pipeline_from_config
except ModuleNotFoundError:
    # If running standalone, use relative imports
    import components
    import state
    from ...controller.pipeline import PipelineArtifacts, compute_comparison_stats, run_pipeline_from_config

# Page configuration
st.set_page_config(
    page_title="ESN UNIZA Buddy Matching",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point."""
    # Initialize session state
    state.init_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.title("ESN UNIZA")
        st.subheader("Buddy Matching System")
        st.markdown("---")

        # Navigation
        screen = st.radio(
            "Navigation",
            ["Input", "Configure", "Run", "Results", "Export", "Logs"],
            key="nav_radio"
        )
        st.session_state.current_screen = screen

        st.markdown("---")

        # Debug mode toggle
        debug_mode = st.checkbox("Debug Mode", value=st.session_state.debug_mode)
        st.session_state.debug_mode = debug_mode

        st.markdown("---")
        st.caption("ESN UNIZA © 2026")

    # Main content area
    if screen == "Input":
        show_input_screen()
    elif screen == "Configure":
        show_configure_screen()
    elif screen == "Run":
        show_run_screen()
    elif screen == "Results":
        show_results_screen()
    elif screen == "Export":
        show_export_screen()
    elif screen == "Logs":
        show_logs_screen()


def show_input_screen():
    """Screen 1: Input data loading."""
    st.title("Input Data")

    input_state = state.get_input_state()

    # A) Input mode selector
    st.subheader("1. Select Input Mode")
    mode = st.radio(
        "Input Format",
        ["XLSX (one file with two sheets)", "CSV (two separate files)"],
        horizontal=True,
        key="input_mode_radio"
    )

    if "XLSX" in mode:
        input_state.mode = "xlsx"
    else:
        input_state.mode = "csv"

    st.markdown("---")

    # B) XLSX mode
    if input_state.mode == "xlsx":
        st.subheader("2. Upload XLSX File")

        uploaded_file = st.file_uploader(
            "Upload Excel workbook",
            type=["xlsx"],
            key="xlsx_uploader"
        )

        if uploaded_file:
            input_state.xlsx_file = uploaded_file.read()
            input_state.xlsx_filename = uploaded_file.name

            # Read sheet names
            try:
                with io.BytesIO(input_state.xlsx_file) as buffer:
                    excel_file = pd.ExcelFile(buffer)
                    input_state.xlsx_sheet_names = excel_file.sheet_names

                st.success(f"Loaded workbook: {input_state.xlsx_filename}")
                st.info(f"Available sheets: {', '.join(input_state.xlsx_sheet_names)}")

                # Sheet selectors
                col1, col2 = st.columns(2)
                with col1:
                    erasmus_sheet = st.selectbox(
                        "Erasmus Sheet",
                        input_state.xlsx_sheet_names,
                        key="erasmus_sheet_select"
                    )
                    input_state.erasmus_sheet = erasmus_sheet

                with col2:
                    esn_sheet = st.selectbox(
                        "ESN Sheet",
                        input_state.xlsx_sheet_names,
                        key="esn_sheet_select"
                    )
                    input_state.esn_sheet = esn_sheet

            except Exception as e:
                components.show_error_with_details(e, "Failed to read XLSX file")

    # C) CSV mode
    else:
        st.subheader("2. Upload CSV Files")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Erasmus CSV**")
            erasmus_file = st.file_uploader(
                "Upload Erasmus CSV",
                type=["csv"],
                key="erasmus_csv_uploader"
            )
            if erasmus_file:
                input_state.erasmus_csv_file = erasmus_file.read()
                input_state.erasmus_csv_filename = erasmus_file.name
                st.success(f"Loaded: {erasmus_file.name}")

        with col2:
            st.write("**ESN CSV**")
            esn_file = st.file_uploader(
                "Upload ESN CSV",
                type=["csv"],
                key="esn_csv_uploader"
            )
            if esn_file:
                input_state.esn_csv_file = esn_file.read()
                input_state.esn_csv_filename = esn_file.name
                st.success(f"Loaded: {esn_file.name}")

        # Delimiter selector
        st.write("**CSV Settings**")
        delimiter = st.radio(
            "Delimiter",
            ["Auto-detect", "Comma (,)", "Semicolon (;)"],
            horizontal=True,
            key="csv_delimiter_radio"
        )

        if delimiter == "Comma (,)":
            input_state.csv_separator = ","
        elif delimiter == "Semicolon (;)":
            input_state.csv_separator = ";"
        else:
            input_state.csv_separator = None  # Auto-detect

    st.markdown("---")

    # D) Load & Preview button
    st.subheader("3. Load and Preview Data")

    if st.button("Load Data", type="primary", key="load_data_btn"):
        try:
            with st.spinner("Loading data..."):
                load_data_from_uploads()
            st.success("Data loaded successfully!")
        except Exception as e:
            components.show_error_with_details(e, "Failed to load data")

    # Show preview if data is loaded
    if input_state.erasmus_df is not None and input_state.esn_df is not None:
        st.markdown("---")
        st.subheader("Dataset Summary")

        col1, col2 = st.columns(2)
        with col1:
            components.show_dataframe_summary(input_state.erasmus_df, "Erasmus")
        with col2:
            components.show_dataframe_summary(input_state.esn_df, "ESN")

        # Preview tables
        st.markdown("---")
        st.subheader("Data Preview")

        tab1, tab2 = st.tabs(["Erasmus Preview", "ESN Preview"])

        with tab1:
            components.show_dataset_preview(input_state.erasmus_df, "Erasmus")
            components.show_column_list(list(input_state.erasmus_df.columns), "Erasmus")

        with tab2:
            components.show_dataset_preview(input_state.esn_df, "ESN")
            components.show_column_list(list(input_state.esn_df.columns), "ESN")

        # E) Autodetection hints
        st.markdown("---")
        st.subheader("Autodetected Suggestions")

        all_columns = list(set(input_state.erasmus_df.columns) & set(input_state.esn_df.columns))

        # Detect questions
        autodetected_questions = components.autodetect_question_columns(all_columns)
        st.session_state.autodetected_questions = autodetected_questions
        st.info(f"Detected {len(autodetected_questions)} potential question columns")

        # Detect timestamp
        autodetected_timestamp = components.autodetect_timestamp_column(all_columns)
        st.session_state.autodetected_timestamp = autodetected_timestamp
        if autodetected_timestamp:
            st.info(f"Detected timestamp column: {autodetected_timestamp}")

        # Detect contact
        autodetected_contact = components.autodetect_contact_column(list(input_state.erasmus_df.columns))
        st.session_state.autodetected_contact = autodetected_contact
        if autodetected_contact:
            st.info(f"Detected contact column: {autodetected_contact}")

        st.success("✓ Ready to configure matching parameters")


def load_data_from_uploads():
    """Load dataframes from uploaded files."""
    input_state = state.get_input_state()

    if input_state.mode == "xlsx":
        if not input_state.xlsx_file:
            raise ValueError("No XLSX file uploaded")
        if not input_state.erasmus_sheet or not input_state.esn_sheet:
            raise ValueError("Please select both Erasmus and ESN sheets")

        with io.BytesIO(input_state.xlsx_file) as buffer:
            input_state.erasmus_df = pd.read_excel(buffer, sheet_name=input_state.erasmus_sheet)
            input_state.esn_df = pd.read_excel(buffer, sheet_name=input_state.esn_sheet)

    else:  # CSV mode
        if not input_state.erasmus_csv_file or not input_state.esn_csv_file:
            raise ValueError("Please upload both Erasmus and ESN CSV files")

        # Try to read with specified or auto-detected separator
        sep = input_state.csv_separator or None

        input_state.erasmus_df = read_csv_with_fallback(
            input_state.erasmus_csv_file,
            sep,
            "Erasmus"
        )
        input_state.esn_df = read_csv_with_fallback(
            input_state.esn_csv_file,
            sep,
            "ESN"
        )

    # Normalize headers using the ingest module's normalization
    from src.model.ingest import _normalize_column_name
    input_state.erasmus_df.columns = [_normalize_column_name(col) for col in input_state.erasmus_df.columns]
    input_state.esn_df.columns = [_normalize_column_name(col) for col in input_state.esn_df.columns]


def read_csv_with_fallback(file_bytes: bytes, separator: Optional[str], label: str) -> pd.DataFrame:
    """Read CSV with fallback separator detection."""
    separators = [separator] if separator else [",", ";"]

    for sep in separators:
        try:
            with io.BytesIO(file_bytes) as buffer:
                df = pd.read_csv(buffer, sep=sep, engine="python")
                if len(df.columns) > 1:  # Valid parse
                    return df
        except Exception:
            continue

    raise ValueError(f"Failed to parse {label} CSV file with any known delimiter")


def apply_config_to_state(config_dict: dict, config_state) -> None:
    """
    Apply loaded YAML config to ConfigState.

    Args:
        config_dict: Parsed YAML configuration dictionary
        config_state: ConfigState instance to update
    """
    # Apply filters
    filters = config_dict.get("filters", {})

    # Buddy filter
    buddy_filter = filters.get("buddy_interest", {})
    if "enabled" in buddy_filter:
        config_state.buddy_filter_enabled = buddy_filter["enabled"]
    if "column" in buddy_filter:
        config_state.buddy_filter_column = buddy_filter["column"]
    if "value" in buddy_filter:
        config_state.buddy_filter_value = buddy_filter["value"]

    # Timestamp filter
    timestamp_filter = filters.get("timestamp_min", {})
    if "enabled" in timestamp_filter:
        config_state.timestamp_filter_enabled = timestamp_filter["enabled"]
    if "column" in timestamp_filter:
        config_state.timestamp_filter_column = timestamp_filter["column"]
    if "min_value" in timestamp_filter:
        config_state.timestamp_filter_min = timestamp_filter["min_value"]
    if "format" in timestamp_filter:
        config_state.timestamp_filter_format = timestamp_filter.get("format", "")

    # Apply schema
    schema = config_dict.get("schema", {})
    if "required_columns" in schema:
        config_state.required_columns = schema["required_columns"]
    if "identifier_column" in schema:
        config_state.identifier_column = schema["identifier_column"]
    if "question_columns" in schema:
        config_state.question_columns = schema["question_columns"]

    # Apply matching settings
    matching = config_dict.get("matching", {})
    if "top_k" in matching:
        config_state.top_k = matching["top_k"]

    # Apply output settings
    output = config_dict.get("output", {})
    if "per_esner_sheets" in output:
        config_state.per_esner_sheets = output["per_esner_sheets"]
    if "include_extra_fields" in output:
        config_state.include_extra_fields = output["include_extra_fields"]
    if "out_prefix" in output:
        config_state.output_prefix = output["out_prefix"]


def show_configure_screen():
    """Screen 2: Configure matching parameters."""
    st.title("Configure Matching")

    input_state = state.get_input_state()
    config_state = state.get_config_state()

    # Check if data is loaded
    if input_state.erasmus_df is None or input_state.esn_df is None:
        st.warning("Please load data first from the Input screen.")
        return

    erasmus_df = input_state.erasmus_df
    esn_df = input_state.esn_df

    # Show current configuration summary
    with st.expander("Current Configuration Summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Question Columns", len(config_state.question_columns))
            st.metric("Required Columns", len(config_state.required_columns))
        with col2:
            st.metric("Top K", config_state.top_k)
            buddy_status = "✓ Enabled" if config_state.buddy_filter_enabled else "✗ Disabled"
            st.metric("Buddy Filter", buddy_status)
        with col3:
            timestamp_status = "✓ Enabled" if config_state.timestamp_filter_enabled else "✗ Disabled"
            st.metric("Timestamp Filter", timestamp_status)
            st.metric("Per-ESN Sheets", "✓ Yes" if config_state.per_esner_sheets else "✗ No")

    st.markdown("---")

    # Get column lists
    erasmus_cols = list(erasmus_df.columns)
    esn_cols = list(esn_df.columns)
    common_cols = list(set(erasmus_cols) & set(esn_cols))

    # Block A: Filters
    st.subheader("A. Filters")

    with st.expander("Buddy Interest Filter (Erasmus only)", expanded=True):
        buddy_enabled = st.checkbox(
            "Enable buddy interest filter",
            value=config_state.buddy_filter_enabled
        )
        config_state.buddy_filter_enabled = buddy_enabled

        if buddy_enabled:
            col1, col2 = st.columns(2)
            with col1:
                # Find index for selectbox
                buddy_col_idx = 0
                if config_state.buddy_filter_column and config_state.buddy_filter_column in erasmus_cols:
                    buddy_col_idx = erasmus_cols.index(config_state.buddy_filter_column)

                buddy_col = st.selectbox(
                    "Buddy interest column",
                    erasmus_cols,
                    index=buddy_col_idx
                )
                config_state.buddy_filter_column = buddy_col

            with col2:
                buddy_val = st.text_input(
                    "Accepted value",
                    value=config_state.buddy_filter_value
                )
                config_state.buddy_filter_value = buddy_val

            # Live preview
            if buddy_col and buddy_val:
                components.show_filter_preview(erasmus_df, buddy_col, buddy_val, "Erasmus")

    with st.expander("Timestamp Filter (optional)", expanded=False):
        timestamp_enabled = st.checkbox(
            "Enable timestamp filter",
            value=config_state.timestamp_filter_enabled
        )
        config_state.timestamp_filter_enabled = timestamp_enabled

        if timestamp_enabled:
            # Find index for selectbox
            timestamp_col_idx = 0
            if st.session_state.autodetected_timestamp and st.session_state.autodetected_timestamp in common_cols:
                timestamp_col_idx = common_cols.index(st.session_state.autodetected_timestamp)
            elif config_state.timestamp_filter_column and config_state.timestamp_filter_column in common_cols:
                timestamp_col_idx = common_cols.index(config_state.timestamp_filter_column)

            timestamp_col = st.selectbox(
                "Timestamp column",
                common_cols,
                index=timestamp_col_idx
            )
            config_state.timestamp_filter_column = timestamp_col

            col1, col2 = st.columns(2)
            with col1:
                timestamp_min = st.text_input(
                    "Minimum timestamp (e.g., 1/22/2026 14:10:12)",
                    value=config_state.timestamp_filter_min
                )
                config_state.timestamp_filter_min = timestamp_min

            with col2:
                timestamp_format = st.text_input(
                    "Format (optional, e.g., %m/%d/%Y %H:%M:%S)",
                    value=config_state.timestamp_filter_format
                )
                config_state.timestamp_filter_format = timestamp_format

            # Live preview
            if timestamp_col and timestamp_min:
                components.show_timestamp_filter_preview(
                    erasmus_df,
                    timestamp_col,
                    timestamp_min,
                    timestamp_format,
                    "Erasmus"
                )

    st.markdown("---")

    # Block B: Schema
    st.subheader("B. Schema")

    with st.expander("Required Columns", expanded=True):
        default_required = ["Timestamp", "Name", "Surname"]
        available_required = [col for col in default_required if col in common_cols]

        # Use config state if available, otherwise use defaults
        default_value = config_state.required_columns if config_state.required_columns else available_required

        required_cols = st.multiselect(
            "Select required columns (must be in both datasets)",
            common_cols,
            default=default_value
        )
        config_state.required_columns = required_cols

        if not required_cols:
            st.warning("At least one required column should be selected")

    with st.expander("Identifier Column (for tie-breaking)", expanded=True):
        default_identifier = st.session_state.autodetected_timestamp or (common_cols[0] if common_cols else None)

        # Use config state if available, otherwise use defaults
        if not config_state.identifier_column and default_identifier:
            config_state.identifier_column = default_identifier

        # Find index for selectbox
        identifier_idx = 0
        if config_state.identifier_column and config_state.identifier_column in common_cols:
            identifier_idx = common_cols.index(config_state.identifier_column)
        elif default_identifier and default_identifier in common_cols:
            identifier_idx = common_cols.index(default_identifier)

        identifier_col = st.selectbox(
            "Identifier column",
            common_cols,
            index=identifier_idx
        )
        config_state.identifier_column = identifier_col

        if identifier_col:
            st.write("**Health Check:**")
            components.show_validation_identifier_health(erasmus_df, identifier_col, "Erasmus")
            components.show_validation_identifier_health(esn_df, identifier_col, "ESN")

    st.markdown("---")

    # Block C: Question columns
    st.subheader("C. Question Columns")

    st.write(f"Select columns to use for matching (from {len(common_cols)} common columns)")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Select Autodetected"):
            config_state.question_columns = st.session_state.autodetected_questions.copy()
            st.rerun()
    with col2:
        if st.button("Clear Selection"):
            config_state.question_columns = []
            st.rerun()
    with col3:
        st.metric("Selected", len(config_state.question_columns))

    question_cols = st.multiselect(
        "Question columns",
        common_cols,
        default=config_state.question_columns
    )
    config_state.question_columns = question_cols

    if question_cols:
        st.success(f"✓ {len(question_cols)} question columns selected")

        # Question health report
        if st.checkbox("Show Question Health Report", value=False):
            components.show_question_health_report(erasmus_df, esn_df, question_cols)
    else:
        st.warning("Please select at least one question column")

    st.markdown("---")

    # Block D: Matching and Output
    st.subheader("D. Matching and Output")

    with st.expander("Matching Settings", expanded=True):
        st.write("**Metric:** Hamming distance (fixed for MVP)")

        top_k = st.slider(
            "Top K matches per ESN member",
            min_value=1,
            max_value=min(50, len(erasmus_df)),
            value=config_state.top_k
        )
        config_state.top_k = top_k

    with st.expander("Output Settings", expanded=True):
        per_esner = st.checkbox(
            "Generate per-ESN-member sheets",
            value=config_state.per_esner_sheets
        )
        config_state.per_esner_sheets = per_esner

        include_extra = st.checkbox(
            "Include extra Erasmus fields in output",
            value=config_state.include_extra_fields
        )
        config_state.include_extra_fields = include_extra

        output_prefix = st.text_input(
            "Output filename prefix",
            value=config_state.output_prefix
        )
        config_state.output_prefix = output_prefix

    st.markdown("---")

    # Config export/import
    st.subheader("Config Export / Import")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Config to YAML"):
            try:
                config_dict = components.build_config_dict(input_state, config_state)
                yaml_str = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)

                st.download_button(
                    label="Download config.yml",
                    data=yaml_str,
                    file_name="buddy_matching_config.yml",
                    mime="text/yaml"
                )
            except Exception as e:
                components.show_error_with_details(e, "Failed to export config")

    with col2:
        uploaded_config = st.file_uploader(
            "Import YAML config",
            type=["yml", "yaml"]
        )

        if uploaded_config:
            try:
                config_dict = yaml.safe_load(uploaded_config)
                apply_config_to_state(config_dict, config_state)
                st.success("Config imported successfully")
            except Exception as e:
                components.show_error_with_details(e, "Failed to import config")


def show_run_screen():
    """Screen 3: Run the matching pipeline."""
    st.title("Run Matching")

    input_state = state.get_input_state()
    config_state = state.get_config_state()

    # A) Pre-run checklist
    st.subheader("Pre-run Checklist")

    checks = []

    # Check 1: Input loaded
    if input_state.erasmus_df is not None and input_state.esn_df is not None:
        checks.append(("✓", "Input data loaded", True))
    else:
        checks.append(("✗", "Input data NOT loaded - Go to Input screen", False))

    # Check 2: Questions selected
    if config_state.question_columns:
        checks.append(("✓", f"{len(config_state.question_columns)} question columns selected", True))
    else:
        checks.append(("✗", "No question columns selected - Go to Configure screen", False))

    # Check 3: Buddy filter configured
    if config_state.buddy_filter_enabled:
        if config_state.buddy_filter_column:
            checks.append(("✓", "Buddy filter configured", True))
        else:
            checks.append(("✗", "Buddy filter enabled but column not selected - Go to Configure screen", False))
    else:
        checks.append(("ℹ", "Buddy filter disabled (optional)", True))

    # Check 4: Required columns
    if config_state.required_columns:
        checks.append(("✓", f"{len(config_state.required_columns)} required columns selected", True))
    else:
        checks.append(("⚠", "No required columns selected (recommended to select at least Name, Surname)", True))

    # Display checks
    for symbol, message, passed in checks:
        if passed:
            if symbol == "✓":
                st.success(f"{symbol} {message}")
            else:
                st.info(f"{symbol} {message}")
        else:
            st.error(f"{symbol} {message}")

    all_passed = all(check[2] for check in checks if check[0] in ["✓", "✗"])

    st.markdown("---")

    # B) Run button
    st.subheader("Run Pipeline")

    if not all_passed:
        st.warning("Please complete the checklist before running.")
        return

    col1, col2 = st.columns([1, 3])

    with col1:
        run_button = st.button("Run Matching", type="primary")

    with col2:
        st.caption("This will process your data and generate matching results.")

    if run_button:
        run_matching_pipeline()

    # C) Logs panel
    if st.session_state.run_logs:
        st.markdown("---")
        st.subheader("Run Logs")

        log_container = st.container()
        with log_container:
            for log in st.session_state.run_logs[-20:]:  # Show last 20 logs
                level = log.get("level", "INFO")
                message = log.get("message", "")

                if level == "ERROR":
                    st.error(message)
                elif level == "WARNING":
                    st.warning(message)
                elif level == "SUCCESS":
                    st.success(message)
                else:
                    st.info(message)


def run_matching_pipeline():
    """Execute the matching pipeline with progress tracking."""
    input_state = state.get_input_state()
    config_state = state.get_config_state()

    # Clear previous logs
    st.session_state.run_logs = []

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Build config
        state.log_message("Building configuration...", "INFO")
        status_text.text("Building configuration...")
        progress_bar.progress(10)

        config = components.build_config_dict(input_state, config_state)

        # Prepare dataframes
        state.log_message("Preparing data...", "INFO")
        status_text.text("Preparing data...")
        progress_bar.progress(20)

        erasmus_df = input_state.erasmus_df.copy()
        esn_df = input_state.esn_df.copy()

        # Apply timestamp filter if enabled
        if config_state.timestamp_filter_enabled and config_state.timestamp_filter_column and config_state.timestamp_filter_min:
            original_count = len(erasmus_df)
            try:
                # Parse the cutoff timestamp
                cutoff = pd.to_datetime(
                    config_state.timestamp_filter_min,
                    format=config_state.timestamp_filter_format if config_state.timestamp_filter_format else None,
                    errors='raise'
                )

                # Parse the timestamp column
                timestamp_series = pd.to_datetime(
                    erasmus_df[config_state.timestamp_filter_column],
                    format=config_state.timestamp_filter_format if config_state.timestamp_filter_format else None,
                    errors='coerce'
                )

                # Apply filter
                erasmus_df = erasmus_df[timestamp_series >= cutoff].copy().reset_index(drop=True)
                filtered_count = len(erasmus_df)

                state.log_message(
                    f"Applied timestamp filter: {filtered_count}/{original_count} Erasmus students (>= {config_state.timestamp_filter_min})",
                    "INFO"
                )
            except Exception as e:
                state.log_message(f"Warning: Failed to apply timestamp filter: {str(e)}", "WARNING")
                st.warning(f"Failed to apply timestamp filter: {str(e)}")

        # Apply buddy filter if enabled
        if config_state.buddy_filter_enabled and config_state.buddy_filter_column:
            original_count = len(erasmus_df)
            erasmus_df = erasmus_df[
                erasmus_df[config_state.buddy_filter_column] == config_state.buddy_filter_value
            ].reset_index(drop=True)
            filtered_count = len(erasmus_df)
            state.log_message(
                f"Applied buddy filter: {filtered_count}/{original_count} Erasmus students",
                "INFO"
            )

        # Stage 1: Ingest (skipped, using loaded data)
        state.log_message("Stage 1/6: Ingest - Using uploaded data", "INFO")
        status_text.text("Stage 1/6: Ingest")
        progress_bar.progress(30)

        # Run pipeline
        state.log_message("Stage 2/6: Validate", "INFO")
        status_text.text("Stage 2/6: Validate")
        progress_bar.progress(40)

        state.log_message("Stage 3/6: Vectorize", "INFO")
        status_text.text("Stage 3/6: Vectorize")
        progress_bar.progress(50)

        state.log_message("Stage 4/6: Match", "INFO")
        status_text.text("Stage 4/6: Match")
        progress_bar.progress(60)

        state.log_message("Stage 5/6: Rank", "INFO")
        status_text.text("Stage 5/6: Rank")
        progress_bar.progress(70)

        state.log_message("Stage 6/6: Export", "INFO")
        status_text.text("Stage 6/6: Export")
        progress_bar.progress(80)

        # Run the pipeline
        artifacts = run_pipeline_from_config(
            config,
            debug=st.session_state.debug_mode,
            input_override=(erasmus_df, esn_df)
        )

        progress_bar.progress(100)
        status_text.text("Complete!")

        # Store results
        results_state = state.get_results_state()
        results_state.artifacts = artifacts

        # Build ESN names list
        results_state.esn_names = [
            f"{row.get('Name', '')} {row.get('Surname', '')}".strip()
            for _, row in artifacts.esn_df.iterrows()
        ]

        state.log_message("Pipeline completed successfully!", "SUCCESS")
        st.success("✓ Matching completed successfully!")

        # Add to run history
        st.session_state.run_history.append({
            "timestamp": datetime.now().isoformat(),
            "esn_count": len(artifacts.esn_df),
            "erasmus_count": len(artifacts.erasmus_df),
            "question_count": len(artifacts.question_columns),
            "status": "success"
        })

    except Exception as e:
        progress_bar.progress(100)
        status_text.text("Error")

        error_msg = str(e)
        state.log_message(f"Pipeline failed: {error_msg}", "ERROR")

        st.error(f"Pipeline failed: {error_msg}")

        if st.session_state.debug_mode:
            with st.expander("Show full traceback"):
                st.code(traceback.format_exc())

        # Add to run history
        st.session_state.run_history.append({
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "error": error_msg
        })


def show_results_screen():
    """Screen 4: Interactive results browser."""
    st.title("Results")

    results_state = state.get_results_state()
    assignment_state = state.get_assignment_state()

    if not results_state.artifacts:
        st.warning("No results available. Please run the matching pipeline first.")
        return

    artifacts = results_state.artifacts

    # A) Summary cards
    st.subheader("Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("ESN Members", len(artifacts.esn_df))

    with col2:
        st.metric("Erasmus Students", artifacts.stats.get("erasmus_after_filter", len(artifacts.erasmus_df)))

    with col3:
        st.metric("Questions", len(artifacts.question_columns))

    with col4:
        st.metric("Top K", artifacts.config.get("matching", {}).get("top_k", 10))

    with col5:
        st.metric("Assignments", assignment_state.get_assignment_count())

    st.markdown("---")

    # B) ESN member selection
    st.subheader("Browse Matches by ESN Member")

    esn_names = results_state.esn_names

    selected_name = st.selectbox(
        "Select ESN Member",
        esn_names,
        index=results_state.selected_esn_index,
        key="esn_member_selector"
    )

    results_state.selected_esn_index = esn_names.index(selected_name)
    esn_idx = results_state.selected_esn_index

    # Get the ranking for this ESN member
    ranking = artifacts.rankings[esn_idx]
    esn_row = artifacts.esn_df.iloc[esn_idx]

    st.info(f"Showing top {len(ranking.candidates)} matches for **{selected_name}**")

    # C) Ranked matches table
    st.subheader("Ranked Matches")

    matches_data = []
    assigned_indices = assignment_state.get_assigned_erasmus_indices()

    for rank_num, candidate in enumerate(ranking.candidates, start=1):
        student_row = artifacts.erasmus_df.iloc[candidate.erasmus_index]

        # Check if this student is already assigned
        is_assigned = candidate.erasmus_index in assigned_indices

        # Compute accurate comparison stats
        esn_vector = artifacts.esn_vectors[esn_idx]
        student_vector = artifacts.erasmus_vectors[candidate.erasmus_index]

        compared_count, same_count, diff_count = compute_comparison_stats(
            esn_vector,
            student_vector,
            candidate.distance
        )

        # Find contact column
        contact_col = components.autodetect_contact_column(list(artifacts.erasmus_df.columns))
        contact_value = student_row.get(contact_col, "") if contact_col else ""

        match_row = {
            "Rank": rank_num,
            "Name": student_row.get("Name", ""),
            "Surname": student_row.get("Surname", ""),
            "Status": "ASSIGNED" if is_assigned else "Available",
            "Contact": contact_value,
            "Compared Questions": compared_count,
            "Same Answers": same_count,
            "Different Answers": diff_count,
            "_erasmus_index": candidate.erasmus_index,  # Hidden field for assignment logic
        }

        # Add extra fields if configured
        if artifacts.config.get("output", {}).get("per_esner_sheets", True):
            for col in artifacts.erasmus_df.columns:
                if col in artifacts.question_columns or col in match_row.keys():
                    continue
                value = student_row.get(col, "")
                if pd.notna(value) and str(value).strip():
                    match_row[col] = value

        matches_data.append(match_row)

    matches_df = pd.DataFrame(matches_data)

    # Display table without the hidden _erasmus_index column
    display_df = matches_df.drop(columns=["_erasmus_index"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # C1) Manual Assignment Section
    st.markdown("---")
    st.subheader("Manual Assignment")

    # Get available students (not already assigned)
    available_matches = [m for m in matches_data if m["Status"] == "Available"]

    if available_matches:
        col_assign1, col_assign2 = st.columns([3, 1])

        with col_assign1:
            # Create selection options
            selection_options = [
                f"Rank {m['Rank']}: {m['Name']} {m['Surname']}"
                for m in available_matches
            ]

            selected_option = st.selectbox(
                "Select a student to assign",
                selection_options,
                key=f"assign_select_{esn_idx}"
            )

            # Find the selected match
            selected_rank = int(selected_option.split(":")[0].replace("Rank ", ""))
            selected_match = next(m for m in available_matches if m['Rank'] == selected_rank)

        with col_assign2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            assign_button = st.button(
                "Assign to this ESN member",
                key=f"assign_btn_{esn_idx}",
                type="primary"
            )

        if assign_button:
            try:
                # Create assignment
                assignment_state.add_assignment(
                    esn_index=esn_idx,
                    erasmus_index=selected_match["_erasmus_index"],
                    esn_name=esn_row.get("Name", ""),
                    esn_surname=esn_row.get("Surname", ""),
                    erasmus_name=selected_match["Name"],
                    erasmus_surname=selected_match["Surname"]
                )

                st.success(
                    f"Student {selected_match['Name']} {selected_match['Surname']} "
                    f"assigned to ESN member {selected_name}."
                )
                st.rerun()

            except ValueError as e:
                st.error(str(e))
    else:
        st.info("All students in the ranking are already assigned.")

    # Download button for this ESN member
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"Download matches for {selected_name} as CSV",
        data=csv,
        file_name=f"matches_{selected_name.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # D) Difference details
    st.subheader("Match Details")

    selected_rank = st.selectbox(
        "Select a match to view question-by-question comparison",
        range(1, len(ranking.candidates) + 1),
        format_func=lambda x: f"Rank {x}: {matches_data[x-1]['Name']} {matches_data[x-1]['Surname']}",
        key="match_detail_selector"
    )

    if selected_rank:
        show_match_details(artifacts, esn_idx, ranking.candidates[selected_rank - 1])


def show_match_details(artifacts: PipelineArtifacts, esn_idx: int, candidate):
    """Show detailed question-by-question comparison."""
    esn_row = artifacts.esn_df.iloc[esn_idx]
    student_row = artifacts.erasmus_df.iloc[candidate.erasmus_index]

    esn_vector = artifacts.esn_vectors[esn_idx]
    student_vector = artifacts.erasmus_vectors[candidate.erasmus_index]
