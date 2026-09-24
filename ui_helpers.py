"""Small Streamlit helpers shared by the tabs."""
import inspect

import pandas as pd
import streamlit as st

from .config import PLOTLY_CONFIG

# Newer Streamlit versions replace use_container_width with width="stretch".
# Checking the signature keeps the app working on both.
_PLOTLY_HAS_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters
_DATAFRAME_HAS_WIDTH = "width" in inspect.signature(st.dataframe).parameters


def show_chart(fig, key: str) -> None:
    """Render a Plotly figure at the full width of its container."""
    if _PLOTLY_HAS_WIDTH:
        st.plotly_chart(fig, width="stretch", key=key, config=PLOTLY_CONFIG)
    else:
        st.plotly_chart(fig, use_container_width=True, key=key, config=PLOTLY_CONFIG)


def show_dataframe(data) -> None:
    """Render a DataFrame (or Styler) at full width without the index."""
    if _DATAFRAME_HAS_WIDTH:
        st.dataframe(data, width="stretch", hide_index=True)
    else:
        st.dataframe(data, use_container_width=True, hide_index=True)


def show_empty_message() -> None:
    """Shown by every data tab when the sidebar filters match no rows."""
    st.warning(
        "No births match the current filters. Select at least one geography "
        "and one month in the sidebar, or click **Reset filters**."
    )


def fmt_int(value) -> str:
    """Format a number with thousands separators."""
    return f"{int(round(value)):,}"
