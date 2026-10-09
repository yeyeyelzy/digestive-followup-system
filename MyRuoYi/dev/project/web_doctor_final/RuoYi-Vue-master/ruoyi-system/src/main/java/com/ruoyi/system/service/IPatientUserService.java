package com.ruoyi.system.service;

import com.ruoyi.common.core.domain.entity.PatientUser;

/**
 * 患者用户业务接口。
 */
public interface IPatientUserService {

    PatientUser selectPatientUserByPatientId(Long patientId);

    PatientUser selectPatientUserByPhonenumber(String phonenumber);

    boolean registerUserAndCreatePatientProfile(PatientUser patientUser);
}
