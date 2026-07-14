# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict

import config
from base.base_crawler import AbstractStore
from tools.async_file_writer import AsyncFileWriter
from var import crawler_type_var


class CctvPeopleCsvStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_people", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_to_csv(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvPeopleJsonStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_people", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_single_item_to_json(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvPeopleJsonlStoreImplement(AbstractStore):
    def __init__(self):
        self.writer = AsyncFileWriter(platform="cctv_people", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        await self.writer.write_to_jsonl(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        pass

    async def store_creator(self, creator: Dict):
        pass


class CctvPeopleExcelStoreImplement:
    def __new__(cls):
        from store.excel_store_base import ExcelStoreBase
        return ExcelStoreBase.get_instance(
            platform="cctv_people",
            crawler_type=crawler_type_var.get()
        )
