#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-25 16:25
# Last modified: 2017-04-27 10:34
# Filename: crawlall.py
# Description:
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ProxyCrawl.rules import Rule
from ProxyCrawl.spiders.proxy_spider import ProxySpider


class CrawlAll(ScrapyCommand):
    requires_project = True
    excludes = []

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        process = CrawlerProcess(get_project_settings())
        try:
            rules = Rule.loads()
            if not rules:
                raise ValueError
        except ValueError:
            print('Error in loading Redis rules, fallback to CSV rules')
            rules = Rule.loads('csv')
        print(rules)
        for rule in rules:
            rule.save()
            if rule.name in self.excludes:
                continue
            process.crawl(ProxySpider, rule)
        process.start()
