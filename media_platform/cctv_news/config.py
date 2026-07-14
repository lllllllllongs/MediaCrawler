# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

# CCTV News (society channel) platform configuration

# Channel list page URL
CCTV_NEWS_LIST_URL = "https://news.cctv.com/society/"

# Channel search URL template (use {keyword} placeholder)
CCTV_NEWS_SEARCH_URL = "https://search.cctv.com/search.php?qtext={keyword}" + [char]38 + "type=web"

# Maximum number of articles to crawl per session
CCTV_NEWS_MAX_ARTICLES = 40

# Pause between article detail requests (seconds)
CCTV_NEWS_CRAWL_INTERVAL = 1.0
