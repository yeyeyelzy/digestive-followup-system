package com.ruoyi.system.service.impl;

import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.mapper.PatientMapper;
import com.ruoyi.system.mapper.PatientUserMapper;
import com.ruoyi.system.service.IPatientService;
import com.ruoyi.system.service.IPatientUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 患者用户业务实现。
 */
@Service
public class PatientUserServiceImpl implements IPatientUserService {

    @Autowired
    private PatientUserMapper patientUserMapper;

    @Autowired
    private IPatientService patientService;

    @Autowired
    private PatientMapper patientMapper;

    @Override
    public PatientUser selectPatientUserByPatientId(Long patientId) {
        return patientUserMapper.selectPatientUserByPatientId(patientId);
    }

    @Override
    public PatientUser selectPatientUserByPhonenumber(String phonenumber) {
        return patientUserMapper.selectPatientUserByPhonenumber(phonenumber);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean registerUserAndCreatePatientProfile(PatientUser patientUser) {
        if (patientUserMapper.selectPatientUserByPhonenumber(patientUser.getPhonenumber()) != null) {
            return false;
        }

        if (StringUtils.isEmpty(patientUser.getPatientName())) {
            patientUser.setPatientName(patientUser.getPhonenumber());
        }

        patientUser.setPassword(SecurityUtils.encryptPassword(patientUser.getPassword()));
        if (StringUtils.isEmpty(patientUser.getStatus())) {
            patientUser.setStatus("0");
        }
        if (StringUtils.isEmpty(patientUser.getDelFlag())) {
            patientUser.setDelFlag("0");
        }

        if (patientUser.getPatientId() == null) {
            Long maxId = patientMapper.selectMaxPatientId();
            patientUser.setPatientId((maxId == null ? 0L : maxId) + 1L);
        }

        int userRows = patientUserMapper.insertPatientUser(patientUser);
        if (userRows == 0) {
            throw new RuntimeException("创建患者登录账号失败");
        }

        if (patientUser.getPatientId() == null) {
            throw new RuntimeException("创建患者登录账号失败");
        }

        Patient profile = new Patient();
        profile.setPatientId(patientUser.getPatientId());
        profile.setPatientName(patientUser.getPatientName());
        profile.setPhoneNumber(patientUser.getPhonenumber());
        profile.setAge(patientUser.getAge());
        profile.setGender(parseGender(patientUser.getSex()));
        return patientService.insertPatient(profile) > 0;
    }

    private Long parseGender(String sex) {
        if (StringUtils.isEmpty(sex)) {
            return null;
        }
        if ("0".equals(sex) || "1".equals(sex) || "2".equals(sex)) {
            return Long.valueOf(sex);
        }
        return null;
    }
}
