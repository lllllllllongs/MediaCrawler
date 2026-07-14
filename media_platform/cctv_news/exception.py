# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from httpx import RequestError


class DataFetchError(RequestError):
    """something error when fetch"""
