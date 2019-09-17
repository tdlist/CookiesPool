# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 18:09
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : scheduler.py
# @Software: PyCharm

from multiprocessing import Process
from api import app
from tester import *
from config import *
from generator import *


class Scheduler:

    def __init__(self, site):
        self.site = site

    def valid_cookies(self, cycle=TESTER_CYCLE):
        """
        调度检测器
        :param cycle: 检测器运行周期
        :return:
        """
        while True:
            print('Cookies 检测进程开始运行...')
            try:
                cls = TESTER_MAP[self.site]
                if cls == '':
                    print('未找到检测器, 请检查配置是否正确, 或是否已编写该站点的检测器! ')
                    return
                tester = eval(cls + '(site="' + self.site + '")')
                tester.run()
                print('Cookies 检测完毕, 休眠半个小时, 等待下一次检测... ')
                del tester
                time.sleep(cycle)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print(e.args)

    def generate_account(self, cycle=GENERATOR_CYCLE):
        """
        调度账号注册器
        :param cycle: 注册器运行周期
        :return:
        """
        while True:
            print('账号注册进程开始运行...')
            try:
                cls = GENERATOR_MAP[self.site]
                if cls[0] == '':
                    print('未找到注册器, 请检查配置是否正确, 或是否已编写该站点的注册器! ')
                    return
                account_generator = eval(cls[0] + '(site="' + self.site + '")')
                account_generator.run()
                print('账号生成完毕, 等待生成 Cookies... ')
                time.sleep(cycle)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print(e.args)

    def generate_cookies(self, cycle=GENERATOR_CYCLE):
        """
        调度 Cookies 生成器
        :param cycle: 生成器运行周期
        :return:
        """
        while True:
            print('Cookies 生成进程开始运行...')
            try:
                cls = GENERATOR_MAP[self.site]
                if cls[1] == '':
                    print('未找到 Cookies 生成器, 请检查配置是否正确, 或是否已编写该站点的 Cookies 生成器! ')
                    return
                cookies_generator = eval(cls[1] + '(site="' + self.site + '")')
                cookies_generator.run()
                print('Cookies 生成完毕, 休眠半个小时, 等待下一次生成... ')
                time.sleep(cycle)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print(e.args)

    def api(self):
        """
        调度 API 接口
        :return:
        """
        print('API接口开始运行...')
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        process_list = []
        try:
            if API_PROCESS:
                api_process = Process(target=self.api)
                process_list.append(api_process)
                api_process.start()

            if ACCOUNT_GENERATOR_PROCESS:
                account_generator_process = Process(target=self.generate_account)
                process_list.append(account_generator_process)
                account_generator_process.start()

            if COOKIES_GENERATOR_PROCESS:
                cookies_generator_process = Process(target=self.generate_cookies)
                process_list.append(cookies_generator_process)
                cookies_generator_process.start()

            if VALID_PROCESS:
                valid_process = Process(target=self.valid_cookies)
                process_list.append(valid_process)
                valid_process.start()

            while True:
                # 避免进入死循环, 无法关闭主进程
                time.sleep(1)

        except KeyboardInterrupt:
            # Ctrl C 杀死未关闭进程
            for process in process_list:
                if process.is_alive():
                    process.terminate()


if __name__ == '__main__':
    pass
