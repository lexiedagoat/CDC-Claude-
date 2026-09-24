"""One Plotly figure per visualization. Functions take a filtered DataFrame."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import (
    BOTTOM_COLOR,
    DATA_YEAR,
    MONTH_ABBRS,
    MONTH_CODE_TO_ABBR,
    PRIMARY_COLOR,
    SEQUENTIAL_SCALE,
    SEX_COLORS,
    SEX_VALUES,
    TOP_COLOR,
)
from .metrics import effective_top_n


def _finish(fig: go.Figure, title: str, height: int | None = None) -> go.Figure:
    """Apply the shared, minimal styling."""
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16)),
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=10),
        font=dict(size=13),
        height=height,
    )
    return fig


def _sex_label(df: pd.DataFrame) -> str:
    sexes = [s for s in SEX_VALUES if s in set(df["sex_of_infant"])]
    return " and ".join(s.lower() for s in sexes)


def monthly_trend(df: pd.DataFrame) -> go.Figure:
    """Births per month. The axis always shows all 12 months; unselected ones are gaps."""
    by_month = df.groupby("month_code")["births"].sum().reindex(range(1, 13))
    fig = go.Figure(
        go.Scatter(
            x=MONTH_ABBRS,
            y=by_month.values,
            mode="lines+markers",
            connectgaps=False,
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate="%{x}: %{y:,.0f} births<extra></extra>",
        )
    )
    fig.update_xaxes(categoryorder="array", categoryarray=MONTH_ABBRS, title="Month")
    fig.update_yaxes(rangemode="tozero", tickformat=",d", title="Births")
    return _finish(fig, f"Births by month, {DATA_YEAR} ({_sex_label(df)} infants)")


def sex_totals(df: pd.DataFrame) -> go.Figure:
    """Total births for female and male infants, with each group's share."""
    totals = df.groupby("sex_of_infant")["births"].sum().reindex(SEX_VALUES).dropna().astype(int)
    shares = totals / totals.sum()
    fig = go.Figure(
        go.Bar(
            x=totals.index,
            y=totals.values,
            marker_color=[SEX_COLORS[s] for s in totals.index],
            text=[f"{v:,} ({s:.1%})" for v, s in zip(totals.values, shares.values)],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}: %{y:,.0f} births<extra></extra>",
        )
    )
    fig.update_yaxes(range=[0, totals.max() * 1.15], tickformat=",d", title="Births")
    fig.update_xaxes(title="Infant sex")
    return _finish(fig, "Female and male births in the selection")


def monthly_by_sex(df: pd.DataFrame) -> go.Figure:
    """Grouped bars: female and male births side by side for each month."""
    m = df.groupby(["month_code", "sex_of_infant"], as_index=False)["births"].sum()
    m["month_abbr"] = m["month_code"].map(MONTH_CODE_TO_ABBR)
    fig = px.bar(
        m, x="month_abbr", y="births", color="sex_of_infant", barmode="group",
        color_discrete_map=SEX_COLORS,
        category_orders={"month_abbr": MONTH_ABBRS, "sex_of_infant": SEX_VALUES},
        labels={"month_abbr": "Month", "births": "Births", "sex_of_infant": "Infant sex"},
    )
    fig.update_traces(hovertemplate="%{x}, %{fullData.name}: %{y:,.0f} births<extra></extra>")
    fig.update_yaxes(rangemode="tozero", tickformat=",d")
    return _finish(fig, f"Female and male births by month, {DATA_YEAR}")


def state_ranking(df: pd.DataFrame) -> go.Figure:
    """Horizontal bars of every selected geography, largest at the top."""
    totals = df.groupby("state_of_residence")["births"].sum().sort_values(ascending=True)
    fig = go.Figure(
        go.Bar(
            x=totals.values,
            y=totals.index,
            orientation="h",
            marker_color=PRIMARY_COLOR,
            text=[f"{v:,}" for v in totals.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,.0f} births<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, totals.max() * 1.15], tickformat=",d", title="Births")
    fig.update_yaxes(dtick=1, title=None)  # dtick=1 keeps every state label visible
    return _finish(fig, "Total births by state / geography", height=max(360, 22 * len(totals) + 120))


def choropleth(df: pd.DataFrame) -> go.Figure:
    """US state map shaded by total births. Unselected states stay blank."""
    totals = df.groupby(["state_of_residence", "state_abbr"], as_index=False)["births"].sum()
    fig = px.choropleth(
        totals,
        locations="state_abbr",
        locationmode="USA-states",
        color="births",
        scope="usa",
        hover_name="state_of_residence",
        hover_data={"state_abbr": False, "births": ":,d"},
        color_continuous_scale=SEQUENTIAL_SCALE,
        range_color=(0, totals["births"].max()),
        labels={"births": "Births"},
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Births", tickformat=",d"))
    return _finish(fig, "Total births by state (darker = more births)", height=480)


def state_month_heatmap(df: pd.DataFrame, as_share: bool = False) -> go.Figure:
    """States (rows) by months (columns). Optionally each state's monthly share."""
    pivot = df.pivot_table(index="state_of_residence", columns="month_code",
                           values="births", aggfunc="sum").sort_index()
    pivot = pivot.reindex(columns=sorted(pivot.columns))
    x_labels = [MONTH_CODE_TO_ABBR[c] for c in pivot.columns]

    if as_share:
        z = pivot.div(pivot.sum(axis=1), axis=0) * 100
        hover = "%{y}, %{x}<br>%{z:.1f}% of this geography's selected births<extra></extra>"
        bar_title, title = "% of state's births", "Share of each geography's births by month"
    else:
        z = pivot
        hover = "%{y}, %{x}<br>%{z:,.0f} births<extra></extra>"
        bar_title, title = "Births", "Births by state and month"

    fig = go.Figure(
        go.Heatmap(
            z=z.values, x=x_labels, y=list(z.index),
            colorscale=SEQUENTIAL_SCALE, zmin=0,
            colorbar=dict(title=bar_title),
            hovertemplate=hover,
        )
    )
    fig.update_xaxes(type="category", title="Month")
    fig.update_yaxes(autorange="reversed", dtick=1, tickfont=dict(size=11))
    return _finish(fig, title, height=max(420, 18 * len(z) + 150))


def top_bottom(df: pd.DataFrame, n: int) -> go.Figure | None:
    """Highest and lowest n geographies by total births, in one chart."""
    totals = df.groupby("state_of_residence")["births"].sum().sort_values(ascending=False)
    k = effective_top_n(len(totals), n)
    if k == 0:
        return None
    top, bottom = totals.head(k), totals.tail(k)
    order = list(top.index) + list(bottom.index)  # top group first, both descending

    fig = go.Figure()
    for name, part, color in (("Highest", top, TOP_COLOR), ("Lowest", bottom, BOTTOM_COLOR)):
        fig.add_trace(go.Bar(
            x=part.values, y=part.index, orientation="h", name=name, marker_color=color,
            text=[f"{v:,}" for v in part.values], textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: %{x:,.0f} births<extra></extra>",
        ))
    fig.update_xaxes(range=[0, top.max() * 1.18], tickformat=",d", title="Births")
    fig.update_yaxes(autorange="reversed", categoryorder="array", categoryarray=order, title=None)
    return _finish(fig, f"Highest {k} and lowest {k} geographies by births", height=max(320, 34 * 2 * k + 120))
