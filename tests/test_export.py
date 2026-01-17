"""Ensure the view layer exports summary and per-member sheets."""

from pathlib import Path

import pandas as pd

from src.model.rank import ESNRanking, RankedCandidate
from src.view import export_xlsx


def test_export_creates_workbook_with_summary(tmp_path):
    esn_df = pd.DataFrame([
        {"Name": "Anna", "Surname": "Alpha"},
    ])
    erasmus_df = pd.DataFrame([
        {"Name": "Eva", "Surname": "Delta", "Email": "e@example.com"},
        {"Name": "Fred", "Surname": "Epsilon", "Email": "f@example.com"},
    ])
    rankings = [
        ESNRanking(
            esn_index=0,
            candidates=[
                RankedCandidate(erasmus_index=0, distance=0.0),
                RankedCandidate(erasmus_index=1, distance=1.0),
            ],
        )
    ]
    stats = {"esn_loaded": 1, "erasmus_loaded": 2, "esn_after_filter": 1, "erasmus_after_filter": 2}
    config = {
        "schema": {"question_columns": ["Q01"], "answer_encoding": "AB"},
        "matching": {"metric": "hamming", "top_k": 2},
        "output": {"out_dir": str(tmp_path), "per_esner_sheets": True},
    }

    out_path = export_xlsx.export_results(rankings, esn_df, erasmus_df, stats, config)

    assert out_path.exists()
    xls = pd.ExcelFile(out_path)
    assert "Summary" in xls.sheet_names
    assert any(sheet for sheet in xls.sheet_names if sheet != "Summary")
