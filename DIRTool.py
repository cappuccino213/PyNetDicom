#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/21 9:15
# @Author  : Zhangyp
# @File    : DIRTool.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com]

from pydicom.filereader import read_dicomdir

dicom_dir = read_dicomdir("DICOMDIR")
file_meta = str(dicom_dir.file_meta)
data_set = str(dicom_dir)
print(file_meta, '\n', data_set)
with open('dicomdir_info.txt', 'w', encoding='utf-8') as file:
	file.write(file_meta + '\n' + data_set)
