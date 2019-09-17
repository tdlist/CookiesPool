# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 21:32
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : config.py
# @Software: PyCharm


# Redis 数据库链接
REDIS_URL = 'redis://:************/2'

# 代理池地址
PROXY_URL = 'http://************/random/'

# 站点集合
SITE_LIST = ['qimai', 'qichacha', 'qixinbao', 'kuchuan', 'tianyancha']

# 生成器类(账号注册, 登录)，如扩展其他站点，请在此配置
GENERATOR_MAP = {
    'qimai': ['QimaiAccountsGenerator', 'QimaiCookiesGenerator'],
    'qichacha': ['QichachaAccountsGenerator', 'QichachaCookiesGenerator'],
    'qixinbao': ['QixinbaoAccountsGenerator', 'QixinbaoCookiesGenerator'],
    'kuchuan': ['', 'KuchuanCookiesGenerator'],
    'tianyancha': ['TianyanchaAccountsGenerator', 'TiantanchaCookiesGenerator']
}

# 检测类，如扩展其他站点，请在此配置
TESTER_MAP = {
    'qimai': 'QimaiValidTester',
    'qichacha': 'QichachaValidTester',
    'qixinbao': 'QixinbaoValidTester',
    'kuchuan': 'KuchuanValidTester',
    'tianyancha': 'TianyanchaValidTester'
}

TEST_URL_MAP = {
    'qimai': 'https://api.qimai.cn/account/userinfo',
    'qichacha': 'https://www.qichacha.com/search?key=%E4%B8%8A%E6%B5%B7%E4%B8%9C%E6%98%8C%E6%B1%BD%E8%BD%A6%E7%AE%A1%E7%90%86%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8',
    'qixinbao': 'https://www.qixin.com/user/home/center',
    'kuchuan': 'https://www.kuchuan.com/u/api/user_info',
    'tianyancha': 'https://www.tianyancha.com/search?key=%E7%BD%91%E6%98%93'
}

# 生成器循环周期
GENERATOR_CYCLE = 60 * 30

# 检测器循环周期
TESTER_CYCLE = 60 * 30

# API地址和端口
API_HOST = '0.0.0.0'
API_PORT = 8778

# 账号注册器开关
ACCOUNT_GENERATOR_PROCESS = True

# Cookies 生成器开关，模拟登录添加 Cookies
COOKIES_GENERATOR_PROCESS = True

# 检测器开关，循环检测数据库中 Cookies 是否可用，不可用删除
VALID_PROCESS = True

# API接口服务: API 接口放在线上服务器跑, 注册登录检测放在线下服务器跑
API_PROCESS = False
