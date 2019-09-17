# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 10:39
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : kuchuan_login.py
# @Software: PyCharm

import requests


class KuchuanLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'kuchuan'
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://user.kuchuan.com',
            'Referer': 'https://user.kuchuan.com/user/login?redirect_uri=http%3A%2F%2Fwww.kuchuan.com%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def _init_cookies(self):
        """
        给 session 装载初始 cookie
        :return:
        """
        self.session.get('https://www.kuchuan.com/')

    def _verify_account(self):
        """
        验证账号是否存在
        :return:
        """
        url = 'https://user.kuchuan.com/api/verifyAccount'
        data = {
            'account': self.username
        }
        self.session.post(url, data=data)

    def login(self):
        login_api = 'https://user.kuchuan.com/api/login'

        data = {
            'account': self.username,
            'passwd': self.password,
            'redirect': 'https://www.kuchuan.com/',
            'isRemember': '1',
            'source': ''
        }
        self._init_cookies()
        # self._verify_account()
        resp = self.session.post(login_api, data=data).json()
        if resp['status'] == 200:
            if resp['msg'] == '账号密码正确':
                print('登录成功! ')
                cookies = self.session.cookies.get_dict()
                return cookies
            return resp['msg']
        return '未知错误'

    def run(self):
        result = self.login()
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        elif isinstance(result, str):
            if result == '账号或密码错误':
                return {
                    'status': '3',
                    'result': '密码错误'
                }
            elif result == '此账号还没有注册':
                return {
                    'status': '3',
                    'result': '账号未注册'
                }
            else:
                return {
                    'status': '2',
                    'result': result
                }


if __name__ == '__main__':
    x = KuchuanLogin('********', '**********').run()
    print(x)
