from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Error as PlaywrightError

from media_platform.douyin.core import DouYinCrawler


@pytest.mark.asyncio
async def test_open_index_page_retries_temporary_connection_error(monkeypatch):
    crawler = DouYinCrawler()
    crawler.context_page = AsyncMock()
    crawler.context_page.goto.side_effect = [
        PlaywrightError("net::ERR_CONNECTION_CLOSED"),
        None,
    ]
    sleep = AsyncMock()
    monkeypatch.setattr("media_platform.douyin.core.asyncio.sleep", sleep)

    await crawler.open_index_page()

    assert crawler.context_page.goto.await_count == 2
    crawler.context_page.goto.assert_awaited_with(
        crawler.index_url,
        wait_until="domcontentloaded",
        timeout=60_000,
    )
    sleep.assert_awaited_once_with(3)


@pytest.mark.asyncio
async def test_open_index_page_raises_after_three_failures(monkeypatch):
    crawler = DouYinCrawler()
    crawler.context_page = AsyncMock()
    crawler.context_page.goto.side_effect = PlaywrightError(
        "net::ERR_CONNECTION_CLOSED"
    )
    monkeypatch.setattr(
        "media_platform.douyin.core.asyncio.sleep",
        AsyncMock(),
    )

    with pytest.raises(PlaywrightError):
        await crawler.open_index_page()

    assert crawler.context_page.goto.await_count == 3
