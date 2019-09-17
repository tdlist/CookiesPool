# -*- coding: utf-8 -*-
# @Time    : 2019/8/23 10:57
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : run_qimai.py
# @Software: PyCharm

import sys
sys.path.append('../../..')

from scheduler import Scheduler


def main():
    s = Scheduler('qimai')
    s.run()


if __name__ == '__main__':
    main()
