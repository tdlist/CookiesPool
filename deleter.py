# -*- coding: utf-8 -*-
# @Time    : 2019/8/25 11:40
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : deleter.py
# @Software: PyCharm

import time
from db import RedisClient


def delete_account(site, type, username):
    conn = RedisClient(type, site)
    num = 0
    while num < 5:
        result = conn.delete(username)
        if result:
            print('删除 {} 成功! '.format(username))
            break
        num += 1
        time.sleep(1)
    print('删除失败, 请手动删除! ')


def scan(site):
    flag = input('删除账号请输入: accounts, 删除 Cookies 请输入: cookies')
    print('请输入键值对(空格隔开), 输入 0 退出读入')
    while True:
        username = input()
        if username == '0':
            break
        delete_account(site, flag, username)


if __name__ == '__main__':
    scan('qimai')