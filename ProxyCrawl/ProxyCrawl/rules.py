#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-26 11:14
# Last modified: 2017-04-27 10:33
# Filename: rules.py
# Description:
import redis

from scrapy.utils.conf import init_env


conn = redis.Redis(decode_responses=True)
labels = ('name', 'url_fmt', 'row_xpath', 'host_xpath', 'port_xpath',
          'addr_xpath', 'mode_xpath', 'proto_xpath', 'vt_xpath', 'max_page')


class Rule:
    """
    A rule tells how to crawl proxies from a site.

    keys in rule_dict:
        name:
        url_fmt:
        row_xpath: Extract one data row from response
        host_xpath: Extract host from data row
        port_xpath: Extract port from data row
        addr_xpath:
        mode_xpath:
        proto_xpath:
        vt_xpath: validation_time
        max_page: 200

    Author: David
    """

    def __getattr__(self, name):
        return self.rule_dict.get(name)

    def __str__(self):
        return 'Rule:{} - {}'.format(self.name, self.rule_dict)

    def __repr__(self):
        return 'Rule:{} - <{}>'.format(self.name, self.url_fmt)

    def __check_vals(self):
        if not all([
                self.name, self.url_fmt, self.row_xpath, self.host_xpath,
                self.port_xpath, self.addr_xpath, self.mode_xpath,
                self.proto_xpath, self.vt_xpath]):
            raise ValueError('Rule arguments not set properly')

    def __init__(self, rule_dict):
        self.rule_dict = rule_dict
        self.__check_vals()

    @staticmethod
    def _load_redis_rule(name=None):
        """
        Load rule from redis, raise ValueError if no rule fetched.

        Author: David
        """
        if name is None:
            keys = ['Rule:'+key for key in conn.smembers('Rules')]
            rule_dicts = []
            for key in keys:
                res = conn.hgetall(key)
                if not res:
                    raise ValueError('No rule fetched.')
                rule_dicts.append(res)
            return rule_dicts
        else:
            key = 'Rule:' + name
            res = conn.hgetall(key)
            if not res:
                raise ValueError('No rule fetched.')
            return res

    @staticmethod
    def _load_csv_rule(name=None):
        data = []
        with open('ProxyCrawl/rules.csv', 'rb') as f:
            for line in f:
                data.append(tuple(line.decode('utf-8').strip('\n').split(' ')))
        rule_dicts = []
        for d in data:
            rule_dicts.append({k: v for k, v in zip(labels, d)})
        if name:
            matches = [r for r in rule_dicts if r['name'] == name]
            if not matches:
                raise ValueError('No rule fetched.')
            elif len(matches) > 1:
                raise ValueError('Multiple rules fetched.')
            else:
                return matches[0]
        return rule_dicts

    @staticmethod
    def _decode_rule(rule, int_keys=('max_page',)):
        """
        Decode rule filed, transform str to int.

        Author: David
        """
        for key in int_keys:
            rule[key] = int(rule[key])
        return rule

    @classmethod
    def load(cls, name, src='redis'):
        """
        Load rule from source and instantiate a new rule item.

        Author: David
        """
        load_method = getattr(cls, '_load_{}_rule'.format(src))
        rule_dict = load_method(name)
        rule_dict = cls._decode_rule(rule_dict)
        return cls(rule_dict)

    @classmethod
    def loads(cls, src='redis'):
        """
        Load rules from source and instantiate all rule items.

        Author: David
        """
        load_method = getattr(cls, '_load_{}_rule'.format(src))
        rule_dicts = load_method()
        rule_dicts = [cls._decode_rule(rule) for rule in rule_dicts]
        insts = [cls(rule_dict) for rule_dict in rule_dicts]
        return insts

    @staticmethod
    def _save_redis_rule(rule_dict):
        key = 'Rule:' + rule_dict['name']
        pipe = conn.pipeline(False)
        pipe.hmset(key, rule_dict)
        pipe.sadd('Rules', rule_dict['name'])
        pipe.execute()

    @staticmethod
    def _save_csv_rule(rule_dict):
        raise NotImplementedError

    def save(self, dst='redis'):
        """
        Save rule to destination.

        Author: David
        """
        self.__check_vals()
        save_method = getattr(self, '_save_{}_rule'.format(dst))
        save_method(self.rule_dict)


if __name__ == '__main__':
    # rule = Rule.load('xici')
    rules = Rule.loads('csv')
    for r in rules:
        r.save()
    print(rules[0])
    # rule.save_rule()
