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
