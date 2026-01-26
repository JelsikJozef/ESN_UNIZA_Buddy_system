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


def test_ingest_applies_timestamp_min_filter():
    data_dir = Path(__file__).parent / "data"
    raw_erasmus = pd.read_csv(data_dir / "Erasmus.csv", sep=";")
    cutoff = "2026-01-15 21:00:00"

    config = {
        "input": {
            "format": "csv",
            "file_path": str(data_dir),
            "esn_csv": "ESN.csv",
            "erasmus_csv": "Erasmus.csv",
            "buddy_interest_column": "Are you interested in getting a buddy?",
            "buddy_interest_value": "Yes",
            "timestamp_min": cutoff,
        }
    }

    erasmus_df, _, stats = ingest.load_tables(config)

    ts_all = pd.to_datetime(raw_erasmus["Timestamp"])
    expected_after_ts = raw_erasmus[ts_all >= pd.to_datetime(cutoff)]
    expected_buddy = expected_after_ts[
        expected_after_ts["Are you interested in getting a buddy?"] == "Yes"
    ]

    assert len(erasmus_df) == len(expected_buddy)
    assert stats["erasmus_loaded"] == len(raw_erasmus)
    assert stats["erasmus_after_timestamp_filter"] == len(expected_after_ts)
    assert stats["erasmus_after_filter"] == len(expected_buddy)
    assert (pd.to_datetime(erasmus_df["Timestamp"]) >= pd.to_datetime(cutoff)).all()


def test_ingest_timestamp_filter_accepts_custom_format(tmp_path):
    data_dir = tmp_path
    buddy_col = "Are you interested in getting a buddy?"
    erasmus_csv = (
        "Timestamp;Name;Surname;" f"{buddy_col}\n"
        "1/21/2026 10:00:00;Jane;Doe;Yes\n"
        "1/22/2026 14:10:12;John;Smith;Yes\n"
    )
    esn_csv = "Timestamp;Name;Surname\n1/20/2026 09:00:00;Eva;Helper\n"
    (data_dir / "Erasmus.csv").write_text(erasmus_csv, encoding="utf-8")
    (data_dir / "ESN.csv").write_text(esn_csv, encoding="utf-8")

    config = {
        "input": {
            "format": "csv",
            "file_path": str(data_dir),
            "esn_csv": "ESN.csv",
            "erasmus_csv": "Erasmus.csv",
            "buddy_interest_column": buddy_col,
            "buddy_interest_value": "Yes",
            "timestamp_min": "1/22/2026 14:10:12",
            "timestamp_format": "%m/%d/%Y %H:%M:%S",
        }
    }

    erasmus_df, _, stats = ingest.load_tables(config)

    assert len(erasmus_df) == 1
    assert erasmus_df.iloc[0]["Name"] == "John"
    assert stats["erasmus_after_timestamp_filter"] == 1
    assert stats["erasmus_after_filter"] == 1

