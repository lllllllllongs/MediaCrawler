# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict

from var import source_keyword_var

from ._store_impl import (
    CctvNewsCsvStoreImplement,
    CctvNewsJsonStoreImplement,
    CctvNewsJsonlStoreImplement,
    CctvNewsExcelStoreImplement,
)

import config
from base.base_crawler import AbstractStore
from tools import utils


class CctvNewsStoreFactory:
    STORES = {
        "csv": CctvNewsCsvStoreImplement,
        "json": CctvNewsJsonStoreImplement,
        "jsonl": CctvNewsJsonlStoreImplement,
        "excel": CctvNewsExcelStoreImplement,
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = CctvNewsStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError(f"[CctvNewsStoreFactory] Invalid save option: {config.SAVE_DATA_OPTION}")
        return store_class()


async def update_cctv_news_article(article_item: Dict):
    if not article_item:
        return

    save_item = {
        "title": article_item.get("title", ""),
        "brief": article_item.get("brief", ""),
        "publish_time": article_item.get("publish_time", ""),
        "source": article_item.get("source", ""),
        "article_url": article_item.get("article_url", ""),
        "image": article_item.get("image", ""),
        "source_keyword": article_item.get("source_keyword", ""),
        "last_modify_ts": utils.get_current_timestamp(),
    }

    utils.logger.info(f"[store.cctv_news] Saving: {save_item.get('title', '')[:40]} ...")
    await CctvNewsStoreFactory.create_store().store_content(content_item=save_item)
