# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

import config
from store import cctv_people as cctv_people_store
from tools import utils
from var import source_keyword_var


class CctvPeopleClient:
    def __init__(self):
        self.max_articles = getattr(config, "CCTV_PEOPLE_MAX_ARTICLES", 40)
        self.crawl_interval = getattr(config, "CCTV_PEOPLE_CRAWL_INTERVAL", 0.5)
        self.items_per_page = 100
        self.api_template = (
            "https://api.cntv.cn/NewArticle/getArticleListByPageId"
            "?serviceId=pcnews"
            "&id=PAGEEbwoCRG76wMgJefnNvVh170118"
            "&p={page}"
            "&n=100"
            "&cb=callback1"
        )
        self._china_tz = timezone(timedelta(hours=8))

    async def crawl_articles(self):
        """Crawl articles from all pages until max_articles reached"""
        crawled = 0
        page = 1

        while crawled < self.max_articles:
            articles = await self._fetch_page(page)
            if not articles:
                utils.logger.info(f"[CctvPeopleClient] No more articles at page {page}, stopping")
                break

            utils.logger.info(f"[CctvPeopleClient] Page {page}: got {len(articles)} articles")

            for article in articles:
                if crawled >= self.max_articles:
                    break

                try:
                    save_item = {
                        "title": article.get("title", ""),
                        "brief": article.get("desc", ""),
                        "publish_time": self._convert_timestamp(article.get("focus_date", "")),
                        "source": "央视网",
                        "article_url": article.get("url", ""),
                        "image": article.get("image", ""),
                        "source_keyword": source_keyword_var.get(),
                    }
                    await cctv_people_store.update_cctv_people_article(save_item)
                    crawled += 1
                except Exception as e:
                    utils.logger.error(f"[CctvPeopleClient] Error saving article: {e}")

                await asyncio.sleep(self.crawl_interval)

            page += 1

        utils.logger.info(f"[CctvPeopleClient] Finished: {crawled} articles crawled")

    def _convert_timestamp(self, ts_value) -> str:
        """Convert millisecond timestamp to datetime string. e.g. 1783464029995 -> 2026-07-08 06:39:29"""
        if not ts_value:
            return ""
        try:
            ts = int(ts_value)
            if ts > 1_000_000_000_000:
                ts = ts // 1000
            dt = datetime.fromtimestamp(ts, tz=self._china_tz)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            return str(ts_value)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _fetch_page(self, page: int) -> List[Dict]:
        """Fetch and parse one page of JSONP data"""
        url = self.api_template.format(page=page)
        utils.logger.info(f"[CctvPeopleClient] Fetching: {url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        text = response.text

        # Strip JSONP wrapper: callback1({...})
        jsonp_match = re.search(r"callback1\s*\((.+)\)\s*;?\s*$", text, re.DOTALL)
        if jsonp_match:
            json_str = jsonp_match.group(1)
        else:
            json_str = text

        data = json.loads(json_str)

        # Data structure: {"data": {"list": [...]}} or {"data": [...]} or {"list": [...]}
        if isinstance(data, dict):
            inner = data.get("data", data)
            if isinstance(inner, dict):
                items = inner.get("list", inner.get("item", []))
                return items if isinstance(items, list) else []
            if isinstance(inner, list):
                return inner
            # Direct list key
            items = data.get("list", data.get("item", []))
            return items if isinstance(items, list) else []
        if isinstance(data, list):
            return data

        return []
