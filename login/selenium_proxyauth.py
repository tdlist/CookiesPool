# -*- coding: utf-8 -*-
# @Time    : 2019/8/25 13:37
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : selenium_proxyauth.py
# @Software: PyCharm

import os
import time
from selenium import webdriver
from requests_spider_model import utils

import string
import zipfile


def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    """代理认证插件

    args:
        proxy_host (str): 你的代理地址或者域名（str类型）
        proxy_port (int): 代理端口号（int类型）
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """
    if plugin_path is None:
        file = './chrome_proxy_helper'
        if not os.path.exists(file):
            os.mkdir(file)
        plugin_path = file + '/%s_%s@%s_%s.zip' % (proxy_username, proxy_password, proxy_host, proxy_port)

    manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                  },
                  bypassList: ["foobar.com"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


# username, password, host, port = utils.get_random_proxy('selenium')

# proxyauth_plugin_path = create_proxyauth_extension(
#     proxy_host=host,
#     proxy_port=int(port),
#     proxy_username=username,
#     proxy_password=password
# )

# options = webdriver.ChromeOptions()
# co.add_argument("--start-maximized")
# options.add_extension(proxyauth_plugin_path)

# driver = webdriver.Chrome(options=options)
# driver.get("https://www.baidu.com")
# time.sleep(10000)
