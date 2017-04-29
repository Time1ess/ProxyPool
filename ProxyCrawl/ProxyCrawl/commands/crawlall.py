#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-25 16:25
# Last modified: 2017-04-29 14:45
# Filename: crawlall.py
# Description:
import os

import redis

from twisted.internet import reactor, task, defer
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from ProxyCrawl.rules import Rule
from ProxyCrawl.spiders.proxy_spider import ProxySpider
from ProxyCrawl.settings import PROJECT_ROOT


class RuleMaintainer:
    """
    A maintainer to maintain rules.

    Author: David
    """
    def __init__(self, conn, runner):
        self.conn = conn
        self.runner = runner

    def _gen_rule_maps(self):
        _rule_maps = {}
        for crawler in self.runner.crawlers:
            rule_name = crawler.spider.rule.name
            _rule_maps[rule_name] = crawler
        return _rule_maps

    def _stop_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            d = rule_maps[rule_name].stop()  # Shutdown gracefully
            self.conn.hset('Rule:' + rule_name, 'status', 'waiting')
            def _callback(*args, **kwargs):
                self.conn.hset('Rule:' + rule_name, 'status', 'stopped')
            d.addBoth(_callback)

    def _start_or_unpause_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            if self.conn.hget('Rule:' + rule_name, 'status') != 'waiting' and\
                    rule_maps[rule_name].engine.paused == True:
                rule_maps[rule_name].engine.unpause()
                self.conn.hset('Rule:' + rule_name, 'status', 'started')
        else:
            rule = Rule.load(rule_name)
            self.runner.crawl(ProxySpider, rule)
            self.conn.hset('Rule:' + rule_name, 'status', 'started')

    def _pause_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            if self.conn.hget('Rule:' + rule_name, 'status') != 'waiting':
                rule_maps[rule_name].engine.pause()
                self.conn.hset('Rule:' + rule_name, 'status', 'paused')

    def _reload_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            return
        if self.conn.hget('Rule:' + rule_name, 'status') == 'waiting':
            return
        spider = rule_maps[rule_name].spider
        try:
            rule = Rule.load(rule_name)
            spider.rule = rule
        except ValueError:
            return

    def __call__(self):
        while True:
            rule_maps = self._gen_rule_maps()
            job = self.conn.lpop('Jobs')
            if not job:
                break
            action, rule_name = job.split('|')
            if action == 'pause':
                self._pause_crawler(rule_maps, rule_name)
            elif action == 'stop':
                self._stop_crawler(rule_maps, rule_name)
            elif action == 'start':
                self._start_or_unpause_crawler(rule_maps, rule_name)
            elif action == 'reload':
                self._reload_crawler(rule_maps, rule_name)

class CrawlAll(ScrapyCommand):
    requires_project = True
    excludes = []

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        conn = redis.Redis(decode_responses=True)
        runner = CrawlerRunner(get_project_settings())
        try:
            rules = Rule.loads()
            if not rules:
                raise ValueError
        except ValueError:
            print('Error in loading Redis rules, fallback to CSV rules')
            rules = Rule.loads('csv')
        for rule in rules:
            rule.save()
            if rule.name in self.excludes:
                continue
            if conn.hget('Rule:' + rule.name, 'status') == 'stopped':
                continue
            runner.crawl(ProxySpider, rule)
        # stop after all spiders closed
        # d = runner.join()
        # if d.called:
        #    return
        # d.addBoth(lambda _: reactor.stop())
        rule_maintainer = RuleMaintainer(conn, runner)
        lc = task.LoopingCall(rule_maintainer)
        lc.start(1)
        reactor.run()
