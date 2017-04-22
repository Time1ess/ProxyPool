#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 16:58
# Last modified: 2017-04-22 19:20
# Filename: maintainer.py
# Description:
import time
import sys

from concurrent.futures import ThreadPoolExecutor

import redis

from utils import test_proxy_alive, rookie_callback, available_callback


def maintain(conn):
    futures = set()
    key_cb = {
        'rookies_checking': rookie_callback(conn, futures),
        'availables_checking': available_callback(conn, futures)
    }
    print('Maintain started.')
    with ThreadPoolExecutor(400) as executor:
        while True:
            if conn.get('system_status') == 'finished':
                sys.stdout.flush()
                print('Detected system finish signal, canceling works')
                for future in futures:
                    future.cancel()
                break
            for idx, (check_key, callback) in enumerate(key_cb.items()):
                check_time = time.time()
                proxies = conn.zrangebyscore(check_key, 0, check_time-10,
                                             withscores=True)
                conn.zremrangebyscore(check_key, 0, check_time-10)
                for proxy, score in proxies:
                    key = 'proxy_info:'+proxy
                    protocol = conn.hget(key, 'protocol')
                    future = executor.submit(test_proxy_alive, proxy, protocol)
                    futures.add(future)
                    future.add_done_callback(callback)
            rookies_num = conn.zcard('rookies_checking')
            availables_num = conn.scard('available_proxies')
            # sys.stdout.flush()
            # sys.stdout.write(
            #     'Rookies: {:5d}, Availables: {:5d}, Futures: {:5d}\r'.format(
            #     rookies_num, availables_num, len(futures)))
            time.sleep(0.1)
    print('Maintain finished.')


if __name__ == '__main__':
    conn = redis.Redis(decode_responses=True)
    maintain(conn)
