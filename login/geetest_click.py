# -*- coding: utf-8 -*-
# @Time    : 2019/8/31 19:13
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : geetest_click.py
# @Software: PyCharm

import time
from PIL import Image
from io import BytesIO
from selenium.webdriver import ActionChains
from login.chaojiying import image_to_text
from selenium.webdriver.support.ui import WebDriverWait


class GeetestClicker:

    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)

    def get_position(self):
        vcode_img = self.browser.find_element_by_css_selector('.geetest_item_img')
        left = int(vcode_img.location['x'])
        top = int(vcode_img.location['y'])
        right = int(vcode_img.location['x']) + int(vcode_img.size['width'])
        bottom = int(vcode_img.location['y']) + int(vcode_img.size['height'])
        return (left, top, right, bottom)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def get_geetest_img(self):
        position = self.get_position()
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(position)
        captcha.save('code.png')

    def click_word(self, pic_pos):
        """
        点击验证码
        :param pic_pos: 验证码需要点击的坐标
        :return:
        """
        print('开始点击验证码...')
        vcode_img = self.browser.find_element_by_css_selector('.geetest_item_img')
        tup_list = pic_pos.split('|')
        pos_list = []
        for tup in tup_list:
            x_list = tup.split(',')
            pos_list.append((int(x_list[0]), int(x_list[1])))
        for pos in pos_list:
            ActionChains(self.browser).move_to_element_with_offset(vcode_img, pos[0], pos[1]).click().perform()
            time.sleep(1)
        print('点击完成！进行验证...')
        self.browser.find_element_by_css_selector('.geetest_commit').click()

    def click(self):
        while True:
            self.get_geetest_img()
            captcha = open('code.png', 'rb').read()
            ok, pic_pos = image_to_text(captcha, img_kind=9004)
            if ok:
                print('成功识别验证码! ')
                self.click_word(pic_pos)
                break
            else:
                print('验证码识别失败! ')

