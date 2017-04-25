#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-25 16:25
# Last modified: 2017-04-25 21:39
# Filename: crawlall.py
# Description:
import scrapy
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CrawlAll(ScrapyCommand):
    requires_project = True
    excludes = []

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        for spider in process.spider_loader.list():
            if spider in self.excludes:
                continue
            spider_cls = process.spider_loader.load(spider)
            process.crawl(spider_cls)
        process.start()
