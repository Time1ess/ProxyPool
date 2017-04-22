#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 20:23
# Last modified: 2017-04-22 19:13
# Filename: base_spiders.py
# Description:
import scrapy

from scrapy.http import Request


class BaseSpider(scrapy.Spider):
    url_fmt = '{}'
    max_page = 100
    current_pages = 0

    def __init__(self, *args, **kwargs):
        self.start_urls = [self.url_fmt.format(k)
            for k in range(1, self.max_page)]

    def new_requests(self):
        if self.current_pages > 500:
            return
        for url in self.start_urls:
            yield Request(url, dont_filter=True)
            self.current_pages += 1
