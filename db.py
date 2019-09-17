# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 21:31
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : db.py
# @Software: PyCharm

import random
import json
from redis import StrictRedis, ConnectionPool
from config import *


class RedisClient(object):
    def __init__(self, type, site):
        """
        初始化 Redis 数据库
        :param type: 存储类型
        :param site: redis 连接
        """
        self.db = StrictRedis(connection_pool=ConnectionPool.from_url(REDIS_URL))
        self.type = type
        self.site = site

    def name(self):
        """
        获取Hash的名称
        :return: Hash名称
        """
        return "{type}:{site}".format(type=self.type, site=self.site)

    def set(self, username, value):
        """
        设置键值对
        :param username: 用户名
        :param value: 密码或 Cookies
        :return:
        """
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        """
        根据键名获取键值
        :param username: 用户名
        :return:
        """
        return self.db.hget(self.name(), username)

    def delete(self, username):
        """
        根据键名删除键值对
        :param username: 用户名
        :return: 删除结果
        """
        return self.db.hdel(self.name(), username)

    def count(self):
        """
        获取数目
        :return: 数目
        """
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值，用于随机 Cookies 获取
        :return: 随机 Cookies
        """
        return random.choice(self.db.hvals(self.name()))

    def usernames(self):
        """
        获取所有账户信息
        :return: 所有用户名
        """
        return self.db.hkeys(self.name())

    def all(self):
        """
        获取所有键值对
        :return: 用户名和密码或 Cookies 的映射表
        """
        return self.db.hgetall(self.name())


if __name__ == '__main__':
    x = [json.loads(value.decode('utf-8')) for value in RedisClient('cookies', 'qimai').all().values()]
    print(x)
