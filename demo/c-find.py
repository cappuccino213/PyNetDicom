#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/28 15:57
# @Author  : Zhangyp
# @File    : c-find.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
from pydicom.dataset import Dataset

from pynetdicom import AE
from pynetdicom.sop_class import _QR_CLASSES as QR

from configuration import LocalAE, AETitle, addr, port

ae = AE(ae_title=LocalAE)
# ae.add_requested_context(QR['PatientRootQueryRetrieveInformationModelFind'])
ae.add_requested_context(QR['StudyRootQueryRetrieveInformationModelFind'])

# 创建我们的标识符(查询)数据集
ds = Dataset()
ds.AccessionNumber = 'DY020069'  # 搜索条件检查号
# ds.QueryRetrieveLevel = 'STUDY' # 检查层QR
ds.QueryRetrieveLevel = 'SERIES'  # 序列层QR
# ds.QueryRetrieveLevel = 'IMAGE'  # 影像层QR

# ds.PatientName = ''
# 病人层查询
# ds.QueryRetrieveLevel = 'PATIENT'

# 创建节点的连接
assoc = ae.associate(addr, port, ae_title=AETitle)

if assoc.is_established:
    # Use the C-FIND service to send the identifier
    responses = assoc.send_c_find(ds, QR['StudyRootQueryRetrieveInformationModelFind'])

    # 返回对象计数
    count = 0
    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04x}'.format(status.Status), '----------')
            # If the status is 'Pending' then identifier is the C-FIND response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)  # 如果有结果则输出影像检查结果
                count += 1
        else:
            print('Connection timed out, was aborted or received invalid response')
    print('返回{0}数量：{1}'.format(ds.QueryRetrieveLevel, count))

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
