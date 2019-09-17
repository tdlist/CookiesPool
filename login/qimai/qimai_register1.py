# -*- coding: utf-8 -*-
# @Time    : 2019/8/23 10:05
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qimai_register.py
# @Software: PyCharm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import re
import time
import random
from PIL import Image
from io import BytesIO
from requests_spider_model import utils
from login.yima_platform import get_phonenumber, get_vcode
from login.selenium_proxyauth import create_proxyauth_extension

THRESHOLD = 60
LEFT = 60
BORDER = 0


class QimaiRegister:

    def __init__(self):
        self.site = 'qimai'
        self.itemid = 21300  # 七麦在易码平台的编号
        self.token = '***********'
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别, 开发者模式下 webdriver 属性为 undefined
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36')
        # options.add_argument('--headless')  有 selenium 无头模式检测
        # 设置认证代理
        username, password, host, port = utils.get_random_proxy('selenium')
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=host,
            proxy_port=int(port),
            proxy_username=username,
            proxy_password=password
        )
        options.add_extension(proxyauth_plugin_path)
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_window_size(1920, 1080)
        self.wait = WebDriverWait(self.browser, 20)

    def __del__(self):
        self.browser.quit()

    @staticmethod
    def get_random_password():
        """
        生成随机8~12位密码
        :return:
        """
        text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!.'
        return ''.join(random.sample(text, random.randint(8, 12)))

    def get_geetest_button(self):
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return button

    def get_geetest_image(self, name, full):
        top, bottom, left, right, size = self.get_position(full)
        # print("验证码位置", top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left, top, right, bottom))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        # captcha.show()
        # captcha.save(name)
        return captcha

    def get_position(self, full):
        img = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_slice")))
        fullbg = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_fullbg")))
        time.sleep(2)

        # 两种执行js写法
        if full:
            self.browser.execute_script(
                'document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style", "")')
        else:
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])", fullbg, "style", "display: none")

        location = img.location
        size = img.size
        top, bottom, left, right = location["y"], location["y"] + \
                                   size["height"], location["x"], location["x"] + size["width"]
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def get_gap(self, image1, image2):
        for i in range(LEFT, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    return i
        return LEFT

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if abs(pixel1[0] - pixel2[0]) < THRESHOLD and abs(pixel1[1] - pixel2[1]) < THRESHOLD and abs(
                pixel1[2] - pixel2[2]) < THRESHOLD:
            return True
        else:
            return False

    def get_track(self, distance):
        """
        获取滑块移动轨迹的列表
        :param distance: 第二个缺块的左侧的x坐标
        :return: 滑块移动轨迹列表
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 2 / 3
        # 计算间隔
        t = 0.4
        # 初速度
        v = 0
        distance += 10  # 使滑块划过目标地点, 然后回退

        while current < distance:
            # 加速度
            if current < mid:
                a = 2
            else:
                a = -3
            # 初速度 v0
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 0.5 * a * t * t
            # 当前位移
            current += move
            track.append(move)

        return track

    def get_slider(self):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_slider_button")))

    def move_to_gap(self, button, track):
        ActionChains(self.browser).click_and_hold(button).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            # time.sleep(0.5)
        # time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def register(self, phonenumber):
        """
        打开浏览器,并且输入账号密码
        :return: None
        """
        print('开始注册...')
        self.browser.get("https://www.qimai.cn/account/signup/r/%2F")
        time.sleep(5)

        username_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="phone"]')))
        username_input.clear()
        username_input.send_keys(phonenumber)
        time.sleep(1)

        # 需要点击空处才能激活获取验证码按钮
        print('点击获取手机验证码...')
        try:
            self.browser.find_element_by_css_selector('.ivu-alert-message').click()
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                 '//button[contains(@class, "get-phone-code")]')))
            button.click()
        except ElementClickInterceptedException:
            # 代理质量问题
            error = '点击获取手机验证码失败! '
            return error

        print('等待滑动验证码加载...')
        time.sleep(3)
        image1 = self.get_geetest_image("captcha1.png", True)
        image2 = self.get_geetest_image("captcha2.png", False)
        gap = self.get_gap(image1, image2)
        track = self.get_track(gap - BORDER)
        slider = self.get_slider()
        print('移动滑块至缺口...')
        self.move_to_gap(slider, track)
        time.sleep(3)

        html = self.browser.page_source
        bsobj = BeautifulSoup(html, 'lxml')
        is_pass = bsobj.select('.ivu-input-group-append button span')[0].get_text()
        if '等待' in is_pass:
            print('滑动验证通过! ')
            second = re.search(r'\d+', is_pass).group(0)
            print('请在{}秒内接收手机验证码! '.format(second))
            msg = get_vcode(self.token, self.itemid, phonenumber, second)
            vcode = re.search(r'您的验证码为(\d+)，', msg).group(1)

            # 输入验证码
            print('成功接收验证码: {}, 输入中...'.format(vcode))
            vcode_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="phoneCode"]')))
            vcode_input.clear()
            vcode_input.send_keys(vcode)
            time.sleep(1)

            # 输入密码
            password = self.get_random_password()
            print('生成随机密码: {}, 输入中...'.format(password))
            password_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="password"]')))
            password_input.send_keys(password)
            time.sleep(1)

            # 在此输入密码确认
            repassword_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="repassword"]')))
            repassword_input.send_keys(password)
            time.sleep(1)

            # 点击注册按钮
            print('输入完成, 点击注册...')
            submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="注册"]')))
            action = ActionChains(self.browser)
            action.move_to_element(submit).click().perform()

            time.sleep(5)
            if self.browser.current_url == 'https://www.qimai.cn/':
                print('注册成功! ')
                return {
                    'username': phonenumber,
                    'password': password
                }
            else:
                error = '未知错误! '
                return error
        else:
            error = '滑动验证未通过! '
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
