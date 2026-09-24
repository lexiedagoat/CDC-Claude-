"""U.S. births dashboard (CDC provisional 2025 counts). Run: streamlit run app.py"""
import streamlit as st

from src import config
from src.data_loader import DataLoadError, has_critical_failure, load_data, validate_data
from src.filters import apply_filters, render_sidebar
from src.metrics import KPIs, compute_kpis
from src.tabs import about, data_table, geographic, monthly_sex, overview
from src.ui_helpers import fmt_int

st.set_page_config(page_title=config.APP_TITLE, layout="wide")


def render_header() -> None:
    st.title(config.APP_TITLE)
    st.write(
        "Explore how many babies were born in each U.S. state and the District of "
        "Columbia, by month and by infant sex. The sidebar filters change every "
        "card, chart, and table."
    )
    st.caption(f"Source: [{config.CDC_SOURCE_NAME}]({config.CDC_SOURCE_URL}), provisional {config.DATA_YEAR} natality data.")
    left, right = st.columns(2)
    left.warning(
        "**Provisional data.** These figures are preliminary and may be revised "
        "as the CDC finalizes records."
    )
    right.info(
        "**Birth counts, not birth rates.** Larger states have more births mainly "
        "because they have more people, not because births are more likely there."
    )


def render_kpis(k: KPIs) -> None:
    dash = "\u2014"
    cols = st.columns(5)
    cols[0].metric("Total births", fmt_int(k.total_births), help="Sum of births in the current selection.")
    cols[1].metric("Geographies selected", f"{k.n_geographies:,}", help="Number of states/geographies with data in the selection.")
    cols[2].metric(
        "Average births per month",
        fmt_int(k.avg_births_per_month) if k.avg_births_per_month is not None else dash,
        help="Total births divided by the number of selected months (all selected geographies combined).",
    )
    cols[3].metric("Highest geography", k.top_geography or dash, help="Geography with the most births in the selection. Ties are noted.")
    if k.top_geography_births is not None:
        cols[3].caption(f"{k.top_geography_births:,} births")
    cols[4].metric("Highest month", k.top_month or dash, help="Month with the most births in the selection. Ties are noted.")
    if k.top_month_births is not None:
        cols[4].caption(f"{k.top_month_births:,} births")


def main() -> None:
    render_header()

    try:
        df = load_data()
    except DataLoadError as err:
        st.error(str(err))
        st.stop()

    results = validate_data(df)
    if has_critical_failure(results):
        st.error("The data failed a validation check, so the dashboard cannot be shown safely.")
        about.render(df, results)
        st.stop()
    failed = [r for r in results if not r.passed]
    if failed:
        st.warning("Data notes: " + " ".join(r.name + " (see About the Data)." for r in failed))

    state = render_sidebar(df)
    filtered = apply_filters(df, state)
    render_kpis(compute_kpis(filtered))

    tabs = st.tabs(["Overview", "Geographic Analysis", "Monthly and Sex Analysis", "Data Table and Download", "About the Data"])
    with tabs[0]:
        overview.render(filtered)
    with tabs[1]:
        geographic.render(filtered)
    with tabs[2]:
        monthly_sex.render(filtered)
    with tabs[3]:
        data_table.render(filtered)
    with tabs[4]:
        about.render(df, results)


main()
