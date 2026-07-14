# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, Optional

from playwright.async_api import BrowserContext, BrowserType

from base.base_crawler import AbstractCrawler
from tools import utils

from .client import CctvPeopleClient


class CctvPeopleCrawler(AbstractCrawler):
    def __init__(self):
        pass

    async def start(self):
        utils.logger.info("[CctvPeopleCrawler] Starting HTTP JSONP crawler ...")
        client = CctvPeopleClient()
        await client.crawl_articles()
        utils.logger.info("[CctvPeopleCrawler] Finished")

    async def search(self):
        await self.start()

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        raise NotImplementedError("CCTV People uses HTTP JSONP API, no browser needed")
