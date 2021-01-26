#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/19 14:24
# @Author  : Zhangyp
# @File    : modify.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com

from pydicom import dcmread
from pydicom.uid import generate_uid


def modify_dcm():
	ds = dcmread(r'E:\Test\eWordImageView\temp\1.2.156.14702.1.1005.128.2.202005111032186851000200002.dic.dcm')
	
	ds.StudyInstanceUID = '1.2.826.0.1.3680043.8.498.10989466672569350505879818254389558410'
	# ds.SeriesInstanceUID = '1.2.156.14702.1.1005.128.1.20200511103415106000010001'
	# ds.StudyInstanceUID = generate_uid()
	ds.Modality = 'CT'
	ds.AccessionNumber = '20200511000305'
	ds[0x10, 0x10].value = '张道社'
	
	# ds.save_as(ds.SOPInstanceUID+'.dic.dcm', write_like_original=False)
	ds.save_as('E:\\Test\\eWordImageView\\temp\\' + ds.SOPInstanceUID + '.dic.dcm', write_like_original=False)
	return 0x0000  # 成功返回0


modify_dcm()
