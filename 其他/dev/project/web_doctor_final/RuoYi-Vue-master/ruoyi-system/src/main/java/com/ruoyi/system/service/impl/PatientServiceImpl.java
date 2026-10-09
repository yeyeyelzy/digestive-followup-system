package com.ruoyi.system.service.impl;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.util.List;

import com.ruoyi.common.core.domain.dto.PatientProfileForm;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.system.mapper.PatientUserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.PatientMapper;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.service.IPatientService;
import org.springframework.transaction.annotation.Transactional;

/**
 * 患者管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class PatientServiceImpl implements IPatientService 
{
    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private PatientUserMapper patientUserMapper;

    /**
     * 查询患者管理
     * 
     * @param patientId 患者管理主键
     * @return 患者管理
     */
    @Override
    public Patient selectPatientByPatientId(Long patientId)
    {
        return patientMapper.selectPatientByPatientId(patientId);
    }

    /**
     * 查询患者管理列表
     * 
     * @param patient 患者管理
     * @return 患者管理
     */
    @Override
    public List<Patient> selectPatientList(Patient patient)
    {
        return patientMapper.selectPatientList(patient);
    }

    /**
     * 新增患者管理
     * 
     * @param patient 患者管理
     * @return 结果
     */
    @Override
    public int insertPatient(Patient patient)
    {
        return patientMapper.insertPatient(patient);
    }

    /**
     * 修改患者管理
     * 
     * @param patient 患者管理
     * @return 结果
     */
    @Override
    public int updatePatient(Patient patient)
    {
        return patientMapper.updatePatient(patient);
    }

    /**
     * 批量删除患者管理
     * 
     * @param patientIds 需要删除的患者管理主键
     * @return 结果
     */
    @Override
    public int deletePatientByPatientIds(Long[] patientIds)
    {
        return patientMapper.deletePatientByPatientIds(patientIds);
    }

    /**
     * 删除患者管理信息
     * 
     * @param patientId 患者管理主键
     * @return 结果
     */
    @Override
    public int deletePatientByPatientId(Long patientId)
    {

        return patientMapper.deletePatientByPatientId(patientId);
    }

    @Override
    @Transactional
    public int updatePatientProfile(Long patientId, PatientProfileForm form) { // 【注意参数类型】

        // 1. 年龄计算逻辑
        Long age = null;
        if (form.getBirthday() != null) {
            // 将 java.util.Date 转换为 LocalDate
            LocalDate birthDate = form.getBirthday().toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
            LocalDate currentDate = LocalDate.now();
            age = (long) Period.between(birthDate, currentDate).getYears();
        }

        // 2. 构建 Patient 对象 (patient表)
        Patient patient = new Patient();
        patient.setPatientId(patientId);
        patient.setPhoneNumber(form.getPhoneNumber());
        patient.setAge(age);
        patient.setWeight(form.getWeight()); // 使用 Double 类型
        patient.setGender(form.getGender()); // Long 0/1
        patient.setAvatarUrl(form.getAvatarUrl());

        int resultPatient = patientMapper.updatePatient(patient);

        // 3. 构建 PatientUser 对象 (patient_user表)
        PatientUser patientUser = new PatientUser();
        patientUser.setPatientId(patientId);
        patientUser.setPhonenumber(form.getPhoneNumber());
        patientUser.setAge(age != null ? age.intValue() : null); // age 存储为 Integer

        // 性别映射：PatientUser.sex 字段是 String (0/1)
        if (form.getGender() != null) {
            patientUser.setSex(String.valueOf(form.getGender()));
        }

        int resultUser = patientUserMapper.updatePatientUserFields(patientUser); // 调用 PatientUser Mapper

        // 4. 检查事务结果
        if (resultPatient < 1 || resultUser < 1) {
            throw new RuntimeException("更新患者档案失败，数据可能不一致，事务回滚。");
        }
        return 1;
    }
}

