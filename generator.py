# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 21:38
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : qichacha_login.py
# @Software: PyCharm

import json
import asyncio
import time
import random
from pprint import pprint
from db import RedisClient
from login.qichacha.qichacha_register import QichachaRegister
from login.qichacha.qichacha_login import QichachaLogin
from login.qixinbao.qixinbao_login import QixinbaoLogin
from login.qixinbao.qixinbao_register import QixinbaoRegister
from login.qimai.qimai_login import QimaiLogin
from login.qimai.qimai_register import QimaiRegister
from login.kuchuan.kuchuan_login import KuchuanLogin
from login.tianyancha.tianyancha_login import TianyanchaLogin
from login.tianyancha.tianyancha_register import TianyanchaRegister
from importer import set_account
from deleter import delete_account


class CookiesGenerator:
    """
    Cookie 生成器基类
    """

    def __init__(self, site, single_cycle_limit):
        self.site = site
        # 单轮登录数量上限
        self.single_cycle_limit = single_cycle_limit
        self.cookies_db = RedisClient('cookies', self.site)
        self.accounts_db = RedisClient('accounts', self.site)

    def new_cookies(self, username, password):
        """
        新生成 Cookies
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def process_cookies(cookies):
        """
        处理 cookies
        :param cookies:
        :return:
        """
        return {cookie['name']: cookie['value'] for cookie in cookies}

    def run(self):
        """
        运行账号池的所有账号生成 cookie
        :return:
        """
        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()
        num = 0
        for username in accounts_usernames:
            if num >= self.single_cycle_limit:
                print('已达单轮登录上限, 停止登录! ')
                return
            if username not in cookies_usernames:
                password = self.accounts_db.get(username).decode('utf-8')
                username = username.decode('utf-8')
                print('正在生成 Cookies -> 账号: {}, 密码: {}'.format(username, password))
                result = self.new_cookies(username, password)
                if result.get('status') == '1':
                    if isinstance(result['result'], list):
                        cookies = self.process_cookies(result['result'])
                    else:
                        cookies = result['result']
                    print('成功生成 Cookies : {}'.format(cookies))
                    if self.cookies_db.set(username, json.dumps(cookies)):
                        print('成功保存至 Cookie Pool!')
                    else:
                        print('疑似 redis 连接断开, 未成功保存, 尝试调用录入器保存...')
                        set_account(self.site, 'cookies', '{} {}'.format(username, json.dumps(cookies)))
                # 密码错误, 移除账号
                elif result.get('status') == '3':
                    print(result['result'])
                    if self.accounts_db.delete(username):
                        print('删除账号: ', username)
                    else:
                        print('疑似 redis 断开连接, 删除失败, 尝试调用删除器删除...')
                        delete_account(self.site, 'accounts', username)
                else:
                    print(result.get('result'))
                num += 1
            else:
                continue
            sleep_time = random.randint(90, 180)
            # print('休息{}秒...'.format(sleep_time))
            time.sleep(sleep_time)
        print('所有账号生成完毕! ')


class QichachaCookiesGenerator(CookiesGenerator):
    """"
    企查查 Cookie 生成器
    """

    def __init__(self, site='qichacha'):
        self.site = site
        self.single_cycle_limit = 8  # 测试用代理连续登录成功5个左右, 继续登录滑块验证可能会失败...
        CookiesGenerator.__init__(self, self.site, self.single_cycle_limit)

    def new_cookies(self, username, password):
        """
        生成 cookies
        :param username:
        :param password:
        :return:
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(QichachaLogin(username, password).run())
        return result


class QixinbaoCookiesGenerator(CookiesGenerator):
    """
    启信宝 Cookies 生成器
    """
    def __init__(self, site='qixinbao'):
        self.site = site
        self.single_cycle_limit = 10
        CookiesGenerator.__init__(self, self.site, self.single_cycle_limit)

    def new_cookies(self, username, password):
        """
        生成 cookies
        :param username:
        :param password:
        :return:
        """
        result = QixinbaoLogin(username, password).run()
        return result


class QimaiCookiesGenerator(CookiesGenerator):
    """
    七麦 Cookies 生成器
    """

    def __init__(self, site='qimai'):
        self.site = site
        self.single_cycle_limit = 10
        CookiesGenerator.__init__(self, self.site, self.single_cycle_limit)

    def new_cookies(self, username, password):
        """
        生成 cookies
        :param username:
        :param password:
        :return:
        """
        result = QimaiLogin(username, password).run()
        return result


