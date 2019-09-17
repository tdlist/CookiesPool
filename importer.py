# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 22:42
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : importer.py
# @Software: PyCharm


import time
from db import RedisClient


def set_account(site, type, account, sep=' '):
    conn = RedisClient(type, site)
    username, value = account.split(sep)
    num = 0
    while num < 5:
        result = conn.set(username, value)
        if result:
            print('{}--{} 录入成功! '.format(username, value))
            return
        num += 1
        time.sleep(1)
    print('录入失败, 请检查 redis 内存是否已满, 尝试手动录入! ')


def scan(site):
    flag = input('录入账号请输入: accounts, 录入 Cookies 请输入: cookies\n')
    while True:
        account = input('请输入键值对(空格隔开), 输入 0 退出读入\n')
        if account == '0':
            break
        set_account(site, flag, account)


if __name__ == '__main__':
    scan('kuchuan')
