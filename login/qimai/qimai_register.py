# -*- coding: utf-8 -*-
# @Time    : 2019/9/8 12:42
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qimai_register.py
# @Software: PyCharm

import re
import requests
import time
import random
from requests_spider_model import utils
from GeetestCracker.server import GeetestServer
from login.qimai.generate_analysis import _get_analysis
from login.yima_platform import get_phonenumber, get_vcode


class QimaiRegister:

    def __init__(self):
        self.site = 'qimai'
        self.itemid = 21300  # 七麦在易码平台的编号
        self.token = '***************'

        self.session = requests.session()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.qimai.cn',
            'Referer': 'https://www.qimai.cn/account/signin/r/%2Frank%2Findex%2Fbrand%2Ffree%2Fcountry%2Fcn%2Fgenre%2F5000%2Fdevice%2Fiphone',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 使用代理注册, 单IP一天注册有上限, 大概是10多个, 具体多少忘了
        self.session.proxies.update(utils.get_random_proxy('requests: https'))

        # 验证码识别服务器
        self.geetester = GeetestServer('3', address="********", port=8778)

    @staticmethod
    def get_random_password():
        """
        生成随机8~12位密码
        :return:
        """
        text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!.'
        return ''.join(random.sample(text, random.randint(8, 12)))

    @staticmethod
    def process_params(params):
        """
        对请求参数值进行排序, 构造加密字符串
        :param params:
        :return:
        """
        xparams = []
        for value in params.values():
            if not isinstance(value, str):
                value = str(value)
            xparams.append(value)
        p_str = ''
        # 对参数列表进行排序
        xparams.sort()
        for p in xparams:
            p_str += p
        return p_str

    def _init_captcha(self):
        url = 'https://api.qimai.cn/error/geetestInfo'
        params = {
            'rand': 83
        }
        p_str = self.process_params(params)
        analysis = _get_analysis(p_str, url)
        params.update({
            'analysis': analysis
        })
        result = self.session.get(url, params=params).json()
        if result['success']:
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
                        'validate[geetest_challenge]': result['challenge'],
                        'validate[geetest_seccode]': result['seccode'],
                        'validate[geetest_validate]': result['validate']
                    }
                num += 1
                print('第{}次验证失败! '.format(num))
            time.sleep(random.random())

    def check_phone(self, phonenumber):
        """
        检查手机号是否已注册
        :return:
        """
        url = 'https://api.qimai.cn/account/userInfoCheck'
        analysis = _get_analysis('', url)
        params = {
            'analysis': analysis
        }
        data = {
            'field': 'phone',
            'value': phonenumber
        }
        result = self.session.post(url, params=params, data=data).json()
        if result['code'] == 10000:
            return True
        elif result['code'] == 92002:
            print(result['msg'])
        return False

    def req_verify(self, phonenumber):
        url = 'https://api.qimai.cn/account/sendPhoneCodeBySignup'
        analysis = _get_analysis('', url)
        params = {
            'analysis': analysis
        }
        validate = self._get_validate()
        validate.update({
            'phone': phonenumber
        })
        result = self.session.post(url, params=params, data=validate).json()
        if result['code'] == 10000:
            return True
        return False

    def register(self, phonenumber):
        is_phone_useful = self.check_phone(phonenumber)
        if not is_phone_useful:
            errors = '手机号已被注册! '
            return errors
        success = self.req_verify(phonenumber)
        if not success:
            errors = '验证码接口请求失败! '
            return errors
        print('验证码接口请求成功, 请在60秒内接收! ')
        msg = get_vcode(self.token, self.itemid, phonenumber, 60)
        vcode = re.search(r'您的验证码为(\d+)，', msg).group(1)
        print('成功接收验证码: {} '.format(vcode))

        # 模拟人为输入验证码延时
        time.sleep(random.uniform(1.5, 3.0))

        register_api = 'https://api.qimai.cn/account/signupForm'
        analysis = _get_analysis('', register_api)
        params = {
            'analysis': analysis
        }
        password = self.get_random_password()
        print('生成随机密码: {}'.format(password))
        data = {
            'username': '',
            'password': password,
            'repassword': password,
            'email': '',
            'phone': phonenumber,
            'phoneCode': vcode,
            'agreement[0]': 'false'
        }
        result = self.session.post(register_api, params=params, data=data).json()
        if result['code'] == 10000:
            print('注册成功! ')
            return {
                'username': phonenumber,
                'password': password
            }
        error = result['msg']
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
    x = QimaiRegister().run()
    print(x)


