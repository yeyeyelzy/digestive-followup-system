package com.ruoyi.system.mapper;

import com.ruoyi.common.core.domain.entity.PatientUser;

/**
 * 患者用户数据层。
 */
public interface PatientUserMapper {

    PatientUser selectPatientUserByPatientId(Long patientId);

    PatientUser selectPatientUserByPhonenumber(String phonenumber);

    int insertPatientUser(PatientUser patientUser);
}
