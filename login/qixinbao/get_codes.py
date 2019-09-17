# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 21:02
# @Author  : xuzhihai0723
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
    url = 'https://cache.qixin.com/pcweb/common.a89140e8.js'
    resp = requests.get(url, headers=headers)
    codes = {}
    for i in range(20):
        text = 'e\.default={' + str(i) + ':"(.*?)"}'
        x = re.search(text, resp.text).group(1)
        codes.setdefault(i, x)
    return codes


if __name__ == '__main__':
    x = get_codes()
    print(x)
