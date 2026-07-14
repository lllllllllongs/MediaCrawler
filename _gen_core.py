content = r'''# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import os
from typing import Dict, List, Optional

from playwright.async_api import BrowserContext, BrowserType, Page, async_playwright

import config
from base.base_crawler import AbstractCrawler
from tools import utils
from var import crawler_type_var, source_keyword_var

from .client import CctvNewsClient
from .exception import DataFetchError
from .help import filter_article_links


class CctvNewsCrawler(AbstractCrawler):
    context_page: Page
    cctv_client: CctvNewsClient
    browser_context: BrowserContext

    def __init__(self):
        self.list_url = "https://news.cctv.com/society/"
        self.user_agent = utils.get_user_agent()

    async def start(self):
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            self.browser_context = await self.launch_browser(
                chromium, None, self.user_agent, headless=config.HEADLESS
            )
            self.context_page = await self.browser_context.new_page()

            self.cctv_client = CctvNewsClient(
                playwright_page=self.context_page,
            )

            crawler_type = crawler_type_var.get()
            if crawler_type == "search":
                await self.search()
            elif crawler_type == "detail":
                await self.search()
            else:
                await self.search()

            utils.logger.info("[CctvNewsCrawler] Crawling finished")

    async def search(self):
        utils.logger.info("[CctvNewsCrawler.search] Begin search articles")

        keyword = source_keyword_var.get()
        if keyword:
            utils.logger.info(f"[CctvNewsCrawler.search] Searching keyword: {keyword}")
            await self.cctv_client.search_articles(keyword)
        else:
            utils.logger.info("[CctvNewsCrawler.search] Crawling latest articles from list page")
            await self.cctv_client.crawl_list_page(self.list_url)

        await self.browser_context.close()
        utils.logger.info("[CctvNewsCrawler.search] Search finished")

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        utils.logger.info("[CctvNewsCrawler.launch_browser] Creating browser context ...")
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(os.getcwd(), "browser_data", "cctv_news")
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
                channel="chrome",
            )
            return browser_context
        else:
            browser = await chromium.launch(headless=headless, proxy=playwright_proxy, channel="chrome")
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context

    async def close(self):
        if self.browser_context:
            await self.browser_context.close()
        utils.logger.info("[CctvNewsCrawler.close] Browser context closed")
'''

with open(r'D:\codex\MediaCrawler\MediaCrawler\media_platform\cctv_news\core.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("core.py created")
