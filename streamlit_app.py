import streamlit as st
import plotly.express as px
import pandas as pd

from src.analytics import (
    county_party_comparison_latest,
    county_trend,
    county_trend_change_pct,
    fastest_growing_counties,
    load_data,
    party_breakdown,
    party_share_change,
    top_counties,
    total_registered_latest,
    data_quality_issues,
    validate_dataframe,
)
from src.data_loader import load_dashboard_data, parse_and_store_pdf
from src.logging_config import get_logger
from src.sbe_scraper import download_reports, scrape_report_links


st.set_page_config(page_title="Maryland Voter Registration Dashboard", layout="wide")
logger = get_logger(__name__)


@st.cache_data
def get_data():
    return load_dashboard_data()


def render_overview(df):
    st.header("Overview")

    total, latest_year, latest_month = total_registered_latest(df)
    latest_df = df[(df["year"] == latest_year) & (df["month"] == latest_month)].copy()
    st.metric("Statewide Total Registered Voters", f"{total:,}")
    st.caption(f"Latest reporting month: {latest_year}-{latest_month:02d}")

    breakdown = party_breakdown(latest_df)
    breakdown_total = breakdown["registered"].sum()
    breakdown["share_pct"] = (breakdown["registered"] / breakdown_total) * 100
    breakdown["label"] = breakdown.apply(
        lambda row: f"{int(row['registered']):,} ({row['share_pct']:.1f}%)",
        axis=1,
    )
    fig_breakdown = px.bar(
        breakdown,
        x="party",
        y="registered",
        title=f"Statewide Party Breakdown ({latest_year}-{latest_month:02d})",
        text="label",
        custom_data=["share_pct"],
    )
    fig_breakdown.update_traces(
        textposition="outside",
        hovertemplate="Party=%{x}<br>Registered=%{y:,.0f}<br>Share=%{customdata[0]:.2f}%<extra></extra>",
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)

    st.subheader("Top Counties by Registration")
    top_counties_df = top_counties(latest_df, n=10).copy()
    top_counties_df["share_pct"] = (top_counties_df["registered"] / total) * 100
    top_counties_df = top_counties_df.rename(columns={"share_pct": "share_percent"})
    top_counties_df["share_percent"] = top_counties_df["share_percent"].map(lambda value: f"{value:.2f}%")
    st.dataframe(top_counties_df, use_container_width=True, hide_index=True)


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

    change_df = county_trend_change_pct(df, selected_county)
    fig_change = px.line(
        change_df,
        x="date",
        y="change_pct",
        markers=True,
        title=f"Month-over-Month Change (%) - {selected_county}",
    )
    fig_change.update_layout(yaxis_title="percent change")
    fig_change.update_traces(hovertemplate="Date=%{x|%b %Y}<br>Change=%{y:.2f}%<extra></extra>")
    st.plotly_chart(fig_change, use_container_width=True)

    party_df, latest_year, latest_month = county_party_comparison_latest(df, selected_county)
    fig_party = px.bar(
        party_df,
        x="party",
        y="registered",
        title=f"Party Comparison - {selected_county} ({latest_year}-{latest_month:02d})",
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


def render_data_import():
    st.header("Data Import")
    st.caption("Download and parse official Maryland SBE voter registration PDF reports.")

    links, source = scrape_report_links()
    if source == "fixture":
        st.warning("Live page unavailable. Using local HTML fixture fallback.")
    elif source == "none":
        st.error("Could not load report links from live source or fixture.")
        return

    if not links:
        st.warning("No PDF report links found.")
        return

    options = {f"{item['title']} ({item['url']})": item["url"] for item in links}
    selected_labels = st.multiselect("Available reports", list(options.keys()))

    if st.button("Download and Parse Selected Reports", type="primary"):
        if not selected_labels:
            st.info("Select at least one report before importing.")
            return

        selected_urls = [options[label] for label in selected_labels]
        download_results = download_reports(selected_urls)
        status_rows = []
        parsed_frames = []

        for item in download_results:
            if not item["success"]:
                status_rows.append(
                    {
                        "url": item["url"],
                        "download": "failed",
                        "parse": "skipped",
                        "details": item["error"],
                    }
                )
                continue

            try:
                normalized, destination = parse_and_store_pdf(item["path"], source_url=item["url"])
                parsed_frames.append(normalized)
                status_rows.append(
                    {
                        "url": item["url"],
                        "download": "ok",
                        "parse": "ok",
                        "details": f"stored in {destination}",
                    }
                )
            except Exception as exc:
                status_rows.append(
                    {
                        "url": item["url"],
                        "download": "ok",
                        "parse": "failed",
                        "details": str(exc),
                    }
                )

        status_df = pd.DataFrame(status_rows)
        st.subheader("Import Status")
        st.dataframe(status_df, use_container_width=True, hide_index=True)

        if parsed_frames:
            preview_df = pd.concat(parsed_frames, ignore_index=True)
            st.subheader("Parsed Data Preview")
            st.write("Columns:", list(preview_df.columns))
            st.dataframe(preview_df.head(5), use_container_width=True, hide_index=True)
            get_data.clear()
        else:
            st.warning("No report was parsed successfully. Dashboard will continue using fallback data.")


def main():
    st.title("Maryland Voter Registration Dashboard")

    try:
        df, data_source = get_data()
    except FileNotFoundError:
        logger.exception("Data load operation failed: fallback file data/sample.csv was not found")
        st.error("Could not find data/sample.csv. Add the file and rerun the app.")
        st.stop()
    except Exception as exc:
        logger.exception("Data load operation failed while reading dashboard input data")
        st.error(f"Failed to load CSV: {exc}")
        st.stop()

    try:
        validate_dataframe(df, ["year", "month", "county", "party", "registered"])
    except ValueError as exc:
        logger.exception("Validation failed for required dashboard dataframe columns")
        st.error(f"Data validation error: {exc}")
        st.stop()

    quality_df = data_quality_issues(df)
    if not quality_df.empty:
        st.sidebar.warning(f"Data quality issues found: {len(quality_df)} rows")

    if data_source == "fallback":
        st.sidebar.info("Using fallback sample data.")
    else:
        st.sidebar.success("Using imported processed data.")

    page = st.sidebar.radio(
        "Choose a page",
        ["Overview", "County Trends", "Growth Analysis", "Data Import"],
    )

    if page == "Overview":
        render_overview(df)
    elif page == "County Trends":
        render_county_trends(df)
    elif page == "Growth Analysis":
        render_growth_analysis(df)
    else:
        render_data_import()


if __name__ == "__main__":
    main()
