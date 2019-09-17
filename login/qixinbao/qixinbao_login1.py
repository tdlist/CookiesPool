# -*- coding: utf-8 -*-
# @Time    : 2019/8/31 19:14
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qixinbao_login1.py
# @Software: PyCharm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login.geetest_crack import Geetest2Cracker
from login.geetest_click import GeetestClicker
import time
from bs4 import BeautifulSoup


"""
当缺口刷在离左边较近时, 滑动验证成功率较低
"""

THRESHOLD = 60
LEFT = 60
BORDER = 0


class QixinbaoLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qixinbao'
        self.username = username
        self.password = password
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)

    def is_element_exist(self, element):
        flag = True
        try:
            # self.browser.find_element_by_css_selector(element)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element)))
            return flag
        except:
            flag = False
            return flag

    def login(self):
        """
        打开浏览器,并且输入账号密码
        :return: None
        """
        print('尝试登录...')
        self.browser.get("https://www.qixin.com/auth/login?return_url=%2F")
        time.sleep(1)
        username = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="text"]')))
        password = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.form-group button')))
        time.sleep(1)
        username.clear()
        username.send_keys(self.username)
        time.sleep(1)
        password.clear()
        password.send_keys(self.password)
        time.sleep(1)
        print('账号密码输入完成, 点击登录按钮...')
        submit.click()

        time.sleep(5)
        if self.is_element_exist('.geetest_item_img'):
            print('出现点选验证码...')
            GeetestClicker(self.browser).click()
        elif self.is_element_exist("canvas.geetest_canvas_slice"):
            print('出现滑动验证码...')
            Geetest2Cracker(self.browser).crack()
        else:
            print('未出现验证码...')
        time.sleep(3)
        if self.browser.current_url == 'https://www.qixin.com/':
            print('登录成功! ')
            nickname = self.browser.find_element_by_css_selector('.user-name').text
            print('Hello, {}! '.format(nickname))
            cookies = self.browser.get_cookies()
            cookies = {item['name']: item['value'] for item in cookies}
            self.browser.close()
            return cookies
        elif self.is_element_exist('.toast-message'):
            html = self.browser.page_source
            bsobj = BeautifulSoup(html, 'lxml')
            errors = bsobj.find('div', {'class': 'toast-message'}).get_text()
            return errors
        elif self.is_element_exist('.geetest_item_img'):
            errors = '点选验证失败! '
            return errors
        elif self.is_element_exist("canvas.geetest_canvas_slice"):
            errors = '滑动验证失败! '
            return errors
        else:
            errors = '未知错误! '
            return errors

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
    x = QixinbaoLogin('**********', '*******').run()
    print(x)
