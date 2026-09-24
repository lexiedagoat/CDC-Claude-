"""Sidebar filters: widgets, Select All, Reset, and the active-filter summary."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from .config import MONTH_NAMES, SEX_OPTIONS, SEX_VALUES

# session_state keys for each widget
GEO_KEY, GEO_ALL_KEY = "geo_selected", "geo_all"
MONTH_KEY, MONTH_ALL_KEY = "month_selected", "month_all"
SEX_KEY = "sex_selected"


@dataclass(frozen=True)
class FilterState:
    geographies: tuple
    months: tuple
    sex: str
    total_geographies: int
    total_months: int

    @property
    def sexes(self) -> tuple:
        return SEX_VALUES if self.sex == "Both" else (self.sex,)


# --- Callbacks: they run before the script reruns, so widget state stays in sync.
def _toggle_all(select_key: str, all_key: str, options: list) -> None:
    """Select All checkbox changed: fill or clear the multiselect."""
    st.session_state[select_key] = list(options) if st.session_state[all_key] else []


def _sync_all_checkbox(select_key: str, all_key: str, options: list) -> None:
    """Multiselect changed: tick Select All only when everything is chosen."""
    st.session_state[all_key] = len(st.session_state[select_key]) == len(options)


def _reset(geos: list, months: list) -> None:
    st.session_state[GEO_KEY] = list(geos)
    st.session_state[MONTH_KEY] = list(months)
    st.session_state[GEO_ALL_KEY] = True
    st.session_state[MONTH_ALL_KEY] = True
    st.session_state[SEX_KEY] = "Both"


def render_sidebar(df: pd.DataFrame) -> FilterState:
    """Draw the sidebar and return the current selections."""
    geos = sorted(df["state_of_residence"].unique())
    present_months = set(df["month"].astype(str))
    months = [m for m in MONTH_NAMES if m in present_months]  # calendar order

    # Default is "everything selected". setdefault keeps choices across reruns.
    st.session_state.setdefault(GEO_KEY, list(geos))
    st.session_state.setdefault(MONTH_KEY, list(months))
    st.session_state.setdefault(GEO_ALL_KEY, True)
    st.session_state.setdefault(MONTH_ALL_KEY, True)
    st.session_state.setdefault(SEX_KEY, "Both")

    with st.sidebar:
        st.header("Filters")
        summary_box = st.container()  # filled in after the widgets are read
        st.button("Reset filters", on_click=_reset, args=(geos, months))

        st.radio("Infant sex", SEX_OPTIONS, key=SEX_KEY,
                 help="Show births for female infants, male infants, or both.")

        st.checkbox("Select all months", key=MONTH_ALL_KEY,
                    on_change=_toggle_all, args=(MONTH_KEY, MONTH_ALL_KEY, months))
        st.multiselect("Months", months, key=MONTH_KEY,
                       on_change=_sync_all_checkbox, args=(MONTH_KEY, MONTH_ALL_KEY, months))

        st.checkbox("Select all geographies", key=GEO_ALL_KEY,
                    on_change=_toggle_all, args=(GEO_KEY, GEO_ALL_KEY, geos))
        st.multiselect("State / geography", geos, key=GEO_KEY,
                       on_change=_sync_all_checkbox, args=(GEO_KEY, GEO_ALL_KEY, geos))

    state = FilterState(
        geographies=tuple(st.session_state[GEO_KEY]),
        months=tuple(st.session_state[MONTH_KEY]),
        sex=st.session_state[SEX_KEY],
        total_geographies=len(geos),
        total_months=len(months),
    )
    with summary_box:
        _render_summary(state)
    return state


def _describe(selected: tuple, total: int, label_fn=None, max_names: int = 3) -> str:
    """Turn a selection into short text: 'All 12', 'None', names, or 'n of N'."""
    n = len(selected)
    if n == 0:
        return "None selected"
    if n == total:
        return f"All {total}"
    if n <= max_names:
        return ", ".join(label_fn(s) if label_fn else s for s in selected)
    return f"{n} of {total}"


def _render_summary(state: FilterState) -> None:
    sex_text = "Both (female and male)" if state.sex == "Both" else f"{state.sex} only"
    st.markdown(
        "**Active filters**\n\n"
        f"- Geographies: {_describe(state.geographies, state.total_geographies)}\n"
        f"- Months: {_describe(state.months, state.total_months, lambda m: m[:3], 4)}\n"
        f"- Infant sex: {sex_text}"
    )
    if not state.geographies or not state.months:
        st.warning("Nothing is selected in one of the filters, so there is no data to show.")


def apply_filters(df: pd.DataFrame, state: FilterState) -> pd.DataFrame:
    """Return only the rows matching the sidebar selections."""
    mask = (
        df["state_of_residence"].isin(state.geographies)
        & df["month"].astype(str).isin(state.months)
        & df["sex_of_infant"].isin(state.sexes)
    )
    return df.loc[mask]
