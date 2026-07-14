content = r'''# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, quote

from playwright.async_api import Page

import config
from store import cctv_news as cctv_news_store
from tools import utils
from var import source_keyword_var


class CctvNewsClient:
    def __init__(self, playwright_page: Page):
        self.playwright_page = playwright_page
        self.base_url = "https://news.cctv.com"
        self.list_url = "https://news.cctv.com/society/"
        self.max_articles = getattr(config, "CCTV_NEWS_MAX_ARTICLES", 40)
        self.crawl_interval = getattr(config, "CCTV_NEWS_CRAWL_INTERVAL", 1.0)

    async def crawl_list_page(self, list_url: str, max_pages: int = 5):
        """Crawl articles from list page with pagination"""
        page = self.playwright_page
        crawled = 0

        for page_num in range(1, max_pages + 1):
            if page_num == 1:
                target_url = list_url
            else:
                target_url = f"{list_url.rstrip('/')}/index_{page_num}.shtml"

            utils.logger.info(f"[CctvNewsClient.crawl_list_page] Navigating to page {page_num}: {target_url}")
            try:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
            except Exception as e:
                utils.logger.error(f"[CctvNewsClient.crawl_list_page] Failed to load page {page_num}: {e}")
                break

            article_links = await self._extract_list_links()
            utils.logger.info(f"[CctvNewsClient.crawl_list_page] Found {len(article_links)} links on page {page_num}")

            if not article_links:
                utils.logger.info("[CctvNewsClient.crawl_list_page] No more articles, stopping pagination")
                break

            for link_info in article_links:
                if crawled >= self.max_articles:
                    utils.logger.info(f"[CctvNewsClient.crawl_list_page] Reached max articles: {self.max_articles}")
                    return

                article_url = link_info.get("url", "")
                if not article_url:
                    continue

                if not article_url.startswith("http"):
                    article_url = urljoin(self.base_url, article_url)

                utils.logger.info(f"[CctvNewsClient.crawl_list_page] Crawling article {crawled + 1}: {article_url}")
                try:
                    await self._crawl_article_detail(article_url)
                    crawled += 1
                except Exception as e:
                    utils.logger.error(f"[CctvNewsClient.crawl_list_page] Error crawling {article_url}: {e}")

                await asyncio.sleep(self.crawl_interval)

    async def search_articles(self, keyword: str):
        """Search articles by keyword"""
        page = self.playwright_page
        search_url = f"https://search.cctv.com/search.php?qtext={quote(keyword)}&type=web"

        utils.logger.info(f"[CctvNewsClient.search_articles] Searching: {keyword}")
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
        except Exception as e:
            utils.logger.error(f"[CctvNewsClient.search_articles] Failed to load search page: {e}")
            return

        article_links = await self._extract_search_links()
        utils.logger.info(f"[CctvNewsClient.search_articles] Found {len(article_links)} search results")

        crawled = 0
        for link_info in article_links:
            if crawled >= self.max_articles:
                break

            article_url = link_info.get("url", "")
            if not article_url:
                continue
            if not article_url.startswith("http"):
                article_url = urljoin(self.base_url, article_url)

            utils.logger.info(f"[CctvNewsClient.search_articles] Crawling article {crawled + 1}: {article_url}")
            try:
                await self._crawl_article_detail(article_url)
                crawled += 1
            except Exception as e:
                utils.logger.error(f"[CctvNewsClient.search_articles] Error: {e}")

            await asyncio.sleep(self.crawl_interval)

    async def _extract_list_links(self) -> List[Dict]:
        """Extract article links from the channel list page"""
        page = self.playwright_page
        links = []

        try:
            items = await page.evaluate('''() => {
                const results = [];
                const selectors = [
                    "ul.list li a",
                    ".list ul li a",
                    ".news_list li a",
                    ".md-list li a",
                    ".content_list li a",
                    "a[href*='/society/']",
                    "a[href*='news.cctv.com']",
                ];
                const seen = new Set();
                for (const sel of selectors) {
                    try {
                        document.querySelectorAll(sel).forEach(el => {
                            const href = el.getAttribute("href");
                            const title = el.textContent.trim();
                            if (href && title && !seen.has(href)) {
                                seen.add(href);
                                results.push({url: href, title: title});
                            }
                        });
                    } catch(e) {}
                }
                return results.slice(0, 30);
            }''')
            links = items if items else []
        except Exception as e:
            utils.logger.error(f"[CctvNewsClient._extract_list_links] Error: {e}")

        return links

    async def _extract_search_links(self) -> List[Dict]:
        """Extract article links from search results page"""
        page = self.playwright_page
        links = []

        try:
            items = await page.evaluate('''() => {
                const results = [];
                const selectors = [
                    ".search_result li a",
                    ".result-list li a",
                    ".search-list a",
                    "a[href*='news.cctv.com']",
                    "a[href*='cctv.com']",
                ];
                const seen = new Set();
                for (const sel of selectors) {
                    try {
                        document.querySelectorAll(sel).forEach(el => {
                            const href = el.getAttribute("href");
                            const title = el.textContent.trim();
                            if (href && title && !seen.has(href) && title.length > 5) {
                                seen.add(href);
                                results.push({url: href, title: title});
                            }
                        });
                    } catch(e) {}
                }
                return results.slice(0, 30);
            }''')
            links = items if items else []
        except Exception as e:
            utils.logger.error(f"[CctvNewsClient._extract_search_links] Error: {e}")

        return links

    async def _crawl_article_detail(self, article_url: str):
        """Crawl a single article detail page"""
        page = self.playwright_page

        try:
            await page.goto(article_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
        except Exception as e:
            utils.logger.error(f"[CctvNewsClient._crawl_article_detail] Failed to load: {article_url}: {e}")
            return

        article_data = await self._extract_article_content(article_url)

        if article_data and article_data.get("title"):
            await cctv_news_store.update_cctv_news_article(article_data)
        else:
            utils.logger.warning(f"[CctvNewsClient._crawl_article_detail] Could not extract content from: {article_url}")

    async def _extract_article_content(self, article_url: str) -> Optional[Dict]:
        """Extract article content fields from detail page"""
        page = self.playwright_page

        try:
            data = await page.evaluate('''() => {
                function getText(selectors) {
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            return el.textContent.trim();
                        }
                    }
                    return "";
                }

                function getContent(selectors) {
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            return el.innerText.trim();
                        }
                    }
                    return "";
                }

                const title = getText([
                    "h1", ".article_title h1", ".title h1",
                    ".content_title", "#title", ".news_title",
                    "meta[property='og:title']",
                ]);

                const body = getContent([
                    ".content_area", ".article_content", "#content_area",
                    ".cnt_bd", ".text_content", "article",
                    ".TRS_Editor", "#article_content",
                ]);

                let publishTime = getText([
                    ".time", ".info .time", ".article_time",
                    ".pub_time", "#pubtime", ".date",
                    "meta[name='publishdate']",
                ]);

                const source = getText([
                    ".source", ".info .source", ".article_source",
                    "#source", ".origin",
                ]);

                return {
                    title: title,
                    body: body,
                    publish_time: publishTime,
                    source: source,
                };
            }''')

            if data and data.get("title"):
                return {
                    "title": data["title"],
                    "body": data.get("body", ""),
                    "publish_time": data.get("publish_time", ""),
                    "source": data.get("source", ""),
                    "article_url": article_url,
                    "source_keyword": source_keyword_var.get(),
                }

        except Exception as e:
            utils.logger.error(f"[CctvNewsClient._extract_article_content] Error: {e}")

        return None
'''

with open(r'D:\codex\MediaCrawler\MediaCrawler\media_platform\cctv_news\client.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("client.py created")
