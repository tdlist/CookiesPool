# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 21:38
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : qichacha_login.py
# @Software: PyCharm

import sys
sys.path.append('../..')

import asyncio
import random
import time
from pyppeteer.launcher import launch
from requests_spider_model import utils
from pyppeteer.navigator_watcher import TimeoutError
from pyppeteer.errors import NetworkError


class QichachaLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qichacha'
        self.username = username
        self.password = password

    @staticmethod
    def input_time_random():
        return random.randint(150, 201)

    @staticmethod
    def retry_if_result_none(result):
        print('滑块判定失败, 重试！')
        return result is None

    async def login(self):
        username, password, proxy = utils.get_random_proxy('pyppeteer')
        browser = await launch(
            {
                'headless': False,
                'args': ['--no-sandbox', '--disable-infobars'],
            },
            args=['--no-sandbox',
                  '--disable-infobars',
                  '--proxy-server={}'.format(proxy),
                  '--ignore-certificate-errors',
                  '--window-size=1366, 768', ]
        )
        page = await browser.newPage()  # 启动个新的浏览器页面
        await page.authenticate({'username': username, 'password': password})  # 代理认证
        await page.setJavaScriptEnabled(enabled=True)  # 启用js
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        )  # 设置模拟浏览器
        await self.page_evaluate(page)  # 修改 webdriver 等属性

        print('尝试登录...')

        try:
            await page.goto('https://www.qichacha.com/user_login?back=%2F')
            time.sleep(2)
        except TimeoutError or NetworkError:
            await self.page_close(browser)

        time.sleep(5)
        try:
            await page.click('#normalLogin')

            time.sleep(1)
            await page.type('#nameNormal', self.username, {'delay': self.input_time_random() - 50})
            time.sleep(1)
            await page.type('#pwdNormal', self.password, {'delay': self.input_time_random()})

            # await page.screenshot({'path': './headless-test-result.png'})   # 截图测试
            time.sleep(3)

            print('拉动滑块验证...')
            # await page.screenshot({'path': './headless-login-slide.png'})   # 截图测试
            flag = await self.mouse_slide(page=page)  # js拉动滑块
            if flag:
                # await page.keyboard.press('Enter')
                await page.click('button.btn')
                time.sleep(5)
                try:
                    global error
                    error = await page.Jeval('.toast-message', 'node => node.textContent')  # 检测是否是账号密码错误
                except Exception as e:
                    error = None
                    print("登录成功! ")
                finally:
                    if error:
                        error = await (await (await page.xpath('//div[@class="toast-message"]'))[0].getProperty(
                            'textContent')).jsonValue()
                        await self.page_close(browser)
                        return error
                    else:
                        await asyncio.sleep(3)
                        cookies = await page.cookies()
                        await self.page_close(browser)
                        return cookies
            else:
                error = '滑动验证失败! '
                await self.page_close(browser)
                return error
        except:
            await self.page_close(browser)

    async def page_evaluate(self, page):
        """
        修改自动化工具标识, evaluateOnNewDocument 方法 : 属性持久化, 页面刷新后值不变
        :param page:
        :return:
        """
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')
        await page.evaluateOnNewDocument('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluateOnNewDocument(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5, 6], }); }''')

    async def page_close(self, browser):
        """
        关闭浏览器驱动
        :param browser:
        :return:
        """
        for _page in await browser.pages():
            await _page.close()
        await browser.close()

    # @retry(retry_on_result=retry_if_result_none, )
    async def mouse_slide(self, page=None):
        await asyncio.sleep(3)
        try:
            # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
            await page.hover('.btn_slide')
            await page.mouse.down()  # 模拟按下鼠标
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})  # js模拟拖动
            await page.mouse.up()  # 模拟松开鼠标
        except:
            return 0
        else:
            await asyncio.sleep(5)
            slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')  # 判断是否通过
            if slider_again != '验证通过':
                return 0
            else:
                # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
                print('验证通过! ')
                return 1

    async def run(self):
        result = await self.login()
        if isinstance(result, list):
            return {
                'status': '1',
                'result': result
            }
        elif isinstance(result, str):
            if result == '滑动验证失败! ':
                return {
                    'status': '2',
                    'result': '滑动验证失败! '
                }
            else:
                return {
                    'status': '3',
                    'result': '密码错误! '
                }


def main(username, password):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(QichachaLogin(username, password).run())
    return result


if __name__ == '__main__':
    x = main('*********', '*********')
    print(x)
