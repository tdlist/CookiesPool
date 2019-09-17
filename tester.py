# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 18:09
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : tester.py
# @Software: PyCharm

import json
import requests
import re
import time
import demjson
import traceback
import base64
from PIL import Image
from urllib.parse import unquote
from bs4 import BeautifulSoup
from urllib.parse import quote
from requests_spider_model import utils
from requests.exceptions import ConnectionError
from db import *
from login.qimai.generate_analysis import _get_analysis, _get_synct
from deleter import delete_account
from login.chaojiying import image_to_text


class ValidTester:

    def __init__(self, site='default'):
        self.site = site
        self.cookies_db = RedisClient('cookies', self.site)
        self.accounts_db = RedisClient('accounts', self.site)

    def test(self, username, cookies):
        raise NotImplementedError

    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.items():
            username = username.decode('utf-8')
            self.test(username, cookies)
            sleep_time = random.randint(60, 180)
            # print('休息{}秒...'.format(sleep_time))
            time.sleep(sleep_time)


class QichachaValidTester(ValidTester):

    def __init__(self, site='qichacha'):
        ValidTester.__init__(self, site)

    def test(self, username, cookies):
        print('正在测试 Cookies : {}'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies 不合法: ', username)
            if self.cookies_db.delete(username):
                print('删除 Cookies: ', username)
            else:
                print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                delete_account(self.site, 'cookies', username)
        try:
            test_url = TEST_URL_MAP[self.site]
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Connection': 'keep-alive', 'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': 'https://www.qixin.com/search?key=%E4%B8%8A%E6%B5%B7%E4%BA%91%E8%81%94'
            }
            # proxies = utils.get_random_proxy('requests: https')
            response = requests.get(test_url, cookies=cookies, headers=headers, allow_redirects=False)
            if 'zhugeIdentify' in response.text:
                print('Cookies 有效!')
                userinfo = demjson.decode(re.search('var zhugeIdentify = (.*?);', response.text, re.S).group(1))
                nickname = userinfo.get('name')
                print('Hello, {}! '.format(nickname))
            else:
                print('Cookies 已过期: {}'.format(username))
                if self.cookies_db.delete(username):
                    print('删除 Cookies: ', username)
                else:
                    print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                    delete_account(self.site, 'cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


class QixinbaoValidTester(ValidTester):

    def __init__(self, site='qixinbao'):
        ValidTester.__init__(self, site)

    def test(self, username, cookies):
        print('正在测试 Cookies : {}'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies 不合法: ', username)
            if self.cookies_db.delete(username):
                print('删除 Cookies: ', username)
            else:
                print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                delete_account(self.site, 'cookies', username)
        try:
            test_url = TEST_URL_MAP[self.site]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Referer': 'https://www.qixin.com/',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
            }
            response = requests.get(test_url, cookies=cookies, headers=headers, allow_redirects=False)
            if '会员中心' in response.text:
                print('Cookies 有效!')
                bsobj = BeautifulSoup(response.text, 'lxml')
                nickname = bsobj.find('div', {'class': 'body'}).find('h5').get_text()
                print('Hello, {}! '.format(nickname))
            else:
                print('Cookies 已过期: {}'.format(username))
                if self.cookies_db.delete(username):
                    print('删除 Cookies: ', username)
                else:
                    print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                    delete_account(self.site, 'cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


class QimaiValidTester(ValidTester):

    def __init__(self, site='qimai'):
        ValidTester.__init__(self, site)

    def test(self, username, cookies):
        print('正在测试 Cookies : {}'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies 不合法: ', username)
            if self.cookies_db.delete(username):
                print('删除 Cookies: ', username)
            else:
                print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                delete_account(self.site, 'cookies', username)
        try:
            test_url = TEST_URL_MAP[self.site]
            session = requests.session()
            session.headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.qimai.cn',
                'Referer': 'https://www.qimai.cn/account/signin/r/%2Frank%2Findex%2Fbrand%2Ffree%2Fcountry%2Fcn%2Fgenre%2F5000%2Fdevice%2Fiphone',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
            }
            analysis = _get_analysis('', test_url)
            test_url += '?analysis={}'.format(quote(analysis))
            resp = session.get(test_url, cookies=cookies).json()
            if resp['code'] == 10000:
                nickname = resp['userinfo']['realname']
                if nickname and nickname != '':
                    print('Cookies 有效!')
                    print('Hello, {}! '.format(nickname))
                else:
                    print('Cookies 已过期: {}'.format(username))
                    if self.cookies_db.delete(username):
                        print('删除 Cookies: ', username)
                    else:
                        print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                        delete_account(self.site, 'cookies', username)
            else:
                print('Cookies 已过期: {}'.format(username))
                if self.cookies_db.delete(username):
                    print('删除 Cookies: ', username)
                else:
                    print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                    delete_account(self.site, 'cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


class KuchuanValidTester(ValidTester):

    def __init__(self, site='kuchuan'):
        ValidTester.__init__(self, site)

    def test(self, username, cookies):
        print('正在测试 Cookies : {}'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies 不合法: ', username)
            if self.cookies_db.delete(username):
                print('删除 Cookies: ', username)
            else:
                print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                delete_account(self.site, 'cookies', username)
        try:
            test_url = TEST_URL_MAP[self.site]
            session = requests.session()
            session.headers = {
                'Accept': '*/*',
                'Referer': 'https://www.kuchuan.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            test_url += '?t={}'.format(int(time.time() * 1000))
            resp = session.get(test_url, cookies=cookies).json()
            if resp['status'] == 200:
                nickname = resp['data']['account']
                print('Cookies 有效!')
                print('Hello, {}! '.format(nickname))
            else:
                print('Cookies 已过期: {}'.format(username))
                if self.cookies_db.delete(username):
                    print('删除 Cookies: ', username)
                else:
                    print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                    delete_account(self.site, 'cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


class TianyanchaValidTester(ValidTester):

    def __init__(self, site='tianyancha'):
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
        ValidTester.__init__(self, site)

    def _init_captcha(self, cookies):
        """
        初始化账号异常验证码
        :return:
        """
        time1 = int(time.time() * 1000)
        time2 = time1 - random.randint(50, 150)
        url = 'https://antirobot.tianyancha.com/captcha/getCaptcha.json?t={}&_={}'.format(time1, time2)
        resp = self.session.get(url, cookies=cookies).json()
        if resp['state'] == 'ok':
            return {
                'bg_img': resp['data']['bgImage'],
                'target_img': resp['data']['targetImage'],
                'captcha_id': resp['data']['id'],
                'timestamp': time2
            }
        else:
            return None

    def account_verify(self, cookies, init_data):
        """
        账号异常时进行验证
        :return:
        """
        bg_data = base64.b64decode(init_data['bg_img'])
        target_data = base64.b64decode(init_data['target_img'])
        with open('./Captcha/bg.jpg', 'wb') as f:
            f.write(bg_data)
        with open('./Captcha/target.jpg', 'wb') as f:
            f.write(target_data)

        arr = ['./Captcha/bg.jpg', './Captcha/target.jpg']
        toImage = Image.new('RGBA', (320, 130))
        for i in range(2):
            fromImge = Image.open(arr[i])
            loc = ((int(i / 2) * 100), (i % 2) * 100)
            toImage.paste(fromImge, loc)

        toImage.save('./Captcha/merged.png')
        with open('./Captcha/merged.png', 'rb') as f:
            img = f.read()
        print('使用超级鹰识别验证码...')
        ok, result = image_to_text(img, img_kind=9004)
        if ok:
            print('验证码识别成功! ')
            clickLocs = json.dumps([{'%22x%22': int(item.split(',')[0]), '%22y%22': int(item.split(',')[1])} for item in
                                    result.split('|')])
            xurl = 'https://antirobot.tianyancha.com/captcha/checkCaptcha.json?captchaId={}&clickLocs={}&t={}&_={}'.format(
                init_data['captcha_id'], clickLocs.replace('"', ''), int(time.time() * 1000), init_data['timestamp'] + 1).replace(' ', '')
            resp = self.session.get(xurl, cookies=cookies).json()
            if resp['state'] == 'ok':
                return True
            return False
        print('验证码识别失败! ')
        return False

    def test(self, username, cookies):
        print('正在测试 Cookies : {}'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies 不合法: ', username)
            if self.cookies_db.delete(username):
                print('删除 Cookies: ', username)
            else:
                print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                delete_account(self.site, 'cookies', username)
        try:
            test_url = TEST_URL_MAP[self.site]
            self.session.proxies.update(utils.get_random_proxy('requests: https'))
            resp = self.session.get(test_url, cookies=cookies, allow_redirects=False, timeout=60)
            if resp.status_code == 200:
                nickname = json.loads(unquote(cookies['tyc-user-info']))['nickname']
                print('Cookies 有效!')
                print('Hello, {}! '.format(nickname))
            elif resp.status_code == 302:
                if 'verify' in resp.headers.get('location', ''):
                    print('账号异常, 进行验证中...')
                    num = 0
                    while num < 5:
                        init_data = self._init_captcha(cookies)
                        if init_data:
                            success = self.account_verify(cookies, init_data)
                            if success:
                                print('账号异常验证通过, Cookie 可正常使用! ')
                                break
                        else:
                            print('初始化失败! ')
                        num += 1
                        print('第 {} 次账号异常验证失败! '.format(num))
                elif 'login' in resp.headers.get('location', ''):
                    print('Cookies 已过期: {}'.format(username))
                    if self.cookies_db.delete(username):
                        print('删除 Cookies: ', username)
                    else:
                        print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                        delete_account(self.site, 'cookies', username)
        except ConnectionError as e:
            # traceback.print_exc()
            print('发生异常', e.args)


if __name__ == '__main__':
    pass
