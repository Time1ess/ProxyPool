#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 14:16
# Last modified: 2017-04-19 21:33
# Filename: xici.py
# Description:
import scrapy

from scrapy.http import Request

from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader
from ProxyCrawl.spiders.base_spiders import BaseSpider


class XiciSpider(BaseSpider):
    name = "xici"
    allowed_domains = ["xicidaili.com"]
    url_fmt = 'http://www.xicidaili.com/nt/{}'

    def parse(self, response):
        self.current_pages -= 1
        self.new_requests()
        if response.status != 200:
            return None
        ip_list = response.xpath('//table[@id="ip_list"]//tr')[1:]
        for ip_item in ip_list:
            content = ip_item.extract()
            l = ProxyItemLoader(item=ProxyItem(), selector=ip_item)
            l.add_xpath('proxy', 'td[2]/text()')
            l.add_xpath('proxy', 'td[3]/text()')
            l.add_xpath('ip', 'td[2]/text()')
            l.add_xpath('port', 'td[3]/text()')
            l.add_xpath('addr', 'td[4]//text()')
            l.add_xpath('mode', 'td[5]/text()')
            l.add_xpath('protocol', 'td[6]/text()')
            l.add_xpath('validation_time', 'td[10]/text()')
            yield l.load_item()
