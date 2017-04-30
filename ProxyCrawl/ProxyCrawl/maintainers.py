#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-29 15:10
# Last modified: 2017-04-30 15:27
# Filename: maintainers.py
# Description:
import time

from twisted.internet import reactor
from twisted.web.client import ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint

from ProxyCrawl.rules import Rule
from ProxyCrawl.spiders.proxy_spider import ProxySpider


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
            d = rule_maps[rule_name].engine.stop()  # Shutdown gracefully
            self.runner.crawlers.discard(rule_maps[rule_name])
            self.conn.hset('Rule:' + rule_name, 'status', 'waiting')

            def _callback(*args, **kwargs):
                self.conn.hset('Rule:' + rule_name, 'status', 'stopped')
            d.addBoth(_callback)
        else:
            if self.conn.hget('Rule:' + rule_name, 'status') != 'waiting':
                self.conn.hset('Rule:' + rule_name, 'status', 'stopped')

    def _start_or_unpause_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            if self.conn.hget('Rule:' + rule_name, 'status') != 'waiting' and\
                    rule_maps[rule_name].engine.paused is True:
                rule_maps[rule_name].engine.unpause()
                self.conn.hset('Rule:' + rule_name, 'status', 'started')
        else:
            rule = Rule.load(rule_name)
            d = self.runner.crawl(ProxySpider, rule)
            # Set status to stopped if crawler finished
            d.addBoth(lambda _: self.conn.hset(
                'Rule:' + rule_name, 'status', 'finished'))
            self.conn.hset('Rule:' + rule_name, 'status', 'started')

    def _pause_crawler(self, rule_maps, rule_name):
        if rule_maps.get(rule_name, None):
            if self.conn.hget('Rule:' + rule_name, 'status') != 'waiting':
                rule_maps[rule_name].engine.pause()
                self.conn.hset('Rule:' + rule_name, 'status', 'paused')

    def _reload_crawler(self, rule_maps, rule_name):
        if not rule_maps.get(rule_name, None):
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


class ProxyMaintainer:
    """
    A maintainer to maintain available and rookie proxies

    Author: David
    """
    def __init__(self, conn):
        self.conn = conn
        self.currents = 0

    def _test_proxy_alive(self, host, port, protocol, proxy_type,
                          url=b'http://www.baidu.com', timeout=10):
        endpoint = TCP4ClientEndpoint(reactor, host, int(port))
        agent = ProxyAgent(endpoint)
        d = agent.request(b'GET', url)
        self.currents += 1
        proxy = '{}:{}'.format(host, port)
        key = 'proxy_info:' + proxy

        if proxy_type == 'rookies_checking':
            def _callback(ignored):
                pipe = self.conn.pipeline(False)
                pipe.zrem('rookies_checking', proxy)
                pipe.hset(key, 'failed_times', 0)
                # Move proxy from rookies to availables
                pipe.smove('rookie_proxies', 'available_proxies',
                           '{}://{}'.format(protocol, proxy))
                pipe.zadd('availables_checking', proxy, time.time() + 30)
                pipe.execute()

            def _errback(err):
                if self.conn.hincrby(key, 'failed_times', 1) < 3:
                    # If not reach the maximum of failed_times
                    # Since it is not important so re-check it after 10 seconds
                    self.conn.zadd('rookies_checking', proxy, time.time() + 10)
                else:
                    pipe = self.conn.pipeline(False)
                    pipe.zrem('rookies_checking', proxy)
                    pipe.smove('rookie_proxies', 'dead_proxies',
                               '{}://{}'.format(protocol, proxy))
                    pipe.execute()
        else:
            def _callback(ignored):
                pipe = self.conn.pipeline(False)
                pipe.hset(key, 'failed_times', 0)
                pipe.zadd('availables_checking', proxy, time.time() + 30)
                pipe.smove('lost_proxies', 'available_proxies',
                           '{}://{}'.format(protocol, proxy))
                pipe.execute()

            def _errback(err):
                pipe = self.conn.pipeline(False)
                if self.conn.hincrby(key, 'failed_times', 1) < 3:
                    pipe.zadd('availables_checking', proxy, time.time() + 10)
                    pipe.smove('available_proxies', 'lost_proxies',
                               '{}://{}'.format(protocol, proxy))
                else:
                    pipe.zrem('availables_checking', proxy)
                    pipe.smove('lost_proxies', 'dead_proxies',
                               '{}://{}'.format(protocol, proxy))
                    pipe.delete(key)
                pipe.execute()

        d.addCallbacks(_callback, _errback)
        reactor.callLater(timeout, d.cancel)

        def _clean(ignored):
            self.currents -= 1

        d.addBoth(_clean)

    def __call__(self):
        for check_key in ['rookies_checking', 'availables_checking']:
            proxies = self.conn.zrangebyscore(check_key, 0, time.time())
            for proxy in proxies:
                key = 'proxy_info:' + proxy
                ret = self.conn.hmget(key, 'ip', 'port', 'protocol')
                if not all(ret):
                    self.conn.zrem(check_key, proxy)
                    self.conn.delete(key)
                    continue
                ip, port, protocol = ret
                self._test_proxy_alive(ip, port, protocol, check_key)
        self.conn.set('currents', self.currents)


class ScheduleMaintainer:
    """
    A maintainer to schedule proxies checking.

    Schedule proxy which is in rookie_proxies or available_proxies or
    lost_proxies but has no checking calls with ProxyMaintainer.

    Author: David
    """
    def __init__(self, conn):
        self.conn = conn

    def __call__(self):
        schedule_pipe = self.conn.pipeline(False)
        for key in ['rookie_proxies', 'available_proxies', 'lost_proxies']:
            proxies = [p[p.rfind('/')+1:] for p in
                       iter(self.conn.smembers(key))]
            pipe = self.conn.pipeline(False)
            for proxy in proxies:
                if key == 'rookie_proxies':
                    pipe.zrank('rookies_checking', proxy)
                else:
                    pipe.zrank('availables_checking', proxy)
            ranks = pipe.execute()
            for idx, rank in enumerate(ranks):
                if rank:
                    continue
                if key == 'rookie_proxies':
                    schedule_pipe.zadd('rookies_checking', proxies[idx],
                                       time.time() + 10)
                else:
                    schedule_pipe.zadd('availables_checking', proxies[idx],
                                       time.time() + 3)
        schedule_pipe.execute()
