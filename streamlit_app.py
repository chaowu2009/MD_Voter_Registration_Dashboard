import streamlit as st
import plotly.express as px

from src.analytics import (
    county_party_comparison,
    county_trend,
    fastest_growing_counties,
    load_data,
    party_breakdown,
    party_share_change,
    top_counties,
    total_registered,
)


st.set_page_config(page_title="Maryland Voter Registration Dashboard", layout="wide")


@st.cache_data
def get_data(path: str):
    return load_data(path)


def render_overview(df):
    st.header("Overview")

    total = total_registered(df)
    st.metric("Statewide Total Registered Voters", f"{total:,}")

    breakdown = party_breakdown(df)
    fig_breakdown = px.bar(
        breakdown,
        x="party",
        y="registered",
        title="Statewide Party Breakdown",
        text="registered",
    )
    fig_breakdown.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_breakdown, use_container_width=True)

    st.subheader("Top Counties by Registration")
    st.dataframe(top_counties(df, n=10), use_container_width=True, hide_index=True)


def render_county_trends(df):
    st.header("County Trends")

    counties = sorted(df["county"].unique())
    selected_county = st.selectbox("Select a county", counties)

    trend_df = county_trend(df, selected_county)
    fig_trend = px.line(
        trend_df,
        x="date",
        y="registered",
        markers=True,
        title=f"Voter Registration Trend - {selected_county}",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    party_df = county_party_comparison(df, selected_county)
    fig_party = px.bar(
        party_df,
        x="party",
        y="registered",
        title=f"Party Comparison - {selected_county}",
        text="registered",
    )
    fig_party.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_party, use_container_width=True)


def render_growth_analysis(df):
    st.header("Growth Analysis")

    growth_df = fastest_growing_counties(df, n=10)
    fig_growth = px.bar(
        growth_df,
        x="county",
        y="growth",
        title="Fastest Growing Counties (Absolute Growth)",
        text="growth",
    )
    fig_growth.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_growth, use_container_width=True)

    st.subheader("Party Share Change (First vs Last Month)")
    st.dataframe(party_share_change(df), use_container_width=True, hide_index=True)


def main():
    st.title("Maryland Voter Registration Dashboard")

    try:
        df = get_data("data/sample.csv")
    except FileNotFoundError:
        st.error("Could not find data/sample.csv. Add the file and rerun the app.")
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load CSV: {exc}")
        st.stop()

    page = st.sidebar.radio(
        "Choose a page",
        ["Overview", "County Trends", "Growth Analysis"],
    )

    if page == "Overview":
        render_overview(df)
    elif page == "County Trends":
        render_county_trends(df)
    else:
        render_growth_analysis(df)


if __name__ == "__main__":
    main()
