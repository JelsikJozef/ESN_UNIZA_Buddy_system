"""Ensure deterministic top-K ordering and tie-breaking."""

import numpy as np
import pandas as pd

from src.model import rank


def test_rank_top_k_and_identifier_tie_break():
    distances = np.array([[1, 1, 2]], dtype=float)
    erasmus_df = pd.DataFrame({
        "Timestamp": [2, 1, 3],
        "Name": ["S1", "S2", "S3"],
    })
    rankings = rank.rank_candidates(distances, erasmus_df, top_k=2, identifier_column="Timestamp")

    first = rankings[0].candidates[0]
    second = rankings[0].candidates[1]
    # Same distance, tie broken by identifier ascending -> index 1 (Timestamp=1) first
    assert first.erasmus_index == 1
    assert second.erasmus_index == 0


def test_rank_falls_back_to_row_order_when_identifier_missing_or_not_unique():
    distances = np.array([[0, 0]], dtype=float)
    erasmus_df = pd.DataFrame({
        "Timestamp": [5, 5],  # not unique triggers fallback
        "Name": ["A", "B"],
    })
    rankings = rank.rank_candidates(distances, erasmus_df, top_k=2, identifier_column="Timestamp")
    # Row order preserved because identifier not unique
    assert [c.erasmus_index for c in rankings[0].candidates] == [0, 1]
