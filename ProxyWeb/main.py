#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-27 10:27
# Last modified: 2017-04-30 14:29
# Filename: main.py
# Description:
import json
import time

import redis

from flask import Flask
from flask import render_template, request


app = Flask('ProxyWeb')
conn = redis.Redis(decode_responses=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rules')
def rules_table():
    rule_keys = conn.smembers('Rules')
    rules = []
    for suffix in rule_keys:
        key = 'Rule:' + suffix
        rule = conn.hgetall(key)
        rules.append(rule)
    context = {}
    context['rules'] = rules
    return render_template('rules.html', **context)

@app.route('/rules/')
@app.route('/rules/<rule_name>')
def rule_detail(rule_name=None):
    if rule_name is None:
        modal_type = 'add_submit'
        rule = {}
    else:
        key = 'Rule:' + rule_name
        rule = conn.hgetall(key)
        modal_type = 'update_submit'
    return render_template('rule_modal.html', **rule, modal_type=modal_type)

@app.route('/api/status')
def api_status():
    availables = conn.scard('available_proxies') or 0
    rookies = conn.scard('rookie_proxies') or 0
    losts = conn.scard('lost_proxies') or 0
    deads = conn.scard('dead_proxies') or 0
    currents = conn.get('currents') or 0
    data = {'availables': availables, 'rookies': rookies, 'losts': losts,
            'deads': deads, 'currents': currents}
    return json.dumps(data)

@app.route('/api/crawlers/<method>/<rule_name>')
def api_crawlers(method, rule_name):
    crawler_methods = ['start', 'stop', 'reload', 'pause']
    if method in crawler_methods:
        cmd = method + '|' + rule_name
        conn.rpush('Jobs', cmd)
        return '0'
    else:
        return '-1'


@app.route('/api/rules/delete/<rule_name>')
def api_rules_delete(rule_name):
    # status should be stopped when deleting
    key = 'Rule:' + rule_name
    pipe = conn.pipeline()
    end = time.time() + 5
    while time.time() < end:
        try:
            pipe.watch(key)
            pipe.watch('Jobs')
            status = pipe.hget(key, 'status')
            if status != 'stopped':
                pipe.unwatch()
                return 'Not finished'
            pipe.multi()
            pipe.lrem('Jobs', 'start|'+rule_name)
            pipe.srem('Rules', rule_name)
            pipe.delete(key)
            pipe.execute()
            return 'Succeed'
        except redis.exceptions.WatchError:
            pass
    return 'Timeout'


@app.route('/api/rules/<method>', methods=['POST'])
def api_rules(method):
    if not all(request.form.values()):
        return 'fail'
    rule_dict = dict(request.form)
    for key in rule_dict:
        rule_dict[key] = rule_dict[key][0]
    rule_name = rule_dict['name']
    key = 'Rule:' + rule_name
    if method == 'add_submit':
        rule_dict['status'] = 'stopped'
        conn.hmset(key, rule_dict)
        conn.sadd('Rules', rule_name)
        cmd = 'start|' + rule_name
    elif method == 'update_submit':
        conn.hmset(key, rule_dict)
        cmd = 'reload|' + rule_name
    conn.rpush('Jobs', cmd)
    return '0'


if __name__ == '__main__':
    app.run()
