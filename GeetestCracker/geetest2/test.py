# -*- coding: utf-8 -*-
# @Time    : 2019/9/8 15:15
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : test.py
# @Software: PyCharm

import execjs
import json
from pprint import pprint

with open('geetest.js', 'rb') as f:
    js = f.read().decode()

ctx = execjs.compile(js)

referer = 'https://www.tianyancha.com/vipintro/?jsid=SEM-360-PZ-SY-081001'
data = {
    'gt': 'f5c10f395211c77e386566112c6abf21',
    'challenge': 'c7f3e7c4a1b535bb89317b343c2426c1ar',
    'c': [12, 58, 98, 36, 43, 95, 62, 15, 12],
    's': '7445632e'
}
trace = [[23, 24, 0], [35, 2, 388], [16, 0, 368], [0, 0, 343]]
distance = 51

x = ctx.call('get_slide_w', referer, data, trace, distance)
pprint(json.loads(x))