class KuchuanCookiesGenerator(CookiesGenerator):
    """
    酷船 Cookies 生成器
    """

    def __init__(self, site='kuchuan'):
        self.site = site
        self.single_cycle_limit = 10
        CookiesGenerator.__init__(self, self.site, self.single_cycle_limit)

    def new_cookies(self, username, password):
        """
        生成 cookies
        :param username:
        :param password:
        :return:
        """
        result = KuchuanLogin(username, password).run()
        return result


class TiantanchaCookiesGenerator(CookiesGenerator):
    """
    天眼查 Cookies 生成器
    """

    def __init__(self, site='tianyancha'):
        self.site = site
        self.single_cycle_limit = 10
        CookiesGenerator.__init__(self, self.site, self.single_cycle_limit)

    def new_cookies(self, username, password):
        """
        生成 cookies
        :param username:
        :param password:
        :return:
        """
        result = TianyanchaLogin(username, password).run()
        return result


class AccountsGenerator:
    """
    账号生成器基类
    """

    def __init__(self, site, accounts_pool_size, single_cycle_limit):
        self.site = site
        # 账号池数量上限
        self.accounts_pool_size = accounts_pool_size
        # 单轮注册数量上限
        self.single_cycle_limit = single_cycle_limit
        self.accounts_db = RedisClient('accounts', self.site)

    def new_account(self):
        """
        新注册账号
        :return:
        """
        raise NotImplementedError

    def run(self):
        num = 0
        # 单轮尝试注册次数上限15次, 防止因为某些原因被识别一直注册失败, 进程卡死在这个循环中
        while num <= 15:
            accounts_count = self.accounts_db.count()
            if accounts_count >= self.accounts_pool_size:
                print('账号池数量已足够, 停止注册！')
                return
            elif num >= self.single_cycle_limit:
                print('数量已达到单轮注册限制, 停止注册! ')
                return
            print('账号池数量未满, 持续注册中...')
            result = self.new_account()
            if result['status'] == '1':
                username = result['result']['username']
                password = result['result']['password']
                print('成功生成账号: {}'.format(result['result']['username']))
                if self.accounts_db.set(username, password):
                    print('成功保存账号: {}'.format(username))
                else:
                    print('疑似 redis 连接断开, 未成功保存, 尝试调用录入器保存...')
                    set_account(self.site, 'accounts', '{} {}'.format(username, password))
                num += 1
            else:
                print(result['result'])
            sleep_time = random.randint(90, 180)
            # print('休息{}秒...'.format(sleep_time))
            time.sleep(sleep_time)


class QichachaAccountsGenerator(AccountsGenerator):
    """
    企查查账号生成器, 经测试, 单 IP 一天注册上限 20 个左右, 再多注册的滑块验证会不通过
    """

    def __init__(self, site='qichacha'):
        self.accounts_pool_size = 50
        self.single_cycle_limit = random.randint(5, 10)
        AccountsGenerator.__init__(self, site, self.accounts_pool_size, self.single_cycle_limit)

    def new_account(self):
        """
        新注册账号
        :return:
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(QichachaRegister().run())
        return result


class QixinbaoAccountsGenerator(AccountsGenerator):
    """
    启信宝账号生成器
    """
    def __init__(self, site='qixinbao'):
        self.accounts_pool_size = 50
        self.single_cycle_limit = random.randint(5, 10)
        AccountsGenerator.__init__(self, site, self.accounts_pool_size, self.single_cycle_limit)

    def new_account(self):
        """
        新注册账号
        :return:
        """
        result = QixinbaoRegister().run()
        return result


class QimaiAccountsGenerator(AccountsGenerator):
    """
    七麦账号生成器
    """
    def __init__(self, site='qimai'):
        self.accounts_pool_size = 55
        self.single_cycle_limit = random.randint(5, 10)
        AccountsGenerator.__init__(self, site, self.accounts_pool_size, self.single_cycle_limit)

    def new_account(self):
        """
        新注册账号
        :return:
        """
        result = QimaiRegister().run()
        return result


class TianyanchaAccountsGenerator(AccountsGenerator):
    """
    天眼查账号生成器
    """
    def __init__(self, site='tianyancha'):
        self.accounts_pool_size = 80
        self.single_cycle_limit = random.randint(5, 10)
        AccountsGenerator.__init__(self, site, self.accounts_pool_size, self.single_cycle_limit)

    def new_account(self):
        """
        新注册账号
        :return:
        """
        result = TianyanchaRegister().run()
        return result


if __name__ == '__main__':
    pass

