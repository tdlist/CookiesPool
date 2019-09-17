import requests
import redis
import pymongo
import pymysql
import functools
import traceback
import time
import re
import json
import random
import hashlib
from requests_spider_model.http import Request


def replace_br(html):
    """
    修正网页中带有换行功能的标签，以提取正确格式的文本
    :param html:
    :return:
    """
    html = re.sub(r'<[ ]*br[ /]*>', '\n', html)
    html = re.sub(r'<[ ]*/[ ]*div[ ]*>', '\n</div>', html)
    html = re.sub(r'<[ ]*/[ ]*p[ ]*>', '\n</p>', html)
    return html


def loopUnlessSeccessOrMaxTry(max_times, sleep_time=1.5):
    """
    重试修饰器，被该修饰器修饰的函数，出错后会循环执行，
    直到执行成功或者到达最大执行次数
    :param max_times: 最大执行次数
    :param sleep_time:出错后的暂停时间
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            cnt = 1
            while True:
                try:
                    result = func(self, *args, **kwargs)
                    self.error_cnt = 0
                    return result
                except Exception as e:
                    if self.log_error:
                        self.log('在执行函数{}时出错: {}'.format(func.__name__, e))
                        traceback.print_exc()
                    self.error_cnt += 1
                    time.sleep(sleep_time)
                if cnt >= max_times:
                    if self.log_error:
                        self.log('出错次数过多，该函数{}已跳过执行'.format(func.__name__))
                    self.counter.add('ingore')
                    if len(args) == 1 and isinstance(args[0], Request):
                        request = args[0]
                        request.dont_filter = True
                        request.property -= 10
                        self.add_task(request)
                        self.log('重新加入到队列中！')
                    break
                cnt += 1

        return wrapper

    return decorator


def get_random_proxy(flag):
    while True:
        try:
            r = requests.get('http://***********/random/')  # 代理池地址
            if flag == 'pyppeteer':
                username = r.text.split('@')[0].split(':')[0]
                password = r.text.split('@')[0].split(':')[1]
                proxy = r.content.decode('utf-8').split('@')[1]
                return username, password, proxy
            elif flag == 'selenium':
                username = r.text.split('@')[0].split(':')[0]
                password = r.text.split('@')[0].split(':')[1]
                host = r.content.decode('utf-8').split('@')[1].split(':')[0]
                port = r.content.decode('utf-8').split('@')[1].split(':')[1]
                return username, password, host, port
            elif flag == 'requests: https':
                proxy = r.content.decode('utf-8')
                proxies = {
                    'https': 'https://{}'.format(proxy)
                }
                return proxies
            elif flag == 'requests: http':
                proxy = r.content.decode('utf-8')
                proxies = {
                    'http': 'http://{}'.format(proxy)
                }
                return proxies
            elif flag == 'scrapy: https':
                proxy = r.content.decode('utf-8')
                proxies = 'https://{}'.format(proxy)
                return proxies
            elif flag == 'scrapy: http':
                proxy = r.content.decode('utf-8')
                proxies = 'http://{}'.format(proxy)
                return proxies
        except Exception as e:
            print('获取代理失败: ', e.args)


def get_random_cookies(site):
    while True:
        try:
            r = requests.get('http://************/{}/random'.format(site))  # cookie 池地址
            cookies = json.loads(r.text)
            return cookies
        except Exception as e:
            print('获取 Cookies 失败: ', e.args)


def md5_encrypt(encrypt_str):
    md5 = hashlib.md5()
    md5.update(encrypt_str.encode())
    return md5.hexdigest()


def get_online_mongo_client():
    """
    连接线上 mongo 数据库
    :param db:
    :return:
    """
    client = pymongo.MongoClient(
        host='ONLINE_MONGO_HOST',
        port='ONLINE_MONGO_PORT'
    )
    # 先用admin数据库完成账号认证
    db = client.admin
    db.authenticate(name='MONGO_USER', password='MONGO_PASSWORD', mechanism='SCRAM-SHA-1')
    return client


def get_local_conn(db):
    """
    连接线上数据库
    :param db:
    :return:
    """
    conn = pymysql.connect(
        host='LOCAL_DB_HOST',
        user='LOCAL_DB_USER',
        password='LOCAL_DB_PASSWORD',
        port='LOCAL_DB_PORT',
        db=db,
    )
    return conn


def get_online_conn(db):
    """
    连接线上数据库
    :param db:
    :return:
    """
    conn = pymysql.connect(
        host='ONLINE_DB_HOST',
        user='ONLINE_DB_USER',
        password='ONLINE_DB_PASSWORD',
        port='ONLINE_DB_PORT',
        db=db,
    )
    return conn


def query_sql(sql, conn=None, db='xxx', online=True):
    """
    执行一条查询语句
    :param sql:
    :param conn:
    :param db:
    :return: 结果的字典列表
    """
    if not conn:
        if online:
            conn = get_online_conn(db)
        else:
            conn = get_local_conn(db)
        close_db = True
    else:
        close_db = False
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    if close_db:
        conn.close()
    return res


def insert_db(sql, params=None, conn=None, db='lz_datastore', use_local=False):
    """
    执行一条查询语句
    :param sql:
    :param conn:
    :param db:
    :return: 影响的行数
    """
    if not conn:
        if use_local:
            conn = get_local_conn(db)
        else:
            conn = get_online_conn(db)
        close_db = True
    else:
        close_db = False
    cursor = conn.cursor()
    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        traceback.print_exc()
    last_id = cursor.lastrowid
    cursor.close()
    if close_db:
        conn.close()
    return last_id


def execute_sql(sql, params=None, conn=None, db='lz_datastore', use_local=False):
    """
    执行一条查询语句
    :param sql:
    :param params:
    :param conn:
    :param db:
    :return: 影响的行数
    """
    if not conn:
        if use_local:
            conn = get_local_conn(db)
        else:
            conn = get_online_conn(db)
        close_db = True
    else:
        close_db = False
    cursor = conn.cursor()
    try:
        if params is None:
            res = cursor.execute(sql)
        else:
            res = cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        res = None
    cursor.close()
    if close_db:
        conn.close()
    return res


def executemany_sql(sql, params, conn=None, db='lz_datastore', use_local=False):
    """
    执行多条查询语句
    :param sql:
    :param conn:
    :param db:
    :return: 影响的行数
    """
    if not conn:
        if use_local:
            conn = get_local_conn(db)
        else:
            conn = get_online_conn(db)
        close_db = True
    else:
        close_db = False
    cursor = conn.cursor()
    try:
        res = cursor.executemany(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        res = None
        traceback.print_exc()
    cursor.close()
    if close_db:
        conn.close()
    return res


def get_dict_cursor(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return cursor


if __name__ == '__main__':
    x = get_random_cookies('qimai')
    print(x)
