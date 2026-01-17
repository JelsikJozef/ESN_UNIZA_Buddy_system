from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    for sep in [";", ","]:
        try:
            return pd.read_csv(path, sep=sep, engine="python")
        except Exception:
            continue
    raise ValueError(f"Unable to read CSV file with expected delimiters: {path}")


def _read_csv_pair(base_dir: Path, esn_name: str, erasmus_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    esn_path = base_dir / esn_name
    erasmus_path = base_dir / erasmus_name
    esn_df = _read_csv(esn_path)
    erasmus_df = _read_csv(erasmus_path)
    return esn_df, erasmus_df


def _apply_buddy_filter(df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
    if column not in df.columns:
        raise ValueError(f"Missing buddy interest column: {column}")
    return df[df[column] == value].reset_index(drop=True)


def load_tables(config: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    input_cfg = config.get("input", {})
    fmt = (input_cfg.get("format") or "").lower()
    file_path = input_cfg.get("file_path")
    erasmus_csv = input_cfg.get("erasmus_csv")
    esn_csv = input_cfg.get("esn_csv")
    erasmus_sheet = input_cfg.get("erasmus_sheet")
    esn_sheet = input_cfg.get("esn_sheet")
    buddy_column = input_cfg.get("buddy_interest_column")
    buddy_value = input_cfg.get("buddy_interest_value")

    if fmt not in {"csv", "xlsx"}:
        raise ValueError(f"Unsupported input format: {fmt}")
    if not file_path:
        raise ValueError("Input file_path is required")
    if not buddy_column or buddy_value is None:
        raise ValueError("Buddy interest column and value are required")

    base_path = Path(file_path)
    if fmt == "csv":
        if not base_path.exists() or not base_path.is_dir():
            raise FileNotFoundError(f"CSV directory not found: {base_path}")
        if not erasmus_csv or not esn_csv:
            raise ValueError("erasmus_csv and esn_csv must be provided for CSV input")
        esn_df, erasmus_df = _read_csv_pair(base_path, esn_csv, erasmus_csv)
    else:
        workbook = base_path
        if not workbook.exists():
            raise FileNotFoundError(f"XLSX file not found: {workbook}")
        if not erasmus_sheet or not esn_sheet:
            raise ValueError("erasmus_sheet and esn_sheet must be provided for XLSX input")
        erasmus_df = pd.read_excel(workbook, sheet_name=erasmus_sheet)
        esn_df = pd.read_excel(workbook, sheet_name=esn_sheet)

    stats = {
        "esn_loaded": len(esn_df),
        "erasmus_loaded": len(erasmus_df),
    }

    erasmus_filtered = _apply_buddy_filter(erasmus_df, buddy_column, buddy_value)

    stats.update(
        {
            "esn_after_filter": len(esn_df),
            "erasmus_after_filter": len(erasmus_filtered),
        }
    )

    return erasmus_filtered, esn_df.reset_index(drop=True), stats
