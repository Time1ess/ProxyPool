#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-27 09:12
# Last modified: 2017-04-27 09:36
# Filename: migrate.py
# Description:
labels = ('name', 'url_fmt', 'row_xpath', 'host_xpath', 'port_xpath',
          'addr_xpath', 'mode_xpath', 'proto_xpath', 'vt_xpath')
data = [
    ('DoubleSixip', 'http://www.66ip.cn/{}.html', '//div[@id="main"]//tr',
     'td[1]/text()', 'td[2]/text()', 'td[3]/text()', 'td[4]/text()', 'null',
     'td[5]/text()'),
    ('kuaidaili', 'http://www.kuaidaili.com/free/intr/{}',
     '//div[@id="list"]/table//tr', 'td[1]/text()', 'td[2]/text()',
     'td[5]//text()', 'td[3]/text()', 'td[4]/text()', 'td[7]/text()'),
    ('kuaidaili2', 'http://www.kuaidaili.com/free/inha/{}',
     '//div[@id="list"]/table//tr', 'td[1]/text()', 'td[2]/text()',
     'td[5]//text()', 'td[3]/text()', 'td[4]/text()', 'td[7]/text()'),
    ('xici', 'http://www.xicidaili.com/nt/{}', '//table[@id="ip_list"]//tr',
     'td[2]/text()', 'td[3]/text()', 'td[4]//text()', 'td[5]/text()',
     'td[6]/text()', 'td[10]/text()')]



with open('rules.csv', 'wb') as f:
    f.write('{}\n'.format(' '.join(labels)).encode('utf-8'))
    for item in data:
        f.write('{}\n'.format(' '.join(item)).encode('utf-8'))
