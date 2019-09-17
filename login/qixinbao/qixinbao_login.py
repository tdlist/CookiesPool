# -*- coding: utf-8 -*-
# @Time    : 2019/8/21 10:10
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qixinbao_login.py
# @Software: PyCharm


import execjs
import json
import random
import time
import requests
from requests_spider_model import utils
from login.qixinbao.get_codes import get_codes
from GeetestCracker.server import GeetestServer


class QixinbaoLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qixinbao'
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # payload提交表单参数, 请求头中必须含有 Content-Type, 并且提交方法为 json.dumps(data)
            'Referer': 'https://www.qixin.com/auth/login?return_url=%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.proxies.update(utils.get_random_proxy('requests: https'))

        with open('../login/qixinbao/encrypt.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)
        self.codes = get_codes()

        # 验证码识别服务器
        self.geetester = GeetestServer(version='3', address="127.0.0.1", port=8778)

    def _encrypt_pwd(self):
        """
        加密密码
        :return:
        """
        return self.ctx.call('encrypt', self.password)

    def _get_header_js(self, url, data):
        """
        获取请求头中的加密参数, 加密对象为提交的表单
        :return:
        """
        return {self.ctx.call('header_key', self.codes, url): self.ctx.call('header_value', self.codes, url, data)}

    def _init_cookies(self):
        """
        请求首页初始化 Cookies
        :return:
        """
        self.session.get('https://www.qixin.com/')

    def _init_captcha(self):
        """
        验证码初始化
        :return:
        """
        url = 'https://www.qixin.com/api/captcha/register'
        data = {"type": 1}
        header_js = self._get_header_js(url, data)
        self.session.headers.update(header_js)
        result = self.session.post(url, data=json.dumps(data)).json()
        return result

    def _get_validate(self):
        """
        获取验证通过参数： validate
        :return:
        """
        num = 0
        print('开始验证...')
        while num <= 5:
            captcha = self._init_captcha()
            if captcha:
                print('验证码加载成功! ')
                result = self.geetester.crack(captcha)
                if result['code'] == 0:
                    print('验证通过! ')
                    return {
                        'data': {
                            'geetest_challenge': result['challenge'],
                            'geetest_seccode': result['seccode'],
                            'geetest_validate': result['validate']
                        },
                        'type': 1
                    }
                num += 1
                print('第{}次验证失败! '.format(num))
            time.sleep(random.random())

    def login(self):
        """
        模拟登录
        :return:
        """
        self._init_cookies()
        login_api = 'https://www.qixin.com/api/user/login'
        validate = self._get_validate()
        pwd = self._encrypt_pwd()
        data = {
            'acc': self.username,
            'captcha': validate,
            'keepLogin': 'true',
            'pass': pwd
        }
        header_js = self._get_header_js(login_api, data)
        self.session.headers.update(header_js)
        # proxies = utils.get_random_proxy('requests: https')
        resp = self.session.post(login_api, data=json.dumps(data))
        cookies = self.session.cookies.get_dict()
        if resp.json()['status'] == 1:
            return cookies
        return resp.json()['message']

    def run(self):
        result = self.login()
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        elif isinstance(result, str):
            if result == '用户名或密码错误':
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
    x = QixinbaoLogin('**********', '**********').run()
    print(x)
