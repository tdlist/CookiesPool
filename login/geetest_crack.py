# -*- coding: utf-8 -*-
# @Time    : 2019/8/31 19:12
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : geetest_crack.py
# @Software: PyCharm

import time
import random
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

THRESHOLD = 60
LEFT = 60
BORDER = 0


class Geetest2Cracker:

    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)

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

    def crack(self):
        """
        滑块验证
        :return:
        """
        image1 = self.get_geetest_image("captcha1.png", True)
        image2 = self.get_geetest_image("captcha2.png", False)
        gap = self.get_gap(image1, image2)
        track = self.get_track(gap - BORDER)
        slider = self.get_slider()
        print('移动滑块至缺口...')
        self.move_to_gap(slider, track)


if __name__ == '__main__':
    pass
