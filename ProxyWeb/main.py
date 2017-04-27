#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-27 10:27
# Last modified: 2017-04-27 20:04
# Filename: main.py
# Description:
import json
import redis

from flask import Flask
from flask import render_template, request


app = Flask('ProxyWeb')
conn = redis.Redis(decode_responses=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rules')
def rules():
    pass

@app.route('/api/status')
def api_status():
    availables = conn.scard('available_proxies') or 0
    rookies = conn.scard('rookie_proxies') or 0
    losts = conn.scard('lost_proxies') or 0
    deads = conn.scard('dead_proxies') or 0
    futures = conn.get('futures') or 0
    data = {'availables': availables, 'rookies': rookies, 'losts': losts,
            'deads': deads, 'futures': futures}
    return json.dumps(data)


if __name__ == '__main__':
    app.run()
