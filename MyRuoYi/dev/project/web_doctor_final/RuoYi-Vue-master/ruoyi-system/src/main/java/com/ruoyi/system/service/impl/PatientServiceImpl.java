package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.PatientMapper;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.service.IPatientService;

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
}
