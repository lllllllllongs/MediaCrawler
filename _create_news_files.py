import os
base = r'D:\codex\MediaCrawler\MediaCrawler\media_platform\cctv_news'

files = {}

files['exception.py'] = '''# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from httpx import RequestError


class DataFetchError(RequestError):
    """something error when fetch"""
'''

files['field.py'] = '''# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from enum import Enum


class SearchSortType(Enum):
    DEFAULT = "default"
    DATE = "date"
'''

files['help.py'] = '''# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, List


def filter_article_links(link_list):
    seen = set()
    result = []
    for link_item in link_list:
        url = link_item.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(link_item)
    return result
'''

for name, content in files.items():
    path = os.path.join(base, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {name}")
