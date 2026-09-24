"""Geographic Analysis tab: map, top/bottom comparison, and ranking."""
import pandas as pd
import streamlit as st

from .. import charts
from ..metrics import effective_top_n
from ..ui_helpers import show_chart, show_empty_message


def render(df: pd.DataFrame) -> None:
    if df.empty:
        show_empty_message()
        return

    st.subheader("Map")
    show_chart(charts.choropleth(df), key="geo_map")
    st.caption(
        "Darker states recorded more births. These are counts, so populous states "
        "look darker mainly because they have more people. Geographies not selected "
        "in the sidebar are left blank."
    )

    st.subheader("Highest and lowest geographies")
    n_geo = df["state_of_residence"].nunique()
    max_n = effective_top_n(n_geo, 10)
    if max_n < 1:
        st.info("Select at least two geographies to compare the highest and lowest.")
    else:
        n = 1
        if max_n > 1:
            n = st.slider("Geographies shown at each end", 1, max_n, min(5, max_n), key="top_bottom_n")
        show_chart(charts.top_bottom(df, n), key="geo_top_bottom")

    st.subheader("Ranking")
    show_chart(charts.state_ranking(df), key="geo_ranking")
