"""Cleaning and feature engineering helpers for scraped listings."""
from __future__ import annotations
import re
import numpy as np
import pandas as pd

EUR_TO_BGN = 1.95583

def parse_price(series: pd.Series) -> pd.Series:
    """Convert price_raw strings (with currency/spacing) to numeric EUR."""
    def _one(val: str | float) -> float | np.nan:
        if pd.isna(val):
            return np.nan
        text = str(val)
        currency = "EUR" if re.search(r"€|eur|евро", text, flags=re.IGNORECASE) else "BGN"
        num_match = re.search(r"([\d\s.,]+)", text)
        if not num_match:
            return np.nan
        num_str = num_match.group(1).replace(" ", "").replace(",", ".")
        try:
            amt = float(num_str)
        except ValueError:
            return np.nan
        return amt if currency == "EUR" else amt / EUR_TO_BGN

    return series.apply(_one)

def parse_area(series: pd.Series) -> pd.Series:
    """Convert area_raw strings (e.g., '75 кв.м') to numeric square meters."""
    def _one(val: str | float) -> float | np.nan:
        if pd.isna(val):
            return np.nan
        m = re.search(r"([\d\s.,]+)", str(val))
        if not m:
            return np.nan
        num_str = m.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(num_str)
        except ValueError:
            return np.nan

    return series.apply(_one)

def parse_floor(series: pd.Series) -> pd.Series:
    """Extract integer floor where possible (supports labels like 'ет. 3 от 8')."""
    def _one(val: str | float) -> float | np.nan:
        if pd.isna(val):
            return np.nan
        m = re.search(r"(\d+)", str(val))
        return float(m.group(1)) if m else np.nan

    return series.apply(_one)

def parse_max_floor(series: pd.Series) -> pd.Series:
    """Extract total floors when available."""
    def _one(val: str | float) -> float | np.nan:
        if pd.isna(val):
            return np.nan
        text = str(val)
        m = re.search(r"(?:от|/)\s*(\d+)", text)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return np.nan
        m2 = re.search(r"(\d+)", text)
        if m2:
            try:
                return float(m2.group(1))
            except ValueError:
                return np.nan
        return np.nan

    return series.apply(_one)

def derive_floor_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_ground_floor / is_top_floor flags using floor and max_floor columns."""
    df = df.copy()
    df["is_ground_floor"] = np.where(df["floor"].fillna(1).astype(float) <= 0, 1, 0)
    df["is_top_floor"] = np.where(
        (df["floor"].notna()) & (df["max_floor"].notna()) & (df["floor"] == df["max_floor"]),
        1,
        0,
    )
    return df

def map_heating(series: pd.Series) -> pd.Series:
    """Map heat_raw into a small set of categories (district/gas/electric/other)."""
    def _one(val: str | float) -> str | None:
        if pd.isna(val):
            return None
        t = str(val).lower()
        if "тец" in t:
            return "district"
        if "газ" in t:
            return "gas"
        if "електр" in t or "ток" in t or "клим" in t:
            return "electric"
        return "other"
    return series.apply(_one)

def map_construction(series: pd.Series) -> pd.Series:
    """Map construction_raw into panel/brick/epk/other."""
    def _one(val: str | float) -> str | None:
        if pd.isna(val):
            return None
        t = str(val).lower()
        if "панел" in t:
            return "panel"
        if "епк" in t or "пк" in t:
            return "epk"
        if "тухл" in t:
            return "brick"
        return "other"

    return series.apply(_one)

def derive_newbuild(
    series_year: pd.Series,
    series_construction: pd.Series | None = None,
    series_desc: pd.Series | None = None,
) -> pd.Series:
    """Return 1 if year suggests recent/new build or labeled as such, else 0.

    Rules:
    - year >= 2010 -> 1; year present and <2010 -> 0
    - if no year:
        * panel/epk -> 0
        * brick -> 1 only if description contains нов/нова/ново, else 0
        * others remain NaN
    """
    years = pd.to_numeric(series_year, errors="coerce")
    newbuild = pd.Series(np.nan, index=series_year.index)
    mask_year = years.notna()
    newbuild.loc[mask_year] = np.where(years[mask_year] >= 2010, 1, 0)

    if series_construction is not None:
        cons = map_construction(series_construction)
        mask_panel = newbuild.isna() & cons.isin(["panel", "epk"])
        newbuild.loc[mask_panel] = 0
        if series_desc is not None:
            desc = series_desc.fillna("").astype(str)
            nov_mask = desc.str.contains(r"\bнов[ао]?\b", case=False, regex=True)
        else:
            nov_mask = pd.Series(False, index=newbuild.index)
        mask_brick = newbuild.isna() & (cons == "brick")
        newbuild.loc[mask_brick] = np.where(nov_mask[mask_brick], 1, 0)
        newbuild = newbuild.fillna(0)
    return newbuild

def standardize_district(series: pd.Series) -> pd.Series:
    """Normalize district_raw strings to canonical district labels."""
    def _one(val: str | float) -> str | None:
        if pd.isna(val):
            return None
        t = str(val)
        t = re.sub(r"^гр\.?\s*София[, ]*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"^град\s*София[, ]*", "", t, flags=re.IGNORECASE)
        return t.strip()
    return series.apply(_one)
