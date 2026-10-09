package com.ruoyi.system.service;

import com.ruoyi.common.core.domain.entity.PatientUser;

/**
 * 病人用户 业务层
 *
 * @author ruoyi
 */
public interface IPatientUserService
{
    /**
     * 根据病人账号查询病人信息
     * @param patientName 病人账号
     * @return 病人信息
     */
    public PatientUser selectPatientUserByPatientName(String patientName);

    /**
     * 根据病人账号查询病人信息
     * @param patientId 病人账号
     * @return 病人信息
     */
    public PatientUser selectPatientUserByPatientId(Long patientId);

    /**
     * 注册病人信息
     * @param patientUser 病人信息
     * @return 结果
     */
    public boolean registerPatientUser(PatientUser patientUser);

    /**
     * 校验病人账号是否唯一
     * (方法名要和 XML 中的 id 完全一致)
     * @param patientName 病人账号
     * @return 结果 (返回查询到的数量, 对应 XML 的 resultType="int")
     */
    public boolean checkPatientNameUnique(String patientName); // 3. 添加这个缺失的方法声明

    /**
     * 注册患者用户并同步创建患者档案。
     * 这是一个事务性操作。
     *
     * @param patientUser 包含注册信息的患者用户对象
     * @return 注册成功返回true，否则返回false
     */
    public boolean registerUserAndCreatePatientProfile(PatientUser patientUser);

    /**
     * 根据手机号查询
     */
    public PatientUser selectPatientUserByPhonenumber(String phonenumber);
}



