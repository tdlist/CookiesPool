# -*- coding: utf-8 -*-
# @Time    : 2019/8/21 10:32
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : yima_platform.py
# @Software: PyCharm


import requests
import random
import time
import re


def get_phonenumber(token, itemid):
    """
    易码平台获取手机号
    :return:
    """
    api = 'http://i.fxhyd.cn:8080/UserInterface.aspx?'
    params = {
        'action': 'getmobile',
        'token': token,
        'itemid': itemid,
        'isp': random.choice([1, 2, 3]),
        'timestamp': int(time.time())
    }
    resp = requests.get(api, params=params)
    if 'success' in resp.text:
        return resp.text.split('|')[1]
    else:
        raise Exception('获取手机号出错! ')


def get_vcode(token, itemid, phonenumber, second):
    """
    易码平台获取手机验证码
    :return:
    """
    api = 'http://i.fxhyd.cn:8080/UserInterface.aspx?'
    params = {
        'action': 'getsms',
        'token': token,
        'itemid': itemid,
        'mobile': phonenumber,
        'release': 1,
        'timestamp': int(time.time())
    }
    start_time = int(time.time())
    current_time = int(time.time())
    while current_time - start_time <= int(second):
        resp = requests.get(api, params=params)
        if 'success' in resp.text:
            return resp.text
        time.sleep(5)
        current_time = int(time.time())


if __name__ == '__main__':
    pass
