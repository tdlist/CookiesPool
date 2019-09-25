# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 21:02
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : get_codes.py
# @Software: PyCharm


import re
import requests


def get_codes():
    """
    获取 js 加密 codes
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
    }
    # 这个 js url 过段时间会换
    resp = requests.get('https://www.qixin.com', headers=headers)
    url = 'https:' + re.search('script src="(.*?common.*?js)"', resp.text, re.S).group(1)
    # url = 'https://cache.qixin.com/pcweb/common.63c2bea8.js'
    response = requests.get(url, headers=headers)
    codes = {}
    for i in range(20):
        text = r'e\.default={' + str(i) + ':"(.*?)"}'
        x = re.search(text, response.text).group(1)
        codes.setdefault(i, x)
    return codes


if __name__ == '__main__':
    x = get_codes()
    print(x)
