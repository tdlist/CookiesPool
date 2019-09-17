# -*- coding: utf-8 -*-
# @Time    : 2019/9/8 13:45
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : zhilian_login.py
# @Software: PyCharm

import requests
import json
import time
import random
from urllib.parse import urlencode
from GeetestCracker.server import GeetestServer


class ZhilianLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'zhilian'
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate, br',  该头部信息控制响应报文压缩, 请求时注释掉
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://passport.zhaopin.com/login?bkUrl=%2F%2Fi.zhaopin.com%2Fblank%3Fhttps%3A%2F%2Fwww.zhaopin.com%2F',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

        # 验证码识别服务器
        self.geetester = GeetestServer('3', address="***********", port=8778)

    def _init_cookies(self):
        """
        给 session 装载初始 cookie
        :return:
        """
        self.session.get(
            'https://passport.zhaopin.com/login?bkUrl=%2F%2Fi.zhaopin.com%2Fblank%3Fhttps%3A%2F%2Fwww.zhaopin.com%2F')

    def _init_captcha(self):
        url = 'https://passport.zhaopin.com/v4/geetest/init'
        params = {
            'scene': '10000020',
            'businessSystem': '1',
            'refer': '121126445',
            'clientType': 'n',
            'redirectURL': '//i.zhaopin.com/blank?https://www.zhaopin.com/',
            'appID': '9f69dd17cf834693b04e06dd5e9b5728',
            'callback': 'jsonp_rqvdxy8m94qcvrv'
        }
        resp = self.session.get(url, params=params)
        result = json.loads(resp.text.replace('jsonp_rqvdxy8m94qcvrv(', '').replace(')', ''))
        if result['code'] == 100000:
            validate_id = result['data']['validateId']
            captcha = result['data']['validateData']
            return validate_id, captcha

    def _get_validate(self):
        """
        获取验证通过参数： validate
        :return:
        """
        num = 0
        print('开始验证...')
        while num <= 5:
            validate_id, captcha = self._init_captcha()
            if captcha:
                print('验证码加载成功! ')
                result = self.geetester.crack(captcha)
                if result['code'] == 0:
                    print('验证通过! ')
                    return validate_id, {
                        'geetest_challenge': result['challenge'],
                        'geetest_seccode': result['seccode'],
                        'geetest_validate': result['validate'],
                        'type': '20'
                    }
                num += 1
                print('第{}次验证失败! '.format(num))
            time.sleep(random.random())

    def login(self):
        self._init_cookies()
        validate_id, validate_data = self._get_validate()

        login_api = 'https://passport.zhaopin.com/v4/account/login'
        params = {
            "validateId": validate_id,
            "validateData": validate_data,
            "passport": self.username,
            "password": self.password,
            "rememberMe": "true",
            "businessSystem": "1",
            "refer": "121126445",
            "clientType": "n",
            "redirectURL": "//i.zhaopin.com/blank?https://www.zhaopin.com/",
            "appID": "9f69dd17cf834693b04e06dd5e9b5728",
            "callback": "jsonp_z2eb02382z8jv2n"
        }
        url = login_api + '?' + urlencode(params)
        resp = self.session.get(url)
        result = json.loads(resp.text.replace('jsonp_z2eb02382z8jv2n(', '').replace(')', ''))
        if result['code'] == 100000:
            print('登录成功! ')
            cookies = self.session.cookies.get_dict()
            return cookies
        return result['message']

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
    x = ZhilianLogin('********', '*********').run()
    print(x)
