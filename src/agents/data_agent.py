from __future__ import annotations

import pandas as pd

from src.data_loader import EXPECTED_COLUMNS, load_dashboard_data, parse_and_store_pdf
from src.logging_config import get_logger
from src.sbe_scraper import download_report, scrape_report_links

logger = get_logger(__name__)


class DataAgent:
    """Data Agent.

    Responsibility: acquire reports, parse/normalize data, and return a
    Stage-1-schema dataframe.
    """

    def run(self, report_selection: str | list[str] = "latest") -> pd.DataFrame:
        logger.info("DataAgent started with report_selection=%s", report_selection)

        selected_urls: list[str] = []
        if isinstance(report_selection, list):
            selected_urls = report_selection
        elif report_selection == "latest":
            links, source = scrape_report_links()
            logger.info("DataAgent link source=%s, links_found=%s", source, len(links))
            if links:
                selected_urls = [links[0]["url"]]

        for url in selected_urls:
            try:
                pdf_path = download_report(url)
                normalized, _destination = parse_and_store_pdf(pdf_path=str(pdf_path), source_url=url)
                logger.info("DataAgent parsed %s normalized rows from %s", len(normalized), url)
                return normalized[[*EXPECTED_COLUMNS]].copy()
            except Exception as exc:
                logger.warning("DataAgent failed import for URL '%s': %s", url, exc)

        fallback_df, source = load_dashboard_data()
        logger.info("DataAgent using fallback dashboard data source=%s, rows=%s", source, len(fallback_df))
        return fallback_df[[*EXPECTED_COLUMNS]].copy()
