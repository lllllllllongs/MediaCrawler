# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

import config
from store import cctv_news as cctv_news_store
from tools import utils
from var import source_keyword_var


class CctvNewsClient:
    def __init__(self):
        self.max_articles = getattr(config, "CCTV_NEWS_MAX_ARTICLES", 40)
        self.crawl_interval = getattr(config, "CCTV_NEWS_CRAWL_INTERVAL", 0.5)
        self.items_per_page = 80
        self.api_template = (
            "https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/"
            "society_{page}.jsonp?cb=society"
        )

    async def crawl_articles(self):
        """Crawl articles from all pages until max_articles reached"""
        crawled = 0
        page = 1

        while crawled < self.max_articles:
            articles = await self._fetch_page(page)
            if not articles:
                utils.logger.info(f"[CctvNewsClient] No more articles at page {page}, stopping")
                break

            utils.logger.info(f"[CctvNewsClient] Page {page}: got {len(articles)} articles")

            for article in articles:
                if crawled >= self.max_articles:
                    break

                try:
                    save_item = {
                        "title": article.get("title", ""),
                        "brief": article.get("brief", ""),
                        "publish_time": article.get("focus_date", ""),
                        "source": "央视网",
                        "article_url": article.get("url", ""),
                        "image": article.get("image", ""),
                        "source_keyword": source_keyword_var.get(),
                    }
                    await cctv_news_store.update_cctv_news_article(save_item)
                    crawled += 1
                except Exception as e:
                    utils.logger.error(f"[CctvNewsClient] Error saving article: {e}")

                await asyncio.sleep(self.crawl_interval)

            page += 1

        utils.logger.info(f"[CctvNewsClient] Finished: {crawled} articles crawled")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _fetch_page(self, page: int) -> List[Dict]:
        """Fetch and parse one page of JSONP data"""
        url = self.api_template.format(page=page)
        utils.logger.info(f"[CctvNewsClient] Fetching: {url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        text = response.text

        # Strip JSONP wrapper: society({...}) or society([...])
        jsonp_match = re.search(r"society\s*\((.+)\)\s*;?\s*$", text, re.DOTALL)
        if jsonp_match:
            json_str = jsonp_match.group(1)
        else:
            json_str = text

        data = json.loads(json_str)

        # Data structure: {"data": {"list": [...]}} or {"data": [...]}
        if isinstance(data, dict):
            inner = data.get("data", data)
            if isinstance(inner, dict):
                return inner.get("list", [])
            if isinstance(inner, list):
                return inner
        if isinstance(data, list):
            return data

        return []
