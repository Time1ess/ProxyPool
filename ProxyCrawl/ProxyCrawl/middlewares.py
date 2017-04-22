#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 13:59
# Last modified: 2017-04-22 19:12
# Filename: middlewares.py
# Description:
# Define here the models for your spider middleware
from random import choice

import redis

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

from .agents import AGENTS


class RandomUserAgentMiddleware:
    def process_request(self, request, spider):
        agent = choice(AGENTS)
        request.headers['User-Agent'] = agent


class RandomProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        s.conn = redis.Redis(decode_responses=True)
        return s

    def process_request(self, request, spider):
        proxies = list(self.conn.smembers('available_proxies'))
        if proxies:
            while True:
                proxy = choice(proxies)
                if proxy.startswith('http'):
                    break
            request.meta['proxy'] = proxy
