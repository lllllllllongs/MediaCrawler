# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import csv
import json
import os
import pathlib
from typing import Dict

import aiofiles

import config
from base.base_crawler import AbstractStore
from tools import utils
from tools.async_file_writer import AsyncFileWriter
from var import crawler_type_var


class CctvNewsCsvStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_news", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_to_csv(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvNewsJsonStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_news", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_single_item_to_json(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvNewsJsonlStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_news", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_to_jsonl(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvNewsExcelStoreImplement:
    def __new__(cls):
        from store.excel_store_base import ExcelStoreBase
        return ExcelStoreBase.get_instance(
            platform="cctv_news",
            crawler_type=crawler_type_var.get()
        )
