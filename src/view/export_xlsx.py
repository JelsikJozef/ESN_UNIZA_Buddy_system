from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.model.rank import ESNRanking


def _safe_sheet_name(name: str) -> str:
    safe = "".join(c for c in name if c not in '[]:*?/\\')
    return safe[:31] if safe else "Sheet"


def _build_summary(stats: Dict, config: Dict, esn_count: int, erasmus_count: int) -> pd.DataFrame:
    schema_cfg = config.get("schema", {})
    matching_cfg = config.get("matching", {})
    question_cols = schema_cfg.get("question_columns", [])
    rows = [
        {"Metric": "Run Timestamp", "Value": datetime.utcnow().isoformat()},
        {"Metric": "Number of ESN members", "Value": esn_count},
        {"Metric": "Number of Erasmus students (filtered)", "Value": stats.get("erasmus_after_filter", erasmus_count)},
        {"Metric": "Question Count", "Value": len(question_cols)},
        {"Metric": "Matching Metric", "Value": matching_cfg.get("metric", "hamming")},
        {"Metric": "Top K", "Value": matching_cfg.get("top_k")},
    ]
    return pd.DataFrame(rows)


def _find_contact_column(columns: List[str]) -> str | None:
    """Locate the whatsapp/contact column by keyword, case-insensitive."""
    for col in columns:
        if isinstance(col, str) and "whatsapp" in col.lower():
            return col
    return None


def _candidate_rows(ranking: ESNRanking, erasmus_df: pd.DataFrame, question_cols: List[str]) -> pd.DataFrame:
    contact_col = _find_contact_column(list(erasmus_df.columns))
    contact_header = contact_col or "Whatsapp contact"
    rows = []
    for rank_num, candidate in enumerate(ranking.candidates, start=1):
        student = erasmus_df.iloc[candidate.erasmus_index]
        # Use candidate.distance (hamming count) as number of different answers
        try:
            distance = float(candidate.distance)
        except Exception:
            distance = 0.0
        # Convert to integer mismatches and clamp
        diff_answers = int(distance)
        if diff_answers < 0:
            diff_answers = 0
        if diff_answers > len(question_cols):
            diff_answers = len(question_cols)
        # Number of same answers is total questions minus different answers
        same_answers = len(question_cols) - diff_answers
        if same_answers < 0:
            same_answers = 0
        row = {
            "Rank": rank_num,
            "Student Name": student.get("Name", ""),
            "Student Surname": student.get("Surname", ""),
            contact_header: student.get(contact_col, "") if contact_col else "",
            "Number of same answers": same_answers,
            "Number of different answers": diff_answers,
        }
        # Append all answered non-question fields (excluding already included keys)
        base_keys = set(row.keys())
        for col in erasmus_df.columns:
            if col in question_cols or col in base_keys:
                continue
            value = student.get(col, "")
            if pd.notna(value) and str(value).strip():
                row[col] = value
        rows.append(row)
    return pd.DataFrame(rows)


def export_results(rankings: List[ESNRanking], esn_df: pd.DataFrame, erasmus_df: pd.DataFrame, stats: Dict, config: Dict) -> Path:
    output_cfg = config.get("output", {})
    out_dir = Path(output_cfg.get("out_dir", "outputs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"matching_{timestamp}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary_df = _build_summary(stats, config, len(esn_df), len(erasmus_df))
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if output_cfg.get("per_esner_sheets", True):
            schema_cfg = config.get("schema", {})
            question_cols = schema_cfg.get("question_columns", [])
            for ranking in rankings:
                esn_row = esn_df.iloc[ranking.esn_index]
                sheet_name = _safe_sheet_name(f"{esn_row.get('Name', '')} {esn_row.get('Surname', '')}")
                candidates_df = _candidate_rows(ranking, erasmus_df, question_cols)
                candidates_df.to_excel(writer, sheet_name=sheet_name or "ESN", index=False)

    return out_path
