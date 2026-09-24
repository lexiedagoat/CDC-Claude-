"""Data Table and Download tab."""
import pandas as pd
import streamlit as st

from ..ui_helpers import show_dataframe, show_empty_message

COLUMNS = {
    "state_of_residence": "State/geography",
    "state_abbr": "State code",
    "month": "Month",
    "month_code": "Month number",
    "sex_of_infant": "Infant sex",
    "births": "Births",
}
SEARCH_COLUMNS = ["State/geography", "Month", "Infant sex"]


def _build_table(df: pd.DataFrame) -> pd.DataFrame:
    """Chronological, alphabetical table with friendly column names."""
    table = df.sort_values(["state_of_residence", "month_code", "sex_of_infant"])
    table = table[list(COLUMNS)].rename(columns=COLUMNS)
    table["Month"] = table["Month"].astype(str)
    return table.reset_index(drop=True)


def _search(table: pd.DataFrame, query: str) -> pd.DataFrame:
    """Keep rows containing every search word in state, month, or sex."""
    haystack = table[SEARCH_COLUMNS].agg(" ".join, axis=1).str.lower()
    mask = pd.Series(True, index=table.index)
    for word in query.lower().replace(",", " ").split():
        mask &= haystack.str.contains(word, regex=False)
    return table[mask]


def render(df: pd.DataFrame) -> None:
    if df.empty:
        show_empty_message()
        return

    query = st.text_input(
        "Search the table", key="table_search", placeholder="e.g. texas march",
        help="Type state, month, or sex. Every word must match.",
    )
    table = _build_table(df)
    if query.strip():
        table = _search(table, query)

    st.caption(f"Showing {len(table):,} of {len(df):,} rows from the current sidebar filters.")
    if table.empty:
        st.info("No rows match that search. Try fewer or different words.")
        return

    show_dataframe(table.style.format({"Births": "{:,}"}))
    st.download_button(
        "Download as CSV",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="births_2025_filtered.csv",
        mime="text/csv",
        help="Downloads the rows shown above (sidebar filters and search).",
    )
