from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

STATS_URL = "https://elections.maryland.gov/voter_registration/stats.html"

logger = logging.getLogger(__name__)


def _extract_pdf_links(html: str, base_url: str) -> list[dict[str, str]]:
    """Extract unique PDF links from page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[dict[str, str]] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()
        if not href:
            continue
        absolute = urljoin(base_url, href)
        if not absolute.lower().endswith(".pdf"):
            continue
        if absolute in seen:
            continue

        seen.add(absolute)
        links.append(
            {
                "title": anchor.get_text(" ", strip=True) or Path(urlparse(absolute).path).name,
                "url": absolute,
            }
        )

    return links


def scrape_report_links(
    url: str = STATS_URL,
    fixture_path: str = "data/fixtures/sbe_stats_fixture.html",
    timeout: int = 25,
) -> tuple[list[dict[str, str]], str]:
    """Scrape PDF report links from SBE stats page, with local fixture fallback.

    Returns a tuple of (links, source) where source is "live" or "fixture".
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        links = _extract_pdf_links(response.text, url)
        if links:
            logger.info("Found %s PDF links from live source", len(links))
            return links, "live"
        logger.warning("Live source returned no PDF links; trying fixture fallback")
    except requests.RequestException as exc:
        logger.warning("Live source unavailable (%s); trying fixture fallback", exc)

    fixture_file = Path(fixture_path)
    if fixture_file.exists():
        html = fixture_file.read_text(encoding="utf-8")
        links = _extract_pdf_links(html, url)
        logger.info("Found %s PDF links from fixture", len(links))
        return links, "fixture"

    logger.error("No live links and fixture not found at %s", fixture_file)
    return [], "none"


def download_report(url: str, output_dir: str = "data/raw", timeout: int = 60) -> Path:
    """Download a PDF report URL into the raw data folder."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = Path(urlparse(url).path).name or "report.pdf"
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    destination = output_path / filename

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    destination.write_bytes(response.content)
    logger.info("Downloaded %s to %s", url, destination)
    return destination


def download_reports(urls: list[str], output_dir: str = "data/raw") -> list[dict[str, Any]]:
    """Download many reports and return status per URL."""
    results: list[dict[str, Any]] = []
    for url in urls:
        try:
            path = download_report(url, output_dir=output_dir)
            results.append({"url": url, "success": True, "path": str(path), "error": ""})
        except requests.RequestException as exc:
            logger.error("Failed to download %s: %s", url, exc)
            results.append({"url": url, "success": False, "path": "", "error": str(exc)})
    return results
