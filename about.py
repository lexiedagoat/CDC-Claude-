"""About the Data tab: source, caveats, column guide, and validation results."""
import pandas as pd
import streamlit as st

from ..config import CDC_SOURCE_NAME, CDC_SOURCE_URL, DATA_FILE_NAME, DATA_YEAR
from ..data_loader import CheckResult
from ..ui_helpers import show_dataframe

COLUMN_GUIDE = pd.DataFrame(
    [
        ("state_of_residence", "State (or District of Columbia) of residence."),
        ("month / month_code", "Month name and its number, 1 (January) to 12 (December)."),
        ("year_code", "Data year (2025 for every row)."),
        ("sex_of_infant", "Female or Male."),
        ("births", "Number of births in that state, month, and sex group."),
        ("state_abbr, month_abbr", "Added by the app: map abbreviation and short month label."),
    ],
    columns=["Column", "Meaning"],
)


def render(df: pd.DataFrame, results: list[CheckResult]) -> None:
    st.subheader("Source")
    st.markdown(
        f"Data: {CDC_SOURCE_NAME}, provisional {DATA_YEAR} natality counts "
        f"(file `{DATA_FILE_NAME}`). [CDC birth data]({CDC_SOURCE_URL})."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Geographies", f"{df['state_of_residence'].nunique():,}")
    c3.metric("Months", f"{df['month_code'].nunique():,}")
    c4.metric("Total births", f"{int(df['births'].sum()):,}")

    st.subheader("Read the numbers carefully")
    st.markdown(
        "- **Provisional.** Preliminary counts can change as records are finalized.\n"
        "- **Counts, not rates.** A birth *rate* divides births by a population "
        "(for example, women of childbearing age). This file has no population "
        "data, so it cannot say which state has a higher rate.\n"
        "- **One year only.** There is no year-over-year comparison.\n"
        "- **Unequal months.** Months differ in length, which affects monthly totals."
    )

    st.subheader("Columns")
    show_dataframe(COLUMN_GUIDE)

    st.subheader("Data validation")
    checks = pd.DataFrame(
        {
            "Check": [r.name for r in results],
            "Result": ["Pass" if r.passed else "Fail" for r in results],
            "Details": [r.detail for r in results],
        }
    )
    show_dataframe(checks)
