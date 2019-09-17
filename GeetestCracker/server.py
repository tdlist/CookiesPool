# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:23
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : server.py
# @Software: PyCharm


import json
import base64
import requests


class GeetestServer:
    def __init__(self, version, address="127.0.0.1", port=8778):
        # 极验版本: 极验 2 / 极验 3
        self.version = version
        self.url = f"http://{address}:{port}"

    def crack(self, params):
        if self.version == '2':
            return self.crack2(params)
        elif self.version == '3':
            return self.crack3(params)
        else:
            raise Exception('Wrong Version! ')

    def crack3(self, params):
        try:
            data = {
                'gt': params.get('gt', ''),
                'challenge': params.get('challenge', ''),
                'success': params.get('success', 1)
            }
            return requests.post(f"{self.url}/crack3", data=data).json()
        except:
            return {
                'code': -4,
                'msg': 'Wrong Server url! '
            }

    def crack2(self, params):
        try:
            data = {
                'referer': base64.b64encode(params.get('referer').encode()).decode(),
                'gt': params.get('gt', ''),
                'challenge': params.get('challenge', '')
            }
            return requests.post(f"{self.url}/crack2", data=data).json()
        except:
            return {
                'code': -4,
                'msg': 'Wrong Server url! '
            }

    def status(self):
        try:
            return requests.get(f"{self.url}/status").json()
        except:
            return {
                'code': -4,
                'msg': 'Wrong Server url! '
            }


if __name__ == '__main__':
    pass
