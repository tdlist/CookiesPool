# -*- coding: utf-8 -*-
# @Time    : 2019/8/23 9:51
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qimai_login.py
# @Software: PyCharm

import requests
import time
from urllib.parse import quote, urlencode
from login.chaojiying import image_to_text
from login.qimai.generate_analysis import _get_analysis


class QimaiLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qimai'
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.qimai.cn',
            'Referer': 'https://www.qimai.cn/account/signin/r/%2Frank%2Findex%2Fbrand%2Ffree%2Fcountry%2Fcn%2Fgenre%2F5000%2Fdevice%2Fiphone',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # self.session.proxies.update(utils.get_random_proxy('requests: https'))

    def check_islogin(self, cookies):
        url = 'https://api.qimai.cn/account/userinfo'
        analysis = _get_analysis('', url)
        url += '?analysis={}'.format(quote(analysis))
        res = self.session.get(url, cookies=cookies).json()
        if res['code'] == 10000:
            print('登录成功！')
            print('Hello, {}! '.format(res['userinfo']['realname']))
            return True
        return False

    def _get_verifycode(self):
        timestamp = int(time.time() * 1000)
        captcha_url = f'https://api.qimai.cn/account/getVerifyCodeImage?{timestamp}'
        img_data = self.session.get(captcha_url).content
        print('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            print('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    def _init_cookies(self):
        """
        请求首页初始化 cookie
        :return:
        """
        self.session.get('https://www.qimai.cn/')

    def login(self):
        url = 'https://api.qimai.cn/account/signinForm'
        params = {
            'analysis': _get_analysis('', url)
        }
        login_api = url + '?' + urlencode(params)
        data = {
            'username': self.username,
            'password': self.password,
            'code': self._get_verifycode()
        }

        self._init_cookies()
        resp = self.session.post(login_api, data=data)
        cookies = self.session.cookies.get_dict()
        if self.check_islogin(cookies):
            return cookies
        elif resp.json()['msg'] == '用户名或密码错误':
            error = '用户名或密码错误'
            return error
        error = resp.json()['msg']
        return error

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
    x = QimaiLogin('**********', '**********').run()
    print(x)
