#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/13 14:29
# @Author  : Zhangyp
# @File    : read.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com

from pydicom import dcmread

data = dcmread('ImageFiles/encr.dcm')

print(data.dir())
print(data.AccessionNumber)