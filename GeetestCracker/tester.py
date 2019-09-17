# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:24
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : tester.py
# @Software: PyCharm


import requests
import time
import execjs
import json
import random
from login.qixinbao import get_codes
from GeetestCracker.server import GeetestServer


class Tester:

    def __init__(self, site, version, max_num=5, address="39.107.69.94"):
        # 待检查站点
        self.site = site
        # 极验版本: 极验 2 / 极验 3
        self.version = version
        # 最大重试次数
        self.max_num = max_num
        # 服务器地址
        self.address = address
        self.geetester = GeetestServer(self.version, address=self.address, port=8778)

    def run(self):
        num = 0
        print('Start Checking: {}...'.format(self.site))
        while num <= self.max_num:
            captcha = self.get_captcha()
            if captcha:
                print('Captcha load success! ')
                result = self.geetester.crack(captcha)
                if result['code'] == 0:
                    print('Verify Success! ')
                    print("=" * 100)
                    print(f"Captcha: {captcha}")
                    print("=" * 100)
                    print(f"Result: {result}")
                    print("=" * 100)
                    return True
                elif result['code'] == -4:
                    print(result['msg'])
                    return False
                num += 1
                print('The {} verification failed! '.format(num))
            else:
                print('Captcha load failed! ')
            time.sleep(random.random())

    def get_captcha(self):
        """
        初始化验证码
        :return:
        """
        raise NotImplementedError


class BilibiliTester(Tester):

    def __init__(self):
        self.site = 'bilibili'
        Tester.__init__(self, self.site, '3')

    def get_captcha(self):
        response = requests.get("https://passport.bilibili.com/web/captcha/combine?plat=5").json()
        if response.get('code') == 0 and response.get('data', {}).get('type') == 1:
            return response.get('data', {}).get('result')
        else:
            return None


class QixinbaoTester(Tester):

    def __init__(self):
        self.site = 'qixinbao'
        Tester.__init__(self, self.site, '3')

    @staticmethod
    def _get_header_js(codes, url, data):
        """
        获取请求头中的加密参数, 加密对象为提交的表单
        :return:
        """
        with open('../login/qixinbao/encrypt.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        return {ctx.call('header_key', codes, url): ctx.call('header_value', codes, url, data)}

    def get_captcha(self):
        url = 'https://www.qixin.com/api/captcha/register'
        data = {"type": 1}
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            # payload提交表单参数, 请求头中必须含有 Content-Type, 并且提交方法为 json.dumps(data)
            'Referer': 'https://www.qixin.com/auth/login?return_url=%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        codes = get_codes.get_codes()
        header_js = self._get_header_js(codes, url, data)
        headers.update(header_js)
        return requests.post(url, data=json.dumps(data), headers=headers).json()


class TianyanchaTester(Tester):

    def __init__(self):
        self.site = 'tianyancha'
        Tester.__init__(self, self.site, '2')

    def get_captcha(self):
        url = 'https://www.tianyancha.com/verify/geetest.xhtml'
        payload = {
            'uuid': int(time.time() * 1000)
        }
        referer = 'https://www.tianyancha.com/vipintro/?jsid=SEM-360-PZ-SY-081001'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        result = requests.post(url, data=json.dumps(payload), headers=headers).json()
        if result['state'] == 'ok':
            return {
                'referer': referer,
                'gt': result['data']['gt'],
                'challenge': result['data']['challenge']
            }
        else:
            return None


if __name__ == "__main__":
    # TianyanchaTester().run()
    QixinbaoTester().run()
