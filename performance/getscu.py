#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 16:06 
# @Author  : Zhangyp
# @File    : getscu.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
from common import setup_logging, create_dataset, handle_store
from configuration import (
     qr_level,
    LocalAE, AETitle, addr, port,
    acse_timeout, dimse_timeout, network_timeout,
    pdu)
from pynetdicom import (
    AE, build_role, evt,
    StoragePresentationContexts,
    QueryRetrievePresentationContexts,
)

from pynetdicom.sop_class import _QR_CLASSES,_STORAGE_CLASSES

# 设置相关pynetdicom uid
PatientRootQueryRetrieveInformationModelGet = _QR_CLASSES.get('PatientRootQueryRetrieveInformationModelGet')
StudyRootQueryRetrieveInformationModelGet = _QR_CLASSES.get('StudyRootQueryRetrieveInformationModelGet')
PatientStudyOnlyQueryRetrieveInformationModelGet = _QR_CLASSES.get('PatientStudyOnlyQueryRetrieveInformationModelGet')
PlannedImagingAgentAdministrationSRStorage = _QR_CLASSES.get('PlannedImagingAgentAdministrationSRStorage')
PerformedImagingAgestAdministrationSRStorage = _QR_CLASSES.get('PerformedImagingAgestAdministrationSRStorage')
EncapsulatedSTLStorage = _STORAGE_CLASSES.get('EncapsulatedSTLStorage')


def main():
    APP_LOGGER = setup_logging('getscu')
    APP_LOGGER.debug('')

    # Create query (identifier) dataset
    # try:
    #     identifier = create_dataset(APP_LOGGER)
    # except Exception as exc:
    #     APP_LOGGER.exception(exc)
    identifier = create_dataset(APP_LOGGER)

    # Exclude these SOP Classes
    _exclusion = [
        PlannedImagingAgentAdministrationSRStorage,
        PerformedImagingAgestAdministrationSRStorage,
        EncapsulatedSTLStorage,
    ]
    store_contexts = [
        cx for cx in StoragePresentationContexts
        if cx.abstract_syntax not in _exclusion
    ]

    # Create application entity
    ae = AE(ae_title=LocalAE)
    ae.acse_timeout = acse_timeout
    ae.dimse_timeout = dimse_timeout
    ae.network_timeout = network_timeout

    # Extended Negotiation - SCP/SCU Role Selection
    ext_neg = []

    # 添加一种查询模型，注意只能添加一种，因为上下文长度有限制128，而之后需要添加127种存储上下文
    # 这里还需要注意区分Model和level，文档：dicom的QR方法和定义（model和level）....
    # http://note.youdao.com/noteshare?id=b748c5aecefddbf8da04c62ece43f510&sub=85FBF3A1D7B24A4986014F5D76E1AF77
    # ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
    # ae.add_requested_context(PatientStudyOnlyQueryRetrieveInformationModelGet)

    for cx in store_contexts:
        ae.add_requested_context(cx.abstract_syntax)
        # Add SCP/SCU Role Selection Negotiation to the extended negotiation
        # We want to act as a Storage SCP
        ext_neg.append(build_role(cx.abstract_syntax, scp_role=True))

    if qr_level == 'STUDY':
        query_model = StudyRootQueryRetrieveInformationModelGet
    elif qr_level == 'PATIENT':
        query_model = PatientRootQueryRetrieveInformationModelGet
    else:
        query_model = StudyRootQueryRetrieveInformationModelGet
        print('qr_level must be STUDY or PATIENT')

    # Request association with remote
    assoc = ae.associate(
        addr,
        port,
        ae_title=AETitle,
        ext_neg=ext_neg,
        evt_handlers=[(evt.EVT_C_STORE, handle_store, [APP_LOGGER])],
        max_pdu=pdu
    )

    if assoc.is_established:
        # Send query
        responses = assoc.send_c_get(identifier, query_model)
        for (status, rsp_identifier) in responses:
            # If `status.Status` is one of the 'Pending' statuses then
            #   `rsp_identifier` is the C-GET response's Identifier dataset
            if status and status.Status in [0xFF00, 0xFF01]:
                # `rsp_identifier` is a pydicom Dataset containing a query
                # response. You may want to do something interesting here...
                pass
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')


if __name__ == '__main__':
    main()
