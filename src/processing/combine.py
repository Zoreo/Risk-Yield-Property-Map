"""Combine raw scrape files into a single DataFrame for cleaning."""
from __future__ import annotations
import glob
from pathlib import Path
from typing import Iterable
import pandas as pd

RAW_GLOB = "data/raw/raw_*.csv"

def list_raw_paths(pattern: str = RAW_GLOB) -> list[Path]:
    """Return sorted list of raw CSV paths to combine."""
    return sorted(Path(p) for p in glob.glob(pattern))

def load_and_concat(paths: Iterable[Path]) -> pd.DataFrame:
    """Load provided CSVs and concatenate into one DataFrame."""
    frames = [pd.read_csv(p) for p in paths]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows based on URL/price/area fields."""
    key_cols = [c for c in ["url", "price_raw", "area_raw"] if c in df.columns]
    if not key_cols:
        return df
    return df.drop_duplicates(subset=key_cols)

def write_combined(df: pd.DataFrame, output_path: str = "data/raw/raw_combined.csv") -> None:
    """Persist the combined raw dataset for downstream cleaning."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
