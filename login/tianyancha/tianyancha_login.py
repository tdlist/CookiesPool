# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 20:03
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : tianyancha_login.py
# @Software: PyCharm

import json
import random
import time
import hashlib
import requests
from urllib.parse import quote
from requests_spider_model import utils
from GeetestCracker.server import GeetestServer


class TianyanchaLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qixinbao'
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': 'https://www.tianyancha.com/vipintro/?jsid=SEM-360-PZ-SY-081001',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.proxies.update(utils.get_random_proxy('requests: https'))
        # 验证码识别服务器
        self.geetester = GeetestServer(version='2', address="127.0.0.1", port=8778)

    def _encrypt_pwd(self):
        """
        密码加密: md5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        return md5.hexdigest()

    def _init_cookies(self):
        """
        初始化
        :return:
        """
        self.session.get('https://www.tianyancha.com/vipintro/?jsid=SEM-360-PZ-SY-081001')

    def _init_captcha(self):
        """
        初始化验证码
        :return:
        """
        url = 'https://www.tianyancha.com/verify/geetest.xhtml'
        payload = {
            'uuid': int(time.time() * 1000)
        }
        return self.session.post(url, data=json.dumps(payload)).json()

    def _get_validate(self):
        """
        获取验证码认证参数: validate
        :return:
        """
        print('开始验证...')
        num = 0
        while num <= 5:
            captcha = self._init_captcha()
            if captcha['state'] == 'ok':
                print('验证码加载成功! ')
                params = {
                    'referer': 'https://www.tianyancha.com/vipintro/?jsid=SEM-360-PZ-SY-081001',
                    'gt': captcha['data']['gt'],
                    'challenge': captcha['data']['challenge']
                }
                result = self.geetester.crack(params)
                if result['code'] == 0:
                    print('验证通过! ')
                    return {
                        'challenge': result['challenge'],
                        'seccode': result['seccode'],
                        'validate': result['validate']
                    }
            num += 1
            print('第{}次验证失败! '.format(num))
            time.sleep(random.random())

    def login(self):
        login_api = 'https://www.tianyancha.com/cd/login.json'
        pwd = self._encrypt_pwd()
        payload = {
            'autoLogin': "true",
            'cdpassword': pwd,
            'loginway': "PL",
            'mobile': self.username
        }
        self._init_cookies()
        validate = self._get_validate()
        payload.update(validate)
        resp = self.session.post(login_api, data=json.dumps(payload)).json()
        if resp['state'] == 'ok':
            tyc_user_info = quote(json.dumps(resp['data']))
            auth_token = resp['data']['token']
            return {
                'auth_token': auth_token,
                'tyc-user-info': tyc_user_info
            }
        return resp['message']

    def run(self):
        result = self.login()
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        elif isinstance(result, str):
            if result == '请确认输入正确的手机号码和密码':
                return {
                    'status': '3',
                    'result': '密码错误'
                }
            else:
                return {
                    'status': '2',
                    'result': result
                }


if __name__ == '__main__':
    x = TianyanchaLogin('*******', '*********').run()
    print(x)
