# -*- coding: utf-8 -*-
# @Time    : 2019/9/3 21:48
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : run_tianyancha.py
# @Software: PyCharm


import sys
sys.path.append('..')
sys.path.append('../../..')

from scheduler import Scheduler


def main():
    s = Scheduler('tianyancha')
    s.run()


if __name__ == '__main__':
    main()
