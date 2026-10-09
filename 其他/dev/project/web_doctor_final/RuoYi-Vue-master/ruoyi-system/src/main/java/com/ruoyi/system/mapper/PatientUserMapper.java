package com.ruoyi.system.mapper;

import com.ruoyi.common.core.domain.entity.PatientUser;
import java.util.List;

/**
 * 病人用户 数据层
 *
 * @author ruoyi
 */
public interface PatientUserMapper
{
    /**
     * 根据条件分页查询病人列表
     * @param patientUser 病人信息
     * @return 病人信息集合信息
     */
    public List<PatientUser> selectPatientUserList(PatientUser patientUser);

    /**
     * 通过病人账号查询病人
     * @param patientName 病人账号
     * @return 病人对象信息
     */
    public PatientUser selectPatientUserByPatientName(String patientName);

    /**
     * 通过病人ID查询病人
     * @param patientId 病人ID
     * @return 病人对象信息
     */
    public PatientUser selectPatientUserByPatientId(Long patientId);

    /**
     * 新增病人信息
     * @param patientUser 病人信息
     * @return 结果
     */
    public int insertPatientUser(PatientUser patientUser);

    /**
     * 修改病人信息
     * @param patientUser 病人信息
     * @return 结果
     */
    public int updatePatientUser(PatientUser patientUser);

    /**
     * 校验病人名称是否唯一
     * @param patientName 用户名称
     * @return 结果 (返回查询到的数量)
     */
    public int checkPatientNameUnique(String patientName);

    /**
     * 【新增】更新 PatientUser 档案中的手机号和性别
     * @param patientUser 包含 patientId, phonenumber, sex 的对象
     * @return 结果
     */
    public int updatePatientUserFields(PatientUser patientUser);

    public PatientUser selectPatientUserByPhonenumber(String phonenumber);
}


