package com.ruoyi.system.service.impl;

import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.service.IPatientService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.system.mapper.PatientUserMapper;
import com.ruoyi.system.service.IPatientUserService;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 病人用户 业务层处理
 *
 * @author ruoyi
 */
@Service
public class PatientUserServiceImpl implements IPatientUserService
{
    @Autowired
    private PatientUserMapper patientUserMapper;
    @Autowired
    private IPatientService patientService;

    @Override
    public PatientUser selectPatientUserByPatientName(String patientName) {
        return patientUserMapper.selectPatientUserByPatientName(patientName);
    }

    @Override
    public PatientUser selectPatientUserByPatientId(Long patientId) {
        return patientUserMapper.selectPatientUserByPatientId(patientId);
    }

    @Override
    public boolean registerPatientUser(PatientUser patientUser) {
        // 检查用户名是否存在
        if (UserConstants.NOT_UNIQUE==(this.checkPatientNameUnique(patientUser.getPatientName()))) {
            // 这里可以抛出自定义异常，例如：throw new UserException("注册账号'" + patientUser.getPatientName() + "'失败，账号已存在");
            return false;
        }
        // 密码加密
        patientUser.setPassword(SecurityUtils.encryptPassword(patientUser.getPassword()));
        return patientUserMapper.insertPatientUser(patientUser) > 0;
    }

    /**
     * 校验病人名称是否唯一
     * @param patientName 用户名称
     * @return 结果
     */
    @Override
    public boolean checkPatientNameUnique(String patientName)
    {
        int count = patientUserMapper.checkPatientNameUnique(patientName);
        if (count > 0)
        {
            return UserConstants.NOT_UNIQUE;
        }
        return UserConstants.UNIQUE;
    }

    /**
     * 【修正】注册患者用户并同步创建患者档案（统一ID版本）。
     * 确保 patient_user.patient_id = patient.patient_id
     */
    @Override
//    @Transactional
    public boolean registerUserAndCreatePatientProfile(PatientUser patientUser) {
        // 1. 检查用户名是否已存在
        if (patientUserMapper.checkPatientNameUnique(patientUser.getPatientName()) > 0) {
            return false; // 用户名已存在
        }

        patientUser.setPassword(SecurityUtils.encryptPassword(patientUser.getPassword()));

        // 2. 【核心】插入 patient_user 记录
        // Mybatis 的 useGeneratedKeys="true" 会将生成的 patient_id 自动赋值给 patientUser 对象
        int userRows = patientUserMapper.insertPatientUser(patientUser);
        if (userRows == 0) {
            throw new RuntimeException("插入患者用户表失败，事务将回滚！");
        }

        // 3. 检查自增ID是否已赋值
        Long unifiedPatientId = patientUser.getPatientId();
        if (unifiedPatientId == null || unifiedPatientId <= 0) {
            throw new RuntimeException("未能获取到生成的患者用户ID，事务回滚！");
        }

        // 4. 创建并插入新的 patient 记录 (档案表)
        Patient newPatient = new Patient();

        // 【核心操作】: 强制设置 patient 表的主键 ID，与 patient_user 的 ID 保持一致！
        newPatient.setPatientId(unifiedPatientId);
        newPatient.setPatientName(patientUser.getPatientName());

        // ... 拷贝其他属性 ...

        int patientRows = patientService.insertPatient(newPatient);
        if (patientRows == 0) {
            throw new RuntimeException("插入患者档案表失败，事务将回滚！");
        }

        return true;
    }

    @Override
    public PatientUser selectPatientUserByPhonenumber(String phonenumber)
    {
        return patientUserMapper.selectPatientUserByPhonenumber(phonenumber);
    }
}
