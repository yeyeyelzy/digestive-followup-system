package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Patient;

/**
 * 患者管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IPatientService 
{
    /**
     * 查询患者管理
     * 
     * @param patientId 患者管理主键
     * @return 患者管理
     */
    public Patient selectPatientByPatientId(Long patientId);

    /**
     * 查询患者管理列表
     * 
     * @param patient 患者管理
     * @return 患者管理集合
     */
    public List<Patient> selectPatientList(Patient patient);

    /**
     * 新增患者管理
     * 
     * @param patient 患者管理
     * @return 结果
     */
    public int insertPatient(Patient patient);

    /**
     * 修改患者管理
     * 
     * @param patient 患者管理
     * @return 结果
     */
    public int updatePatient(Patient patient);

    /**
     * 批量删除患者管理
     * 
     * @param patientIds 需要删除的患者管理主键集合
     * @return 结果
     */
    public int deletePatientByPatientIds(Long[] patientIds);

    /**
     * 删除患者管理信息
     * 
     * @param patientId 患者管理主键
     * @return 结果
     */
    public int deletePatientByPatientId(Long patientId);
}
