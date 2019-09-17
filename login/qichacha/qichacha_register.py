# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 16:35
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : qichacha_register.py
# @Software: PyCharm


import asyncio
import random
import time
import re
from bs4 import BeautifulSoup
from pyppeteer.launcher import launch
from pyppeteer.errors import TimeoutError, NetworkError
from login.yima_platform import get_phonenumber, get_vcode


class QichachaRegister:

    def __init__(self):
        self.site = 'qichacha'
        self.itemid = 3970  # 企查查在易码平台的编号
        self.token = '***********'

    @staticmethod
    def input_time_random():
        return random.randint(150, 201)

    def retry_if_result_none(self, result):
        print('滑块判定失败, 重试！')
        return result is None

    @staticmethod
    def get_random_password():
        """
        生成随机8位密码
        :return:
        """
        text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!.'
        return ''.join(random.sample(text, 8))

    async def register(self, phonenumber):
        browser = await launch(
            {
                'headless': False,
                'args': ['--no-sandbox', '--disable-infobars'],
            },
            # userDataDir=r'D:\login\userdata',
            args=['--window-size=1366, 768']
        )
        page = await browser.newPage()  # 启动个新的浏览器页面
        await page.setJavaScriptEnabled(enabled=True)  # 启用js
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        )  # 设置模拟浏览器

        print('开始注册...')
        try:
            await page.goto('https://www.qichacha.com/user_register')
            time.sleep(2)
        except TimeoutError or NetworkError:
            await self.page_close(browser)

        await self.page_evaluate(page)

        time.sleep(1)
        await page.type('#phone', phonenumber, {'delay': self.input_time_random() - 50})

        # await page.screenshot({'path': './headless-test-result.png'})   # 截图测试
        time.sleep(2)

        print('拉动滑块验证...')
        # await page.screenshot({'path': './headless-login-slide.png'})   # 截图测试
        flag = await self.mouse_slide(page=page)  # js拉动滑块
        if flag:
            print('滑块验证通过! ')
            # await page.keyboard.press('Enter')
            await page.click('a.get-mobile-code')
            await asyncio.sleep(3)

            html = await page.content()
            bsobj = BeautifulSoup(html, 'lxml')
            flag = bsobj.select('.get-mobile-code')[0].get_text()
            if '重新发送' in flag:
                second = re.search(r'\d+', flag).group(0)
                print('验证码发送成功, 请在{}s内接收! '.format(second))
                msg = get_vcode(self.token, self.itemid, phonenumber, second)
                vcode = re.search(r'您的验证码是(\d+)。', msg).group(1)

                # 输入验证码
                print('成功接收验证码: {} , 输入中...'.format(vcode))
                await page.type('#vcodeNormal', vcode, {'delay': self.input_time_random() - 50})
                time.sleep(1)

                # 输入密码
                password = self.get_random_password()
                print('生成随机密码: {}, 输入中...'.format(password))
                await page.type('#pswd', password, {'delay': self.input_time_random() - 50})
                time.sleep(1)
                # 点击注册
                print('点击注册...')
                await page.click('#register_btn')
                await asyncio.sleep(5)

                if page.url == 'https://www.qichacha.com/':
                    print('注册成功! ')
                    await self.page_close(browser)
                    return {
                        'username': phonenumber,
                        'password': password
                    }
                error = '未知错误, 注册失败! '
                return error
            else:
                error = '验证码发送失败, 请重试! '
                await self.page_close(browser)
                return error
        else:
            error = '滑动验证失败! '
            await self.page_close(browser)
            return error

    async def page_evaluate(self, page):
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

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
            await asyncio.sleep(2)
            slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')  # 判断是否通过
            if slider_again != '验证通过':
                return 0
            else:
                # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
                return 1

    async def run(self):
        phonenumber = get_phonenumber(self.token, self.itemid)
        print('成功获取手机号: {}'.format(phonenumber))
        result = await self.register(phonenumber)
        if isinstance(result, dict):
            return {
                'status': '1',
                'result': result
            }
        return {
            'status': '2',
            'result': result
        }


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(QichachaRegister().run())


if __name__ == '__main__':
    main()
