"""Load the CDC natality CSV and run data-validation checks."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from .config import (
    DATA_PATH,
    MONTH_CODE_TO_ABBR,
    MONTH_CODE_TO_NAME,
    MONTH_NAMES,
    REQUIRED_COLUMNS,
    SEX_VALUES,
)
from .state_codes import STATE_ABBREVIATIONS


class DataLoadError(Exception):
    """Raised when the data file is missing or lacks required columns."""


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str
    critical: bool = True  # a failed critical check stops the app


@st.cache_data(show_spinner="Loading data...")
def load_data(path: str = str(DATA_PATH)) -> pd.DataFrame:
    """Read the CSV, tidy text columns, and add helper columns.

    The path is passed as a string so Streamlit can hash it for caching.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DataLoadError(
            f"Data file not found: {file_path.name}. "
            "Place it in the data/ folder next to app.py."
        )

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataLoadError(f"The data file is missing required columns: {', '.join(missing)}.")

    df["state_of_residence"] = df["state_of_residence"].astype(str).str.strip()
    df["sex_of_infant"] = df["sex_of_infant"].astype(str).str.strip().str.title()
    df["month"] = df["month"].astype(str).str.strip().str.title()

    # Helper columns used by the map and by compact month labels.
    df["state_abbr"] = df["state_of_residence"].map(STATE_ABBREVIATIONS)
    df["month_abbr"] = df["month_code"].map(MONTH_CODE_TO_ABBR)

    # Ordered categorical keeps months chronological if anything sorts by name.
    df["month"] = pd.Categorical(df["month"], categories=MONTH_NAMES, ordered=True)
    return df


def validate_data(df: pd.DataFrame) -> list[CheckResult]:
    """Run integrity checks and return one result per check."""
    results: list[CheckResult] = []

    def add(name: str, passed: bool, detail: str, critical: bool = True) -> None:
        results.append(CheckResult(name, bool(passed), detail, critical))

    n_missing = int(df[REQUIRED_COLUMNS].isna().sum().sum())
    add("No missing values", n_missing == 0, f"{n_missing} missing cells in the required columns.")

    is_int = pd.api.types.is_integer_dtype(df["births"])
    n_negative = int((df["births"] < 0).sum()) if is_int else -1
    add(
        "Births are non-negative whole numbers",
        is_int and n_negative == 0,
        "All values are whole numbers >= 0." if is_int and n_negative == 0
        else "The births column has non-integer or negative values.",
    )

    codes = sorted(df["month_code"].dropna().unique().tolist())
    add("All 12 months present", codes == list(range(1, 13)), f"Month codes found: {codes}.")

    expected_names = df["month_code"].map(MONTH_CODE_TO_NAME)
    mismatches = int((expected_names != df["month"].astype(str)).sum())
    add("Month names match month codes", mismatches == 0, f"{mismatches} rows where name and code disagree.")

    sexes = sorted(df["sex_of_infant"].unique().tolist())
    add("Infant sex values are Female and Male", sexes == sorted(SEX_VALUES), f"Values found: {sexes}.")

    n_dupes = int(df.duplicated(["state_of_residence", "month_code", "sex_of_infant"]).sum())
    add("No duplicate state/month/sex rows", n_dupes == 0, f"{n_dupes} duplicate rows.")

    unmapped = sorted(df.loc[df["state_abbr"].isna(), "state_of_residence"].unique().tolist())
    add(
        "Every geography has a map abbreviation",
        not unmapped,
        "All geographies mapped." if not unmapped else f"Unmapped: {', '.join(unmapped)}.",
    )

    n_geo = df["state_of_residence"].nunique()
    expected_rows = n_geo * df["month_code"].nunique() * df["sex_of_infant"].nunique()
    add(
        "Complete geography x month x sex grid",
        len(df) == expected_rows and n_dupes == 0,
        f"{len(df):,} rows found; {expected_rows:,} expected.",
    )

    # Informational checks: a failure here should warn, not stop the app.
    add(
        "51 geographies (50 states + DC)",
        n_geo == len(STATE_ABBREVIATIONS),
        f"{n_geo} geographies found.",
        critical=False,
    )
    add(
        "Single data year",
        df["year_code"].nunique() == 1,
        f"Year(s) found: {sorted(df['year_code'].unique().tolist())}.",
        critical=False,
    )
    return results


def has_critical_failure(results: list[CheckResult]) -> bool:
    return any(not r.passed and r.critical for r in results)
