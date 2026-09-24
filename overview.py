"""Overview tab: monthly trend and female/male comparison."""
import pandas as pd
import streamlit as st

from .. import charts
from ..ui_helpers import show_chart, show_empty_message


def render(df: pd.DataFrame) -> None:
    if df.empty:
        show_empty_message()
        return

    left, right = st.columns([3, 2])
    with left:
        show_chart(charts.monthly_trend(df), key="overview_trend")
        st.caption(
            "Each point is the total births in that month across the selected "
            "geographies. The vertical axis starts at zero. Months are not equal "
            "in length, so February's shorter total is partly a calendar effect."
        )
    with right:
        show_chart(charts.sex_totals(df), key="overview_sex")
        if df["sex_of_infant"].nunique() < 2:
            st.info("Only one infant sex is selected. Choose **Both** in the sidebar to compare.")
        else:
            st.caption("Bars show total births and each group's share of the selection.")
