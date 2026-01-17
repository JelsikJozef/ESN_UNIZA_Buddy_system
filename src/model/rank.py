from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class RankedCandidate:
    erasmus_index: int
    distance: float


@dataclass
class ESNRanking:
    esn_index: int
    candidates: List[RankedCandidate]


def _identifier_key(df: pd.DataFrame, identifier_column: Optional[str]) -> List:
    if identifier_column and identifier_column in df.columns:
        values = df[identifier_column]
        if values.is_unique and not values.isna().any():
            return list(values)
    return list(range(len(df)))


def rank_candidates(distances: np.ndarray, erasmus_df: pd.DataFrame, top_k: int, identifier_column: Optional[str]) -> List[ESNRanking]:
    erasmus_keys = _identifier_key(erasmus_df, identifier_column)
    rankings: List[ESNRanking] = []
    for esn_idx in range(distances.shape[0]):
        row_dist = distances[esn_idx]
        sortable = list(zip(row_dist, erasmus_keys, range(len(row_dist))))
        sortable.sort(key=lambda x: (x[0], x[1]))
        selected = sortable[: min(top_k, len(sortable))]
        candidates = [RankedCandidate(erasmus_index=idx, distance=float(dist)) for dist, _key, idx in selected]
        rankings.append(ESNRanking(esn_index=esn_idx, candidates=candidates))
    return rankings
