"""Verify Erasmus-only buddy-interest filtering during ingestion."""

import pandas as pd
from pathlib import Path

from src.model import ingest


def test_ingest_filters_buddy_interest_erasmus_only():
    data_dir = Path(__file__).parent / "data"
    raw_erasmus = pd.read_csv(data_dir / "Erasmus.csv", sep=";")
    raw_esn = pd.read_csv(data_dir / "ESN.csv", sep=";")

    config = {
        "input": {
            "format": "csv",
            "file_path": str(data_dir),
            "esn_csv": "ESN.csv",
            "erasmus_csv": "Erasmus.csv",
            "buddy_interest_column": "Are you interested in getting a buddy?",
            "buddy_interest_value": "Yes",
        }
    }

    erasmus_df, esn_df, stats = ingest.load_tables(config)

    expected_filtered = raw_erasmus[raw_erasmus["Are you interested in getting a buddy?"] == "Yes"]

    assert len(esn_df) == len(raw_esn)
    assert len(erasmus_df) == len(expected_filtered)
    assert stats["erasmus_after_filter"] == len(expected_filtered)
    assert set(erasmus_df["Are you interested in getting a buddy?"].unique()) == {"Yes"}


def test_ingest_normalizes_multiline_headers(tmp_path):
    data_dir = tmp_path
    buddy_column = "Are you interested in getting a buddy?"
    multiline_header_raw = "Intro line\r\nA) Mountains\r\nB) Sea  "
    esn_header_raw = "Volunteer Name\r"

    erasmus_csv = (
        f'"{buddy_column}";"{multiline_header_raw}"\r\n'
        '"Yes";"Hiking"\r\n'
        '"No";"Swimming"\r\n'
    )
    esn_csv = (
        f'"{esn_header_raw}";"City"\r\n'
        '"Alex";"ZA"\r\n'
    )

    (data_dir / "Erasmus.csv").write_text(erasmus_csv, encoding="utf-8")
    (data_dir / "ESN.csv").write_text(esn_csv, encoding="utf-8")

    config = {
        "input": {
            "format": "csv",
            "file_path": str(data_dir),
            "esn_csv": "ESN.csv",
            "erasmus_csv": "Erasmus.csv",
            "buddy_interest_column": buddy_column,
            "buddy_interest_value": "Yes",
        }
    }

    erasmus_df, esn_df, _ = ingest.load_tables(config)

    normalized_multiline = "A) Mountains\nB) Sea"
    assert normalized_multiline in erasmus_df.columns
    assert "Volunteer Name" in esn_df.columns
    assert all("\r" not in col for col in erasmus_df.columns)
    assert len(erasmus_df) == 1
    assert set(erasmus_df[buddy_column]) == {"Yes"}
