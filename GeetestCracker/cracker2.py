# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:17
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : cracker2.py
# @Software: PyCharm

from GeetestCracker.geetest2 import geetest


class Cracker:

    def __init__(self, referer, gt, challenge):
        self.referer = referer
        self.gt = gt
        self.challenge = challenge

    def run(self):
        result = geetest.crack(self.gt, self.challenge, self.referer)
        if result['data']['success']:
            return result
        else:
            return {
                'data': {
                    'success': 0
                }
            }


if __name__ == '__main__':
    pass
