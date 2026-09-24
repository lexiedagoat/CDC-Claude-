"""Monthly and Sex Analysis tab: female/male by month and a state-by-month heatmap."""
import pandas as pd
import streamlit as st

from .. import charts
from ..ui_helpers import show_chart, show_empty_message

COUNT_MODE = "Births"
SHARE_MODE = "Share of each geography's births"


def render(df: pd.DataFrame) -> None:
    if df.empty:
        show_empty_message()
        return

    st.subheader("Female and male births by month")
    if df["sex_of_infant"].nunique() < 2:
        st.info("Only one infant sex is selected. Choose **Both** in the sidebar to compare.")
    show_chart(charts.monthly_by_sex(df), key="ms_by_sex")

    st.subheader("State-by-month heatmap")
    single_month = df["month_code"].nunique() < 2
    mode = st.radio(
        "Color shows", [COUNT_MODE, SHARE_MODE], horizontal=True, key="heatmap_mode",
        disabled=single_month,
        help="Counts mostly reflect state size. The share view removes size so you can compare monthly patterns.",
    )
    as_share = mode == SHARE_MODE and not single_month
    if single_month:
        st.caption("Select two or more months to enable the share view.")
    show_chart(charts.state_month_heatmap(df, as_share=as_share), key="ms_heatmap")
    st.caption(
        "In the counts view, large states look darker in every month. Switch to the "
        "share view to see which months are relatively busier within each geography."
    )
