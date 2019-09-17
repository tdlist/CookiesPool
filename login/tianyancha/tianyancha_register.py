# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 20:37
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : tianyancha_register.py
# @Software: PyCharm

import hashlib
import random
import requests
import json
import re
import time
from requests_spider_model import utils
from GeetestCracker.server import GeetestServer
from login.yima_platform import get_phonenumber, get_vcode


class TianyanchaRegister:

    def __init__(self):
        self.site = 'tianyancha'
        self.itemid = 7344  # 天眼查在易码平台的编号
        self.token = '**********'  # 易码平台api 账号认证 token

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

    @staticmethod
    def get_random_password():
        """
        生成随机8~12位密码
        :return:
        """
        text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!.'
        return ''.join(random.sample(text, random.randint(8, 12)))

    @staticmethod
    def _encrypt_pwd(password):
        """
        密码加密: md5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(password.encode())
        return md5.hexdigest()

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

    def req_verify(self, phonenumber):
        """
        请求发送验证码
        :return:
        """
        req_api = 'https://www.tianyancha.com/verify/sms.json?p={}'.format(phonenumber)
        validate = self._get_validate()
        data = {
            "funtype": 0,
            "phone": phonenumber,
            "type": "SMS",
        }
        data.update(validate)
        resp = self.session.post(req_api, data=json.dumps(data)).json()
        if resp['state'] == 'ok':
            return True
        return False

    def register(self, phonenumber):
        """
        模拟登录
        :return:
        """
        success = self.req_verify(phonenumber)
        if success:
            print('验证码接口请求成功, 请在60秒内接收! ')
            msg = get_vcode(self.token, self.itemid, phonenumber, 60)
            vcode = re.search(r'你的验证码是：(\d+)，', msg).group(1)
            print('成功接收验证码: {} '.format(vcode))

            # 模拟人为输入验证码延时
            time.sleep(random.uniform(1.5, 3.0))

            register_api = 'https://www.tianyancha.com/cd/reg.json'
            password = self.get_random_password()
            print('生成随机密码: {}'.format(password))
            pwd = self._encrypt_pwd(password)
            data = {
                "cdpassword": pwd,
                "mobile": phonenumber,
                "smsCode": vcode,
            }
            validate = self._get_validate()
            data.update(validate)
            resp = self.session.post(register_api, data=json.dumps(data))
            if resp.json()['state'] == 'ok':
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
    x = TianyanchaRegister().run()
    print(x)
