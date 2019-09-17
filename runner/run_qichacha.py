# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 23:07
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : run.py
# @Software: PyCharm

import sys
sys.path.append('../../..')

from scheduler import Scheduler


def main():
    s = Scheduler('qichacha')
    s.run()


if __name__ == '__main__':
    main()
