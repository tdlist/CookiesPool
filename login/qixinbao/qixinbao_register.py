# -*- coding: utf-8 -*-
# @Time    : 2019/8/21 10:22
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qixinbao_register.py
# @Software: PyCharm

import execjs
import random
import requests
import json
import re
import time
from login.qixinbao.get_codes import get_codes
from GeetestCracker.server import GeetestServer
from login.yima_platform import get_phonenumber, get_vcode


class QixinbaoRegister:

    def __init__(self):
        self.site = 'qixinbao'
        self.itemid = 2542  # 企信宝在易码平台的编号
        self.token = '***************'

        self.session = requests.session()
        self.session.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://www.qixin.com/auth/regist',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        with open('../login/qixinbao/encrypt.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)
        self.codes = get_codes()

        # 验证码识别服务器
        self.geetester = GeetestServer('3', address="127.0.0.1", port=8778)

    @staticmethod
    def get_random_password():
        """
        生成随机8~12位密码
        :return:
        """
        text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!.'
        return ''.join(random.sample(text, random.randint(8, 12)))

    def _get_header_js(self, url, data):
        """
        获取请求头中的加密参数, 加密对象为提交的表单
        :return:
        """
        return {self.ctx.call('header_key', self.codes, url): self.ctx.call('header_value', self.codes, url, data)}

    def req_verify(self, phonenumber):
        """
        请求发送验证码
        :return:
        """
        req_api = 'https://www.qixin.com/api/user/send-regist-code'
        validate = self._get_validate()
        data = {
            'captcha': validate,
            'mobile': phonenumber,
            'type': 'MESSAGE'
        }
        header_js = self._get_header_js(req_api, data)
        self.session.headers.update(header_js)
        resp = self.session.post(req_api, data=json.dumps(data))
        if '验证码发送成功' in resp.text:
            return True
        return False

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

    def register(self, phonenumber):
        """
        模拟登录
        :return:
        """
        success = self.req_verify(phonenumber)
        if success:
            print('验证码接口请求成功, 请在60秒内接收! ')
            msg = get_vcode(self.token, self.itemid, phonenumber, 60)
            vcode = re.search(r'您的网页验证码(\d+)。', msg).group(1)
            print('成功接收验证码: {} '.format(vcode))

            # 模拟人为输入验证码延时
            time.sleep(random.uniform(1.5, 3.0))

            register_api = 'https://www.qixin.com/api/user/regist'
            password = self.get_random_password()
            print('生成随机密码: {}'.format(password))
            data = {
                'acc': phonenumber,
                'code': vcode,
                'name': '',
                'pass': password
            }
            header_js = self._get_header_js(register_api, data)
            self.session.headers.update(header_js)
            resp = self.session.post(register_api, data=json.dumps(data))
            cookies = resp.cookies.get_dict()
            if 'sid' in cookies.keys():
                print('注册成功! ')
                return {
                    'username': phonenumber,
                    'password': password
                }
            print(resp.text)
            error = '未知错误, 注册失败! '
            return error
        error = '验证码接口请求失败! '
        return error

    def run(self):
        phonenumber = get_phonenumber(self.token, self.itemid)
        print('成功获取手机号: {}'.format(phonenumber))
        result = self.register(phonenumber)
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        return {
            'status': '2',
            'result': result
        }


if __name__ == '__main__':
    x = QixinbaoRegister().run()
    print(x)
