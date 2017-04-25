#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 19:46
# Last modified: 2017-04-25 17:03
# Filename: kuaidaili.py
# Description:
import scrapy

from scrapy.http import Request

from ProxyCrawl.items import ProxyItem
from ProxyCrawl.loaders import ProxyItemLoader
from ProxyCrawl.spiders.base_spiders import BaseSpider


class KuaidailiSpider(BaseSpider):
    name = "kuaidaili"
    allowed_domains = ["kuaidaili.com"]
    url_fmt = 'http://www.kuaidaili.com/free/intr/{}'

    def parse(self, response):
        if response.status != 200:
            return None
        ip_list = response.xpath('//div[@id="list"]/table//tr')[1:]
        for ip_item in ip_list:
            l = ProxyItemLoader(item=ProxyItem(), selector=ip_item)
            l.add_xpath('proxy', 'td[1]/text()')
            l.add_xpath('proxy', 'td[2]/text()')
            l.add_xpath('ip', 'td[1]/text()')
            l.add_xpath('port', 'td[2]/text()')
            l.add_xpath('addr', 'td[5]//text()')
            l.add_xpath('mode', 'td[3]/text()')
            l.add_xpath('protocol', 'td[4]/text()')
            l.add_xpath('validation_time', 'td[7]/text()')
            yield l.load_item()



class KuaidailiSpider2(KuaidailiSpider):
    name = "kuaidaili2"
    url_fmt = 'http://www.kuaidaili.com/free/inha/{}'
