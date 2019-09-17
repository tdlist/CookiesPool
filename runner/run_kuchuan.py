# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 14:53
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : run_kuchuan.py
# @Software: PyCharm

import sys
sys.path.append('..')
sys.path.append('../../..')

from scheduler import Scheduler


def main():
    s = Scheduler('kuchuan')
    s.run()


if __name__ == '__main__':
    main()
