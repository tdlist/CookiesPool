# -*- coding: utf-8 -*-
# @Time    : 2019/8/21 13:48
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : run_qixinbao.py
# @Software: PyCharm


import sys
sys.path.append('..')
sys.path.append('../../..')

from scheduler import Scheduler


def main():
    s = Scheduler('qixinbao')
    s.run()


if __name__ == '__main__':
    main()
