# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 9:25
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : zhilian_login.py
# @Software: PyCharm


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login.geetest_crack import Geetest2Cracker
import requests
import time


THRESHOLD = 60
LEFT = 60
BORDER = 0


class ZhilianLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'zhilian'
        self.username = username
        self.password = password
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)

    def check_islogin(self, cookies):
        """
        检查登录状态, 跳转至个人主页则 cookies 有效
        :param cookies:
        :return:
        """
        url = 'https://fe-api.zhaopin.com/c/i/user/detail'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        res = requests.get(url, headers=headers, cookies=cookies).json()
        if res['code'] == 200:
            print('Cookies 有效!')
            nickname = res['data']['Name']
            print('Hello, {}! '.format(nickname))
            return True
        return False

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
        self.browser.get("https://passport.zhaopin.com/login?bkUrl=%2F%2Fi.zhaopin.com%2Fblank%3Fhttps%3A%2F%2Fwww.zhaopin.com%2F")
        time.sleep(1)
        self.browser.find_element_by_xpath('//li[@class="zppp-panel-tab"]').click()
        time.sleep(1)
        username = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="text"]')))
        password = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.zppp-submit')))
        time.sleep(1)
        username.clear()
        username.send_keys(self.username)
        time.sleep(1)
        password.clear()
        password.send_keys(self.password)
        time.sleep(1)
        print('账号密码输入完成, 点击登录按钮')
        submit.click()

        print('等待验证码加载...')
        if self.is_element_exist('canvas.geetest_canvas_slice'):
            print('出现滑动验证码...')
            Geetest2Cracker(self.browser).crack()
            print('校验滑动验证是否成功...')
        else:
            print('未出现滑动验证码...')
        time.sleep(3)
        if self.browser.current_url == 'https://www.zhaopin.com/':
            print('校验完成, 登录成功! ')
            nickname = self.browser.find_element_by_css_selector('.zp-userinfo').text
            print('Hello, {}! '.format(nickname))
            cookies = self.browser.get_cookies()
            cookies = {item['name']: item['value'] for item in cookies}
            self.browser.close()
            return cookies
        elif self.browser.find_element_by_xpath('//p[contains(@class, "zppp-password__error")]'):
            errors = self.browser.find_element_by_xpath('//p[contains(@class, "zppp-password__error")]').text
            return errors
        elif self.browser.find_element_by_xpath('//p[@class="tips"]'):
            errors = self.browser.find_element_by_xpath('//p[@class="tips"]').text
            return errors
        elif self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas.geetest_canvas_slice"))):
            errors = '滑动验证失败! '
            return errors

    def run(self):
        result = self.login()
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        elif isinstance(result, str):
            if result == '用户名或密码错误，请重试':
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
    x = ZhilianLogin('账号', '密码').run()
    print(x)
