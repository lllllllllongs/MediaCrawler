# -*- coding: utf-8 -*-
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
