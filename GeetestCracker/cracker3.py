# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:23
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : cracker3.py
# @Software: PyCharm

import base64
import os
import platform
import random
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from selenium import webdriver
from login.chaojiying import image_to_text
from selenium.webdriver.common.action_chains import ActionChains


def main(address="127.0.0.1", port=8778, headless=False, workers=2, delay=2):
    def task(thread_id):
        time.sleep(thread_id * delay)
        driver = create_driver(f"http://{address}:{port}/task", headless=headless)
        while True:
            try:
                crack(driver)
                time.sleep(2)
            except:
                time.sleep(1)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(task, range(workers))


def create_driver(url, headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("log-level=3")
    # 设置为开发者模式，避免被识别, 开发者模式下 webdriver 属性为 undefined
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    if headless:
        options.add_argument("headless")
    else:
        options.add_argument("disable-infobars")
        options.add_argument("window-size=380,460")
    if platform.system() == "Linux":
        options.add_argument("no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def crack(driver):
    if is_element_exist(driver, '.geetest_item_img'):
        # print('出现点选验证码...')
        click_geetest(driver)
    elif is_element_exist(driver, "canvas.geetest_canvas_slice"):
        # print('出现滑动验证码...')
        crack_geetest(driver)


def click_geetest(driver, img_class=".geetest_item_img", success_class="geetest_success"):
    rand = str(random.randint(0, 100000000))
    img_path = save_img(driver, img_path=os.path.join("tmp", f"bg_{rand}.png"), img_class=img_class)
    captcha = open(img_path, 'rb').read()
    while True:
        ok, pic_pos = image_to_text(captcha, img_kind=9004)
        if ok:
            # print('成功识别验证码! ')
            click_word(driver, pic_pos)
            break
        else:
            # print('验证码识别失败! ')
            pass


def click_word(driver, pic_pos):
    """
    点击验证码
    :param pic_pos: 验证码需要点击的坐标
    :return:
    """
    # print('开始点击验证码...')
    vcode_img = driver.find_element_by_css_selector('.geetest_item_img')
    tup_list = pic_pos.split('|')
    pos_list = []
    for tup in tup_list:
        x_list = tup.split(',')
        pos_list.append((int(x_list[0]), int(x_list[1])))
    for pos in pos_list:
        ActionChains(driver).move_to_element_with_offset(vcode_img, pos[0], pos[1]).click().perform()
        time.sleep(1)
    # print('点击完成！进行验证...')
    driver.find_element_by_css_selector('.geetest_commit').click()


def crack_geetest(driver, bg_class="geetest_canvas_bg geetest_absolute",
                  full_bg_class="geetest_canvas_fullbg geetest_fade geetest_absolute",
                  slider_class="geetest_slider_button", success_class="geetest_success"):
    driver.find_element_by_class_name(slider_class)
    rand = str(random.randint(0, 100000000))
    bg_path = save_bg(driver, bg_path=os.path.join("tmp", f"bg_{rand}.png"), bg_class=bg_class)
    full_bg_path = save_full_bg(driver, full_bg_path=os.path.join("tmp", f"fullbg_{rand}.png"),
                                full_bg_class=full_bg_class)
    distance = get_offset(full_bg_path, bg_path)
    os.remove(full_bg_path)
    os.remove(bg_path)
    track = get_track(distance)
    # print('开始滑动...')
    move_to_gap(driver, track, slider_class=slider_class)
    # print('滑动完成, 进行验证...')
    # drag_the_ball(driver, track, slider_class=slider_class)


def is_element_exist(driver, element):
    flag = True
    try:
        driver.find_element_by_css_selector(element)
        return flag
    except:
        flag = False
        return flag


def save_base64img(data_str, save_name):
    img_data = base64.b64decode(data_str)
    file = open(save_name, "wb")
    file.write(img_data)
    file.close()


def get_base64_by_canvas(driver, class_name, contain_type):
    bg_img = ""
    while len(bg_img) < 5000:
        get_img_js = f"return document.getElementsByClassName(\"{class_name}\")[0].toDataURL(\"image/png\");"
        bg_img = driver.execute_script(get_img_js)
        time.sleep(0.5)
    if contain_type:
        return bg_img
    else:
        return bg_img[bg_img.find(",") + 1:]


def save_img(driver, img_path="img.png", img_class=".geetest_item_img"):
    img_url = driver.find_element_by_css_selector(img_class).get_attribute('src')
    img_data = requests.get(img_url).content
    with open(img_path, 'wb') as f:
        f.write(img_data)
    return img_path


def save_bg(driver, bg_path="bg.png", bg_class="geetest_canvas_bg geetest_absolute"):
    bg_img_data = get_base64_by_canvas(driver, bg_class, False)
    save_base64img(bg_img_data, bg_path)
    return bg_path


def save_full_bg(driver, full_bg_path="fbg.png", full_bg_class="geetest_canvas_fullbg geetest_fade geetest_absolute"):
    bg_img_data = get_base64_by_canvas(driver, full_bg_class, False)
    save_base64img(bg_img_data, full_bg_path)
    return full_bg_path


def get_slider(driver, slider_class="geetest_slider_button"):
    while True:
        try:
            slider = driver.find_element_by_class_name(slider_class)
            break
        except:
            time.sleep(0.5)
    return slider


def is_pixel_equal(img1, img2, x, y):
    pix1 = img1.load()[x, y]
    pix2 = img2.load()[x, y]
    threshold = 60
    if abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] < threshold):
        return True
    else:
        return False


def get_offset(full_bg_path, bg_path, initial_offset=39):
    full_bg = Image.open(full_bg_path)
    bg = Image.open(bg_path)
    left = initial_offset
    for i in range(left, full_bg.size[0]):
        for j in range(full_bg.size[1]):
            if not is_pixel_equal(full_bg, bg, i, j):
                left = i
                return left
    return left


def get_track(distance):
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


def move_to_gap(driver, track, slider_class="geetest_slider_button"):
    slider = get_slider(driver, slider_class)
    ActionChains(driver).click_and_hold(slider).perform()
    for x in track:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
        # time.sleep(0.5)
    # time.sleep(0.5)
    ActionChains(driver).release().perform()


def drag_the_ball(driver, track, slider_class="geetest_slider_button"):
    slider = get_slider(driver, slider_class)
    ActionChains(driver).click_and_hold(slider).perform()
    while track:
        x = random.choice(track)
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
        track.remove(x)
    time.sleep(0.1)
    imitate = ActionChains(driver).move_by_offset(xoffset=-1, yoffset=0)
    time.sleep(0.015)
    imitate.perform()
    # time.sleep(random.randint(6, 10) / 10)
    imitate.perform()
    time.sleep(0.04)
    imitate.perform()
    time.sleep(0.012)
    imitate.perform()
    time.sleep(0.019)
    imitate.perform()
    time.sleep(0.033)
    ActionChains(driver).move_by_offset(xoffset=1, yoffset=0).perform()
    ActionChains(driver).pause(random.randint(6, 14) / 10).release(slider).perform()


if __name__ == "__main__":
    main()
