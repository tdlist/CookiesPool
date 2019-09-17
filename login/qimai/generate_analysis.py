# -*- coding: utf-8 -*-
# @Time    : 2019/8/23 10:45
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : generate_analysis.py
# @Software: PyCharm


import execjs
import time
import random
import requests


def _get_synct():
    """
    请求首页获取 synct： 这个参数的意思是首次访问时间戳
    :return:
    """
    while True:
        resp = requests.get('https://www.qimai.cn/rank')
        cookies = resp.cookies.get_dict()
        synct = cookies.get('synct')
        if synct:
            return cookies.get('synct')
        time.sleep(random.random())


def _get_analysis(p_str, url):
    synct = _get_synct()
    with open('../login/qimai/analysis.js', 'rb') as f:
        js = f.read().decode()
    ctx = execjs.compile(js)
    return ctx.call('getAnalysis', p_str, url, synct)


if __name__ == '__main__':
    x = _get_analysis('46', 'https://api.qimai.cn/andapp/baseinfo')
    print(x)
